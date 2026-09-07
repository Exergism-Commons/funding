import json
from pathlib import Path
import unittest

from rdflib import Graph, Namespace, RDF


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "ontology" / "dependencies" / "downstream-authority.json"
SHAPES = ROOT / "ontology" / "funding-authority.shacl.ttl"
EC = Namespace("https://id.exergism.org/commons#")
ECG = Namespace("https://id.exergism.org/governance#")
ECF = Namespace("https://id.exergism.org/funding#")
SH = Namespace("http://www.w3.org/ns/shacl#")


class DownstreamAuthorityContractTests(unittest.TestCase):
    def test_current_governance_profile_is_fail_closed_and_matches_funding_gate(self):
        authority = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        contract = authority["downstream_contract"]

        self.assertFalse(authority["operative"])
        self.assertFalse(authority["operative_decision_validation_available"])
        self.assertTrue(contract["proposed_records_allowed"])
        self.assertFalse(contract["approved_records_authoritative"])
        self.assertFalse(contract["operative_records_allowed"])
        self.assertTrue(contract["decision_class_is_requirement_not_proof"])
        self.assertTrue(contract["downstream_must_fail_closed_without_supported_authority_validation"])

        text = SHAPES.read_text(encoding="utf-8")
        self.assertIn(f'sh:hasValue "{authority["governance_version"]}"', text)
        self.assertIn('sh:hasValue "proposed"', text)
        self.assertIn("sh:hasValue false", text)

        declared = set(authority["declared_decision_rule_iris"])
        self.assertIn(str(ECG.OrdinaryApproval), declared)
        self.assertIn(str(ECG.QualifiedApproval), declared)
        if not authority["emergency_action_policy_adopted"]:
            decision_shape_section = text.split("ecf:HostedGovernanceDecisionAuthorityShape", 1)[1].split("ecf:HostedVoteIntegrityShape", 1)[0]
            self.assertNotIn("ecg:EmergencyAction", decision_shape_section)

    def test_governance_becoming_operative_requires_explicit_funding_integration(self):
        authority = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        if authority["operative"] or authority["operative_decision_validation_available"]:
            self.fail(
                "Governance now exposes operative authority validation; Funding must replace its PRE1 fail-closed profile "
                "with an evidence-backed integration before accepting the new snapshot."
            )


if __name__ == "__main__":
    unittest.main()
