#!/usr/bin/env python3
"""Read-only TOC/XML structure checks; this does not validate a WoW client."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PureWindowsPath
import re
import sys
import xml.etree.ElementTree as ET


_FLAVORS = {"retail", "mainline", "classic", "vanilla", "bcc", "tbc", "wrath", "cata", "mists"}
_LUA_KEYWORDS = set("and break do else elseif end false for function goto if in local nil not or repeat return then true until while".split())


class _NoDTD(ET.TreeBuilder):
    def doctype(self, name, pubid, system):
        raise ValueError("DTD/entity declarations are forbidden")


def check_addon(root: Path, toc: Path | None = None) -> dict:
    """Check one selected TOC, or every top-level TOC, without executing files.

    Invalid addon/TOC arguments raise ValueError. Findings are strings in
    errors/warnings/info. load_order is the reference traversal order across
    the selected TOCs; duplicate XML files are recorded but expanded once per TOC.
    """
    try:
        root = Path(root).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError(f"Cannot access addon directory: {exc}") from exc
    if not root.is_dir():
        raise ValueError(f"Addon path is not a directory: {root}")

    report = {
        "addon": str(root),
        "tocs": [],
        "errors": [],
        "warnings": [],
        "info": [
            "Structural inspection only: Lua syntax, runtime behavior, taint, combat restrictions, "
            "Secret Values, and client/flavor compatibility were not validated.",
            "Load order lists reference traversal across the selected TOCs; each XML file is expanded once per TOC.",
        ],
        "load_order": [],
    }

    def relative(path: Path) -> str:
        return path.relative_to(root).as_posix()

    def resource(value: str, base: Path, source: str) -> Path | None:
        value = value.strip().replace("\\", "/")
        parts = value.split("/")
        if (not value or value.startswith("/") or PureWindowsPath(value).drive
                or ".." in parts or any(":" in part for part in parts)):
            report["errors"].append(f"{source}: unsafe resource path {value!r} (absolute paths and traversal are forbidden).")
            return None
        current = base
        for part in parts:
            if part in ("", "."):
                continue
            try:
                entries = list(current.iterdir())
                exact = next((entry for entry in entries if entry.name == part), None)
                matches = [entry for entry in entries if entry.name.casefold() == part.casefold()]
                if exact is None:
                    if len(matches) != 1:
                        reason = "ambiguous casing" if matches else "missing file"
                        report["errors"].append(f"{source}: {reason} for {value!r}.")
                        return None
                    exact = matches[0]
                    report["errors"].append(
                        f"{source}: case mismatch in {value!r}: {part!r} should be {exact.name!r}."
                    )
                if not exact.resolve().is_relative_to(root):
                    report["errors"].append(f"{source}: resource {value!r} resolves outside the addon.")
                    return None
                current = exact
            except (OSError, RuntimeError, ValueError) as exc:
                report["errors"].append(f"{source}: cannot access resource {value!r}: {exc}.")
                return None
        if not current.is_file():
            report["errors"].append(f"{source}: resource {value!r} is not a file.")
            return None
        return current

    if toc is not None:
        selected = resource(str(toc), root, "--toc")
        if report["errors"] or selected is None:
            raise ValueError(" ".join(report["errors"]))
        if selected.suffix.lower() != ".toc":
            raise ValueError("--toc must name a .toc file relative to the addon directory.")
        selected_tocs = [selected]
    else:
        try:
            candidates = sorted((path for path in root.iterdir() if path.suffix.lower() == ".toc"), key=lambda path: path.name)
        except OSError as exc:
            raise ValueError(f"Cannot list addon directory: {exc}") from exc
        selected_tocs = []
        for candidate in candidates:
            selected = resource(candidate.name, root, "TOC discovery")
            if selected is not None:
                selected_tocs.append(selected)
        if not candidates:
            report["errors"].append("No top-level .toc file found.")
        if len(selected_tocs) > 1:
            report["info"].append("Multiple TOCs were checked independently; this does not select a client flavor.")

    for selected in selected_tocs:
        toc_name = relative(selected)
        report["tocs"].append(toc_name)
        try:
            lines = selected.read_text(encoding="utf-8-sig").splitlines()
        except (OSError, UnicodeError) as exc:
            report["errors"].append(f"{toc_name}: cannot read UTF-8 TOC: {exc}.")
            continue

        metadata = {}
        listed = []
        for number, line in enumerate(lines, 1):
            line = line.strip()
            source = f"{toc_name}:{number}"
            if line.startswith("##"):
                key, separator, value = line[2:].partition(":")
                if not separator:
                    report["warnings"].append(f"{source}: metadata has no colon.")
                    continue
                key = key.strip().lower()
                if key in metadata:
                    report["warnings"].append(f"{source}: duplicate metadata field {key!r}; checking its last value.")
                metadata[key] = (value.strip(), source)
            elif line and not line.startswith("#"):
                listed.append((line, source))

        interfaces = [key for key in metadata if key == "interface" or key.startswith("interface-")]
        if not interfaces:
            report["errors"].append(f"{toc_name}: missing Interface metadata.")
        for key in interfaces:
            value, source = metadata[key]
            if not re.fullmatch(r"[0-9]+(?:\s*,\s*[0-9]+)*", value) or any(not item.strip().strip("0") for item in value.split(",")):
                report["errors"].append(f"{source}: {key} must contain positive numeric Interface IDs separated by commas.")
            if key != "interface" and key.removeprefix("interface-") not in _FLAVORS:
                report["warnings"].append(f"{source}: unknown Interface flavor tag {key!r}; review it against the intended client.")
        for key in ("title", "version"):
            if key not in metadata or not metadata[key][0]:
                report["warnings"].append(f"{toc_name}: missing or empty {key.title()} metadata.")
        for key in ("savedvariables", "savedvariablespercharacter"):
            if key not in metadata:
                continue
            value, source = metadata[key]
            if not value:
                report["warnings"].append(f"{source}: {key} contains no variable names.")
            for name in re.split(r"[\s,]+", value):
                if name and (not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name) or name in _LUA_KEYWORDS):
                    report["warnings"].append(f"{source}: SavedVariables name {name!r} is not a plain Lua global identifier; review it manually.")

        loaded = set()
        expanded = set()
        active = set()

        def visit(value: str, base: Path, source: str, include: bool = False) -> None:
            path = resource(value, base, source)
            if path is None:
                return
            name = relative(path)
            identity = path.resolve()
            report["load_order"].append(name)
            if identity in loaded:
                report["warnings"].append(f"{source}: duplicate load of {name!r} within {toc_name}.")
            loaded.add(identity)
            is_xml = include or path.suffix.lower() == ".xml"
            if not is_xml:
                if path.suffix.lower() != ".lua":
                    report["warnings"].append(f"{source}: unrecognized TOC/Script resource extension for {name!r}; only existence was checked.")
                return
            if identity in active:
                report["warnings"].append(f"{source}: XML include cycle at {name!r}; expansion stopped.")
                return
            if identity in expanded:
                return
            expanded.add(identity)
            try:
                data = path.read_bytes()
                xml = ET.fromstring(data, parser=ET.XMLParser(target=_NoDTD()))
            except (OSError, ET.ParseError, ValueError) as exc:
                report["errors"].append(f"{name}: cannot parse XML: {exc}.")
                return
            active.add(identity)
            try:
                for element in xml.iter():
                    tag = element.tag.rsplit("}", 1)[-1]
                    if tag not in ("Script", "Include"):
                        continue
                    reference = element.get("file")
                    if reference is None:
                        if tag == "Include":
                            report["errors"].append(f"{name}: Include is missing its file attribute.")
                        continue
                    visit(reference, path.parent, name, include=tag == "Include")
            finally:
                active.remove(identity)

        try:
            for value, source in listed:
                visit(value, selected.parent, source)
        except RecursionError:
            report["errors"].append(f"{toc_name}: XML include nesting exceeds the checker's recursion limit.")

    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("addon", type=Path, help="addon directory to inspect")
    parser.add_argument("--toc", type=Path, help="one .toc path relative to the addon directory (default: all top-level TOCs)")
    parser.add_argument("--json", action="store_true", help="print a JSON report")
    arguments = parser.parse_args(argv)
    try:
        report = check_addon(arguments.addon, arguments.toc)
    except ValueError as exc:
        parser.error(str(exc))
    if arguments.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(f"Addon: {report['addon']}")
        for level in ("errors", "warnings", "info"):
            for message in report[level]:
                print(f"{level[:-1].upper() if level != 'info' else 'INFO'}: {message}")
        print("Reference load order:")
        for path in report["load_order"]:
            print(f"  {path}")
        print(f"{len(report['errors'])} error(s), {len(report['warnings'])} warning(s).")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
