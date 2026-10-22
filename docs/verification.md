# Verification record

Latest update: **2026-10-22**. Earlier checks below retain their 2026-10-21 scope. This record distinguishes local checks, actual host checks, and the historical manual sample check. The repository's Actions page reports subsequent GitHub CI runs; no OpenAI directory approval is claimed.

## 0.2.1 English publication preparation (2026-10-22)

- Windows / Python 3.12.14: **46 tests passed**, including the translated smoke messages with real Lua 5.4.6.
- Windows / Node 24.20.0: **8 tests passed; 3 POSIX-only checks skipped**.
- Offline project validation and native Claude manifest/marketplace validation passed.
- The English quick-start guide is included in both host archive allowlists. The optional MCP installation command is user-run only; no installer invokes npm automatically.
- No new game-client check was performed for the English smoke messages. The 0.2.0 MCP startup code and connection declarations are unchanged.

## 0.2.0 packaged MCP connection (2026-10-22)

- Windows / Python 3.12.14: all **46 regression tests passed**, including real Lua sample checks, Windows wrappers, host archive content, read-only discovery, package identity, path boundaries, and explicit empty-override handling.
- Windows / Node 24.20.0: **8 launcher tests passed; 3 POSIX-only symlink/signal tests skipped**. Tests preserve literal arguments, exit codes and JSON stdio; the server uses the launcher PID, so force-stopping the launcher cannot leave a separate spawned server process.
- The portable Codex, compatibility Codex and inline Claude declarations each launched the existing external Nighthawk 0.2.2 server through the original adapter. All three completed MCP initialization (2024-11-05), listed **14 tools**, and successfully called `list_flavors`. These are direct configuration/adapter protocol checks, not native-host checks.
- A clean Codex 0.163.0 install into an isolated temporary home listed version 0.2.0 as installed/enabled. Its actual app-server discovered all **seven namespaced skills** and **14 MCP tools**. The first native check exposed Codex's filtered process environment; declaring only `WAE_WOW_API_MCP` in the compatibility configuration's `env_vars` fixed the handshake. The portable schema remains valid. Codex logged optional resource-list methods as unsupported; tool discovery succeeded.
- A clean Claude 2.1.215 marketplace install into a private temporary `CLAUDE_CONFIG_DIR` passed. Its real first-turn initialization reported `plugin:wow-addon-engineer:wow_api` connected, **14 MCP tools**, and all **seven namespaced skills**. Only the model response was simulated by an original HTTP fixture bound to loopback; no real model inference or external Anthropic request occurred. Earlier sandbox preview attempts omitted MCP because the private profile could not be written; those attempts do not establish a format defect. The successful installation used the unmodified host-specific Claude ZIP and no extra root MCP file.
- Node 20.11.1 launcher tests are configured in the Windows/Linux/macOS CI matrix. This new launcher has not been executed on Linux/macOS or that minimum Node release locally; remote CI has not run. The earlier Linux addon tests do not establish the new launcher's portability.

Only original connection configuration and the Node adapter are packaged. The server, runtime, installed npm dependencies, and datasets remain outside this repository and both archives. No game-process access, publishing, credential changes, or real model inference formed part of these MCP checks. Native client tests used isolated settings; no personal plugin installation was replaced.

## Earlier automated and host checks

