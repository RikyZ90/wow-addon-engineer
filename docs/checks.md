# Checks and evidence levels

## Built-in addon checker

`scripts/check_addon.py ADDON [--toc relative.toc] [--json]` reads only the supplied addon directory. Without `--toc` it inspects every top-level TOC independently. It reports `addon`, `tocs`, `errors`, `warnings`, `info`, and `load_order`; paths in the load order are addon-relative and use forward slashes.

It checks numeric Interface metadata, file presence and exact portable case, XML well-formedness, recursive Script/Include file references, duplicates/cycles, and addon-directory boundaries. Missing Interface or referenced files are errors. Metadata and unrecognized conventions may produce warnings. Windows backslashes in resource references are accepted.

Exit **0** means no structural errors, with possible warnings. Exit **1** means structural errors. Exit **2** means invalid addon/path/CLI input. Neither 0 nor 1 establishes a compatible WoW client.

The checker rejects absolute paths, drive/UNC paths, parent traversal (`..` even if it would remain in the addon), and symlinks escaping the addon. DTD declarations/entities are rejected during XML parsing. It does not execute Lua, expand TOC variables/client-specific directives, resolve cross-addon XML imports, validate XML templates against a client schema, or parse Lua syntax/types. XML is expanded once per TOC: reference traversal order is reported, not a claim to emulate all client loader behavior. Correctness of SavedVariables initialization, taint, combat behavior, API availability, and Secret Values needs separate evidence.

## External static and simulated checks

[Integration commands](integrations.md) distinguish formatting from static analysis and simulation. Inspect tool help/version and target data before use. Preserve the actual diagnostics and exit code; do not suppress warnings into a fabricated clean result.

Use small addon-specific tests for pure Lua logic with the project's installed harness. Keep stubbed APIs visibly stubbed. A mock accepting an invented API signature is not evidence that the game supports it.

## Runtime

Use a user-authorized game session and existing debugging facilities. Record client build, test action, expected/observed behavior, relevant stack/events, combat state, and addon interactions. Avoid logging secret or private data. Lychee process access/hotkeys are a separate explicit action; detection never triggers them.

## Repository checks and evals

`python -m unittest discover -s tests -v` tests the checker, literal argument forwarding, non-executing detection, and host package isolation/reproducibility.

`python scripts/validate_project.py` validates this project's expected manifests, shared references, skill frontmatter, assets, and eval definition structure. It is a local contract check, not a full vendor JSON-schema validator. Claude's own `plugin validate --strict` and an isolated Codex install supply host validation when available.

[Behavioral evals](../evals/README.md) require an agent run with recorded output and rubric scoring. Merely loading their JSON or matching skill wording is not a passed behavioral eval.
