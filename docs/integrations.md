# External integrations

Connection guidance checked **2026-10-22**; other upstream observations below retain their stated version limits. Recheck the installed version's documentation and license for the actual task. Claude Code installs the one pinned MCP npm dependency when caching the marketplace plugin; the project scripts and doctor do not install tools. Tool calls may perform network/cache operations; inspect the chosen operation and the user's authorization. See [notices](../THIRD_PARTY_NOTICES.md).

## Detection and explicit invocation

Run <code>scripts/doctor.py --json</code> with Python 3.10+, or the PowerShell wrapper. It performs PATH/file lookup only.

| Adapter key | PATH candidate | Single-file override |
| --- | --- | --- |
| wow-api-mcp | wow-api-mcp, resolved to its installed Nighthawk JS entrypoint | WAE_WOW_API_MCP |
| wowlua-ls | wowlua_ls | WAE_WOWLUA_LS |
| stylua | stylua | WAE_STYLUA |
| wow-ui-sim | wow-sim | WAE_WOW_UI_SIM |
| lychee | lycheedev | WAE_LYCHEE |
| bigwigs-packager | release.sh | WAE_BIGWIGS_PACKAGER |

Statuses: available, missing, invalid-override, missing-interpreter, needs-direct-entrypoint, not-executable. "Available" is local detection, not a verified version, license, protocol handshake, data coverage, or client compatibility. The wow-api-mcp resolver additionally checks the installed package identity; that does not certify its behavior or data.

<code>python scripts/run_tool.py TOOL -- ARGS</code> forwards literal arguments, inherits stdio, and preserves the tool's exit status. Adapter failures: 127 unavailable, 126 failed start, 130 interrupted. Overrides contain one executable/entrypoint path without flags. No shell command strings or automatic installs are used. Arguments can still request upstream side effects: the caller must inspect them.

JS/MJS entrypoints use existing Node; PY uses the current Python; SH uses existing Bash. On Windows, shell scripts prefer Git Bash next to the installed Git executable; WAE_BASH can select an existing native Bash executable. Windows CMD/BAT/PS1 shims are not executed. For wow-api-mcp, known installed npm global/local layouts are inspected to resolve the shim to the package's real JS entrypoint; other adapters may require a direct entrypoint override. No npx/uvx, package-manager download, Docker pull, or curl-to-shell fallback exists.

## wow-api-mcp: packaged connection

Version 0.2.2 packages a `wow_api` MCP connection for both hosts. It requires native Node.js >=20.11 on the executing host's `PATH`. Claude Code installs pinned [Nighthawk42/wow_api_mcp](https://github.com/Nighthawk42/wow_api_mcp) package `@nighthawk42/wow-api-mcp@0.2.2` from npm into its plugin cache, then starts `dist/index.js` directly. Codex uses the original Node launcher and a separately installed copy. No upstream source, dependency, binary, API data, or cache is vendored in this repository or either ZIP.

The Codex launcher first uses `WAE_WOW_API_MCP` when set. It must name one existing direct `.js` or `.mjs` server entrypoint, without flags or shell syntax, belonging to the expected package. An invalid override fails explicitly and does not fall back to another installation. Without an override, it inspects `wow-api-mcp` candidates on `PATH` and known installed npm global/local layouts, checking package identity before selecting the real entrypoint. It never invokes npm or the shim. The Python doctor follows the same installed-package resolution without executing the server.

