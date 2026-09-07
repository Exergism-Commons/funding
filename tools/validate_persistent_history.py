#!/usr/bin/env python3
"""Enforce append-only Funding PIDs and opportunity identifiers across Git history."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
LEGACY_BOOTSTRAP = "knowledge/decisions/ECF-DEC-MRG-BOOTSTRAP-001.jsonld"
OLD_CONTEXT_PATH = "ontology/funding-context.jsonld"
FROZEN_CONTEXT_PATH = "ontology/contexts/funding-context-0.1.0-draft.jsonld"


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def show(ref: str, path: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return result.stdout if result.returncode == 0 else None


def knowledge_paths(ref: str) -> set[str]:
    out = git("ls-tree", "-r", "--name-only", ref, "knowledge")
    return {line for line in out.splitlines() if line.endswith(".jsonld")}


def opportunity_ids(ref: str) -> set[str]:
    raw = show(ref, "data/opportunities.yaml")
    if raw is None:
        return set()
    doc = yaml.safe_load(raw) or {}
    rows = doc.get("opportunities") or []
    result: set[str] = set()
    for row in rows:
        value = row.get("id") if isinstance(row, dict) else None
        if not isinstance(value, str) or not value:
            raise AssertionError(f"{ref}: every opportunity must retain a non-empty id")
        if value in result:
            raise AssertionError(f"{ref}: duplicate opportunity id {value}")
        result.add(value)
    return result


def assert_context_freeze_is_semantics_preserving(base: str, head: str) -> None:
    before_raw = show(base, LEGACY_BOOTSTRAP)
    after_raw = show(head, LEGACY_BOOTSTRAP)
    old_context = show(base, OLD_CONTEXT_PATH)
    frozen_context = show(head, FROZEN_CONTEXT_PATH)
    if None in (before_raw, after_raw, old_context, frozen_context):
        raise AssertionError("legacy bootstrap context-freeze migration is incomplete")

    before = json.loads(before_raw)
    after = json.loads(after_raw)
    before_context = before.pop("@context", None)
    after_context = after.pop("@context", None)
    if before_context != "../../ontology/funding-context.jsonld":
        raise AssertionError("unexpected legacy bootstrap source context")
    if after_context != "../../ontology/contexts/funding-context-0.1.0-draft.jsonld":
        raise AssertionError("legacy bootstrap must point to its frozen 0.1 context")
    if before != after:
        raise AssertionError("legacy bootstrap migration may change only @context location")
    if old_context.encode() != frozen_context.encode():
        raise AssertionError("frozen 0.1 context bytes must equal the context that originally interpreted the record")


def compare_endpoint(base: str, head: str, *, bootstrap_contract: bool) -> None:
    before_paths = knowledge_paths(base)
    after_paths = knowledge_paths(head)
    removed = sorted(before_paths - after_paths)
    if removed:
        raise AssertionError(f"persistent knowledge records cannot disappear: {removed}")

    for path in sorted(before_paths & after_paths):
        before = show(base, path)
        after = show(head, path)
        if before == after:
            continue
        if bootstrap_contract and path == LEGACY_BOOTSTRAP:
            assert_context_freeze_is_semantics_preserving(base, head)
            continue
        raise AssertionError(f"persistent knowledge record changed in place: {path}")

    old_ids = opportunity_ids(base)
    new_ids = opportunity_ids(head)
    removed_ids = sorted(old_ids - new_ids)
    if removed_ids:
        raise AssertionError(
            "published opportunity identifiers cannot be removed/renamed; retain the id and change lifecycle status instead: "
            + ", ".join(removed_ids)
        )


def contract_exists(ref: str) -> bool:
    return show(ref, "tools/validate_persistent_history.py") is not None


def main() -> None:
    base = os.environ.get("EC_FUNDING_HISTORY_BASE", "").strip()
    if not base or set(base) == {"0"}:
        print("no trusted Funding history base supplied; persistence history check skipped")
        return

    git("cat-file", "-e", f"{base}^{{commit}}")

    # One-time introduction mode: establish the append-only contract against the
    # pre-contract base tree. The only mutation permitted to an existing record
    # is the semantics-preserving freeze of bootstrap 001's original JSON-LD
    # context. Once this tool exists in main, every committed transition is
    # checked individually so add-then-delete/rewrite sequences cannot hide in a
    # final-tree diff.
    if not contract_exists(base):
        compare_endpoint(base, "HEAD", bootstrap_contract=True)
        print("Funding persistence contract bootstrap transition verified")
        return

    commits = git("rev-list", "--reverse", "--ancestry-path", f"{base}..HEAD").splitlines()
    previous = base
    for commit in commits:
        compare_endpoint(previous, commit, bootstrap_contract=False)
        previous = commit

    print(f"Funding persistent history verified across {len(commits)} committed transition(s)")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"persistent history validation failed: {exc}", file=sys.stderr)
        raise
