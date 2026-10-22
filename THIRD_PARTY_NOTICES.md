# Third-party notices

**No third-party source, binaries, databases, bundled skills/addons, or dependencies are redistributed in this repository or its ZIPs.** Claude Code downloads the pinned optional MCP dependency from npm into its own plugin cache; other integrations remain user-installed. These notices record boundaries, not replacement license grants.

Evidence reviewed **2026-10-21**. Immutable links preserve inspected snapshots; recheck installed versions.

| Tool/material | Observed license evidence | Boundary |
| --- | --- | --- |
| wow-api-mcp, unscoped spartanui-wow | [package.json at 81e96a3](https://github.com/spartanui-wow/wow-api-mcp/blob/81e96a304315bca2ac0ac1c064feaf97c323803e/package.json) declares MIT; no standalone LICENSE found | Full grant unverified; invoke only |
| wow-api-mcp, @nighthawk42 alternative | [MIT LICENSE at c3fb8bd](https://github.com/Nighthawk42/wow_api_mcp/blob/c3fb8bdb0beef34c2041ad9fd02ac80bd83016f2/LICENSE) for server; [attribution](https://github.com/Nighthawk42/wow_api_mcp/blob/c3fb8bdb0beef34c2041ad9fd02ac80bd83016f2/README.md) separately identifies Blizzard data and CC BY-SA 4.0 wiki content | No source/data/wiki cache bundled; provider and data rights checked separately |
| wowlua-ls | [GPL-3.0 LICENSE.md at 12587ed](https://github.com/TradeSkillMaster/wowlua-ls/blob/12587edbe51a47d4ca362dd542672842a4996899/LICENSE.md) | External process only; no GPL source/binary/schema/stubs |
| StyLua | [MPL-2.0 LICENSE.md at d6562ca](https://github.com/JohnnyMorganz/StyLua/blob/d6562caedd4a45c2bd0e734574dd8ff200a44d63/LICENSE.md) | External formatter |
| wow-ui-sim | [GPL-3.0-only README](https://github.com/Osso/wow-ui-sim/blob/1f57e6b186e1baa3fc3aedf4392d1f08b4a15113/README.md) and [LICENSE at 1f57e6b](https://github.com/Osso/wow-ui-sim/blob/1f57e6b186e1baa3fc3aedf4392d1f08b4a15113/LICENSE) | External simulator; no code/container/game assets/data |
| Lychee Dev | [MIT LICENSE at b524921](https://github.com/Follen/Lychee-Dev/blob/b524921c5480b2dfb4ec231901137b06dcc43aef/LICENSE); [notices](https://github.com/Follen/Lychee-Dev/blob/b524921c5480b2dfb4ec231901137b06dcc43aef/THIRD_PARTY_NOTICES.md) identify separate dependency terms and unresolved GitHub.png/Logo.png provenance | User-installed only; no MIT claim for its whole bundle |
| BigWigs Packager | [release.sh header at 0f24d21](https://github.com/BigWigsMods/packager/blob/0f24d2169de3ceb3b79a981311b2ebab4c6160c7/release.sh#L3) contains Unlicense/public-domain dedication; no root LICENSE detected | External script only; no redistribution |
| Blizzard APIs, FrameXML/game data/assets | Respective owner terms; access through user-provided client data or authorized research | No Blizzard source/game data bundled; build evidence is not a redistribution grant |
| Project logo | User-supplied previously generated artwork; [provenance](assets/README.md) | Included unchanged; excluded from original-code MIT; public-use rights not independently verified |

Codex packages an original MCP launcher and connection configuration, not a server. Its npm-shim discovery is restricted to the identified @nighthawk42/wow-api-mcp package; an explicit direct JavaScript entrypoint can select a separately installed provider. Claude Code packages an npm manifest and lockfile pinned to @nighthawk42/wow-api-mcp 0.2.2; the host downloads it at install/update into its plugin cache. Node remains user-provided. Upstream code, data and dependencies stay outside Git and both ZIPs. This wiring was reviewed on 2026-10-22.

The two MCP providers share a command name and must not be conflated. Tool data selectors/packaging features do not certify client compatibility.

Python, Node, Bash, host clients and other integrations remain separate user-provided software. No interpreter/dependency is vendored. [Project licensing](docs/licensing.md).
