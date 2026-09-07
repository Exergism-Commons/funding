#!/usr/bin/env python3
"""Fail closed when canonical Funding review obligations are overdue."""

from __future__ import annotations

from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "knowledge"


def evaluation_date() -> date:
    override = os.environ.get("EC_FUNDING_VALIDATION_DATE", "").strip()
    if override:
        return date.fromisoformat(override)
    return datetime.now(timezone.utc).date()


def validate_document(path: Path, on_date: date) -> list[str]:
    document = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    review_due = document.get("reviewDue")
    if review_due is not None:
        if not isinstance(review_due, str):
            errors.append(f"{path}: reviewDue must be an ISO date string")
        else:
            try:
                due = date.fromisoformat(review_due)
            except ValueError:
                errors.append(f"{path}: invalid reviewDue {review_due!r}")
            else:
                if due < on_date:
                    errors.append(
                        f"{path}: reviewDue {due.isoformat()} is overdue on {on_date.isoformat()}; "
                        "supersede/review the canonical record instead of carrying an expired state"
                    )

    target_date = document.get("targetDate")
    if review_due is not None and target_date is not None:
        try:
            due = date.fromisoformat(review_due)
            target = date.fromisoformat(target_date)
        except (TypeError, ValueError):
            pass
        else:
            if due > target:
                errors.append(f"{path}: reviewDue must not be later than targetDate")
    return errors


def validate_knowledge(on_date: date | None = None) -> list[str]:
    on_date = on_date or evaluation_date()
    errors: list[str] = []
    for path in sorted(KNOWLEDGE.rglob("*.jsonld")):
        errors.extend(validate_document(path, on_date))
    return errors


def main() -> None:
    on_date = evaluation_date()
    errors = validate_knowledge(on_date)
    if errors:
        print("Funding temporal-governance validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Funding review deadlines are current as of {on_date.isoformat()}")


if __name__ == "__main__":
    main()
