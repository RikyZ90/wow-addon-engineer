"""Offline validation of manifests, shared skill resources, and eval definitions."""

import argparse
import json
from pathlib import Path
import re

SKILLS = {"get-started", "wow-addon-create", "wow-addon-debug", "wow-addon-review",
          "wow-addon-research", "wow-addon-test", "wow-addon-release"}


def validate(root):
    root = Path(root).resolve()
    errors = []

    def load(name):
        try:
            return json.loads((root / name).read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as error:
            errors.append(f"{name}: {error}")
            return {}

    portable = load("plugin.json")
    codex = load(".codex-plugin/plugin.json")
    claude = load(".claude-plugin/plugin.json")
    for name, manifest in (("portable", portable), ("Codex", codex), ("Claude", claude)):
        if manifest.get("name") != "wow-addon-engineer":
            errors.append(f"{name}: unexpected plugin identity")
        if manifest.get("version") != portable.get("version"):
            errors.append(f"{name}: version differs from portable manifest")
        if manifest.get("license") != "MIT":
            errors.append(f"{name}: expected original-code MIT license")
    if portable.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json":
        errors.append("Portable manifest schema missing")
    if codex.get("skills") != "./skills/":
        errors.append("Codex skill path must point at shared skills")
    for host, filename in (("codex", ".agents/plugins/marketplace.json"),
                           ("claude", ".claude-plugin/marketplace.json")):
        marketplace = load(filename)
        entries = marketplace.get("plugins", [])
        if marketplace.get("name") != "wow-addon-engineer-marketplace" or len(entries) != 1:
            errors.append(f"{host}: invalid marketplace identity/entries")
            continue
        entry = entries[0]
        source = entry.get("source")
        if entry.get("name") != portable.get("name"):
            errors.append(f"{host}: marketplace plugin identity differs")
        if host == "codex":
            if source != {"source": "local", "path": "./"}:
                errors.append("Codex marketplace must resolve to the shared repository root")
            if entry.get("policy") != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}:
                errors.append("Codex marketplace policy missing")
        elif source != "./" or not marketplace.get("owner", {}).get("name"):
            errors.append("Claude marketplace source/owner invalid")
    portable_mcp = load("mcp.json")
    compat_mcp = load(".mcp.json")
    if portable_mcp.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json":
        errors.append("Portable MCP schema missing")
    if codex.get("mcpServers") != "./.mcp.json":
        errors.append("Codex MCP path must reference the compatibility configuration")
    expected = {"wow_api": {"type": "stdio", "command": "node",
                            "args": ["${PLUGIN_ROOT}/scripts/mcp_launcher.mjs"]}}
    compat_expected = {"wow_api": {**expected["wow_api"], "env_vars": ["WAE_WOW_API_MCP"]}}
    if portable_mcp.get("mcpServers") != expected or compat_mcp.get("mcpServers") != compat_expected:
        errors.append("Codex MCP configurations must launch the packaged local adapter")
    claude_expected = {"wow_api": {"type": "stdio", "command": "node",
                                  "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/mcp_launcher.mjs"]}}
    if claude.get("mcpServers") != claude_expected:
        errors.append("Claude MCP configuration must use its own plugin-root placeholder")
    if not (root / "scripts/mcp_launcher.mjs").is_file():
        errors.append("Original MCP launcher missing")
    actual = {path.parent.name for path in (root / "skills").glob("*/SKILL.md")}
    if actual != SKILLS:
        errors.append(f"Expected seven skills; found {sorted(actual)}")
    for name in sorted(actual):
        path = root / "skills" / name / "SKILL.md"
        content = path.read_text(encoding="utf-8-sig")
        match = re.match(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", content, re.S)
        fields = dict(re.findall(r"^([a-z-]+):\s*(.+)$", match[1], re.M)) if match else {}
        if fields.get("name") != name or not fields.get("description"):
            errors.append(f"{path.relative_to(root)}: invalid name/description frontmatter")
    for path in sorted(root.rglob("*.md")):
        if any(part in {".tmp", "dist", ".git", ".venv", "node_modules"} for part in path.relative_to(root).parts):
            continue
        content = path.read_text(encoding="utf-8-sig")
        for target in re.findall(r"!?\[[^\]]*\]\(([^)\s]+)\)", content):
            if target.startswith(("https://", "http://", "#", "mailto:")):
                continue
            target = target.split("#", 1)[0]
            resolved = (path.parent / target).resolve()
            if not resolved.is_relative_to(root) or not resolved.exists():
                errors.append(f"{path.relative_to(root)}: missing/escaping relative link {target}")
    for field in ("logo", "composerIcon"):
        target = codex.get("interface", {}).get(field, "")
        resolved = (root / target).resolve()
        if not target.startswith("./") or not resolved.is_relative_to(root) or not resolved.is_file():
            errors.append(f"Codex interface: invalid {field} path")
    cases = load("evals/cases.json")
    identifiers = set()
    for case in cases.get("cases", []):
        if case.get("id") in identifiers or case.get("skill") not in SKILLS:
            errors.append("Eval case has duplicate identity or unknown skill")
        identifiers.add(case.get("id"))
        if not case.get("prompt") or not case.get("must") or not case.get("must_not"):
            errors.append(f"Eval {case.get('id')}: missing behavioral expectations")
    if not identifiers:
        errors.append("No behavioral eval cases found")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    errors = validate(args.root)
    for error in errors:
        print(error)
    if not errors:
        print("Project validation passed: manifests, MCP wiring, seven skills, local links, assets, and eval definitions.")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
