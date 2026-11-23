from pathlib import Path
import json
import unittest

from rdflib import Graph, Namespace
from rdflib.namespace import XSD


ROOT = Path(__file__).resolve().parents[1]
CONTEXT = ROOT / "ontology" / "funding-context.jsonld"
FIXTURE = ROOT / "tests" / "fixtures" / "valid-governance.jsonld"
EC = Namespace("https://id.exergism.org/commons#")
ECG = Namespace("https://id.exergism.org/governance#")
ECF = Namespace("https://id.exergism.org/funding#")


class JsonLdContextTests(unittest.TestCase):
    def test_context_declares_explicit_prefixes(self):
        context = json.loads(CONTEXT.read_text(encoding="utf-8"))["@context"]
        self.assertEqual(
            context["ec"],
            {"@id": "https://id.exergism.org/commons#", "@prefix": True},
        )
        self.assertEqual(
            context["ecg"],
            {"@id": "https://id.exergism.org/governance#", "@prefix": True},
        )
        self.assertEqual(
            context["ecf"],
            {"@id": "https://id.exergism.org/funding#", "@prefix": True},
        )
        self.assertEqual(
            context["xsd"],
            {"@id": "http://www.w3.org/2001/XMLSchema#", "@prefix": True},
        )

    def test_generic_terms_expand_outside_funding_namespace(self):
        context = json.loads(CONTEXT.read_text(encoding="utf-8"))["@context"]
        self.assertEqual(context["id"], "ec:stableId")
        self.assertEqual(context["title"], "ec:title")
        self.assertEqual(context["provenance"], "ec:provenance")
        self.assertEqual(context["GovernanceDecision"], "ecg:GovernanceDecision")
        self.assertEqual(context["Vote"], "ecg:Vote")
        self.assertEqual(context["ConflictDisclosure"], "ecg:ConflictDeclaration")

    def test_approval_alias_expands_to_governance_decision_class_iri(self):
        graph = Graph().parse(FIXTURE.as_posix(), format="json-ld")
        values = list(graph.objects(None, ECG.decisionClass))
        self.assertGreater(len(values), 0)
        self.assertIn(ECG.OrdinaryApproval, values)
        self.assertIn(ECG.QualifiedApproval, values)

    def test_numeric_terms_expand_to_real_xsd_decimal(self):
        graph = Graph().parse(FIXTURE.as_posix(), format="json-ld")
        predicates = (
            ECF.amount,
            ECF.singleFunderConcentrationAfter,
            ECF.compensationAmount,
            ECF.principalWithdrawalAmount,
        )
        for predicate in predicates:
            values = list(graph.objects(None, predicate))
            self.assertGreater(len(values), 0, predicate)
            for value in values:
                self.assertEqual(value.datatype, XSD.decimal, (predicate, value, value.datatype))


if __name__ == "__main__":
    unittest.main()
