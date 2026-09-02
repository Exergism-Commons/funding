#!/usr/bin/env python3
"""Build the derived Exergism Commons funding-governance RDF graph.

Canonical editable sources remain:
- data/opportunities.yaml for opportunity intelligence;
- knowledge/**/*.jsonld for explicit governance records.

The generated RDF is disposable and must be reproducible from those sources.
"""

from __future__ import annotations

import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

import yaml
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD


ROOT = Path(__file__).resolve().parents[1]
VOCABULARY_NAMESPACE = "https://id.exergism.org/funding#"
ONTOLOGY_IRI = "https://id.exergism.org/ontology/funding"
RECORD_BASE = "https://id.exergism.org/funding/id/"
ECF = Namespace(VOCABULARY_NAMESPACE)

DIMENSION_PREDICATES = {
    "fit": ECF.fit,
    "funding_value": ECF.fundingValue,
    "capability_value": ECF.capabilityValue,
    "strategic_optional ity": ECF.strategicOptionality,
    "autonomy_value": ECF.autonomyValue,
    "network_value": ECF.networkValue,
    "recurrence": ECF.recurrence,
    "capture_risk": ECF.captureRisk,
    "admin_cost": ECF.adminCost,
    "execution_risk": ECF.executionRisk,
}


def stable_token(value: str) -> str:
    token = re.sub(r"[^A-Z0-9]+", "-", value.upper()).strip("-")
    if not token:
        raise ValueError(f"cannot derive stable token from {value!r}")
    return token


def decimal_score(value, key: str, opportunity_id: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{opportunity_id}: {key} must be numeric")
    score = Decimal(str(value))
    if score < 0 or score > 1:
        raise ValueError(f"{opportunity_id}: {key} must be in [0,1]")
    return score


def load_opportunity_graph(path: Path) -> tuple[Graph, dict]:
    raw = path.read_bytes()
    document = yaml.safe_load(raw)
    if not isinstance(document, dict):
        raise ValueError("opportunity registry must be a mapping")

    scoring = document.get("scoring") or {}
    required = scoring.get("required_dimensions") or []
    expected = list(DIMENSION_PREDICATES)
    if required != expected:
        raise ValueError(
            "scoring.required_dimensions must exactly match the machine-governance "
            f"dimension order; expected {expected!r}, got {required!r}"
        )

    opportunities = document.get("opportunities") or []
    if not isinstance(opportunities, list):
        raise ValueError("opportunities must be a list")

    graph = Graph()
    seen = set()
    rank_eligible_count = 0

    for opportunity in opportunities:
        if not isinstance(opportunity, dict):
            raise ValueError("every opportunity must be a mapping")
        raw_id = opportunity.get("id")
        name = opportunity.get("name")
        if not isinstance(raw_id, str) or not raw_id:
            raise ValueError("every opportunity requires a non-empty id")
        if not isinstance(name, str) or not name:
            raise ValueError(f"{raw_id}: name is required")

        stable_id = f"ECF-OPP-{stable_token(raw_id)}"
        if stable_id in seen:
            raise ValueError(f"duplicate derived stable ID: {stable_id}")
        seen.add(stable_id)
        subject = URIRef(f"{RECORD_BASE}{stable_id}")

        graph.add((subject, RDF.type, ECF.FundingOpportunity))
        graph.add((subject, ECF.stableId, Literal(stable_id)))
        graph.add((subject, ECF.title, Literal(name)))
        graph.add((subject, ECF.provenance, Literal(f"data/opportunities.yaml#{raw_id}")))

        if isinstance(opportunity.get("status"), str):
            graph.add((subject, ECF.status, Literal(opportunity["status"])))

        complete = True
        parsed_scores: dict[str, Decimal] = {}
        for key in required:
            if key not in opportunity:
                complete = False
                continue
            parsed_scores[key] = decimal_score(opportunity[key], key, raw_id)

        graph.add((subject, ECF.rankEligible, Literal(complete, datatype=XSD.boolean)))
        if complete:
            rank_eligible_count += 1

        for key, score in parsed_scores.items():
            graph.add((subject, DIMENSION_PREDICATES[key], Literal(score, datatype=XSD.decimal)))

    metadata = {
        "schema_version": document.get("schema_version"),
        "source": "data/opportunities.yaml",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "opportunity_count": len(opportunities),
        "rank_eligible_count": rank_eligible_count,
        "vocabulary_namespace": VOCABULARY_NAMESPACE,
        "ontology_iri": ONTOLOGY_IRI,
        "record_base": RECORD_BASE,
    }
    return graph, metadata


def load_canonical_knowledge(directory: Path) -> tuple[Graph, int]:
    graph = Graph()
    paths = sorted(directory.rglob("*.jsonld"))
    for path in paths:
        graph.parse(path.as_posix(), format="json-ld")
    return graph, len(paths)


def sorted_ntriples(graph: Graph) -> str:
    serialized = graph.serialize(format="nt")
    lines = sorted(line for line in serialized.splitlines() if line.strip())
    return "\n".join(lines) + "\n"


def build(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    graph, metadata = load_opportunity_graph(ROOT / "data" / "opportunities.yaml")
    knowledge, knowledge_count = load_canonical_knowledge(ROOT / "knowledge")
    graph += knowledge

    nt = sorted_ntriples(graph)
    nt_path = output_dir / "funding-governance.nt"
    ttl_path = output_dir / "funding-governance.ttl"
    manifest_path = output_dir / "funding-governance-build.json"

    nt_path.write_text(nt, encoding="utf-8")
    graph.serialize(destination=ttl_path.as_posix(), format="turtle")

    manifest = {
        **metadata,
        "knowledge_record_count": knowledge_count,
        "triple_count": len(graph),
        "rdf_sha256": hashlib.sha256(nt.encode("utf-8")).hexdigest(),
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="build", type=Path)
    args = parser.parse_args()
    manifest = build(args.output_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
