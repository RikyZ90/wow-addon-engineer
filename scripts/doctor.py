"""Report local prerequisites without executing optional tools or making requests."""

import argparse
import json
import sys
import shutil

try:
    from .tooling import TOOLS, find_tool
except ImportError:
    from tooling import TOOLS, find_tool


def diagnose():
    return {
        "python": sys.version.split()[0],
        "platform": sys.platform,
        "hosts": {name: shutil.which(name) for name in ("codex", "claude")},
        "tools": [find_tool(name) for name in TOOLS],
        "notes": ["Detection only: versions, upstream identity, licenses, MCP connectivity, and client compatibility are not verified.",
                  "Every external tool is optional. No downloads, tool startup, or game process access occurred."],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable diagnostics")
    args = parser.parse_args(argv)
    result = diagnose()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"WoW Addon Engineer doctor | Python {result['python']} | {result['platform']}")
        for tool in result["tools"]:
            print(f"{tool['tool']}: {tool['status']}" + (f" ({tool['path']})" if tool["path"] else ""))
        for note in result["notes"]:
            print(note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
