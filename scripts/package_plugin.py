"""Build host-specific plugin ZIPs from an explicit first-party file allowlist."""

import argparse
from pathlib import Path
import json
import zipfile

SKILL_NAMES = ("get-started", "wow-addon-create", "wow-addon-debug", "wow-addon-review",
               "wow-addon-research", "wow-addon-test", "wow-addon-release")
COMMON_FILES = (
    "README.md", "LICENSE", "THIRD_PARTY_NOTICES.md", "CHANGELOG.md",
    "docs/quick-start.md", "docs/installation.md", "docs/wow-engineering.md", "docs/checks.md",
    "docs/integrations.md", "docs/licensing.md", "docs/verification.md",
    "assets/logo.png", "assets/README.md", "examples/usage.md",
    "evals/README.md", "evals/cases.json", "evals/forward-test-2026-10-21.md",
    "evals/results-2026-10-21.json", "docs/runtime-test.md",
    "examples/WoWAddonEngineerSmoke/WoWAddonEngineerSmoke.toc",
    "examples/WoWAddonEngineerSmoke/Core.lua", "examples/WoWAddonEngineerSmoke/Smoke.xml",
    "examples/WoWAddonEngineerSmoke/Runtime.xml", "examples/WoWAddonEngineerSmoke/Runtime.lua",
    "examples/WoWAddonEngineerSmoke/README.md", "examples/WoWAddonEngineerSmoke/LICENSE",
)
SCRIPTS = ("doctor.py", "tooling.py", "run_tool.py", "mcp_launcher.mjs", "check_addon.py",
           "python.ps1", "doctor.ps1", "check-addon.ps1")
HOST_FILES = {
    "codex": ("plugin.json", "mcp.json", ".mcp.json", ".codex-plugin/plugin.json", ".agents/plugins/marketplace.json"),
    "claude": (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"),
}


def package_files(root, host):
    root = Path(root).resolve()
    selected = [root / name for name in COMMON_FILES + HOST_FILES[host]]
    selected += [root / "scripts" / name for name in SCRIPTS]
    selected += [root / "skills" / name / "SKILL.md" for name in SKILL_NAMES]
    for path in selected:
        if not path.is_file() or not path.resolve().is_relative_to(root):
            raise ValueError(f"Missing or unsafe package file: {path}")
        for component in (path, *path.parents):
            if component == root:
                break
            if component.is_symlink():
                raise ValueError(f"Symlink not allowed in package: {component}")
    return sorted(selected)


def build_package(root, host, output_dir):
    root = Path(root).resolve()
    files = package_files(root, host)
    manifest = json.loads((root / HOST_FILES[host][0]).read_text(encoding="utf-8"))
    version = manifest["version"]
    if not version or any(char not in "0123456789abcdefghijklmnopqrstuvwxyz.-+" for char in version):
        raise ValueError("Unsafe package version")
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"wow-addon-engineer-{host}-{version}.zip"
    # Exclusive creation protects an existing reviewed artifact from overwrite.
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            relative = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo("wow-addon-engineer/" + relative, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=HOST_FILES, required=True)
    parser.add_argument("--out-dir", type=Path, default=Path("dist"))
    args = parser.parse_args(argv)
    try:
        output = build_package(Path(__file__).resolve().parents[1], args.host, args.out_dir)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"Packaging failed: {error}\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
