#!/usr/bin/env python3
"""Build deterministic public Funding representations for id.exergism.org.

The Funding repository owns this transform. The identifier service may publish
its outputs, but must not invent or reinterpret Funding semantics itself.
"""

from __future__ import annotations

import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]
RECORD_BASE = "https://id.exergism.org/funding/id/"
LEGACY_CONTEXT_IRI = "https://id.exergism.org/context/funding/0.1.0-draft"
CURRENT_CONTEXT_IRI = "https://id.exergism.org/context/funding/0.2.0-pre1"
LEGACY_SOURCE_CONTEXT = "../../ontology/contexts/funding-context-0.1.0-draft.jsonld"
CURRENT_SOURCE_CONTEXT = "../../ontology/funding-context.jsonld"

DIMENSIONS = (
    ("fit", "fit"),
    ("funding_value", "fundingValue"),
    ("capability_value", "capabilityValue"),
    ("strategic_optionality", "strategicOptionality"),
    ("autonomy_value", "autonomyValue"),
    ("network_value", "networkValue"),
    ("recurrence", "recurrence"),
    ("capture_risk", "captureRisk"),
    ("admin_cost", "adminCost"),
    ("execution_risk", "executionRisk"),
)


def stable_token(value: str) -> str:
    token = re.sub(r"[^A-Z0-9]+", "-", value.upper()).strip("-")
    if not token:
        raise ValueError(f"cannot derive stable token from {value!r}")
    return token


def score(value, key: str, opportunity_id: str):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{opportunity_id}: {key} must be numeric")
    parsed = Decimal(str(value))
    if parsed < 0 or parsed > 1:
        raise ValueError(f"{opportunity_id}: {key} must be in [0,1]")
    return value


def write_json(path: Path, document: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def export_knowledge(output_dir: Path) -> list[dict]:
    artifacts: list[dict] = []
    for source in sorted((ROOT / "knowledge").rglob("*.jsonld")):
        document = json.loads(source.read_text(encoding="utf-8"))
        stable_id = document.get("id")
        if not isinstance(stable_id, str) or not stable_id:
            raise ValueError(f"{source}: missing stable id")
        if document.get("@id") != RECORD_BASE + stable_id:
            raise ValueError(f"{source}: canonical @id does not match stable id")

        source_context = document.get("@context")
        if source_context == LEGACY_SOURCE_CONTEXT:
            document["@context"] = LEGACY_CONTEXT_IRI
        elif source_context == CURRENT_SOURCE_CONTEXT:
            document["@context"] = CURRENT_CONTEXT_IRI
        else:
            raise ValueError(f"{source}: unsupported publication context {source_context!r}")

        target = output_dir / "records" / f"{stable_id}.jsonld"
        write_json(target, document)
        artifacts.append(
            {
                "kind": "record",
                "stable_id": stable_id,
                "source_path": source.relative_to(ROOT).as_posix(),
                "output_path": target.relative_to(output_dir).as_posix(),
            }
        )
    return artifacts


def export_opportunities(output_dir: Path) -> list[dict]:
    source = ROOT / "data" / "opportunities.yaml"
    document = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("opportunity registry must be a mapping")
    required = list((document.get("scoring") or {}).get("required_dimensions") or [])
    expected = [source_key for source_key, _ in DIMENSIONS]
    if required != expected:
        raise ValueError(f"required scoring dimensions changed: expected {expected!r}, got {required!r}")

    opportunities = document.get("opportunities") or []
    if not isinstance(opportunities, list):
        raise ValueError("opportunities must be a list")

    artifacts: list[dict] = []
    seen: set[str] = set()
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
        complete = all(key in opportunity for key in required)
        record = {
            "@context": CURRENT_CONTEXT_IRI,
            "@id": RECORD_BASE + stable_id,
            "@type": "FundingOpportunity",
            "id": stable_id,
            "title": name,
        }
        if isinstance(opportunity.get("status"), str):
            record["status"] = opportunity["status"]
        record["provenance"] = f"data/opportunities.yaml#{raw_id}"
        record["rankEligible"] = complete
        for source_key, public_key in DIMENSIONS:
            if source_key in opportunity:
                record[public_key] = score(opportunity[source_key], source_key, raw_id)
        target = output_dir / "records" / f"{stable_id}.jsonld"
        write_json(target, record)
        artifacts.append(
            {
                "kind": "derived-opportunity",
                "stable_id": stable_id,
                "source_path": "data/opportunities.yaml",
                "source_fragment": raw_id,
                "output_path": target.relative_to(output_dir).as_posix(),
            }
        )
    return artifacts


def copy_exact(source: Path, target: Path) -> dict:
    target.parent.mkdir(parents=True, exist_ok=True)
    data = source.read_bytes()
    target.write_bytes(data)
    return {
        "source_path": source.relative_to(ROOT).as_posix(),
        "output_path": target.as_posix(),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def build(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    exact = []
    for source, relative_target in (
        (ROOT / "ontology" / "funding.owl.ttl", Path("ontology/funding-0.2.0-pre1.ttl")),
        (ROOT / "ontology" / "contexts" / "funding-context-0.1.0-draft.jsonld", Path("contexts/funding-context-0.1.0-draft.jsonld")),
        (ROOT / "ontology" / "contexts" / "funding-context-0.2.0-pre1.jsonld", Path("contexts/funding-context-0.2.0-pre1.jsonld")),
    ):
        entry = copy_exact(source, output_dir / relative_target)
        entry["output_path"] = relative_target.as_posix()
        exact.append(entry)

    artifacts = export_knowledge(output_dir) + export_opportunities(output_dir)
    for artifact in artifacts:
        path = output_dir / artifact["output_path"]
        artifact["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()

    manifest = {
        "schema_version": 1,
        "publication_version": "0.2.0-pre1",
        "ontology_version_iri": "https://id.exergism.org/ontology/funding/0.2.0-pre1",
        "contexts": {
            "legacy": LEGACY_CONTEXT_IRI,
            "current": CURRENT_CONTEXT_IRI,
        },
        "exact_artifacts": exact,
        "records": sorted(artifacts, key=lambda item: item["stable_id"]),
    }
    write_json(output_dir / "manifest.json", manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("build/publication"))
    args = parser.parse_args()
    build(args.output_dir)
    print(args.output_dir)


if __name__ == "__main__":
    main()
