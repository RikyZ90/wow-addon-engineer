# WoW Addon Engineer Smoke 0.1.1

A small original addon with no dependencies. Commands: `/waesmoke help`, `/waesmoke status`, `/waesmoke test`, `/waesmoke toggle`. It writes local chat messages only; it does not send messages to other players.

This sample targets manual testing on the local `wowf 1.60.1.70532` client. Its TOC declares Interface `16001`, taken from the `forever` track metadata supplied by wow-api-mcp 0.2.2 for **1.60.1.70450**. Matching sources for build 70532 were unavailable in the consulted source. The user subsequently confirmed the earlier sample on client 70532; that limited result does not certify all addons or every Forever client. Version 0.1.1 translates the sample's messages to English; this revision has not been retested in the game client.

The original load path is `TOC -> Core.lua -> Smoke.xml -> Include Runtime.xml -> Script Runtime.lua`. The event frame is anonymous and has no template. Combat transitions update Lua state and produce messages; they do not configure frames, attributes, or protected actions. The sample does not read combat data or verify Secret Values, secure actions, or taint.

`WoWAddonEngineerSmokeDB` is the only declared SavedVariable. Schema 2 preserves valid settings, all unmanaged fields, and the legacy `showMessages` field from schema 1; it repairs only invalid values in managed fields. A future schema leaves the data unchanged and disables the addon. `load` counts initializations, `login` counts `PLAYER_LOGIN` events, and `reload` counts only the reload flag in the first `PLAYER_ENTERING_WORLD` event. Counters persist through the client's normal save process. `/waesmoke test` uses temporary data separate from the actual settings.

## Evidence consulted on October 21, 2026

Gethe mirror of Blizzard sources, commit `172a387e3ab85b26e6640d3058d5ec1e6ccd4c63`, build **1.60.1.70450**, not 70532. No upstream source code or API database is included in this sample.

| Symbol used | Evidence inspected |
| --- | --- |
| `ADDON_LOADED(addOnName, containsBindings)` | [AddOnsDocumentation.lua, event](https://github.com/Gethe/wow-ui-source/blob/172a387e3ab85b26e6640d3058d5ec1e6ccd4c63/Interface/AddOns/Blizzard_APIDocumentationGenerated/AddOnsDocumentation.lua#L387-L398) |
| `PLAYER_LOGIN()`; `PLAYER_ENTERING_WORLD(isInitialLogin, isReloadingUi)` | [SystemDocumentation.lua](https://github.com/Gethe/wow-ui-source/blob/172a387e3ab85b26e6640d3058d5ec1e6ccd4c63/Interface/AddOns/Blizzard_APIDocumentationGenerated/SystemDocumentation.lua#L133-L155), two non-nil booleans for the second event |
| `PLAYER_REGEN_DISABLED()`, `PLAYER_REGEN_ENABLED()` | [UnitDocumentation.lua](https://github.com/Gethe/wow-ui-source/blob/172a387e3ab85b26e6640d3058d5ec1e6ccd4c63/Interface/AddOns/Blizzard_APIDocumentationGenerated/UnitDocumentation.lua#L3884-L3895), no payload |
| `CreateFrame("Frame")` | [FrameUtil.lua](https://github.com/Gethe/wow-ui-source/blob/172a387e3ab85b26e6640d3058d5ec1e6ccd4c63/Interface/AddOns/Blizzard_SharedXMLBase/FrameUtil.lua#L324), direct single-argument use; [four-argument wrapper](https://github.com/Gethe/wow-ui-source/blob/172a387e3ab85b26e6640d3058d5ec1e6ccd4c63/Interface/AddOns/Blizzard_SharedXMLBase/FrameUtil.lua#L155-L159) |
| `frame:RegisterEvent(eventName)` | [SimpleFrameAPIDocumentation.lua](https://github.com/Gethe/wow-ui-source/blob/172a387e3ab85b26e6640d3058d5ec1e6ccd4c63/Interface/AddOns/Blizzard_APIDocumentationGenerated/SimpleFrameAPIDocumentation.lua#L1019-L1033), returns a boolean; arguments are non-secret in this sample |
| `frame:SetScript(scriptTypeName, script)` | [SimpleScriptRegionAPIDocumentation.lua](https://github.com/Gethe/wow-ui-source/blob/172a387e3ab85b26e6640d3058d5ec1e6ccd4c63/Interface/AddOns/Blizzard_APIDocumentationGenerated/SimpleScriptRegionAPIDocumentation.lua#L712-L722), requires an assignable script |
| `SLASH_*1`, `SlashCmdList[name]` | [SlashCommandsRegistry.lua](https://github.com/Gethe/wow-ui-source/blob/172a387e3ab85b26e6640d3058d5ec1e6ccd4c63/Interface/AddOns/Blizzard_ChatFrameBase/Shared/SlashCommandsRegistry.lua#L42-L49), path for insecure commands |
| `DEFAULT_CHAT_FRAME:AddMessage(text, r, g, b)` | [ChatFrameUtil.lua](https://github.com/Gethe/wow-ui-source/blob/172a387e3ab85b26e6640d3058d5ec1e6ccd4c63/Interface/AddOns/Blizzard_ChatFrameBase/Shared/ChatFrameUtil.lua#L19), initialization; [ScrollingMessageFrame.lua](https://github.com/Gethe/wow-ui-source/blob/172a387e3ab85b26e6640d3058d5ec1e6ccd4c63/Interface/AddOns/Blizzard_SharedXML/ScrollingMessageFrame.lua#L10), method signature; [ChatFrame.lua](https://github.com/Gethe/wow-ui-source/blob/172a387e3ab85b26e6640d3058d5ec1e6ccd4c63/Interface/AddOns/Blizzard_ChatFrameBase/Shared/ChatFrame.lua#L35-L36), delegation |
| `Include file`, `Script file` | [UI.xsd](https://github.com/Gethe/wow-ui-source/blob/172a387e3ab85b26e6640d3058d5ec1e6ccd4c63/Interface/AddOns/Blizzard_SharedXML/UI.xsd#L1283-L1300), both are fields of `Ui`; `file` is required for Include |
| `GetBuildInfo()` | [BuildDocumentation.lua](https://github.com/Gethe/wow-ui-source/blob/172a387e3ab85b26e6640d3058d5ec1e6ccd4c63/Interface/AddOns/Blizzard_APIDocumentationGenerated/BuildDocumentation.lua#L10-L20), reads version, build, and Interface for status output |

The guards check function and frame availability; they do not prove compatibility or secure correctness on a different build.

## Local checks

Earlier checks: the installed plugin's structural checker (0 errors, 0 warnings); two Python tests, one running real Lua **5.4.6** for migration, idempotence, preservation, defaults, commands, and events with mocked APIs; `luac 5.4.6 -p` on both Lua files. The mocks cover only the signatures above, not client execution.

The user subsequently confirmed the manual tests on client 70532 and supplied a screenshot of status/toggle output from the earlier Italian-language revision. Linux checks also ran Lua 5.1.5. Secure execution, taint, and Secret Values remain unverified. A PASS from `/waesmoke test` checks local Lua logic only. The complete manual procedure, updated for the English output, is in the repository at `docs/runtime-test.md`.

Original code license: MIT; see `LICENSE`. Product and source names identify interoperability targets only.
