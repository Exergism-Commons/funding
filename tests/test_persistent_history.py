from pathlib import Path
import subprocess
import tempfile
import unittest

import tools.validate_persistent_history as history


FROZEN = "ontology/contexts/funding-context-0.2.0-pre1.jsonld"


class FrozenContextHistoryTests(unittest.TestCase):
    def setUp(self):
        self.original_root = history.ROOT
        self.addCleanup(setattr, history, "ROOT", self.original_root)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        history.ROOT = self.root
        self._git("init", "-q")
        # Commit bytes exactly as written, whatever the machine's global config.
        self._git("config", "core.autocrlf", "false")
        self._write("tools/validate_persistent_history.py", "# contract marker\n")
        self._write(FROZEN, '{"@context": {"title": "https://id.exergism.org/commons#title"}}\n')
        self.base = self._commit("base")

    def _git(self, *args: str) -> str:
        return subprocess.check_output(
            ["git", "-c", "user.name=test", "-c", "user.email=test@example.invalid", *args],
            cwd=self.root,
            text=True,
        ).strip()

    def _write(self, relative: str, text: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")

    def _commit(self, message: str) -> str:
        self._git("add", "-A")
        self._git("commit", "-q", "--allow-empty", "-m", message)
        return self._git("rev-parse", "HEAD")

    def test_unchanged_frozen_context_is_accepted(self):
        self._write("README.md", "unrelated\n")
        head = self._commit("unrelated change")
        history.compare_endpoint(self.base, head, bootstrap_contract=False)

    def test_frozen_context_cannot_change_in_place(self):
        self._write(FROZEN, '{"@context": {"title": "https://example.invalid/retargeted"}}\n')
        head = self._commit("retarget frozen context")
        with self.assertRaisesRegex(AssertionError, "frozen JSON-LD context"):
            history.compare_endpoint(self.base, head, bootstrap_contract=False)

    def test_frozen_context_bytes_cannot_change_even_by_line_endings(self):
        path = self.root / FROZEN
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        head = self._commit("rewrite frozen context line endings")
        with self.assertRaisesRegex(AssertionError, "frozen JSON-LD context"):
            history.compare_endpoint(self.base, head, bootstrap_contract=False)

    def test_frozen_context_cannot_disappear(self):
        (self.root / FROZEN).unlink()
        head = self._commit("remove frozen context")
        with self.assertRaisesRegex(AssertionError, "frozen JSON-LD context"):
            history.compare_endpoint(self.base, head, bootstrap_contract=False)


if __name__ == "__main__":
    unittest.main()
