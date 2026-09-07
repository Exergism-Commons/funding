#!/usr/bin/env python3
"""Verify content-addressed evidence referenced by canonical Funding records."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "knowledge"


def validate_record(path: Path, *, repository_root: Path = ROOT) -> list[str]:
    document = json.loads(path.read_text(encoding="utf-8"))
    evidence_path = document.get("concentrationEvidencePath")
    evidence_sha = document.get("concentrationEvidenceSha256")
    if evidence_path is None and evidence_sha is None:
        return []
    if not isinstance(evidence_path, str) or not evidence_path.strip():
        return [f"{path}: concentrationEvidencePath must be a non-empty repository-relative path"]
    if not isinstance(evidence_sha, str) or len(evidence_sha) != 64:
        return [f"{path}: concentrationEvidenceSha256 must be a 64-character SHA-256 hex digest"]
    try:
        int(evidence_sha, 16)
    except ValueError:
        return [f"{path}: concentrationEvidenceSha256 is not hexadecimal"]

    root = repository_root.resolve()
    candidate = (root / evidence_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return [f"{path}: concentration evidence escapes the repository: {evidence_path}"]
    if not candidate.is_file():
        return [f"{path}: concentration evidence does not exist: {evidence_path}"]
    actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
    if actual != evidence_sha:
        return [f"{path}: concentration evidence SHA-256 mismatch: got {actual}, expected {evidence_sha}"]
    return []


def validate_knowledge() -> list[str]:
    errors: list[str] = []
    for path in sorted(KNOWLEDGE.rglob("*.jsonld")):
        errors.extend(validate_record(path))
    return errors


def main() -> None:
    errors = validate_knowledge()
    if errors:
        print("Funding evidence-binding validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    print("Canonical Funding evidence bindings verified")


if __name__ == "__main__":
    main()
