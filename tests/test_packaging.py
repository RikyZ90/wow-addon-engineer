import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.package_plugin import build_package, package_files

ROOT = Path(__file__).resolve().parents[1]


class PackagingTests(unittest.TestCase):
    def test_host_archives_have_one_root_and_identical_shared_payloads(self):
        with tempfile.TemporaryDirectory() as temp:
            archives = {}
            for host in ("codex", "claude"):
                path = build_package(ROOT, host, temp)
                with zipfile.ZipFile(path) as archive:
                    archives[host] = {name: archive.read(name) for name in archive.namelist()}
            codex, claude = archives["codex"], archives["claude"]
            self.assertTrue(all(name.startswith("wow-addon-engineer/") for files in archives.values() for name in files))
            self.assertIn("wow-addon-engineer/plugin.json", codex)
            self.assertNotIn("wow-addon-engineer/plugin.json", claude)
            self.assertFalse(any(".claude-plugin/" in name for name in codex))
            self.assertFalse(any(".codex-plugin/" in name or ".agents/" in name for name in claude))
            common = codex.keys() & claude.keys()
            self.assertEqual(sum(name.endswith("/SKILL.md") for name in common), 7)
            self.assertTrue(all(codex[name] == claude[name] for name in common))
            self.assertFalse(any(".git/" in name or ".env" in name or "__pycache__" in name for files in archives.values() for name in files))

    def test_mcp_configurations_resolve_to_the_archived_original_launcher(self):
        with tempfile.TemporaryDirectory() as temp:
            for host in ("codex", "claude"):
                with zipfile.ZipFile(build_package(ROOT, host, temp)) as archive:
                    prefix = "wow-addon-engineer/"
                    if host == "codex":
                        config = json.loads(archive.read(prefix + "mcp.json"))
                        compat = json.loads(archive.read(prefix + ".mcp.json"))
                        self.assertEqual(compat["mcpServers"]["wow_api"].pop("env_vars"), ["WAE_WOW_API_MCP"])
                        self.assertEqual(config["mcpServers"], compat["mcpServers"])
                        manifest = json.loads(archive.read(prefix + ".codex-plugin/plugin.json"))
                        self.assertEqual(manifest["mcpServers"], "./.mcp.json")
                        variable = "${PLUGIN_ROOT}/"
                    else:
                        config = json.loads(archive.read(prefix + ".claude-plugin/plugin.json"))
                        variable = "${CLAUDE_PLUGIN_ROOT}/"
                        self.assertNotIn(prefix + ".mcp.json", archive.namelist())
                        self.assertNotIn(prefix + "mcp.json", archive.namelist())
                    server = config["mcpServers"]["wow_api"]
                    self.assertEqual(server["type"], "stdio")
                    self.assertEqual(server["command"], "node")
                    self.assertEqual(len(server["args"]), 1)
                    self.assertTrue(server["args"][0].startswith(variable))
                    launcher = prefix + server["args"][0].removeprefix(variable)
                    self.assertIn(launcher, archive.namelist())
                    self.assertEqual(archive.read(launcher), (ROOT / "scripts/mcp_launcher.mjs").read_bytes())
                    self.assertFalse(any("node_modules/" in name for name in archive.namelist()))

    def test_packages_are_reproducible_and_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as one, tempfile.TemporaryDirectory() as two:
            first = build_package(ROOT, "codex", one)
            second = build_package(ROOT, "codex", two)
            before = first.read_bytes()
            self.assertEqual(hashlib.sha256(before).digest(), hashlib.sha256(second.read_bytes()).digest())
            with self.assertRaises(FileExistsError):
                build_package(ROOT, "codex", one)
            self.assertEqual(first.read_bytes(), before)

    def test_private_cache_and_upstream_files_are_never_packaged(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as output:
            fixture = Path(temp)
            for original in package_files(ROOT, "codex"):
                destination = fixture / original.relative_to(ROOT)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(original.read_bytes())
            for name in ("docs/.cache/private-review.md", "assets/tool-cache/upstream/README.md",
                         "docs/private-notes.md", "scripts/extra.py", ".env"):
                path = fixture / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("MUST NOT SHIP", encoding="utf-8")
            archive_path = build_package(fixture, "codex", output)
            with zipfile.ZipFile(archive_path) as archive:
                self.assertFalse(any(b"MUST NOT SHIP" in archive.read(name) for name in archive.namelist()))

    def test_package_file_allowlist_excludes_unrelated_sources(self):
        selected = [path.relative_to(ROOT).as_posix() for path in package_files(ROOT, "codex")]
        self.assertFalse(any(name.startswith(("tests/", ".github/")) for name in selected))
        self.assertNotIn("scripts/package_plugin.py", selected)


if __name__ == "__main__":
    unittest.main()
