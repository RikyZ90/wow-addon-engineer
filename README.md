<p align="center"><img src="assets/logo.png" width="360" alt="WoW Addon Engineer logo"></p>

# WoW Addon Engineer

[![Checks](https://github.com/RikyZ90/wow-addon-engineer/actions/workflows/ci.yml/badge.svg)](https://github.com/RikyZ90/wow-addon-engineer/actions/workflows/ci.yml)

A plugin for **OpenAI Codex** and **Claude Code** that helps agents create, research, debug, review, test, and prepare releases of World of Warcraft addons in Lua.

**One repository. Seven shared skills. Packaged MCP connection. Separate host manifests and installable ZIPs.**
Original source and documentation use MIT. External tools remain user-installed: **invoke, do not vendor**.

## Quick start

This is an **AI coding plugin**, not an in-game addon. Install it in Codex or Claude Code; do not copy this repository into WoW's `Interface/AddOns` folder.

Use a current plugin-capable host. The local helpers require **Python 3.10+**. The optional API research connection also needs **Node.js 20.11+** and a separately installed `@nighthawk42/wow-api-mcp` server. The plugin starts an existing server; it never downloads or installs one.

**Codex** — run in your addon workspace:

```sh
codex plugin marketplace add RikyZ90/wow-addon-engineer
codex plugin add wow-addon-engineer@wow-addon-engineer-marketplace
```

**Claude Code** — run in your addon workspace, outside this plugin repository:

```sh
claude plugin marketplace add RikyZ90/wow-addon-engineer --scope local
claude plugin install wow-addon-engineer@wow-addon-engineer-marketplace --scope local
```

Start a fresh session. In Codex, ask: **"Use WoW Addon Engineer / get-started for this addon."** In Claude Code, invoke:

```text
/wow-addon-engineer:get-started
```

See the [quick installation guide](docs/quick-start.md) for prerequisites, local checks, and optional MCP setup. Both hosts use the same seven skills.

## What it does

| Skill | Outcome |
| --- | --- |
| `get-started` | Identify the addon and client target; inspect prerequisites |
| `wow-addon-create` | Build a minimal addon or feature using verified APIs |
| `wow-addon-debug` | Trace reproducible errors, event timing, taint, and combat restrictions |
| `wow-addon-review` | Review correctness, persistence, performance, and architecture |
| `wow-addon-research` | Find build-specific API, Blizzard generated documentation, and FrameXML evidence |
| `wow-addon-test` | Separate structural, static, simulated, and real-client checks |
| `wow-addon-release` | Prepare and inspect an addon package with license and release checks |

The workflows require evidence for flavor, build, TOC Interface, and API signatures. They cover secure frames, combat lockdown, taint, and Secret Values without suggesting bypasses.

**No blanket client compatibility claim:** an upstream tool accepting a flavor label does not establish addon correctness on that client. Each task must verify the installed tool's actual data/build coverage. This project does not certify Retail, Forever, or any other flavor.

## Install

The [quick installation guide](docs/quick-start.md) covers installation directly from GitHub. For an existing local checkout or a host-specific ZIP you built yourself, see [installation and format evidence](docs/installation.md). Extract ZIPs before registration; marketplace commands do not accept ZIP paths. Codex desktop can also discover the repository's `.agents/plugins/marketplace.json` in its Plugins UI.

## Check prerequisites and an addon

Windows PowerShell, from this checkout:

```powershell
.\scripts\doctor.ps1 --json
.\scripts\check-addon.ps1 "C:\Games\World of Warcraft\CLIENT\Interface\AddOns\MyAddon" --json
```

If Python is outside PATH, set `WAE_PYTHON` to the executable path. The wrappers skip Microsoft Store execution aliases; no system settings are changed.

On macOS/Linux, or with a directly selected Python interpreter:

```sh
python3 scripts/doctor.py --json
python3 scripts/check_addon.py "/path/to/MyAddon" --toc MyAddon.toc --json
```

The checker reads TOCs and referenced XML/Lua paths, follows XML includes, verifies portable casing and addon boundaries, and reports load order. It does not execute Lua or validate API semantics. Exit codes: **0** structural checks pass (warnings possible), **1** structural findings, **2** invalid arguments/path. See [check limitations](docs/checks.md).

## Optional integrations

| Integration | Actual command | Purpose |
| --- | --- | --- |
| wow-api-mcp | `wow-api-mcp` | Connected API/documentation/source research; provider identity must be recorded |
| wowlua-ls | `wowlua_ls` | Static analysis using installed, target-specific data |
| StyLua | `stylua` | Lua formatting checks |
| wow-ui-sim | `wow-sim` | Headless simulated UI checks |
| Lychee Dev | `lycheedev` | Explicit local/runtime development workflows |
| BigWigs Packager | external `release.sh` through Bash | Addon release packaging |

`doctor` only detects paths. It does not launch servers, query versions, contact WoW, or install anything.
The plugin declares a local `wow_api` MCP connection for both hosts. Its original Node launcher starts an existing server selected by `WAE_WOW_API_MCP`, or detects the installed Nighthawk npm package associated with `wow-api-mcp` on PATH. It never downloads or installs a server. An invalid explicit override fails without falling back. Set environment overrides before restarting the host app; use a new session after upgrading the plugin. A missing server produces an unavailable MCP connection while the skills remain usable.

[Integration setup](docs/integrations.md) documents Windows and macOS/Linux setup, verified upstream identities, and invocation limits. GPL tools are external processes; their code and binaries are absent from this repository and its packages. Lychee also remains user-installed.

## Develop and package

```sh
node --test tests/test_mcp_launcher.mjs
python3 -m unittest discover -s tests -v
python3 scripts/validate_project.py
python3 scripts/package_plugin.py --host codex
python3 scripts/package_plugin.py --host claude
```

On Windows, substitute your installed `python`, `py -3`, or explicit executable for `python3`. ZIPs are written to `dist/`; existing archives are preserved, so use a fresh `--out-dir` for rebuilds. Packaging makes no network requests and does not install or publish the plugin.

CI is configured for Windows, Linux, and macOS, including minimum Python 3.10. The original local Linux checks also executed actual Lua 5.1; Node launcher checks are included in CI for all three operating systems. [Ten behavioral response assessments](evals/results-2026-10-21.json) are recorded separately; offline CI validates definitions, not model behavior. See [verification](docs/verification.md) for actual results and limits.

The original [smoke addon](examples/WoWAddonEngineerSmoke/README.md) and [manual procedure](docs/runtime-test.md) exercise persistence and safe event handling. The owner confirmed the earlier sample revision on client 1.60.1 build 70532; the English message revision has local tests but no new in-game check; this is a bounded sample result, not flavor-wide certification.

See [usage examples](examples/usage.md), [engineering baseline](docs/wow-engineering.md), [licensing](docs/licensing.md), and [third-party notices](THIRD_PARTY_NOTICES.md).

World of Warcraft and Blizzard are trademarks of their respective owners. This is an independent project, without Blizzard, OpenAI, or Anthropic endorsement. The supplied logo's scope is recorded in the licensing documentation.
