from pathlib import Path
import unittest

from pyshacl import validate as shacl_validate
from rdflib import Graph


ROOT = Path(__file__).resolve().parents[1]
COMMONS = ROOT / "ontology" / "dependencies" / "commons.ttl"
GOVERNANCE = ROOT / "ontology" / "dependencies" / "governance.ttl"
GOVERNANCE_SHAPES = ROOT / "ontology" / "dependencies" / "governance-shapes.ttl"
FUNDING = ROOT / "ontology" / "funding.owl.ttl"
FUNDING_SHAPES = ROOT / "ontology" / "funding.shacl.ttl"
AUTHORITY_SHAPES = ROOT / "ontology" / "funding-authority.shacl.ttl"


def validate_turtle(data: str):
    graph = Graph().parse(data=data, format="turtle")
    for path in (COMMONS, GOVERNANCE, FUNDING):
        graph.parse(path.as_posix(), format="turtle")
    shapes = Graph().parse(FUNDING_SHAPES.as_posix(), format="turtle")
    shapes.parse(GOVERNANCE_SHAPES.as_posix(), format="turtle")
    shapes.parse(AUTHORITY_SHAPES.as_posix(), format="turtle")
    return shacl_validate(
        graph,
        shacl_graph=shapes,
        inference="none",
        advanced=True,
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
    )


def decision(extra: str = "", *, decision_class: str = "ecg:OrdinaryApproval", governance_version: str = "0.1-DRAFT", status: str = "proposed", operative: str = "false") -> str:
    return f"""
        @prefix ec: <https://id.exergism.org/commons#> .
        @prefix ecg: <https://id.exergism.org/governance#> .
        @prefix ecf: <https://id.exergism.org/funding#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        <urn:decision> a ecg:GovernanceDecision ;
            ec:stableId "ECF-DEC-AUTHORITY-TEST" ;
            ec:title "Authority test" ;
            ec:status "{status}" ;
            ec:operative {operative} ;
            ec:provenance "tests/test_authority_profile.py" ;
            ec:rationale "Adversarial authority-profile test" ;
            ecg:governanceVersion "{governance_version}" ;
            ecg:decisionDate "2026-09-07"^^xsd:date ;
            ecg:decisionClass {decision_class} {extra} .
    """


class FundingAuthorityProfileTests(unittest.TestCase):
    def assert_rejected(self, ttl: str, expected: str):
        conforms, _, report = validate_turtle(ttl)
        self.assertFalse(conforms, report)
        self.assertIn(expected.lower(), report.lower())

    def test_proposed_nonoperative_decision_is_structurally_allowed(self):
        conforms, _, report = validate_turtle(decision())
        self.assertTrue(conforms, report)

    def test_nonoperative_governance_rejects_operative_downstream_decision(self):
        self.assert_rejected(decision(operative="true"), "hasValue")

    def test_nonoperative_governance_rejects_approved_downstream_decision(self):
        self.assert_rejected(decision(status="approved"), "hasValue")

    def test_governance_version_is_institutional_release_not_ontology_version(self):
        self.assert_rejected(decision(governance_version="0.1-PRE1"), "0.1-DRAFT")

    def test_emergency_action_is_unavailable_without_adopted_policy(self):
        self.assert_rejected(decision(decision_class="ecg:EmergencyAction"), "in")

    def test_unknown_funding_predicate_cannot_enter_hosted_abox(self):
        self.assert_rejected(decision(extra='; ecf:inventedSharedAuthority "true"'), "declared")

    def test_legacy_funding_governance_predicate_cannot_reenter_abox(self):
        self.assert_rejected(decision(extra='; ecf:approvalClass "ordinary"'), "declared")

    def test_domain_record_cannot_also_be_governance_vote(self):
        ttl = """
            @prefix ec: <https://id.exergism.org/commons#> .
            @prefix ecg: <https://id.exergism.org/governance#> .
            @prefix ecf: <https://id.exergism.org/funding#> .
            <urn:person> a ec:Person .
            <urn:record> a ecf:FundingOpportunity, ecg:Vote ;
                ec:stableId "ECF-OPP-DUAL-TYPE" ;
                ec:title "Dual type" ;
                ec:provenance "tests/test_authority_profile.py" ;
                ecf:rankEligible false ;
                ecg:voter <urn:person> ;
                ecg:voteValue "for" .
        """
        self.assert_rejected(ttl, "cannot also be")


if __name__ == "__main__":
    unittest.main()
