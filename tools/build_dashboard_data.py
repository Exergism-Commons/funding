#!/usr/bin/env python3
"""Build public dashboard JSON from canonical funding and proposal sources."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "docs" / "data"
REPOSITORY_BLOB_BASE = "https://github.com/Exergism-Commons/funding/blob/main/"

POSITIVE_DIMENSIONS = [
    "fit",
    "funding_value",
    "capability_value",
    "strategic_optionality",
    "autonomy_value",
    "network_value",
    "recurrence",
]
NEGATIVE_DIMENSIONS = ["capture_risk", "admin_cost", "execution_risk"]
DISPLAY_OVERRIDES = {
    "horizon_europe": "Horizon Europe",
}
ALLOWED_KINDS = {"funding_call", "network_call", "strategic_engagement"}
ALLOWED_STATUSES = {"forthcoming", "open", "continuous", "closed", "cancelled"}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return data


def scalar(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def humanize(value: Any) -> Any:
    value = scalar(value)
    if not isinstance(value, str):
        return value
    if value in DISPLAY_OVERRIDES:
        return DISPLAY_OVERRIDES[value]
    return value.replace("_", " ").strip().capitalize()


def github_blob(path: str | None) -> str | None:
    if not path:
        return None
    return REPOSITORY_BLOB_BASE + path.lstrip("/")


def build_opportunities() -> dict[str, Any]:
    source = load_yaml(ROOT / "data" / "opportunities.yaml")
    rows: list[dict[str, Any]] = []

    for opportunity in source.get("opportunities", []):
        if not isinstance(opportunity, dict):
            raise ValueError("Every opportunity must be a mapping")

        kind = opportunity.get("kind")
        status = opportunity.get("status")
        if kind not in ALLOWED_KINDS:
            raise ValueError(f"{opportunity.get('id')}: invalid opportunity kind {kind!r}")
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"{opportunity.get('id')}: invalid opportunity status {status!r}")

        sources = opportunity.get("sources") or []
        funding = opportunity.get("funding") or {}
        row = {
            "id": opportunity["id"],
            "kind": kind,
            "name": opportunity["name"],
            "funder": opportunity.get("funder"),
            "programme": opportunity.get("programme"),
            "status": status,
            "opens": scalar(opportunity.get("opens")),
            "deadline": scalar(opportunity.get("deadline")),
            "geography": humanize(opportunity.get("geography")),
            "ec_role": humanize(opportunity.get("ec_role")),
            "priority": opportunity.get("priority"),
            **{key: opportunity.get(key) for key in POSITIVE_DIMENSIONS + NEGATIVE_DIMENSIONS},
            "funding_note": funding.get("note"),
            "next_action": opportunity.get("next_action"),
            "dossier": github_blob(opportunity.get("dossier_path")),
            "source": sources[0] if sources else None,
        }
        rows.append(row)

    rows.sort(key=lambda item: item["id"])
    return {
        "schema_version": 3,
        "updated": scalar(source.get("updated")),
        "classification": {
            "kinds": sorted(ALLOWED_KINDS),
            "statuses": sorted(ALLOWED_STATUSES),
            "description": "Kind, lifecycle status and EC priority are independent classification axes.",
        },
        "heuristic": {
            "positive_dimensions": POSITIVE_DIMENSIONS,
            "negative_dimensions": NEGATIVE_DIMENSIONS,
            "description": "Indicative signal only: average positive value and inverted average risk receive equal weight. It is not a governance decision or probability of award.",
        },
        "opportunities": rows,
    }


def build_proposals() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    metadata_files = sorted((ROOT / "proposals").glob("*/proposal.yaml"))

    for path in metadata_files:
        proposal = load_yaml(path)
        rows.append(
            {
                "id": proposal["id"],
                "opportunity_id": proposal.get("opportunity_id"),
                "title": proposal["title"],
                "funder": proposal.get("funder"),
                "fund": proposal.get("fund"),
                "status": scalar(proposal.get("status")),
                "updated": scalar(proposal.get("updated")),
                "deadline": scalar(proposal.get("deadline")),
                "currency": proposal.get("currency", "EUR"),
                "requested_amount": proposal.get("requested_amount"),
                "summary": proposal.get("summary"),
                "next_action": proposal.get("next_action"),
                "links": {
                    "proposal": github_blob(proposal.get("proposal_path")),
                    "budget": github_blob(proposal.get("budget_path")),
                    "provenance": github_blob(proposal.get("provenance_path")),
                    "source": proposal.get("source"),
                },
            }
        )

    rows.sort(key=lambda item: item["id"])
    updated_values = [row["updated"] for row in rows if row.get("updated")]
    return {
        "schema_version": 2,
        "updated": max(updated_values) if updated_values else None,
        "proposals": rows,
    }


def encoded(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def emit(path: Path, payload: dict[str, Any], check: bool) -> bool:
    expected = encoded(payload)
    if check:
        actual = path.read_text(encoding="utf-8") if path.exists() else None
        if actual != expected:
            print(f"out of date: {path.relative_to(ROOT)}")
            return False
        print(f"current: {path.relative_to(ROOT)}")
        return True

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(expected, encoding="utf-8")
    print(f"wrote: {path.relative_to(ROOT)}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if checked-in dashboard JSON is stale")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir

    results = [
        emit(output_dir / "opportunities.json", build_opportunities(), args.check),
        emit(output_dir / "proposals.json", build_proposals(), args.check),
    ]
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
