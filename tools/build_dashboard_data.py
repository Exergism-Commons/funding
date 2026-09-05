#!/usr/bin/env python3
"""Build public dashboard JSON from canonical funding and proposal sources."""

from __future__ import annotations

import argparse
import json
import math
import re
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
ALLOWED_PROPOSAL_STATUSES = {"scoping", "drafting", "submitted", "awarded", "rejected"}
TERMINAL_PROPOSAL_STATUSES = {"awarded", "rejected"}
CURRENCY_CODE = re.compile(r"^[A-Z]{3}$")


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
    """Return a GitHub blob URL only for an existing file inside this repository."""
    if not path:
        return None
    if not isinstance(path, str):
        raise ValueError(f"Repository path must be a string, got {type(path).__name__}")

    relative = Path(path)
    if relative.is_absolute():
        raise ValueError(f"Repository path must be relative: {path!r}")

    target = (ROOT / relative).resolve()
    try:
        normalized = target.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"Repository path escapes the repository root: {path!r}") from exc

    if not target.is_file():
        raise ValueError(f"Repository path does not resolve to an existing file: {path!r}")

    return REPOSITORY_BLOB_BASE + normalized.as_posix()


def display_path(path: Path) -> str:
    """Display repository-relative paths when possible, otherwise the absolute path."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def opportunity_index(source: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for opportunity in source.get("opportunities", []):
        if not isinstance(opportunity, dict):
            raise ValueError("Every opportunity must be a mapping")
        opportunity_id = opportunity.get("id")
        if not isinstance(opportunity_id, str) or not opportunity_id:
            raise ValueError("Every opportunity must have a non-empty string id")
        if opportunity_id in index:
            raise ValueError(f"Duplicate opportunity id: {opportunity_id}")
        index[opportunity_id] = opportunity
    return index


def build_opportunities() -> dict[str, Any]:
    source = load_yaml(ROOT / "data" / "opportunities.yaml")
    rows: list[dict[str, Any]] = []

    for opportunity in opportunity_index(source).values():
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
    proposal_ids: set[str] = set()
    metadata_files = sorted((ROOT / "proposals").glob("*/proposal.yaml"))
    opportunity_source = load_yaml(ROOT / "data" / "opportunities.yaml")
    opportunities = opportunity_index(opportunity_source)
    default_currency = opportunity_source.get("currency_default")
    if not isinstance(default_currency, str) or not CURRENCY_CODE.fullmatch(default_currency):
        raise ValueError(
            "data/opportunities.yaml: currency_default must be a three-letter uppercase code"
        )

    for path in metadata_files:
        proposal = load_yaml(path)
        proposal_id = proposal.get("id")
        if not isinstance(proposal_id, str) or not proposal_id:
            raise ValueError(f"{path}: proposal must have a non-empty string id")
        if proposal_id != path.parent.name:
            raise ValueError(
                f"{path}: proposal id {proposal_id!r} must match directory name {path.parent.name!r}"
            )
        if proposal_id in proposal_ids:
            raise ValueError(f"Duplicate proposal id: {proposal_id}")
        proposal_ids.add(proposal_id)

        status = proposal.get("status")
        if not isinstance(status, str) or not status:
            raise ValueError(f"{proposal_id}: proposal must have a non-empty string status")
        if status not in ALLOWED_PROPOSAL_STATUSES:
            raise ValueError(f"{proposal_id}: invalid proposal status {status!r}")

        currency = proposal.get("currency", default_currency)
        if not isinstance(currency, str) or not CURRENCY_CODE.fullmatch(currency):
            raise ValueError(
                f"{proposal_id}: currency must be a three-letter uppercase code, got {currency!r}"
            )

        requested_amount = proposal.get("requested_amount")
        if requested_amount is not None:
            if isinstance(requested_amount, bool) or not isinstance(requested_amount, (int, float)):
                raise ValueError(
                    f"{proposal_id}: requested_amount must be null or a numeric value, got {requested_amount!r}"
                )
            if not math.isfinite(requested_amount) or requested_amount < 0:
                raise ValueError(
                    f"{proposal_id}: requested_amount must be finite and non-negative, got {requested_amount!r}"
                )

        opportunity_id = proposal.get("opportunity_id")
        if not isinstance(opportunity_id, str) or not opportunity_id:
            raise ValueError(f"{proposal_id}: proposal must reference an opportunity_id")
        if opportunity_id not in opportunities:
            raise ValueError(f"{proposal_id}: unknown opportunity_id {opportunity_id!r}")

        opportunity = opportunities[opportunity_id]
        sources = opportunity.get("sources") or []
        rows.append(
            {
                "id": proposal_id,
                "opportunity_id": opportunity_id,
                "title": proposal["title"],
                "funder": opportunity.get("funder"),
                "fund": proposal.get("fund"),
                "status": status,
                "updated": scalar(proposal.get("updated")),
                "deadline": scalar(opportunity.get("deadline")),
                "currency": currency,
                "requested_amount": requested_amount,
                "summary": proposal.get("summary"),
                "next_action": proposal.get("next_action"),
                "links": {
                    "proposal": github_blob(proposal.get("proposal_path")),
                    "budget": github_blob(proposal.get("budget_path")),
                    "provenance": github_blob(proposal.get("provenance_path")),
                    "source": sources[0] if sources else None,
                },
            }
        )

    rows.sort(key=lambda item: item["id"])
    updated_values = [row["updated"] for row in rows if row.get("updated")]
    return {
        "schema_version": 3,
        "updated": max(updated_values) if updated_values else None,
        "classification": {
            "statuses": sorted(ALLOWED_PROPOSAL_STATUSES),
            "terminal_statuses": sorted(TERMINAL_PROPOSAL_STATUSES),
            "description": "Proposal lifecycle states are controlled; terminal states are excluded from the active dashboard view.",
        },
        "proposals": rows,
    }


def encoded(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def emit(path: Path, payload: dict[str, Any], check: bool) -> bool:
    expected = encoded(payload)
    label = display_path(path)
    if check:
        actual = path.read_text(encoding="utf-8") if path.exists() else None
        if actual != expected:
            print(f"out of date: {label}")
            return False
        print(f"current: {label}")
        return True

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(expected, encoding="utf-8")
    print(f"wrote: {label}")
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