The unscoped [spartanui-wow/wow-api-mcp](https://github.com/spartanui-wow/wow-api-mcp) exposes the same executable name but is a different provider. It is not the packaged connection's target; a name match alone does not establish identity or compatible tools.

For a separately installed Codex server, set the override before launching the host. Replace these example paths with the real entrypoint:

Windows PowerShell:

~~~powershell
$env:WAE_WOW_API_MCP = 'C:\Tools\wow_api_mcp\dist\index.js'
.\scripts\doctor.ps1 --json
~~~

POSIX shell:

~~~sh
export WAE_WOW_API_MCP='/opt/wow_api_mcp/dist/index.js'
python3 scripts/doctor.py --json
~~~

These examples set the variable for the current shell and its child processes only. Fully quit and restart a desktop host so it inherits the intended environment; a GUI app opened elsewhere may not inherit this shell. Do not place secrets in manifests. Missing prerequisites leave the MCP unavailable while the skills remain usable.

Codex uses root `mcp.json` with the Agent Plugins schema, `type: "stdio"`, `command: "node"`, and `args: ["${PLUGIN_ROOT}/scripts/mcp_launcher.mjs"]`. Compatibility `.mcp.json` carries the same connection without the schema and explicitly forwards `WAE_WOW_API_MCP` through `env_vars`. Claude declares `wow_api` inline with `args: ["${CLAUDE_PLUGIN_ROOT}/node_modules/@nighthawk42/wow-api-mcp/dist/index.js"]`; its ZIP has the pinned npm manifest and lockfile but excludes the root MCP files. Its cached dependency is managed by Claude Code, so a missing `wow-api-mcp` on the global PATH does not indicate a Claude connection failure. See [installation and upgrade guidance](installation.md).

An existing manually configured MCP may duplicate the packaged connection. Inspect the host's server list and disable one manually; neither the launcher nor doctor edits configuration. After a fresh session connects, inspect its actual tool list, including the documented `list_flavors` operation when present. Record upstream version/revision and the returned data track/build for each research task. A connection does not promise support for any particular WoW flavor or build.

The upstream server provides generated API documentation, source/FrameXML, and wiki research. Tool operations can access the network and populate upstream-managed caches even though the launcher performs no installation. Apply the user's authorization to those operations. Upstream software licensing and Blizzard/wiki/cache content rights are separate from this plugin's original-code MIT license. Host references: [OpenAI packaging](https://developers.openai.com/plugins/build/plugins), [OpenAI local MCP requirements](https://developers.openai.com/plugins/deploy/desktop-only), [Claude MCP](https://code.claude.com/docs/en/mcp).

## wowlua-ls

[TradeSkillMaster/wowlua-ls](https://github.com/TradeSkillMaster/wowlua-ls), GPL-3.0. Native executable <code>wowlua_ls</code> / <code>wowlua_ls.exe</code>. Plain invocation starts an LSP server; do not use it as a version probe.

~~~powershell
python scripts/run_tool.py wowlua-ls -- check "C:/Work/MyAddon" --severity warning
~~~

Verify installed configuration schema and target data. Diagnostics can return exit 1. Selectors are versioned tool data, not a plugin compatibility promise. [CLI docs](https://tradeskillmaster.github.io/wowlua-ls/guide/cli.html). No GPL source, generated stubs, schema, or binaries are bundled.

## StyLua

[JohnnyMorganz/StyLua](https://github.com/JohnnyMorganz/StyLua), MPL-2.0. Check before formatting:

~~~powershell
python scripts/run_tool.py stylua -- --check --syntax lua51 "C:/Work/MyAddon"
~~~

Verify installed syntax options against the target dialect; this example selects Lua 5.1 syntax. Exit 1 may mean formatting differences. Formatting does not establish API correctness. No formatter source/binary is bundled.

## wow-ui-sim

[Osso/wow-ui-sim](https://github.com/Osso/wow-ui-sim), GPL-3.0-only. In the inspected 0.1.32 release, <code>wow-sim</code> implements GUI and headless subcommands. The separate <code>wow-cli</code> is a thin client for a running simulator and does not implement the headless commands below. Doctor detects wow-sim. Optional probe:

~~~powershell
python scripts/run_tool.py wow-ui-sim -- --no-addons --no-saved-vars lua-errors
~~~

This probe does not load/test the user's addon. Follow the installed version's profile, data, addon-mount and test setup; record what was loaded. Profile names/compiler features do not certify fidelity. The adapter never pulls images automatically and bundles no game/source assets. Native execution requires the upstream Blizzard UI/CASC data setup. The independent test used an explicitly downloaded, digest-pinned container outside this repository; see the verification record. Simulation cannot prove real-client secure/taint/Secret Values behavior.

## Lychee Dev

[Follen/Lychee-Dev](https://github.com/Follen/Lychee-Dev). Actual executable <code>lycheedev</code>. Optional metadata commands:

~~~powershell
python scripts/run_tool.py lychee -- version --format json
python scripts/run_tool.py lychee -- describe --format json
~~~

Existing npm entrypoint: <code>bin/lycheedev.mjs</code>, Node >=22.14; a native executable is another option. Current project code declares MIT, but notices separately identify dependency terms and unresolved image provenance. **User-installed only:** no binary, runtime addon, generated skill, image, or dependency is copied.

Live currently requires Windows amd64, a logged-in client, and upstream-managed in-game addon. It can read Lua mailbox state from process memory and send execution/reload hotkeys. These are explicit runtime operations, never automatic detection. Verify current prerequisites and obtain runtime authorization. Local structural checks and log-based diagnosis work without it.

## BigWigs Packager

[BigWigsMods/packager](https://github.com/BigWigsMods/packager). Existing external release.sh requires Bash >=4.3 plus documented archive/Unix/VCS prerequisites. Example disabling upload, external fetches, and localization fetches:

~~~powershell
$env:WAE_BIGWIGS_PACKAGER = 'C:/Tools/packager/release.sh'
python scripts/run_tool.py bigwigs-packager -- -d -e -l -t "/c/Work/MyAddon" -r "/c/Work/artifacts"
~~~

The example uses Git Bash /c/... paths. Pass paths in the chosen Bash environment, not Windows backslash paths; WSL needs Linux paths. The Windows test also required separately installed zip tooling, which the adapter never downloads. Inspect .pkgmeta and current help. Flag -d alone only disables uploads; -e and -l skip externals/localization, potentially leaving required dependencies missing. Such an archive is incomplete.

The inspected release.sh header contains the Unlicense/public-domain dedication; no root LICENSE was found. This is evidence about that script, not every repository artifact. No copy is included.
