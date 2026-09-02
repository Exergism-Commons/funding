from pathlib import Path
import tempfile
import unittest

from pyshacl import validate as shacl_validate
from rdflib import Graph
from rdflib.namespace import OWL

from tools.build_governance_graph import build


ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "ontology" / "funding.owl.ttl"
SHAPES = ROOT / "ontology" / "funding.shacl.ttl"
FIXTURES = ROOT / "tests" / "fixtures"


def parse_jsonld(path: Path) -> Graph:
    return Graph().parse(path.as_posix(), format="json-ld")


def validate_graph(data_graph: Graph):
    ontology_graph = Graph().parse(ONTOLOGY.as_posix(), format="turtle")
    shapes_graph = Graph().parse(SHAPES.as_posix(), format="turtle")
    return shacl_validate(
        data_graph,
        shacl_graph=shapes_graph,
        ont_graph=ontology_graph,
        inference="rdfs",
        advanced=True,
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
    )


class MachineGovernanceIntegrityTests(unittest.TestCase):
    def test_ontology_and_shapes_parse(self):
        ontology = Graph().parse(ONTOLOGY.as_posix(), format="turtle")
        shapes = Graph().parse(SHAPES.as_posix(), format="turtle")
        self.assertGreater(len(ontology), 0)
        self.assertGreater(len(shapes), 0)

    def test_ontology_has_no_property_chain_governance_inference(self):
        ontology = Graph().parse(ONTOLOGY.as_posix(), format="turtle")
        chains = list(ontology.triples((None, OWL.propertyChainAxiom, None)))
        self.assertEqual(chains, [])

    def test_canonical_knowledge_conforms(self):
        graph = Graph()
        paths = sorted((ROOT / "knowledge").rglob("*.jsonld"))
        self.assertGreater(len(paths), 0)
        for path in paths:
            graph.parse(path.as_posix(), format="json-ld")

        conforms, _, report = validate_graph(graph)
        self.assertTrue(conforms, report)

    def test_live_registry_builds_deterministically_and_conforms(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first"
            second = Path(tmp) / "second"
            manifest_a = build(first)
            manifest_b = build(second)

            self.assertEqual(manifest_a, manifest_b)
            self.assertEqual(
                (first / "funding-governance.nt").read_bytes(),
                (second / "funding-governance.nt").read_bytes(),
            )
            self.assertGreater(manifest_a["opportunity_count"], 0)
            self.assertEqual(
                manifest_a["rank_eligible_count"],
                manifest_a["opportunity_count"],
            )

            graph = Graph().parse(
                (first / "funding-governance.ttl").as_posix(),
                format="turtle",
            )
            conforms, _, report = validate_graph(graph)
            self.assertTrue(conforms, report)

    def test_valid_fixture_conforms(self):
        graph = parse_jsonld(FIXTURES / "valid-governance.jsonld")
        conforms, _, report = validate_graph(graph)
        self.assertTrue(conforms, report)

    def test_concentration_with_explicit_plan_conforms(self):
        graph = parse_jsonld(FIXTURES / "valid-concentration-with-plan.jsonld")
        conforms, _, report = validate_graph(graph)
        self.assertTrue(conforms, report)

    def test_bootstrap_can_accept_first_funder_at_100_percent(self):
        graph = parse_jsonld(FIXTURES / "valid-bootstrap-100-percent.jsonld")
        conforms, _, report = validate_graph(graph)
        self.assertTrue(conforms, report)

    def test_invalid_funder_control_is_rejected(self):
        graph = parse_jsonld(FIXTURES / "invalid-funder-control.jsonld")
        conforms, _, report = validate_graph(graph)
        self.assertFalse(conforms)
        self.assertIn("governanceRightGranted", report)

    def test_concentration_without_diversification_plan_is_rejected(self):
        graph = parse_jsonld(FIXTURES / "invalid-concentration.jsonld")
        conforms, _, report = validate_graph(graph)
        self.assertFalse(conforms)
        self.assertIn("DiversificationPlan", report)

    def test_strategic_dependency_requires_qualified_approval(self):
        graph = parse_jsonld(FIXTURES / "invalid-strategic-dependency-approval.jsonld")
        conforms, _, report = validate_graph(graph)
        self.assertFalse(conforms)
        self.assertIn("qualified approval", report)

    def test_dependency_state_must_match_numeric_concentration(self):
        graph = parse_jsonld(FIXTURES / "invalid-dependency-state-mismatch.jsonld")
        conforms, _, report = validate_graph(graph)
        self.assertFalse(conforms)
        self.assertIn("StrategicDependencyState", report)

    def test_self_compensation_vote_is_rejected(self):
        graph = parse_jsonld(FIXTURES / "invalid-self-compensation-vote.jsonld")
        conforms, _, report = validate_graph(graph)
        self.assertFalse(conforms)
        self.assertIn("compensation beneficiary may not cast", report)

    def test_ordinary_endowment_principal_withdrawal_is_rejected(self):
        graph = parse_jsonld(FIXTURES / "invalid-endowment-withdrawal.jsonld")
        conforms, _, report = validate_graph(graph)
        self.assertFalse(conforms)
        self.assertTrue(
            "exceptionalCondition" in report or "approvalClass" in report,
            report,
        )

    def test_membership_economic_share_is_rejected(self):
        graph = parse_jsonld(FIXTURES / "invalid-membership-economic-share.jsonld")
        conforms, _, report = validate_graph(graph)
        self.assertFalse(conforms)
        self.assertIn("membershipEconomicShare", report)

    def test_incomplete_ranked_eiv_is_rejected(self):
        graph = parse_jsonld(FIXTURES / "invalid-incomplete-eiv.jsonld")
        conforms, _, report = validate_graph(graph)
        self.assertFalse(conforms, report)


if __name__ == "__main__":
    unittest.main()
