#!/usr/bin/env python3
"""Verify content-addressed evidence referenced by canonical Funding records.

Bindings are read from the record's RDF interpretation, not from the top-level
JSON mapping, so every node that SHACL sees is checked: nodes inside @graph,
nested objects and aliased keys alike.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys

from rdflib import Graph, Literal, URIRef

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "knowledge"
VOCABULARY_NAMESPACE = "https://id.exergism.org/funding#"
EVIDENCE_PATH = URIRef(VOCABULARY_NAMESPACE + "concentrationEvidencePath")
EVIDENCE_SHA256 = URIRef(VOCABULARY_NAMESPACE + "concentrationEvidenceSha256")


def _single_string(graph: Graph, subject, predicate) -> str | None:
    values = list(graph.objects(subject, predicate))
    if len(values) != 1 or not isinstance(values[0], Literal):
        return None
    return str(values[0])


def validate_binding(label: str, evidence_path: str | None, evidence_sha: str | None, *, repository_root: Path) -> list[str]:
    if evidence_path is None or not evidence_path.strip():
        return [f"{label}: concentrationEvidencePath must be exactly one non-empty repository-relative path"]
    if evidence_sha is None or len(evidence_sha) != 64:
        return [f"{label}: concentrationEvidenceSha256 must be exactly one 64-character SHA-256 hex digest"]
    try:
        int(evidence_sha, 16)
    except ValueError:
        return [f"{label}: concentrationEvidenceSha256 is not hexadecimal"]

    root = repository_root.resolve()
    candidate = (root / evidence_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return [f"{label}: concentration evidence escapes the repository: {evidence_path}"]
    if not candidate.is_file():
        return [f"{label}: concentration evidence does not exist: {evidence_path}"]
    actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
    if actual != evidence_sha:
        return [f"{label}: concentration evidence SHA-256 mismatch: got {actual}, expected {evidence_sha}"]
    return []


def validate_record(path: Path, *, repository_root: Path = ROOT) -> list[str]:
    graph = Graph().parse(path.as_posix(), format="json-ld")
    bound = set(graph.subjects(EVIDENCE_PATH, None)) | set(graph.subjects(EVIDENCE_SHA256, None))
    errors: list[str] = []
    for subject in sorted(bound):
        errors.extend(
            validate_binding(
                f"{path} <{subject}>",
                _single_string(graph, subject, EVIDENCE_PATH),
                _single_string(graph, subject, EVIDENCE_SHA256),
                repository_root=repository_root,
            )
        )
    return errors


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
