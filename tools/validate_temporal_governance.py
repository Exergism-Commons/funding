#!/usr/bin/env python3
"""Fail closed when canonical Funding review obligations are overdue.

Dates are read from the record's RDF interpretation (every node, every graph),
so aliased keys, full-IRI keys and embedded nodes are checked just like the
conventional top-level ``reviewDue`` key.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
import os
from pathlib import Path
import sys

from rdflib import Dataset, Literal, URIRef

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "knowledge"
REVIEW_DUE = (
    URIRef("https://id.exergism.org/commons#reviewDue"),
    # Interpretation of the frozen 0.1.0-draft context (ECF-DEC-MRG-BOOTSTRAP-001).
    URIRef("https://id.exergism.org/funding#reviewDue"),
)
TARGET_DATE = URIRef("https://id.exergism.org/funding#targetDate")


def evaluation_date() -> date:
    override = os.environ.get("EC_FUNDING_VALIDATION_DATE", "").strip()
    if override:
        return date.fromisoformat(override)
    return datetime.now(timezone.utc).date()


def _dates(dataset: Dataset, subject, predicate, label: str, errors: list[str]) -> list[date]:
    parsed: list[date] = []
    for value in dataset.objects(subject, predicate):
        if not isinstance(value, Literal):
            errors.append(f"{label}: {predicate.n3()} must be an ISO date literal")
            continue
        try:
            parsed.append(date.fromisoformat(str(value)))
        except ValueError:
            errors.append(f"{label}: invalid {predicate.n3()} {str(value)!r}")
    return parsed


def validate_document(path: Path, on_date: date) -> list[str]:
    dataset = Dataset(default_union=True)
    dataset.parse(path.as_posix(), format="json-ld")
    errors: list[str] = []
    subjects = {s for predicate in (*REVIEW_DUE, TARGET_DATE) for s in dataset.subjects(predicate, None)}
    for subject in sorted(subjects):
        label = f"{path} <{subject}>"
        review_dates = [due for predicate in REVIEW_DUE for due in _dates(dataset, subject, predicate, label, errors)]
        target_dates = _dates(dataset, subject, TARGET_DATE, label, errors)
        for due in review_dates:
            if due < on_date:
                errors.append(
                    f"{label}: reviewDue {due.isoformat()} is overdue on {on_date.isoformat()}; "
                    "supersede/review the canonical record instead of carrying an expired state"
                )
            if any(due > target for target in target_dates):
                errors.append(f"{label}: reviewDue must not be later than targetDate")
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
