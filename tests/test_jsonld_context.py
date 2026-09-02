from pathlib import Path
import json
import unittest

from rdflib import Graph, Namespace
from rdflib.namespace import XSD


ROOT = Path(__file__).resolve().parents[1]
CONTEXT = ROOT / "ontology" / "funding-context.jsonld"
FIXTURE = ROOT / "tests" / "fixtures" / "valid-governance.jsonld"
ECF = Namespace("https://id.exergism.org/funding#")


class JsonLdContextTests(unittest.TestCase):
    def test_context_declares_explicit_prefixes(self):
        context = json.loads(CONTEXT.read_text(encoding="utf-8"))["@context"]
        self.assertEqual(
            context["ecf"],
            {"@id": "https://id.exergism.org/funding#", "@prefix": True},
        )
        self.assertEqual(
            context["xsd"],
            {"@id": "http://www.w3.org/2001/XMLSchema#", "@prefix": True},
        )

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
