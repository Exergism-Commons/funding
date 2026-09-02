from pathlib import Path
import json
import tempfile
import unittest

import yaml
from pyshacl import validate as shacl_validate
from rdflib import Graph, Namespace, RDF, URIRef
from rdflib.namespace import OWL

from tools.build_governance_graph import DIMENSION_PREDICATES, build


ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "ontology" / "funding.owl.ttl"
SHAPES = ROOT / "ontology" / "funding.shacl.ttl"
CONTEXT = ROOT / "ontology" / "funding-context.jsonld"
FIXTURES = ROOT / "tests" / "fixtures"
OPPORTUNITIES = ROOT / "data" / "opportunities.yaml"
VOCABULARY_NAMESPACE = "https://id.exergism.org/funding#"
ONTOLOGY_IRI = "https://id.exergism.org/ontology/funding"
RECORD_BASE = "https://id.exergism.org/funding/id/"
ECF = Namespace(VOCABULARY_NAMESPACE)
SH = Namespace("http://www.w3.org/ns/shacl#")


def parse_jsonld(path: Path) -> Graph:
    return Graph().parse(path.as_posix(), format="json-ld")


def validate_graph(data_graph: Graph, *, fixture: bool = False):
    ontology_graph = Graph().parse(ONTOLOGY.as_posix(), format="turtle")
    shapes_graph = Graph().parse(SHAPES.as_posix(), format="turtle")
    if fixture:
        # Fixture mode is selected by the test harness, never by record data.
        # It removes only the public-IRI constraint so adversarial examples can
        # use non-public node IRIs without minting fake stable identifiers.
        shapes_graph.remove(
            (
                ECF.GovernanceRecordShape,
                SH.sparql,
                ECF.CanonicalRecordIdentityConstraint,
            )
        )
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
        self.assertIn((URIRef(ONTOLOGY_IRI), RDF.type, OWL.Ontology), ontology)
        self.assertIn((ECF.GovernanceRecord, RDF.type, OWL.Class), ontology)
        self.assertIn((ECF.GovernanceRecordShape, RDF.type, SH.NodeShape), shapes)
        self.assertIn(
            (ECF.GovernanceRecordShape, SH.targetClass, ECF.GovernanceRecord),
            shapes,
        )

        context = json.loads(CONTEXT.read_text(encoding="utf-8"))["@context"]
        self.assertEqual(context["ecf"]["@id"], VOCABULARY_NAMESPACE)
        self.assertIs(context["ecf"]["@prefix"], True)

    def test_ontology_has_no_property_chain_governance_inference(self):
        ontology = Graph().parse(ONTOLOGY.as_posix(), format="turtle")
        chains = list(ontology.triples((None, OWL.propertyChainAxiom, None)))
        self.assertEqual(chains, [])

    def test_canonical_semantic_sources_do_not_reintroduce_urn_ecf(self):
        paths = [
            ONTOLOGY,
            SHAPES,
            CONTEXT,
            ROOT / "tools" / "build_governance_graph.py",
            *sorted((ROOT / "knowledge").rglob("*.jsonld")),
        ]
        for path in paths:
            self.assertNotIn("urn:ecf:", path.read_text(encoding="utf-8"), path)

    def test_canonical_identity_cannot_be_disabled_by_provenance_data(self):
        graph = Graph().parse(
            data=f"""
                @prefix ecf: <{VOCABULARY_NAMESPACE}> .
                <urn:forged:record> a ecf:FundingOpportunity ;
                    ecf:stableId "ECF-OPP-FORGED" ;
                    ecf:title "Forged fixture-looking record" ;
                    ecf:rankEligible false ;
                    ecf:provenance "tests/fixtures/not-really-a-fixture.jsonld" .
            """,
            format="turtle",
        )
        conforms, _, report = validate_graph(graph)
        self.assertFalse(conforms)
        self.assertIn("Canonical governance-record IRIs", report)

    def test_canonical_knowledge_uses_id_exergism_record_base(self):
        graph = Graph()
        paths = sorted((ROOT / "knowledge").rglob("*.jsonld"))
        self.assertGreater(len(paths), 0)
        for path in paths:
            graph.parse(path.as_posix(), format="json-ld")

        records = list(graph.subject_objects(ECF.stableId))
        self.assertGreater(len(records), 0)
        for subject, stable_id in records:
            self.assertEqual(str(subject), f"{RECORD_BASE}{stable_id}")

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

            source = yaml.safe_load(OPPORTUNITIES.read_text(encoding="utf-8"))
            expected_rank_eligible = sum(
                all(key in opportunity for key in DIMENSION_PREDICATES)
                for opportunity in source["opportunities"]
            )
            self.assertEqual(
                manifest_a["rank_eligible_count"],
                expected_rank_eligible,
            )
            self.assertLessEqual(
                manifest_a["rank_eligible_count"],
                manifest_a["opportunity_count"],
            )
            self.assertEqual(manifest_a["vocabulary_namespace"], VOCABULARY_NAMESPACE)
            self.assertEqual(manifest_a["ontology_iri"], ONTOLOGY_IRI)
            self.assertEqual(manifest_a["record_base"], RECORD_BASE)

            graph = Graph().parse(
                (first / "funding-governance.ttl").as_posix(),
                format="turtle",
            )
            self.assertGreater(len(list(graph.subjects(RDF.type, ECF.FundingOpportunity))), 0)
            for subject, stable_id in graph.subject_objects(ECF.stableId):
                self.assertEqual(str(subject), f"{RECORD_BASE}{stable_id}")

            conforms, _, report = validate_graph(graph)
            self.assertTrue(conforms, report)

    def test_valid_fixture_conforms(self):
        graph = parse_jsonld(FIXTURES / "valid-governance.jsonld")
        conforms, _, report = validate_graph(graph, fixture=True)
        self.assertTrue(conforms, report)

    def test_concentration_with_explicit_plan_conforms(self):
        graph = parse_jsonld(FIXTURES / "valid-concentration-with-plan.jsonld")
        conforms, _, report = validate_graph(graph, fixture=True)
        self.assertTrue(conforms, report)

    def test_bootstrap_can_accept_first_funder_at_100_percent(self):
        graph = parse_jsonld(FIXTURES / "valid-bootstrap-100-percent.jsonld")
        conforms, _, report = validate_graph(graph, fixture=True)
        self.assertTrue(conforms, report)

    def test_abstract_phase_superclass_is_rejected(self):
        graph = parse_jsonld(FIXTURES / "invalid-abstract-phase.jsonld")
        conforms, _, report = validate_graph(graph, fixture=True)
        self.assertFalse(conforms)
        self.assertIn("xone", report.lower())

    def test_state_cannot_be_reused_as_diversification_plan(self):
        graph = parse_jsonld(FIXTURES / "invalid-reused-state-as-plan.jsonld")
        conforms, _, report = validate_graph(graph, fixture=True)
        self.assertFalse(conforms)
        self.assertIn("xone", report.lower())

    def test_dependency_state_has_exactly_one_concrete_class(self):
        graph = parse_jsonld(FIXTURES / "invalid-multiple-dependency-classes.jsonld")
        conforms, _, report = validate_graph(graph, fixture=True)
        self.assertFalse(conforms)
        self.assertIn("xone", report.lower())

    def test_invalid_funder_control_is_rejected(self):
        graph = parse_jsonld(FIXTURES / "invalid-funder-control.jsonld")
        conforms, _, report = validate_graph(graph, fixture=True)
        self.assertFalse(conforms)
        self.assertIn("governanceRightGranted", report)

    def test_concentration_without_diversification_plan_is_rejected(self):
        graph = parse_jsonld(FIXTURES / "invalid-concentration.jsonld")
        conforms, _, report = validate_graph(graph, fixture=True)
        self.assertFalse(conforms)
        self.assertIn("DiversificationPlan", report)

    def test_strategic_dependency_requires_qualified_approval(self):
        graph = parse_jsonld(FIXTURES / "invalid-strategic-dependency-approval.jsonld")
        conforms, _, report = validate_graph(graph, fixture=True)
        self.assertFalse(conforms)
        self.assertIn("qualified approval", report)

    def test_dependency_state_must_match_numeric_concentration(self):
        graph = parse_jsonld(FIXTURES / "invalid-dependency-state-mismatch.jsonld")
        conforms, _, report = validate_graph(graph, fixture=True)
        self.assertFalse(conforms)
        self.assertIn("StrategicDependencyState", report)

    def test_self_compensation_vote_is_rejected(self):
        graph = parse_jsonld(FIXTURES / "invalid-self-compensation-vote.jsonld")
        conforms, _, report = validate_graph(graph, fixture=True)
        self.assertFalse(conforms)
        self.assertIn("compensation beneficiary may not cast", report)

    def test_ordinary_endowment_principal_withdrawal_is_rejected(self):
        graph = parse_jsonld(FIXTURES / "invalid-endowment-withdrawal.jsonld")
        conforms, _, report = validate_graph(graph, fixture=True)
        self.assertFalse(conforms)
        self.assertTrue(
            "exceptionalCondition" in report or "approvalClass" in report,
            report,
        )

    def test_membership_economic_share_is_rejected(self):
        graph = parse_jsonld(FIXTURES / "invalid-membership-economic-share.jsonld")
        conforms, _, report = validate_graph(graph, fixture=True)
        self.assertFalse(conforms)
        self.assertIn("membershipEconomicShare", report)

    def test_incomplete_ranked_eiv_is_rejected(self):
        graph = parse_jsonld(FIXTURES / "invalid-incomplete-eiv.jsonld")
        conforms, _, report = validate_graph(graph, fixture=True)
        self.assertFalse(conforms, report)


if __name__ == "__main__":
    unittest.main()
