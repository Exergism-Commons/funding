#!/usr/bin/env python3
"""Enforce the canonical form of Funding knowledge records.

Each file under knowledge/ is one persistent record, published as one document
at https://id.exergism.org/funding/id/{stableId}. Its RDF interpretation must
therefore describe exactly one subject, the record's own @id, in the default
graph. Anything else would be invisible to the other validators (rdflib's
Graph keeps only the default graph) while the exporter still publishes it, or
would attach triples to other records, including frozen ones.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

from rdflib import Dataset, URIRef

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "knowledge"


def validate_record(path: Path) -> list[str]:
    document = json.loads(path.read_text(encoding="utf-8"))
    record_iri = document.get("@id") if isinstance(document, dict) else None
    if not isinstance(record_iri, str) or not record_iri:
        return [f"{path}: a canonical record must be a JSON object with a root @id"]
    subject = URIRef(record_iri)

    dataset = Dataset()
    dataset.parse(path.as_posix(), format="json-ld")
    errors: list[str] = []
    own_triples = 0
    for s, p, o, graph in dataset.quads((None, None, None, None)):
        if graph != dataset.default_graph.identifier:
            errors.append(f"{path}: content in named graph <{graph}>: {s.n3()} {p.n3()} {o.n3()}")
        elif s != subject:
            errors.append(f"{path}: record <{record_iri}> also describes {s.n3()} via {p.n3()}")
        else:
            own_triples += 1
    if own_triples == 0:
        errors.append(f"{path}: record <{record_iri}> has no triples about itself")
    return errors


def validate_knowledge() -> list[str]:
    errors: list[str] = []
    for path in sorted(KNOWLEDGE.rglob("*.jsonld")):
        errors.extend(validate_record(path))
    return errors


def main() -> None:
    errors = validate_knowledge()
    if errors:
        print("Canonical Funding record form validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    print("Canonical Funding records describe exactly their own IRI in the default graph")


if __name__ == "__main__":
    main()
