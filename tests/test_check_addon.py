import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts.check_addon import check_addon, main


class CheckAddonTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "Addon con spazi é"
        self.root.mkdir()

    def write(self, name, content=""):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def toc(self, body="", name="Example.toc", metadata=None):
        if metadata is None:
            metadata = "## Interface: 120000, 120001\n## Title: Example\n## Version: 1.0\n"
        return self.write(name, metadata + body)

    def test_valid_unicode_spaces_backslashes_and_xml_order(self):
        self.toc("cartella é\\primo file.lua\nUI\\main.xml\nlast.lua\n")
        self.write("cartella é/primo file.lua", "this is deliberately not valid Lua")
        self.write("UI/main.xml", '<Ui xmlns="http://www.blizzard.com/wow/ui/"><Script file="nested\\script.lua"/><Include file="nested/other.xml"/></Ui>')
        self.write("UI/nested/script.lua")
        self.write("UI/nested/other.xml", '<Ui><Script file="second.lua"/></Ui>')
        self.write("UI/nested/second.lua")
        self.write("last.lua")
        report = check_addon(self.root)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["warnings"], [])
        self.assertEqual(report["load_order"], [
            "cartella é/primo file.lua", "UI/main.xml", "UI/nested/script.lua",
            "UI/nested/other.xml", "UI/nested/second.lua", "last.lua",
        ])
        self.assertIn("Lua syntax", " ".join(report["info"]))

    def test_missing_toc_is_error(self):
        self.assertIn("No top-level .toc", " ".join(check_addon(self.root)["errors"]))

    def test_missing_resource_is_error(self):
        self.toc("missing.lua\n")
        self.assertIn("missing file", " ".join(check_addon(self.root)["errors"]))

    def test_resource_directory_is_error(self):
        self.toc("folder.lua\n")
        (self.root / "folder.lua").mkdir()
        self.assertIn("not a file", " ".join(check_addon(self.root)["errors"]))

    def test_path_boundaries(self):
        for value in ("../outside.lua", "sub/../main.lua", "/tmp/outside.lua", r"C:\outside.lua", r"C:outside.lua", r"\\server\share\outside.lua", "main.lua:stream"):
            with self.subTest(value=value):
                self.toc(value + "\n")
                self.assertIn("unsafe resource path", " ".join(check_addon(self.root)["errors"]))

    def test_exact_casing_checked_on_every_platform(self):
        self.toc("folder\\main.lua\n")
        self.write("Folder/Main.lua")
        errors = check_addon(self.root)["errors"]
        self.assertEqual(sum("case mismatch" in message for message in errors), 2)
        self.assertNotIn("missing file", " ".join(errors))

    def test_duplicate_resource_warning(self):
        self.toc("main.lua\nmain.lua\n")
        self.write("main.lua")
        report = check_addon(self.root)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["load_order"], ["main.lua", "main.lua"])
        self.assertIn("duplicate load", " ".join(report["warnings"]))

    def test_xml_include_cycle_stops_and_warns(self):
        self.toc("a.xml\n")
        self.write("a.xml", '<Ui><Include file="b.xml"/></Ui>')
        self.write("b.xml", '<Ui><Include file="a.xml"/></Ui>')
        report = check_addon(self.root)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["load_order"], ["a.xml", "b.xml", "a.xml"])
        self.assertIn("include cycle", " ".join(report["warnings"]))

    def test_repeated_xml_expanded_once_per_toc(self):
        self.toc("a.xml\na.xml\n")
        self.write("a.xml", '<Ui><Script file="main.lua"/></Ui>')
        self.write("main.lua")
        report = check_addon(self.root)
        self.assertEqual(report["load_order"], ["a.xml", "main.lua", "a.xml"])
        self.assertIn("duplicate load", " ".join(report["warnings"]))

    def test_xml_malformed_or_missing_reference(self):
        for xml, expected in (
            ("<Ui>", "cannot parse XML"),
            ('<Ui><Include file="missing.xml"/></Ui>', "missing file"),
            ("<Ui><Include/></Ui>", "missing its file attribute"),
            ('<Ui><Script file=""/></Ui>', "unsafe resource path"),
            ('<Ui><Include file="../outside.xml"/></Ui>', "unsafe resource path"),
        ):
            with self.subTest(xml=xml):
                self.toc("a.xml\n")
                self.write("a.xml", xml)
                self.assertIn(expected, " ".join(check_addon(self.root)["errors"]))

    def test_inline_xml_scripts_are_not_executed(self):
        self.toc("a.xml\n")
        self.write("a.xml", '<Ui><Script>error("must never run")</Script></Ui>')
        self.assertEqual(check_addon(self.root)["errors"], [])

    def test_dtd_and_entity_declarations_rejected_with_utf_encodings(self):
        self.toc("a.xml\n")
        for encoding in ("utf-8", "utf-16"):
            with self.subTest(encoding=encoding):
                (self.root / "a.xml").write_bytes('<!DOCTYPE Ui [<!ENTITY value "expanded">]><Ui>&value;</Ui>'.encode(encoding))
                self.assertIn("DTD/entity declarations", " ".join(check_addon(self.root)["errors"]))

    def test_xml_comment_with_declaration_text_is_allowed(self):
        self.toc("a.xml\n")
        self.write("a.xml", "<!-- <!DOCTYPE Ui> --><Ui/>")
        self.assertEqual(check_addon(self.root)["errors"], [])

    def test_utf8_bom_toc(self):
        self.toc(metadata="\ufeff## Interface: 120000\n## Title: Example\n## Version: 1\n")
        self.assertEqual(check_addon(self.root)["errors"], [])

    def test_interface_metadata_missing_and_invalid(self):
        for value in (None, "", "latest", "120000,", "0", "120000 120001"):
            with self.subTest(value=value):
                self.toc(metadata="" if value is None else f"## Interface: {value}\n")
                self.assertTrue(check_addon(self.root)["errors"])

    def test_missing_title_version_and_bad_saved_variables_are_warnings(self):
        self.toc(metadata="## Interface: 120000\n## SavedVariables: Good_Name, bad.name, 2bad, end\n## SavedVariablesPerCharacter: \n")
        report = check_addon(self.root)
        self.assertEqual(report["errors"], [])
        warnings = " ".join(report["warnings"])
        for expected in ("Title", "Version", "bad.name", "2bad", "end", "no variable names"):
            self.assertIn(expected, warnings)
        self.assertNotIn("'Good_Name'", warnings)

    def test_flavor_tags_do_not_establish_compatibility(self):
        self.toc(metadata="## Interface-Retail: 120000\n## Interface-Future: 999999\n## Title: Example\n## Version: 1\n")
        report = check_addon(self.root)
        self.assertEqual(report["errors"], [])
        self.assertIn("unknown Interface flavor tag", " ".join(report["warnings"]))
        self.assertIn("client/flavor compatibility were not validated", " ".join(report["info"]))

    def test_multiple_tocs_are_independent_and_can_be_selected(self):
        self.toc("main.lua\n", name="Example_Mainline.toc")
        self.toc("main.lua\n", name="Example_Classic.toc")
        self.write("main.lua")
        report = check_addon(self.root)
        self.assertEqual(len(report["tocs"]), 2)
        self.assertFalse(any("duplicate load" in message for message in report["warnings"]))
        selected = check_addon(self.root, Path("Example_Classic.toc"))
        self.assertEqual(selected["tocs"], ["Example_Classic.toc"])
        self.assertEqual(selected["load_order"], ["main.lua"])

    def test_bad_root_or_toc_arguments_raise_valueerror(self):
        self.toc()
        for root, toc in ((self.root / "missing", None), (self.root / "Example.toc", None), (self.root, Path("../Example.toc")), (self.root, Path("missing.toc")), (self.root, self.root / "Example.toc")):
            with self.subTest(root=root, toc=toc), self.assertRaises(ValueError):
                check_addon(root, toc)

    def test_symlink_outside_addon_is_rejected(self):
        outside = Path(self.temporary.name) / "outside.lua"
        outside.write_text("", encoding="utf-8")
        self.toc("link.lua\n")
        try:
            (self.root / "link.lua").symlink_to(outside)
        except OSError as exc:
            self.skipTest(f"Symlink permission unavailable: {exc}")
        self.assertIn("outside the addon", " ".join(check_addon(self.root)["errors"]))

    def test_cli_json_exit_status_and_no_file_changes(self):
        self.toc()
        before = {path.relative_to(self.root): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main([str(self.root), "--json"]), 0)
        self.assertEqual(json.loads(output.getvalue())["errors"], [])
        self.toc("missing.lua\n")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main([str(self.root)]), 1)
        self.toc()
        after = {path.relative_to(self.root): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(before, after)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exit_result:
            main([str(self.root / "missing"), "--json"])
        self.assertEqual(exit_result.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
