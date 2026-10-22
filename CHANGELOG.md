# Changelog

## 0.2.2 - 2026-10-22

- Add a Claude Code-only npm manifest and lockfile pinned to @nighthawk42/wow-api-mcp 0.2.2, allowing supported marketplace installs to fetch the MCP server into Claude's plugin cache.
- Run the Claude MCP directly from the host-managed dependency; keep Codex's installed-server launcher and one-time manual npm setup.
- Verify the Claude ZIP contains dependency metadata but no upstream code or node_modules; update installation, integration, and licensing guidance.

## 0.2.1 - 2026-10-22

- Add an English quick-start guide with direct GitHub marketplace installation for Codex and Claude Code.
- Include repository links and homepage metadata in both host packages.
- Translate the optional smoke addon's messages and manual test procedure to English; sample version 0.1.1 preserves its saved-data schema and behavior.
- Include the quick-start guide in both distributable archives and exclude local npm dependency folders from Git.

## 0.2.0 - 2026-10-22

- Declare a local wow_api MCP connection in the portable Codex, compatibility Codex, and Claude packages.
- Add an original Node launcher for already-installed MCP servers, with explicit path overrides and Nighthawk npm-package discovery on Windows, macOS, and Linux.
- Keep server code, binaries, data and dependencies external; no automatic downloads or installation.
- Align read-only doctor discovery with the installed Nighthawk npm entrypoint and test MCP paths in host archives.
- Add launcher regression checks to CI and document environment setup and local-MCP publication eligibility.
- Shorten the Codex listing summary to fit the documented length limit.

## 0.1.1 - 2026-10-21

- Correct wow-ui-sim discovery to wow-sim; the current wow-cli is a separate thin client.
- Prefer installed Git Bash on Windows and support WAE_BASH for external shell scripts.
- Add an original TOC/XML/Lua smoke addon with saved-data migration and actual Lua tests.
- Record all ten behavioral scenarios, native host skill discovery, six integration checks, and the owner's client smoke confirmation.
- Complete local Linux Python 3.10/3.12 checks and preserve explicit runtime/source coverage limits.

## 0.1.0 - 2026-10-21

- Initial shared Codex and Claude Code plugin packaging and marketplaces.
- Seven addon engineering skills with build-specific API evidence requirements.
- Read-only TOC/XML checks, optional tool detection, and explicit invocation adapter.
- Python standard-library implementation and Windows PowerShell wrappers.
- Host-specific ZIP builder, cross-platform CI, regression tests, and behavioral eval scenarios.
- Invoke-do-not-vendor integration and licensing documentation; supplied project logo.
