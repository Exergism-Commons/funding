from pathlib import Path
import json
import unittest

from rdflib import Graph, RDF, URIRef


ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "knowledge"
GOVERNANCE_DECISION = URIRef("https://id.exergism.org/governance#GovernanceDecision")


class HostedGovernanceContractTests(unittest.TestCase):
    def test_generic_governance_decisions_have_funding_lifecycle_fields(self):
        paths = sorted(KNOWLEDGE.rglob("*.jsonld"))
        self.assertGreater(len(paths), 0)

        found = 0
        required = ("title", "status", "decisionDate", "rationale")
        for path in paths:
            graph = Graph().parse(path.as_posix(), format="json-ld")
            generic_decisions = set(graph.subjects(RDF.type, GOVERNANCE_DECISION))
            if not generic_decisions:
                continue

            document = json.loads(path.read_text(encoding="utf-8"))
            found += len(generic_decisions)
            self.assertEqual(
                len(generic_decisions),
                1,
                f"{path}: canonical hosted-decision documents must contain one generic GovernanceDecision",
            )

            for field in required:
                value = document.get(field)
                self.assertIsInstance(value, str, f"{path}: {field} must be a string")
                self.assertTrue(value.strip(), f"{path}: {field} must not be empty")

            self.assertIn(
                document["status"],
                {"proposed", "approved", "rejected", "superseded"},
                f"{path}: unsupported Funding decision lifecycle status",
            )

        self.assertGreater(found, 0, "expected at least one hosted generic GovernanceDecision")


if __name__ == "__main__":
    unittest.main()
