# Installation and plugin format

Format and installation guidance checked against official documentation on **2026-10-22**:

- [OpenAI: Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [OpenAI: Desktop-only plugins](https://developers.openai.com/plugins/deploy/desktop-only)
- [OpenAI: Submission requirements](https://developers.openai.com/plugins/deploy/submission)
- [Claude Code: Plugin reference](https://code.claude.com/docs/en/plugins-reference)
- [Claude Code: Plugin loading and npm dependencies](https://code.claude.com/docs/en/plugins/loading#nodejs-package-dependencies)
- [Claude Code: Marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference)
- [Claude Code: Skills](https://code.claude.com/docs/en/skills)

## Shared repository, distinct entry points

```text
plugin.json                         Portable Agent Plugins identity (Codex package)
.codex-plugin/plugin.json           Codex compatibility overlay and presentation
mcp.json                            Portable stdio MCP connection (Codex package)
.mcp.json                           Codex compatibility MCP connection
.agents/plugins/marketplace.json    Codex repository marketplace
.claude-plugin/plugin.json          Claude Code manifest and inline MCP connection
.claude-plugin/marketplace.json     Claude Code marketplace
package.json / package-lock.json    Claude-only pinned npm dependency metadata
skills/<name>/SKILL.md              The same seven skills for both hosts
scripts/                           Original Python, PowerShell, and Node helpers
docs/                              Shared engineering and integration references
assets/logo.png                    Supplied project artwork
```

Current OpenAI documentation prefers root `plugin.json` with the Agent Plugins 1.0.0 schema. It also supports the `.codex-plugin/plugin.json` compatibility overlay. This project supplies both: portable identity stays at the root; Codex-specific settings stay in the separate overlay. There is no inline `extensions.com.openai` object overriding the overlay. The overlay marks local execution as required and declares `./.mcp.json` for compatibility. Portable hosts discover root `mcp.json` automatically; each server declares its transport type. The Codex compatibility connection additionally declares `env_vars: ["WAE_WOW_API_MCP"]`; Codex overlays that explicit allowlist onto the portable server so a custom installed path reaches the MCP process. The portable MCP schema remains unchanged.

Claude discovers `skills/` at the plugin root automatically. Its manifest stays in `.claude-plugin/`, while skills, scripts, assets, and references stay outside that metadata directory. Its inline `mcpServers.wow_api` connection uses `${CLAUDE_PLUGIN_ROOT}`; the Codex files use `${PLUGIN_ROOT}`. Within a plugin, Claude loads root `.mcp.json` first and then the inline declaration, so the same-name inline server replaces the Codex entry. Running Claude from this repository root additionally loads `.mcp.json` as a separate project configuration, which can report an unexpanded `PLUGIN_ROOT` or duplicate the connection. Preview from another workspace with an absolute plugin path, as shown below. The Claude ZIP excludes the root MCP files, so its installed package has no such project-file collision.

Each marketplace points at `./`, relative to the repository/extracted package root. No symlinks or copied skill trees are necessary. Supporting links inside skills resolve relative to their own `SKILL.md`, as the instructions explicitly state. This is a shared Markdown convention; packaging tests verify targets remain inside both archives.

The Codex ZIP includes its portable manifest, overlay, marketplace, and both MCP configuration files. The Claude ZIP includes its own manifests/marketplace, `package.json`, and `package-lock.json`; it excludes root `plugin.json`, `mcp.json`, `.mcp.json`, and Codex metadata. Neither ZIP contains `node_modules/` or upstream code/data. Shared skills and helpers are byte-identical between ZIPs.

## Packaged MCP connection

Version 0.2.2 declares a `wow_api` stdio connection for both hosts, with native **Node.js >=20.11** on the executing host's `PATH`. Claude Code installs exact `@nighthawk42/wow-api-mcp@0.2.2` from npm into its cached marketplace plugin using the packaged lockfile, then runs its `dist/index.js` directly. This requires a Claude Code version supporting [plugin npm dependencies](https://code.claude.com/docs/en/plugins/loading#nodejs-package-dependencies). Claude's dependency installation uses `--ignore-scripts`; it is performed by the host, not by this project's scripts. A checkout previewed with `--plugin-dir` or installed from a **local-path marketplace** is loaded in place and needs a manual `npm ci --ignore-scripts` there to test MCP startup.

Codex continues to run the original `scripts/mcp_launcher.mjs`, which resolves a separately installed external package or an existing `WAE_WOW_API_MCP` entrypoint. See [integration setup](integrations.md#wow-api-mcp-packaged-connection). The Python doctor reports only PATH-based local detection; it cannot inspect Claude's cached dependency. Inspect the host's actual MCP status and tool list. If Node or the server is unavailable, the seven skills and other helpers remain usable. Disable duplicate independent MCP connections manually.

A desktop app must inherit Node's `PATH` and, for Codex overrides, `WAE_WOW_API_MCP`. Fully quit and restart it after environment changes; setting a variable in an unrelated terminal does not update an already-running app.

## Windows

Use a real Python 3.10+ installation, or an existing interpreter already available to the agent. The project does not install Python. Python supports the addon helpers; the packaged MCP launcher uses Node independently.

```powershell
$env:WAE_PYTHON = 'C:\Path With Spaces\Python\python.exe'
.\scripts\doctor.ps1 --json
.\scripts\check-addon.ps1 'C:\Path With Spaces\MyAddon' --json
```

`WAE_PYTHON` contains one path, without embedded arguments. The wrappers also try `py -3`, `python`, and `python3`; they skip Microsoft Store aliases and preserve the script exit code. Existing PowerShell execution policy remains in force.

Paths with spaces and Unicode are supported. No Unix shell is needed for the built-in helpers. BigWigs Packager is the exception: an externally installed Bash 4.3+ and its Unix prerequisites are required. A detected `bash` executable alone does not establish those prerequisites; WSL and Git Bash paths may need explicit conversion.

Some Windows installations protect Documents through Controlled Folder Access. If a trusted interpreter cannot write build/test artifacts there, use an allowed temporary `--out-dir` and copy the reviewed result with an allowed file tool. Do not disable security controls. This affects artifact creation, not the read-only addon checker.

## Register, inspect, remove

Run from the root of the checkout or the extracted host-specific plugin folder:

```powershell
codex plugin marketplace add .
codex plugin add wow-addon-engineer@wow-addon-engineer-marketplace
codex plugin list
```

These CLI commands are supported by the locally inspected Codex 0.163.0. Host availability and the Plugins UI may differ on older clients. The documented desktop alternative is to open this repository, refresh/restart the app, and install from the repository marketplace in Plugins.

```powershell
claude plugin validate --strict .claude-plugin/plugin.json
claude plugin validate --strict .claude-plugin/marketplace.json
claude plugin marketplace add . --scope local
claude plugin install wow-addon-engineer@wow-addon-engineer-marketplace --scope local
```

The Claude command syntax was checked against 2.1.215. `--scope local` keeps installation settings local to the current project. Because these examples add a **local-path** marketplace, run `npm ci --ignore-scripts` once in the checkout before checking its MCP; a GitHub marketplace install is copied and receives the host-managed dependency. For a session preview without registering a marketplace, run `claude --plugin-dir "C:\Path\wow-addon-engineer"` from a different workspace, or `claude --plugin-dir "/path/to/wow-addon-engineer"` on POSIX. Do not start this preview from the plugin repository root. Current Claude documentation requires 2.1.281 or later for MCP-entry validation in `claude plugin validate`; validation on an older client does not establish that the MCP configuration loads or connects.

After an update, refresh the installed copy from the selected marketplace and restart the host with the intended environment. Open a fresh session, inspect the host's MCP status and actual tools, and test a small permitted query. Also test a clean install from each host-specific ZIP: a successful manifest check alone is not a protocol handshake or evidence of API data coverage. The commands above are installation instructions, not a claim that these checks have run.

Optional removal:

```powershell
codex plugin remove wow-addon-engineer@wow-addon-engineer-marketplace
codex plugin marketplace remove wow-addon-engineer-marketplace
claude plugin uninstall wow-addon-engineer@wow-addon-engineer-marketplace --scope local
claude plugin marketplace remove wow-addon-engineer-marketplace
```

Marketplace registration and installation change host settings. The project never runs these automatically or modifies global configuration through a hook. Public-directory submission, Git hosting, and publishing are separate user-authorized operations. OpenAI public submissions with a local MCP require an approved partner and an allowlisted submitting organization. Include the MCP integration in the initial submission ZIP: the current portal does not support adding MCP to an existing skills-only plugin. See [desktop-only eligibility](https://developers.openai.com/plugins/deploy/desktop-only) and [submission requirements](https://developers.openai.com/plugins/deploy/submission).
