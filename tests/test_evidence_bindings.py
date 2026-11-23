import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools.validate_evidence_bindings import validate_record

EVIDENCE_CONTEXT = {
    "ecf": "https://id.exergism.org/funding#",
    "concentrationEvidencePath": "ecf:concentrationEvidencePath",
    "concentrationEvidenceSha256": "ecf:concentrationEvidenceSha256",
}


class EvidenceBindingTests(unittest.TestCase):
    def _record_and_evidence(self, evidence: bytes, declared_sha: str | None = None):
        directory = tempfile.TemporaryDirectory()
        root = Path(directory.name)
        evidence_path = root / "evidence.txt"
        evidence_path.write_bytes(evidence)
        record = root / "record.jsonld"
        payload = {
            "@context": EVIDENCE_CONTEXT,
            "@id": "urn:ecf:ECF-DEC-EVIDENCE-TEST",
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
            "@context": EVIDENCE_CONTEXT,
            "@id": "urn:ecf:ECF-DEC-EVIDENCE-ESCAPE",
            "concentrationEvidencePath": "../outside.txt",
            "concentrationEvidenceSha256": "0" * 64,
        }), encoding="utf-8")
        self.addCleanup(directory.cleanup)
        errors = validate_record(record, repository_root=root)
        self.assertEqual(len(errors), 1)
        self.assertIn("escapes", errors[0])

    def _graph_record(self, nodes: list[dict]):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        (root / "evidence.txt").write_bytes(b"evidence")
        record = root / "record.jsonld"
        record.write_text(json.dumps({"@context": EVIDENCE_CONTEXT, "@graph": nodes}), encoding="utf-8")
        return root, record

    def test_wrong_evidence_hash_inside_graph_is_rejected(self):
        root, path = self._graph_record([
            {"@id": "urn:ecf:ECF-STATE-TEST"},
            {
                "@id": "urn:ecf:ECF-DEC-NESTED",
                "concentrationEvidencePath": "evidence.txt",
                "concentrationEvidenceSha256": "0" * 64,
            },
        ])
        errors = validate_record(path, repository_root=root)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("mismatch", errors[0])

    def test_missing_evidence_file_inside_graph_is_rejected(self):
        root, path = self._graph_record([
            {
                "@id": "urn:ecf:ECF-DEC-NESTED-MISSING",
                "concentrationEvidencePath": "missing.txt",
                "concentrationEvidenceSha256": hashlib.sha256(b"evidence").hexdigest(),
            },
        ])
        errors = validate_record(path, repository_root=root)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("does not exist", errors[0])

    def test_every_bound_node_in_graph_is_checked(self):
        good = hashlib.sha256(b"evidence").hexdigest()
        root, path = self._graph_record([
            {"@id": "urn:ecf:ECF-DEC-GOOD", "concentrationEvidencePath": "evidence.txt", "concentrationEvidenceSha256": good},
            {"@id": "urn:ecf:ECF-DEC-BAD", "concentrationEvidencePath": "evidence.txt", "concentrationEvidenceSha256": "1" * 64},
        ])
        errors = validate_record(path, repository_root=root)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("ECF-DEC-BAD", errors[0])

    def test_half_binding_inside_graph_is_rejected(self):
        root, path = self._graph_record([
            {"@id": "urn:ecf:ECF-DEC-HALF", "concentrationEvidencePath": "evidence.txt"},
        ])
        errors = validate_record(path, repository_root=root)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("SHA-256", errors[0])


if __name__ == "__main__":
    unittest.main()
