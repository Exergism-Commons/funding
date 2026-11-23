import json
from pathlib import Path
import tempfile
import unittest

import tools.validate_canonical_records as canonical


RECORD_BASE = "https://id.exergism.org/funding/id/"
CONTEXT = {
    "ec": "https://id.exergism.org/commons#",
    "ecf": "https://id.exergism.org/funding#",
    "ecg": "https://id.exergism.org/governance#",
    "id": "ec:stableId",
    "title": "ec:title",
    "supersedes": {"@id": "ec:supersedes", "@type": "@id"},
}


class CanonicalRecordFormTests(unittest.TestCase):
    def _errors(self, document: dict) -> list[str]:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "record.jsonld"
        path.write_text(json.dumps(document), encoding="utf-8")
        return canonical.validate_record(path)

    def _record(self, stable_id: str = "ECF-DEC-FORM-TEST", **extra) -> dict:
        return {"@context": CONTEXT, "@id": RECORD_BASE + stable_id, "id": stable_id, "title": "Form test", **extra}

    def test_flat_single_subject_record_is_accepted(self):
        self.assertEqual(self._errors(self._record(supersedes=RECORD_BASE + "ECF-DEC-OLDER")), [])

    def test_named_graph_content_is_rejected(self):
        errors = self._errors(self._record(**{"@graph": [{"@id": RECORD_BASE + "ECF-DEC-HIDDEN", "ecf:inventedSharedAuthority": True}]}))
        self.assertTrue(any("named graph" in error for error in errors), errors)

    def test_nested_node_describing_another_record_is_rejected(self):
        errors = self._errors(
            self._record(supersedes={"@id": RECORD_BASE + "ECF-DEC-MRG-BOOTSTRAP-001", "ecf:approvalClass": "qualified"})
        )
        self.assertTrue(any("ECF-DEC-MRG-BOOTSTRAP-001" in error for error in errors), errors)

    def test_included_node_is_rejected(self):
        errors = self._errors(
            self._record(**{"@included": [{"@id": RECORD_BASE + "ECF-STATE-INCLUDED", "ec:reviewDue": "2020-01-01"}]})
        )
        self.assertTrue(any("ECF-STATE-INCLUDED" in error for error in errors), errors)

    def test_blank_node_subject_is_rejected(self):
        errors = self._errors(self._record(**{"ecf:detail": {"ec:reviewDue": "2020-01-01"}}))
        self.assertTrue(any("describes" in error for error in errors), errors)

    def test_record_must_describe_its_own_iri(self):
        document = self._record()
        document.pop("title")
        document.pop("id")
        document["@context"] = {}
        errors = self._errors(document)
        self.assertTrue(any("no triples" in error for error in errors), errors)

    def test_live_canonical_knowledge_conforms(self):
        self.assertEqual(canonical.validate_knowledge(), [])


if __name__ == "__main__":
    unittest.main()
