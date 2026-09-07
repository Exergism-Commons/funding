import json
from pathlib import Path
import tempfile
import unittest

import yaml

import tools.export_publication as publication


class PublicationExportTests(unittest.TestCase):
    def setUp(self):
        self.original_root = publication.ROOT
        self.addCleanup(setattr, publication, "ROOT", self.original_root)

    def _root(self) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        publication.ROOT = root
        return root

    def test_score_rejects_boolean_and_out_of_range_values(self):
        for value in (True, False, -0.01, 1.01):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    publication.score(value, "fit", "example")

    def test_knowledge_export_rejects_unknown_context(self):
        root = self._root()
        source = root / "knowledge" / "decisions" / "bad.jsonld"
        source.parent.mkdir(parents=True)
        source.write_text(
            json.dumps(
                {
                    "@context": "https://example.invalid/mutable-context",
                    "@id": publication.RECORD_BASE + "ECF-DEC-BAD-CONTEXT",
                    "id": "ECF-DEC-BAD-CONTEXT",
                }
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "unsupported publication context"):
            publication.export_knowledge(root / "out")

    def test_knowledge_export_rejects_noncanonical_id(self):
        root = self._root()
        source = root / "knowledge" / "decisions" / "bad.jsonld"
        source.parent.mkdir(parents=True)
        source.write_text(
            json.dumps(
                {
                    "@context": publication.CURRENT_SOURCE_CONTEXT,
                    "@id": "urn:not-canonical",
                    "id": "ECF-DEC-BAD-ID",
                }
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "canonical @id"):
            publication.export_knowledge(root / "out")

    def test_opportunity_export_rejects_duplicate_derived_ids(self):
        root = self._root()
        source = root / "data" / "opportunities.yaml"
        source.parent.mkdir(parents=True)
        required = [key for key, _ in publication.DIMENSIONS]
        record = {"id": "same", "name": "Same opportunity"}
        record.update({key: 0.5 for key in required})
        source.write_text(
            yaml.safe_dump(
                {
                    "scoring": {"required_dimensions": required},
                    "opportunities": [record, dict(record)],
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "duplicate derived stable ID"):
            publication.export_opportunities(root / "out")

    def test_current_context_is_rewritten_to_immutable_public_iri(self):
        root = self._root()
        source = root / "knowledge" / "states" / "state.jsonld"
        source.parent.mkdir(parents=True)
        stable_id = "ECF-STATE-EXPORT-TEST"
        source.write_text(
            json.dumps(
                {
                    "@context": publication.CURRENT_SOURCE_CONTEXT,
                    "@id": publication.RECORD_BASE + stable_id,
                    "id": stable_id,
                }
            ),
            encoding="utf-8",
        )
        output = root / "out"
        publication.export_knowledge(output)
        exported = json.loads((output / "records" / f"{stable_id}.jsonld").read_text(encoding="utf-8"))
        self.assertEqual(exported["@context"], publication.CURRENT_CONTEXT_IRI)


if __name__ == "__main__":
    unittest.main()
