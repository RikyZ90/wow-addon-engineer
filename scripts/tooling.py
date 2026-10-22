"""Discover optional user-installed tools; never install or probe by execution."""

import json
import os
from pathlib import Path
import shutil
import sys


# Commands are names, never shell fragments. Overrides are one executable/file.
TOOLS = {
    "wow-api-mcp": ("WAE_WOW_API_MCP", ("wow-api-mcp",)),
    "wowlua-ls": ("WAE_WOWLUA_LS", ("wowlua_ls",)),
    "stylua": ("WAE_STYLUA", ("stylua",)),
    "wow-ui-sim": ("WAE_WOW_UI_SIM", ("wow-sim",)),
    "lychee": ("WAE_LYCHEE", ("lycheedev",)),
    "bigwigs-packager": ("WAE_BIGWIGS_PACKAGER", ("release.sh",)),
}


def _nighthawk_entrypoint(shim, actual):
    for package in (actual.parent.parent,
                    shim.parent / "node_modules/@nighthawk42/wow-api-mcp",
                    shim.parent / "../@nighthawk42/wow-api-mcp",
                    shim.parent / "../lib/node_modules/@nighthawk42/wow-api-mcp"):
        package = package.resolve()
        manifest = package / "package.json"
        if not manifest.is_file():
            continue
        metadata = json.loads(manifest.read_text(encoding="utf-8"))
        if not isinstance(metadata, dict) or metadata.get("name") != "@nighthawk42/wow-api-mcp":
            raise ValueError("Unexpected npm package identity")
        bins = metadata.get("bin")
        entry = bins.get("wow-api-mcp") if isinstance(bins, dict) else None
        if not isinstance(entry, str):
            raise ValueError("Missing npm entry point")
        target = (package / entry).resolve(strict=True)
        target.relative_to(package)
        if target.suffix.lower() not in (".js", ".mjs") or not target.is_file():
            raise ValueError("Invalid npm entry point")
        return target
    return None

def find_tool(name):
    variable, candidates = TOOLS[name]
    override = os.environ.get(variable)
    found = None
    for candidate in (override,) if override is not None else candidates:
        found = shutil.which(candidate)
        if not found and override is not None:
            path = Path(candidate).expanduser()
            if path.is_file():
                found = str(path.resolve())
        if found:
            break
    result = {"tool": name, "environment_variable": variable,
              "path": found, "status": "missing", "command": []}
    if not found:
        if override is not None:
            result["status"] = "invalid-override"
        return result
    path = Path(found)
    if name == "wow-api-mcp":
        try:
            actual = path.resolve(strict=True)
            if override is not None:
                if Path(override).suffix.lower() not in (".js", ".mjs") or actual.suffix.lower() not in (".js", ".mjs"):
                    raise ValueError("The override must be a JavaScript entry point")
                path = actual
            else:
                path = _nighthawk_entrypoint(path, actual)
                if path is None:
                    raise ValueError("The Nighthawk npm package was not found")
        except (OSError, ValueError, RuntimeError):
            result["status"] = "needs-direct-entrypoint"
            result["detail"] = "Use an existing .js/.mjs override or install @nighthawk42/wow-api-mcp with its JavaScript entry point inside the package."
            return result
        result["path"] = str(path)
    suffix = path.suffix.lower()
    interpreter = {".js": "node", ".mjs": "node", ".sh": "bash"}.get(suffix)
    if suffix == ".py":
        interpreter = sys.executable
    if suffix in (".cmd", ".bat", ".ps1"):
        result["status"] = "needs-direct-entrypoint"
        result["detail"] = "Set the override to the installed .js, .mjs, .py, .sh, or executable entry point."
    elif interpreter:
        runner = shutil.which(os.environ.get("WAE_BASH", "bash") if interpreter == "bash" else interpreter)
        if interpreter == "bash" and sys.platform == "win32" and not os.environ.get("WAE_BASH"):
            git = shutil.which("git")
            git_bash = Path(git).parent.parent / "bin" / "bash.exe" if git else None
            if git_bash and git_bash.is_file():
                runner = str(git_bash)
        if not runner:
            result["status"] = "missing-interpreter"
            result["detail"] = interpreter
        elif Path(runner).suffix.lower() in (".cmd", ".bat", ".ps1"):
            result["status"] = "needs-direct-entrypoint"
            result["detail"] = "The interpreter must be a native executable, not a shell shim."
        else:
            result.update(status="available", command=[runner, str(path)])
    elif os.name != "nt" and not os.access(path, os.X_OK):
        result["status"] = "not-executable"
    else:
        result.update(status="available", command=[str(path)])
    return result
