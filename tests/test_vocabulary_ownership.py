from pathlib import Path
import unittest

from rdflib import Graph, RDF
from rdflib.namespace import OWL


ROOT = Path(__file__).resolve().parents[1]
COMMONS = ROOT / "ontology" / "dependencies" / "commons.ttl"
GOVERNANCE = ROOT / "ontology" / "dependencies" / "governance.ttl"
FUNDING = ROOT / "ontology" / "funding.owl.ttl"
COMMONS_NS = "https://id.exergism.org/commons#"
GOVERNANCE_NS = "https://id.exergism.org/governance#"
FUNDING_NS = "https://id.exergism.org/funding#"
DECLARATION_TYPES = {
    OWL.Class,
    OWL.ObjectProperty,
    OWL.DatatypeProperty,
    OWL.AnnotationProperty,
}


def declared_local_names(path: Path, namespace: str) -> set[str]:
    graph = Graph().parse(path.as_posix(), format="turtle")
    result: set[str] = set()
    for subject, _, kind in graph.triples((None, RDF.type, None)):
        if kind not in DECLARATION_TYPES:
            continue
        iri = str(subject)
        if iri.startswith(namespace):
            result.add(iri[len(namespace):])
    return result


class VocabularyOwnershipTests(unittest.TestCase):
    def test_funding_does_not_mint_local_names_already_owned_upstream(self):
        upstream = declared_local_names(COMMONS, COMMONS_NS) | declared_local_names(GOVERNANCE, GOVERNANCE_NS)
        funding = declared_local_names(FUNDING, FUNDING_NS)
        collisions = sorted(upstream & funding)
        self.assertEqual(
            collisions,
            [],
            "Funding minted local names already owned by Commons/Governance; reuse the canonical upstream IRI instead",
        )


if __name__ == "__main__":
    unittest.main()
