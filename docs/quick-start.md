# Quick installation guide

WoW Addon Engineer is a plugin for **OpenAI Codex** and **Claude Code**. It gives both hosts the same seven skills for creating, researching, debugging, reviewing, testing, and preparing addon releases.

**Install it in your AI coding host. Do not copy the plugin repository into WoW's `Interface/AddOns` folder.** Your addon remains a separate project.

## 1. Check prerequisites

- A current Codex or Claude Code version with plugin support.
- **Python 3.10+** for the local diagnostic and addon-checking helpers. They use only the standard library.
- Optional API research: native **Node.js 20.11+** on the host's `PATH`. Claude Code installs the pinned **`@nighthawk42/wow-api-mcp@0.2.2`** dependency from npm into its plugin cache when installed from the marketplace on a version supporting [plugin npm dependencies](https://code.claude.com/docs/en/plugins/loading#nodejs-package-dependencies). Codex needs a separately installed server from [Nighthawk42/wow_api_mcp](https://github.com/Nighthawk42/wow_api_mcp).

The plugin does not install Python or Node. Claude Code handles its one pinned MCP dependency; the Codex launcher only starts an already-installed server. Missing MCP prerequisites leave that connection unavailable; the seven skills and Python helpers remain usable.

## 2. Install from GitHub

Open a terminal in the **addon workspace where you want to use the plugin**. Choose your host below. These commands register the GitHub repository as a marketplace and install its plugin.

### Codex

```sh
codex plugin marketplace add RikyZ90/wow-addon-engineer
codex plugin add wow-addon-engineer@wow-addon-engineer-marketplace
codex plugin list
```

### Claude Code

Run these commands from your addon workspace, **outside the WoW Addon Engineer repository**:

```sh
claude plugin marketplace add RikyZ90/wow-addon-engineer --scope local
claude plugin install wow-addon-engineer@wow-addon-engineer-marketplace --scope local
```

The local scope keeps the installation settings local to the current project. Running Claude from the plugin repository root can also load its Codex-oriented `.mcp.json` as a project configuration, causing duplicate connections or an unexpanded `PLUGIN_ROOT`. Use your addon workspace for normal sessions.

For local checkouts, extracted packages, session previews, removal, and host format details, see [installation](installation.md).

## 3. Start a fresh session

In **Codex**, start a new chat and ask:

```text
Use WoW Addon Engineer / get-started for this addon.
```

In **Claude Code**, start a new session and invoke:

```text
/wow-addon-engineer:get-started
```

Provide your addon folder and the target WoW flavor, client build, and TOC Interface when known. The workflow verifies the target before relying on API or client behavior. An MCP connection alone does not establish support for a particular flavor or build.

## 4. Run local checks

Run these commands from the plugin's installed directory or a separate clone of this repository. If you prefer a clone for inspecting the helpers:

```sh
git clone https://github.com/RikyZ90/wow-addon-engineer.git
cd wow-addon-engineer
```

**Windows PowerShell:**

```powershell
.\scripts\doctor.ps1 --json
.\scripts\check-addon.ps1 'C:\Path\To\MyAddon' --json
```

Replace the addon path with your own. If Python is outside `PATH`, set `$env:WAE_PYTHON` to the existing Python executable before running the wrappers. They skip Microsoft Store execution aliases and do not change system settings.

**macOS/Linux:**

```sh
python3 scripts/doctor.py --json
python3 scripts/check_addon.py '/path/to/MyAddon' --toc MyAddon.toc --json
```

Replace the addon path and TOC filename with your own. `doctor` detects local paths without starting servers, installing tools, or contacting WoW. The addon checker inspects TOCs and referenced Lua/XML files without executing Lua. It does not prove API correctness or in-game behavior. See [check details and exit codes](checks.md).

## Optional: connect API research

**Claude Code marketplace install:** with Node available, Claude Code downloads the exact npm dependency selected by this plugin's `package-lock.json` into its own plugin cache. You do not need a global MCP installation. A local checkout loaded with `--plugin-dir` or installed from a **local-path marketplace** runs in place and is not copied into that cache; run `npm ci --ignore-scripts` in that checkout if you want to preview its MCP. This creates an ignored `node_modules/` directory, never a distributable file.

**Codex:** install the optional server yourself once, then restart Codex:

```sh
npm install --global @nighthawk42/wow-api-mcp@0.2.2
```

Review the [server's license and data terms](https://github.com/Nighthawk42/wow_api_mcp). The Codex launcher detects the installed package behind `wow-api-mcp` on `PATH`. For a custom Codex server location, set **`WAE_WOW_API_MCP`** to its existing direct `.js` or `.mjs` entrypoint before launching the host. See the [Windows and macOS/Linux examples](integrations.md#wow-api-mcp-packaged-connection).

Fully quit and restart the host after installing or changing its environment, then inspect actual MCP status and tools in a fresh session. If the same server is configured separately, disable one connection manually. Server operations may access the network and maintain upstream caches. No server code or dependencies are included in this repository or its ZIPs.

See [integration setup](integrations.md) for the other optional tools and [usage examples](../examples/usage.md) for common addon tasks.
