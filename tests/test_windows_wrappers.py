import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell")


@unittest.skipUnless(os.name == "nt" and POWERSHELL, "Windows PowerShell integration")
class WindowsWrapperTests(unittest.TestCase):
    def invoke(self, name, *arguments, python=sys.executable):
        env = dict(os.environ, WAE_PYTHON=python, PYTHONDONTWRITEBYTECODE="1")
        return subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-File",
                               str(ROOT / "scripts" / name), *arguments],
                              env=env, text=True, capture_output=True, encoding="utf-8")

    def test_doctor_arguments_are_forwarded_as_json(self):
        result = self.invoke("doctor.ps1", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(json.loads(result.stdout)["tools"]), 6)

    def test_missing_python_returns_two(self):
        result = self.invoke("doctor.ps1", "--json", python="wae-nonexistent-python-interpreter")
        self.assertEqual(result.returncode, 2, result.stderr)

    def test_addon_path_with_spaces_and_exit_status(self):
        with tempfile.TemporaryDirectory(prefix="wae addon ") as temp:
            root = Path(temp)
            (root / "Example.toc").write_text("## Interface: 12345\n## Title: Test\n## Version: 1\nMain.lua\n", encoding="utf-8")
            (root / "Main.lua").write_text("-- no execution", encoding="utf-8")
            good = self.invoke("check-addon.ps1", str(root), "--json")
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertEqual(json.loads(good.stdout)["errors"], [])
            (root / "Main.lua").unlink()
            bad = self.invoke("check-addon.ps1", str(root), "--json")
            self.assertEqual(bad.returncode, 1, bad.stderr)
            self.assertTrue(json.loads(bad.stdout)["errors"])


if __name__ == "__main__":
    unittest.main()
