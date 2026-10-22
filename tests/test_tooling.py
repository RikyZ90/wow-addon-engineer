import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import doctor, run_tool, tooling


class ToolingTests(unittest.TestCase):

    def test_doctor_never_executes_tools(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(tooling.shutil, "which", return_value=None), patch.object(subprocess, "run") as run:
            report = doctor.diagnose()
        run.assert_not_called()
        self.assertEqual(len(report["tools"]), 6)
        self.assertTrue(all(tool["status"] == "missing" for tool in report["tools"]))

    def test_invalid_override_does_not_fall_back(self):
        with patch.dict(os.environ, {"WAE_STYLUA": "uninstalled-tool"}), patch.object(tooling.shutil, "which", return_value=None):
            result = tooling.find_tool("stylua")
        self.assertEqual(result["status"], "invalid-override")

    def test_empty_override_does_not_fall_back_to_installed_path(self):
        for name, (variable, _) in tooling.TOOLS.items():
            with self.subTest(tool=name):
                def which(command):
                    return None if command == "" else "C:/tools/installed.exe"
                with patch.dict(os.environ, {variable: ""}, clear=True), patch.object(tooling.shutil, "which", side_effect=which) as find:
                    result = tooling.find_tool(name)
                self.assertEqual(result["status"], "invalid-override")
                self.assertEqual(result["command"], [])
                find.assert_called_once_with("")

    def test_batch_shims_are_not_sent_to_a_shell(self):
        with patch.object(tooling.shutil, "which", return_value="C:/tools/stylua.cmd"):
            result = tooling.find_tool("stylua")
        self.assertEqual(result["status"], "needs-direct-entrypoint")
        self.assertEqual(result["command"], [])

    def test_nighthawk_npm_shims_use_direct_node_entrypoint(self):
        for layout in ("windows-global", "local", "unix-global"):
            with self.subTest(layout=layout), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                if layout == "windows-global":
                    shim = root / "wow-api-mcp.cmd"
                    package = root / "node_modules/@nighthawk42/wow-api-mcp"
                elif layout == "local":
                    shim = root / "node_modules/.bin/wow-api-mcp.cmd"
                    package = root / "node_modules/@nighthawk42/wow-api-mcp"
                else:
                    shim = root / "bin/wow-api-mcp"
                    package = root / "lib/node_modules/@nighthawk42/wow-api-mcp"
                shim.parent.mkdir(parents=True, exist_ok=True)
                shim.write_text("this shell shim must never be read or executed", encoding="utf-8")
                entry = package / "dist/server.mjs"
                entry.parent.mkdir(parents=True)
                entry.touch()
                (package / "package.json").write_text(json.dumps({
                    "name": "@nighthawk42/wow-api-mcp", "bin": {"wow-api-mcp": "dist/server.mjs"}
                }), encoding="utf-8")
                node = root / "node.exe"
                node.touch()
                def which(command):
                    if command == "node":
                        return str(node)
                    return str(shim) if command == "wow-api-mcp" else None
                with patch.dict(os.environ, {}, clear=True), patch.object(tooling.shutil, "which", side_effect=which), patch.object(subprocess, "run") as run, patch.object(subprocess, "Popen") as popen:
                    report = doctor.diagnose()
                result = next(tool for tool in report["tools"] if tool["tool"] == "wow-api-mcp")
                self.assertEqual(result["status"], "available")
                self.assertEqual(result["command"], [str(node), str(entry.resolve())])
                self.assertEqual(result["path"], str(entry.resolve()))
                run.assert_not_called()
                popen.assert_not_called()

    def test_mcp_path_symlink_requires_nighthawk_identity_but_direct_override_is_explicit(self):
        for identity in ("@nighthawk42/wow-api-mcp", "other-provider"):
            with self.subTest(identity=identity), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                shim = root / "bin/wow-api-mcp"
                shim.parent.mkdir()
                shim.touch()
                package = root / "installed/provider"
                entry = package / "dist/server.js"
                entry.parent.mkdir(parents=True)
                entry.touch()
                (package / "package.json").write_text(json.dumps({
                    "name": identity, "bin": {"wow-api-mcp": "dist/server.js"}
                }), encoding="utf-8")
                node = str(root / "node.exe")
                def which(command):
                    return node if command == "node" else str(shim) if command == "wow-api-mcp" else None
                native_resolve = Path.resolve
                def resolve(path, *args, **kwargs):
                    return entry if path == shim else native_resolve(path, *args, **kwargs)
                with patch.dict(os.environ, {}, clear=True), patch.object(tooling.shutil, "which", side_effect=which), patch.object(Path, "resolve", autospec=True, side_effect=resolve), patch.object(subprocess, "run") as run:
                    automatic = tooling.find_tool("wow-api-mcp")
                run.assert_not_called()
                if identity == "@nighthawk42/wow-api-mcp":
                    self.assertEqual(automatic["command"], [node, str(entry.resolve())])
                else:
                    self.assertEqual(automatic["status"], "needs-direct-entrypoint")
                    self.assertEqual(automatic["command"], [])
                with patch.dict(os.environ, {"WAE_WOW_API_MCP": str(entry)}, clear=True), patch.object(tooling.shutil, "which", side_effect=which):
                    explicit = tooling.find_tool("wow-api-mcp")
                self.assertEqual(explicit["command"], [node, str(entry.resolve())])

    def test_mcp_override_rejects_non_javascript_files(self):
        with tempfile.TemporaryDirectory() as temp:
            for suffix in (".cmd", ".bat", ".ps1", ".exe", ".py", ".sh", ""):
                with self.subTest(suffix=suffix):
                    entry = Path(temp) / ("server" + suffix)
                    entry.touch()
                    with patch.dict(os.environ, {"WAE_WOW_API_MCP": str(entry)}, clear=True), patch.object(tooling.shutil, "which", return_value=None):
                        result = tooling.find_tool("wow-api-mcp")
                    self.assertEqual(result["status"], "needs-direct-entrypoint")
                    self.assertEqual(result["command"], [])

    def test_mcp_path_entry_without_nighthawk_package_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            for suffix in ("", ".cmd", ".exe", ".js"):
                with self.subTest(suffix=suffix):
                    entry = Path(temp) / ("wow-api-mcp" + suffix)
                    entry.touch()
                    with patch.dict(os.environ, {}, clear=True), patch.object(tooling.shutil, "which", return_value=str(entry)):
                        result = tooling.find_tool("wow-api-mcp")
                    self.assertEqual(result["status"], "needs-direct-entrypoint")
                    self.assertEqual(result["command"], [])

    def test_nighthawk_npm_metadata_must_identify_and_contain_entrypoint(self):
        cases = (
            ("wrong-identity", "other-package", "dist/server.js"),
            ("escaped-entry", "@nighthawk42/wow-api-mcp", "../outside.js"),
            ("non-string-entry", "@nighthawk42/wow-api-mcp", ["dist/server.js"]),
            ("shell-entry", "@nighthawk42/wow-api-mcp", "dist/server.cmd"),
            ("missing-entry", "@nighthawk42/wow-api-mcp", "dist/missing.js"),
        )
        for label, identity, bin_entry in cases:
            with self.subTest(case=label), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                shim = root / "wow-api-mcp.cmd"
                shim.touch()
                package = root / "node_modules/@nighthawk42/wow-api-mcp"
                (package / "dist").mkdir(parents=True)
                (package / "dist/server.js").touch()
                (package / "dist/server.cmd").touch()
                (package.parent / "outside.js").touch()
                (package / "package.json").write_text(json.dumps({
                    "name": identity, "bin": {"wow-api-mcp": bin_entry}
                }), encoding="utf-8")
                with patch.dict(os.environ, {}, clear=True), patch.object(tooling.shutil, "which", side_effect=lambda command: str(shim) if command == "wow-api-mcp" else None):
                    result = tooling.find_tool("wow-api-mcp")
                self.assertEqual(result["status"], "needs-direct-entrypoint")
                self.assertEqual(result["command"], [])

    def test_missing_tool_does_not_start_or_install_anything(self):
        with patch.object(run_tool, "find_tool", return_value={"status": "missing", "environment_variable": "WAE_STYLUA"}), patch.object(subprocess, "run") as run, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(run_tool.main(["stylua", "--", "--check", "addon"]), 127)
        run.assert_not_called()

    def test_arguments_remain_literal_and_exit_status_is_preserved(self):
        with tempfile.TemporaryDirectory(prefix="wae tooling ") as temp:
            root = Path(temp)
            script = root / "installed tool.py"
            output = root / "arguments.json"
            script.write_text("import json, pathlib, sys\npathlib.Path(sys.argv[1]).write_text(json.dumps(sys.argv[2:]), encoding='utf-8')\nsys.exit(7)\n", encoding="utf-8")
            arguments = ["path with spaces", "semi;colon", "$(echo nope)", "&", "%PATH%"]
            with patch.dict(os.environ, {"WAE_STYLUA": str(script)}):
                status = run_tool.main(["stylua", "--", str(output)] + arguments)
            self.assertEqual(status, 7)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), arguments)

    def test_shell_interpreter_shim_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "server.mjs"
            path.touch()
            def which(command):
                return "C:/tools/node.cmd" if command == "node" else None
            with patch.dict(os.environ, {"WAE_WOW_API_MCP": str(path)}), patch.object(tooling.shutil, "which", side_effect=which):
                result = tooling.find_tool("wow-api-mcp")
            self.assertEqual(result["status"], "needs-direct-entrypoint")
            self.assertEqual(result["command"], [])

    def test_windows_packager_prefers_git_bash_to_wsl_launcher(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            script = root / "release.sh"
            script.touch()
            git = root / "Git" / "cmd" / "git.exe"
            bash = root / "Git" / "bin" / "bash.exe"
            git.parent.mkdir(parents=True)
            bash.parent.mkdir(parents=True)
            git.touch()
            bash.touch()
            def which(command):
                if command == "git":
                    return str(git)
                if command == "bash":
                    return "C:/Windows/System32/bash.exe"
                return None
            with patch.dict(os.environ, {"WAE_BIGWIGS_PACKAGER": str(script)}, clear=True), patch.object(tooling.sys, "platform", "win32"), patch.object(tooling.shutil, "which", side_effect=which):
                result = tooling.find_tool("bigwigs-packager")
            self.assertEqual(result["status"], "available")
            self.assertEqual(result["command"], [str(bash), str(script.resolve())])

    def test_explicit_bash_override_does_not_fall_back(self):
        with tempfile.TemporaryDirectory() as temp:
            script = Path(temp) / "release.sh"
            script.touch()
            with patch.dict(os.environ, {"WAE_BIGWIGS_PACKAGER": str(script), "WAE_BASH": "missing-bash"}, clear=True), patch.object(tooling.shutil, "which", return_value=None):
                result = tooling.find_tool("bigwigs-packager")
            self.assertEqual(result["status"], "missing-interpreter")
            self.assertEqual(result["command"], [])

    def test_node_entrypoint_requires_an_existing_interpreter(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "server.mjs"
            path.touch()
            with patch.dict(os.environ, {"WAE_WOW_API_MCP": str(path)}), patch.object(tooling.shutil, "which", return_value=None):
                result = tooling.find_tool("wow-api-mcp")
            self.assertEqual(result["status"], "missing-interpreter")


if __name__ == "__main__":
    unittest.main()
