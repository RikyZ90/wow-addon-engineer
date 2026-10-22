"""Explicitly invoke an already-installed tool; no shell, fetch, or installation."""

import argparse
import subprocess
import sys

try:
    from .tooling import TOOLS, find_tool
except ImportError:
    from tooling import TOOLS, find_tool


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool", choices=TOOLS)
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    arguments = args.arguments
    if arguments[:1] == ["--"]:
        arguments = arguments[1:]
    tool = find_tool(args.tool)
    if tool["status"] != "available":
        print(f"{args.tool}: {tool['status']}. Configure {tool['environment_variable']} with an installed entry point.", file=sys.stderr)
        return 127
    try:
        return subprocess.run(tool["command"] + arguments, shell=False, check=False).returncode
    except OSError as error:
        print(f"Could not start {args.tool}: {error}", file=sys.stderr)
        return 126
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