- The original 35 regression tests passed on Windows/Python 3.12.14.
- After adding the smoke addon and Windows Bash selection tests, Linux/Python 3.10 and 3.12 each completed **39 tests: 36 passed, 3 Windows-only tests skipped**. Containers mounted this repository read-only; actual Lua 5.1.5 ran the state/event tests.
- Windows Python 3.10.20 was installed only in an external temporary lab, without PATH or registry registration. Its initial run passed the original tests and Lua test while a concurrent sample-file write left one structural test incomplete. That partial run is not reported as a complete Windows 3.10 pass. A later restricted rerun encountered fixture-directory ACL errors during setup/cleanup; its two read-only sample checks passed, but the full rerun remains blocked by the environment. No stronger-permission retry was attempted after approval review became unavailable.
- Two focused sample tests and nine tool-adapter tests passed on Windows, using existing Lua 5.4.6 for the sample and isolated fixtures for the adapters.
- Codex CLI 0.163.0 installed the ZIP in an isolated home; its actual app-server initialize/skills/list returned all **seven enabled namespaced skills**.
- Claude Code 2.1.215 strict manifest validation and isolated installation passed. Its actual initialization event registered all **seven namespaced slash skills**. A separate read-only model request failed with ConnectionRefused at the configured endpoint, with zero input/output tokens and zero recorded cost; native Claude response quality remains unverified.
- All **ten behavioral response scenarios** were run by an independent agent using the installed skills without the grading rubric. Parent assessment passed each scenario's reasoning/boundary expectations. Missing-context replies are not claims of completed addon edits. See [results](../evals/results-2026-10-21.json).
- The original sample exercises existing namespaces, conservative saved-data migration, recursive XML, commands, and event ordering. Tests use original API mocks; they do not certify game behavior.

The CI file contains the intended platform matrix. Linux runs were local Docker runs, not GitHub Actions. macOS and remote CI remain unexecuted; no remote repository was created to run them.

## Real external integration checks

All external tooling was installed independently under a temporary lab, outside the repository. No upstream source, binary, container layer, database or dependency is included in the plugin packages.

| Integration | Actual check | Result and limit |
| --- | --- | --- |
| @nighthawk42/wow-api-mcp 0.2.2 | MCP initialize, tools/list, flavor/API queries | Handshake and 14 tools available; Forever data is 1.60.1.70450, Interface 16001 |
| wowlua-ls 0.35.1 | Valid fixture; typed-call mismatch and invalid token | Valid exit 0; negative exit 1 with type-mismatch warning and syntax error. Sample check reported no issues |
| StyLua 2.6.0 | Normalized fixture; unformatted fixture | Check exit 0 versus expected exit 1. Sample's default formatting check reported differences; these are not syntax/runtime failures |
| wow-ui-sim release 0.1.32 | Native --version; Docker headless base and original fixture | Native version works; native headless needs a separate Blizzard UI/CASC setup. Docker network-none base returned no Lua errors; explicit-load fixture passed 2/2 tests |
| Lychee Dev 3.2.5 | version/describe JSON | Metadata commands exit 0. No game process attachment, hotkeys, runtime addon or live operation |
| BigWigs Packager 2.6.1 | Original external fixture with -d -e -l | Local archive created and CRC checked, no upload/externals/localization fetch. Used Bash 5.3.15 and external Info-ZIP |

Simulator detail: the image tagged 0.1.32 reports an executable version 0.1.0, while the Windows executable reports 0.1.32. The working container was pinned to amd64 digest sha256:451e83425d4a67d08325ae7c834a81ce67f73d979053c93bc0b4158d3b102a8e. Automatic fixture startup failed; the 2/2 result used explicit --exec-lua loading before run-tests. It does not certify automatic addon startup or Forever fidelity.

Source detail: one MCP-rendered API name incorrectly added a namespace to InCombatLockdown. The literal pinned documentation declared an empty namespace. Source declarations take precedence over tool rendering; the sample does not depend on that function.

## Manual client test

The owner authorized deployment of six original runtime files to the selected Forever AddOns folder. Copies were hash-checked; existing addons and SavedVariables were untouched.

On 2026-10-21 the owner reported that all instructed manual tests worked and supplied a screenshot. Directly visible: client **1.60.1**, build **70532**, Interface **16001**, schema **2**, load/login/reload counters, saved messages-off state and messages-on toggle output. The broader login/reload/persistence/combat result is **user-reported**, not an automated observation. The screenshot's combat state is unknown; it alone does not demonstrate a combat transition.

The API evidence used for preparation was the older matching-product source build 70450. The smoke result on 70532 validates the earlier sample revision; the English sample 0.1.1 changes messages only and has not had a new in-game test. That result makes no blanket Forever or other-flavor compatibility claim. Secure actions, taint correctness, Secret Values and unrelated addons were not tested. See [procedure](runtime-test.md).
