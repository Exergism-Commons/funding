from pathlib import Path
import hashlib
import json
import tempfile
import unittest

import yaml
from pyshacl import validate as shacl_validate
from rdflib import Graph, Namespace, RDF, URIRef
from rdflib.namespace import OWL, RDFS

from tools.build_governance_graph import DIMENSION_PREDICATES, build


ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "ontology" / "funding.owl.ttl"
SHAPES = ROOT / "ontology" / "funding.shacl.ttl"
DEPENDENCY_DIR = ROOT / "ontology" / "dependencies"
DEPENDENCY_MANIFEST = DEPENDENCY_DIR / "manifest.json"
COMMONS_ONTOLOGY = DEPENDENCY_DIR / "commons.ttl"
GOVERNANCE_ONTOLOGY = DEPENDENCY_DIR / "governance.ttl"
GOVERNANCE_SHAPES = DEPENDENCY_DIR / "governance-shapes.ttl"
CONTEXT = ROOT / "ontology" / "funding-context.jsonld"
FIXTURES = ROOT / "tests" / "fixtures"
OPPORTUNITIES = ROOT / "data" / "opportunities.yaml"
COMMONS_NAMESPACE = "https://id.exergism.org/commons#"
GOVERNANCE_NAMESPACE = "https://id.exergism.org/governance#"
VOCABULARY_NAMESPACE = "https://id.exergism.org/funding#"
ONTOLOGY_IRI = "https://id.exergism.org/ontology/funding"
RECORD_BASE = "https://id.exergism.org/funding/id/"
GOVERNANCE_SOURCE_COMMIT = "06e614c21f9623658c16175a381279f9c36ef526"
EC = Namespace(COMMONS_NAMESPACE)
ECG = Namespace(GOVERNANCE_NAMESPACE)
ECF = Namespace(VOCABULARY_NAMESPACE)
SH = Namespace("http://www.w3.org/ns/shacl#")


def parse_jsonld(path: Path) -> Graph:
    return Graph().parse(path.as_posix(), format="json-ld")


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def validate_graph(data_graph: Graph, *, fixture: bool = False):
    # Put the ontology triples in the validation graph so SHACL can use the
    # explicit rdf:type/rdfs:subClassOf hierarchy without enabling the broader
    # RDFS entailment regime. In particular, rdfs:domain/rdfs:range must not
    # manufacture types that a sh:class constraint is meant to validate.
    validation_graph = Graph()
    for triple in data_graph:
        validation_graph.add(triple)
    validation_graph.parse(COMMONS_ONTOLOGY.as_posix(), format="turtle")
    validation_graph.parse(GOVERNANCE_ONTOLOGY.as_posix(), format="turtle")
    validation_graph.parse(ONTOLOGY.as_posix(), format="turtle")

    shapes_graph = Graph().parse(SHAPES.as_posix(), format="turtle")
    shapes_graph.parse(GOVERNANCE_SHAPES.as_posix(), format="turtle")
    if fixture:
        # Fixture mode is selected by the test harness, never by record data.
        # It relaxes only the public-IRI constraint so non-canonical adversarial
        # examples do not mint fake persistent identifiers. Governance shapes
        # remain identical to the canonical production validation profile.
        shapes_graph.remove(
            (
                ECF.GovernanceRecordShape,
                SH.sparql,
                ECF.CanonicalRecordIdentityConstraint,
            )
        )
    return shacl_validate(
        validation_graph,
        shacl_graph=shapes_graph,
        inference="none",
        advanced=True,
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
    )


