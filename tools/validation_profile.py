#!/usr/bin/env python3
"""Compose and run the complete Funding validation profile.

The SHACL profile resolves term declarations and class membership from the
data graph, so it is only sound when every schema-level triple in that graph
comes from the trusted, vendored ontologies. Hosted ABox data is therefore
checked for schema-level triples *before* it is merged with the ontologies:
a record cannot declare Funding terms for itself, mint subclasses that combine
roles, or describe vocabulary terms. Live CI and the test suite both validate
through this module so they cannot drift onto a weaker profile.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from pyshacl import validate as shacl_validate
from rdflib import Graph, Namespace, RDF, URIRef
from rdflib.namespace import OWL, RDFS


ROOT = Path(__file__).resolve().parents[1]
DEPENDENCIES = ROOT / "ontology" / "dependencies"
TRUSTED_ONTOLOGIES = (
    DEPENDENCIES / "commons.ttl",
    DEPENDENCIES / "governance.ttl",
    ROOT / "ontology" / "funding.owl.ttl",
)
SHAPES = (
    ROOT / "ontology" / "funding.shacl.ttl",
    DEPENDENCIES / "governance-shapes.ttl",
    ROOT / "ontology" / "funding-authority.shacl.ttl",
)

SH = Namespace("http://www.w3.org/ns/shacl#")
ECF = Namespace("https://id.exergism.org/funding#")
VOCABULARY_NAMESPACES = (
    "https://id.exergism.org/commons#",
    "https://id.exergism.org/governance#",
    "https://id.exergism.org/funding#",
)
# RDFS annotations such as rdfs:label stay usable; only its schema predicates
# are reserved. Every OWL and SHACL predicate is schema-level in hosted data.
SCHEMA_PREDICATES = {
    RDFS.subClassOf,
    RDFS.subPropertyOf,
    RDFS.domain,
    RDFS.range,
}
SCHEMA_PREDICATE_NAMESPACES = (str(OWL), str(SH))
SCHEMA_TYPE_NAMESPACES = (str(RDFS), str(OWL), str(SH))
SCHEMA_TYPES = {RDF.Property}


def _in_namespace(term, namespaces: tuple[str, ...]) -> bool:
    return isinstance(term, URIRef) and str(term).startswith(namespaces)


def abox_schema_violations(abox: Graph) -> list[str]:
    """Return every schema-level triple in hosted ABox data."""
    violations: list[str] = []
    for subject, predicate, value in sorted(abox):
        if _in_namespace(subject, VOCABULARY_NAMESPACES):
            reason = "describes a vocabulary term"
        elif predicate in SCHEMA_PREDICATES or _in_namespace(predicate, SCHEMA_PREDICATE_NAMESPACES):
            reason = "uses a schema predicate"
        elif predicate == RDF.type and (value in SCHEMA_TYPES or _in_namespace(value, SCHEMA_TYPE_NAMESPACES)):
            reason = "declares a schema type"
        else:
            continue
        violations.append(f"{subject.n3()} {predicate.n3()} {value.n3()} ({reason})")
    return violations


def schema_violation_message(violations: list[str]) -> str:
    return "hosted ABox data may not contain schema-level triples:\n" + "\n".join(
        f"- {violation}" for violation in violations
    )


def validate_abox(abox: Graph, *, fixture: bool = False):
    """Validate hosted ABox data against the trusted ontologies and all shapes.

    Returns the pyshacl ``(conforms, results_graph, report_text)`` tuple; a
    schema-level triple in the ABox is reported as a non-conforming result.
    """
    violations = abox_schema_violations(abox)
    if violations:
        return False, None, schema_violation_message(violations)

    data = Graph()
    for triple in abox:
        data.add(triple)
    for path in TRUSTED_ONTOLOGIES:
        data.parse(path.as_posix(), format="turtle")

    shapes = Graph()
    for path in SHAPES:
        shapes.parse(path.as_posix(), format="turtle")
    if fixture:
        # Fixture mode relaxes only canonical public-IRI allocation. Every
        # semantic and authority invariant remains identical to production.
        shapes.remove((ECF.GovernanceRecordShape, SH.sparql, ECF.CanonicalRecordIdentityConstraint))

    return shacl_validate(
        data,
        shacl_graph=shapes,
        inference="none",
        advanced=True,
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("abox", type=Path, help="Turtle ABox produced by tools/build_governance_graph.py")
    args = parser.parse_args()
    conforms, _, report = validate_abox(Graph().parse(args.abox.as_posix(), format="turtle"))
    if not conforms:
        print(report, file=sys.stderr)
        raise SystemExit(1)
    print("composed Funding + Governance + authority SHACL profile conforms")


if __name__ == "__main__":
    main()
