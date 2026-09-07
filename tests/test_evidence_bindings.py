import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools.validate_evidence_bindings import validate_record


class EvidenceBindingTests(unittest.TestCase):
    def _record_and_evidence(self, evidence: bytes, declared_sha: str | None = None):
        directory = tempfile.TemporaryDirectory()
        root = Path(directory.name)
        evidence_path = root / "evidence.txt"
        evidence_path.write_bytes(evidence)
        record = root / "record.jsonld"
        payload = {
            "concentrationEvidencePath": "evidence.txt",
            "concentrationEvidenceSha256": declared_sha or hashlib.sha256(evidence).hexdigest(),
        }
        record.write_text(json.dumps(payload), encoding="utf-8")
        self.addCleanup(directory.cleanup)
        return root, record

    def test_absent_evidence_binding_is_allowed_for_non_concentration_record(self):
        directory = tempfile.TemporaryDirectory()
        root = Path(directory.name)
        path = root / "record.jsonld"
        path.write_text("{}", encoding="utf-8")
        self.addCleanup(directory.cleanup)
        self.assertEqual(validate_record(path, repository_root=root), [])

    def test_matching_evidence_hash_is_valid(self):
        root, path = self._record_and_evidence(b"evidence")
        self.assertEqual(validate_record(path, repository_root=root), [])

    def test_wrong_evidence_hash_is_rejected(self):
        root, path = self._record_and_evidence(b"evidence", "0" * 64)
        errors = validate_record(path, repository_root=root)
        self.assertEqual(len(errors), 1)
        self.assertIn("mismatch", errors[0])

    def test_evidence_path_cannot_escape_repository(self):
        directory = tempfile.TemporaryDirectory()
        root = Path(directory.name)
        record = root / "record.jsonld"
        record.write_text(json.dumps({
            "concentrationEvidencePath": "../outside.txt",
            "concentrationEvidenceSha256": "0" * 64,
        }), encoding="utf-8")
        self.addCleanup(directory.cleanup)
        errors = validate_record(record, repository_root=root)
        self.assertEqual(len(errors), 1)
        self.assertIn("escapes", errors[0])


if __name__ == "__main__":
    unittest.main()