class MachineGovernanceIntegrityTests(unittest.TestCase):
    def test_ontology_and_shapes_parse(self):
        ontology = Graph().parse(ONTOLOGY.as_posix(), format="turtle")
        commons = Graph().parse(COMMONS_ONTOLOGY.as_posix(), format="turtle")
        governance = Graph().parse(GOVERNANCE_ONTOLOGY.as_posix(), format="turtle")
        shapes = Graph().parse(SHAPES.as_posix(), format="turtle")
        governance_shapes = Graph().parse(GOVERNANCE_SHAPES.as_posix(), format="turtle")
        self.assertGreater(len(ontology), 0)
        self.assertGreater(len(commons), 0)
        self.assertGreater(len(governance), 0)
        self.assertGreater(len(shapes), 0)
        self.assertGreater(len(governance_shapes), 0)
        self.assertIn((URIRef(ONTOLOGY_IRI), RDF.type, OWL.Ontology), ontology)
        self.assertIn(
            (ECF.FundingAcceptanceDecision, RDFS.subClassOf, ECG.GovernanceDecision),
            ontology,
        )
        self.assertIn((ECF.GovernanceRecordShape, RDF.type, SH.NodeShape), shapes)
        self.assertIn(
            (ECF.GovernanceRecordShape, SH.targetClass, ECF.FundingOpportunity),
            shapes,
        )
        self.assertIn((ECG.GovernanceDecisionShape, RDF.type, SH.NodeShape), governance_shapes)
        self.assertIn((ECG.VoteShape, RDF.type, SH.NodeShape), governance_shapes)
        self.assertIn(
            (ECG.ConflictDeclarationShape, RDF.type, SH.NodeShape),
            governance_shapes,
        )

        context = json.loads(CONTEXT.read_text(encoding="utf-8"))["@context"]
        self.assertEqual(context["ec"]["@id"], COMMONS_NAMESPACE)
        self.assertEqual(context["ecg"]["@id"], GOVERNANCE_NAMESPACE)
        self.assertEqual(context["ecf"]["@id"], VOCABULARY_NAMESPACE)
        self.assertEqual(context["operative"]["@id"], "ec:operative")
        self.assertEqual(context["governanceVersion"], "ecg:governanceVersion")

    def test_governance_dependency_snapshots_match_pinned_git_blobs(self):
        manifest = json.loads(DEPENDENCY_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["source_repository"], "Exergism-Commons/governance")
        self.assertEqual(manifest["source_commit"], GOVERNANCE_SOURCE_COMMIT)
        for filename, metadata in manifest["files"].items():
            path = DEPENDENCY_DIR / filename
            self.assertTrue(path.is_file(), filename)
            self.assertEqual(
                git_blob_sha(path.read_bytes()),
                metadata["git_blob_sha"],
                f"{filename} drifted from pinned Governance blob",
            )

    def test_funding_does_not_redefine_shared_or_governance_terms(self):
        ontology = Graph().parse(ONTOLOGY.as_posix(), format="turtle")
        forbidden_classes = (
            ECF.Actor,
            ECF.Person,
            ECF.Organization,
            ECF.GovernanceRecord,
            ECF.GovernanceDecision,
            ECF.Vote,
            ECF.ConflictDisclosure,
        )
        for term in forbidden_classes:
            self.assertNotIn((term, RDF.type, OWL.Class), ontology, term)

        forbidden_properties = (
            ECF.stableId,
            ECF.title,
            ECF.status,
            ECF.rationale,
            ECF.provenance,
            ECF.supersedes,
            ECF.reviewDue,
            ECF.approvalClass,
            ECF.hasVote,
            ECF.voter,
            ECF.voteValue,
            ECF.conflictDisclosure,
            ECF.interestedParty,
            ECF.membershipEconomicShare,
        )
        for term in forbidden_properties:
            self.assertFalse(
                any(ontology.triples((term, RDF.type, None))),
                f"Funding must not define shared/governance property {term}",
            )

    def test_generic_governance_decision_shape_is_enforced(self):
        graph = Graph().parse(
            data=f"""
                @prefix ecg: <{GOVERNANCE_NAMESPACE}> .
                <urn:decision> a ecg:GovernanceDecision ;
                    ecg:decisionClass ecg:OrdinaryApproval ;
                    ecg:governanceVersion "0.1-PRE1" .
            """,
            format="turtle",
        )
        conforms, _, report = validate_graph(graph)
        self.assertFalse(conforms)
        self.assertIn("operative", report)

    def test_active_member_can_vote_via_governance_subclass_hierarchy(self):
        graph = Graph().parse(
            data=f"""
                @prefix ecg: <{GOVERNANCE_NAMESPACE}> .
                <urn:member> a ecg:ActiveMember .
                <urn:vote> a ecg:Vote ;
                    ecg:voter <urn:member> ;
                    ecg:voteValue "for" .
            """,
            format="turtle",
        )
        conforms, _, report = validate_graph(graph)
        self.assertTrue(conforms, report)

    def test_governance_range_axiom_does_not_manufacture_person_type(self):
        graph = Graph().parse(
            data=f"""
                @prefix ec: <{COMMONS_NAMESPACE}> .
                @prefix ecg: <{GOVERNANCE_NAMESPACE}> .
                <urn:organization> a ec:Organization .
                <urn:vote> a ecg:Vote ;
                    ecg:voter <urn:organization> ;
                    ecg:voteValue "for" .
            """,
            format="turtle",
        )
        conforms, _, report = validate_graph(graph)
        self.assertFalse(conforms)
        self.assertIn("Person", report)

    def test_delegated_governance_vote_shape_rejects_legacy_vote_value(self):
        graph = Graph().parse(
            data=f"""
                @prefix ec: <{COMMONS_NAMESPACE}> .
                @prefix ecg: <{GOVERNANCE_NAMESPACE}> .
                <urn:person> a ec:Person .
                <urn:vote> a ecg:Vote ;
                    ecg:voter <urn:person> ;
                    ecg:voteValue "approve" .
            """,
            format="turtle",
        )
        conforms, _, report = validate_graph(graph)
        self.assertFalse(conforms)
        self.assertIn("voteValue", report)

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
                @prefix ec: <{COMMONS_NAMESPACE}> .
                @prefix ecf: <{VOCABULARY_NAMESPACE}> .
                <urn:forged:record> a ecf:FundingOpportunity ;
                    ec:stableId "ECF-OPP-FORGED" ;
                    ec:title "Forged fixture-looking record" ;
                    ecf:rankEligible false ;
                    ec:provenance "tests/fixtures/not-really-a-fixture.jsonld" .
            """,
            format="turtle",
        )
        conforms, _, report = validate_graph(graph)
        self.assertFalse(conforms)
        self.assertIn("Canonical funding-record IRIs", report)

    def test_each_canonical_knowledge_document_has_identity_and_provenance(self):
        paths = sorted((ROOT / "knowledge").rglob("*.jsonld"))
        self.assertGreater(len(paths), 0)
        for path in paths:
            document = json.loads(path.read_text(encoding="utf-8"))
            stable_id = document.get("id")
            self.assertIsInstance(stable_id, str, path)
            self.assertRegex(stable_id, r"^ECF-[A-Z0-9-]+$", path)
            self.assertEqual(document.get("@id"), f"{RECORD_BASE}{stable_id}", path)
            provenance = document.get("provenance")
            self.assertIsInstance(provenance, str, path)
            self.assertTrue(provenance.strip(), path)

    def test_canonical_knowledge_uses_id_exergism_record_base(self):
        graph = Graph()
        paths = sorted((ROOT / "knowledge").rglob("*.jsonld"))
        self.assertGreater(len(paths), 0)
        for path in paths:
            graph.parse(path.as_posix(), format="json-ld")

        records = list(graph.subject_objects(EC.stableId))
        self.assertEqual(len(records), len(paths))
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
            self.assertEqual(manifest_a["rank_eligible_count"], expected_rank_eligible)
            self.assertLessEqual(manifest_a["rank_eligible_count"], manifest_a["opportunity_count"])
            self.assertEqual(manifest_a["commons_namespace"], COMMONS_NAMESPACE)
            self.assertEqual(manifest_a["governance_namespace"], GOVERNANCE_NAMESPACE)
            self.assertEqual(manifest_a["vocabulary_namespace"], VOCABULARY_NAMESPACE)
            self.assertEqual(manifest_a["ontology_iri"], ONTOLOGY_IRI)
            self.assertEqual(manifest_a["record_base"], RECORD_BASE)

            graph = Graph().parse((first / "funding-governance.ttl").as_posix(), format="turtle")
            self.assertGreater(len(list(graph.subjects(RDF.type, ECF.FundingOpportunity))), 0)
            for subject, stable_id in graph.subject_objects(EC.stableId):
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
            "exceptionalCondition" in report or "decisionClass" in report,
            report,
        )

    def test_incomplete_ranked_eiv_is_rejected(self):
        graph = parse_jsonld(FIXTURES / "invalid-incomplete-eiv.jsonld")
        conforms, _, report = validate_graph(graph, fixture=True)
        self.assertFalse(conforms, report)


if __name__ == "__main__":
    unittest.main()
