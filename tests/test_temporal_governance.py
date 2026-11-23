import json
from datetime import date
from pathlib import Path
import tempfile
import unittest

from tools.validate_temporal_governance import validate_document

CONTEXT = {
    "ec": "https://id.exergism.org/commons#",
    "ecf": "https://id.exergism.org/funding#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "reviewDue": {"@id": "ec:reviewDue", "@type": "xsd:date"},
    "targetDate": {"@id": "ecf:targetDate", "@type": "xsd:date"},
}


class TemporalGovernanceTests(unittest.TestCase):
    def _document(self, payload: dict):
        directory = tempfile.TemporaryDirectory()
        path = Path(directory.name) / "record.jsonld"
        document = {"@context": CONTEXT, "@id": "urn:ecf:ECF-STATE-TEMPORAL-TEST", **payload}
        path.write_text(json.dumps(document), encoding="utf-8")
        self.addCleanup(directory.cleanup)
        return path

    def test_future_review_due_is_valid(self):
        path = self._document({"reviewDue": "2026-09-08"})
        self.assertEqual(validate_document(path, date(2026, 9, 7)), [])

    def test_review_due_today_is_valid(self):
        path = self._document({"reviewDue": "2026-09-07"})
        self.assertEqual(validate_document(path, date(2026, 9, 7)), [])

    def test_overdue_review_fails_closed(self):
        path = self._document({"reviewDue": "2026-09-06"})
        errors = validate_document(path, date(2026, 9, 7))
        self.assertEqual(len(errors), 1)
        self.assertIn("overdue", errors[0])

    def test_plan_review_cannot_follow_target(self):
        path = self._document({"reviewDue": "2027-07-01", "targetDate": "2027-06-30"})
        errors = validate_document(path, date(2026, 9, 7))
        self.assertEqual(len(errors), 1)
        self.assertIn("targetDate", errors[0])

    def test_overdue_review_under_full_iri_key_fails_closed(self):
        path = self._document({"https://id.exergism.org/commons#reviewDue": {"@value": "2026-09-06", "@type": "http://www.w3.org/2001/XMLSchema#date"}})
        errors = validate_document(path, date(2026, 9, 7))
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("overdue", errors[0])

    def test_overdue_review_on_included_node_fails_closed(self):
        path = self._document({"reviewDue": "2027-01-01", "@included": [{"@id": "urn:ecf:ECF-STATE-INCLUDED", "reviewDue": "2020-01-01"}]})
        errors = validate_document(path, date(2026, 9, 7))
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("ECF-STATE-INCLUDED", errors[0])

    def test_legacy_review_due_predicate_is_still_checked(self):
        path = self._document({"https://id.exergism.org/funding#reviewDue": {"@value": "2026-09-06", "@type": "http://www.w3.org/2001/XMLSchema#date"}})
        errors = validate_document(path, date(2026, 9, 7))
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("overdue", errors[0])


if __name__ == "__main__":
    unittest.main()
