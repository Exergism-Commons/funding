import json
from datetime import date
from pathlib import Path
import tempfile
import unittest

from tools.validate_temporal_governance import validate_document


class TemporalGovernanceTests(unittest.TestCase):
    def _document(self, payload: dict):
        directory = tempfile.TemporaryDirectory()
        path = Path(directory.name) / "record.jsonld"
        path.write_text(json.dumps(payload), encoding="utf-8")
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


if __name__ == "__main__":
    unittest.main()
