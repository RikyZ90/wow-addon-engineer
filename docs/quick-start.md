# Quick installation guide

WoW Addon Engineer is a plugin for **OpenAI Codex** and **Claude Code**. It gives both hosts the same seven skills for creating, researching, debugging, reviewing, testing, and preparing addon releases.

**Install it in your AI coding host. Do not copy the plugin repository into WoW's `Interface/AddOns` folder.** Your addon remains a separate project.

## 1. Check prerequisites

- A current Codex or Claude Code version with plugin support.
- **Python 3.10+** for the local diagnostic and addon-checking helpers. They use only the standard library.
- Optional API research: an existing native **Node.js 20.11+** on the host's `PATH`, plus a separately installed **`@nighthawk42/wow-api-mcp`** server from [Nighthawk42/wow_api_mcp](https://github.com/Nighthawk42/wow_api_mcp). Follow that project's setup instructions before enabling the connection.

The plugin does not install Python, Node, or external tools. Its MCP launcher starts an already-installed server without `npx` or package downloads. Missing MCP prerequisites leave that connection unavailable; the seven skills and Python helpers remain usable.

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

If you choose to install the optional server yourself, the version used in this project's MCP verification can be installed separately with npm:

```sh
npm install --global @nighthawk42/wow-api-mcp@0.2.2
```

This is a manual upstream installation, not part of the plugin installer. Review the [server's license and data terms](https://github.com/Nighthawk42/wow_api_mcp) first. No server code or dependencies are included in this repository or its ZIPs.

With Node and the Nighthawk server already installed, the host can start the packaged `wow_api` connection when the plugin is enabled. The launcher detects the installed package behind `wow-api-mcp` on `PATH`.

For a custom server location, set **`WAE_WOW_API_MCP`** to its existing direct `.js` or `.mjs` entrypoint before launching the host. It accepts one path, without flags. See the [Windows and macOS/Linux examples](integrations.md#wow-api-mcp-packaged-connection). An invalid explicit override fails instead of selecting another installation.

Fully quit and restart a desktop host after changing its environment, then open a fresh session and inspect its MCP status and actual tools. If you already configured the same server separately, disable one connection manually to avoid duplicates. Server operations may access the network and maintain upstream caches; the launcher itself performs no installation.

See [integration setup](integrations.md) for the other optional tools and [usage examples](../examples/usage.md) for common addon tasks.
