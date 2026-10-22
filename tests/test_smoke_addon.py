import os
from pathlib import Path
import shutil
import subprocess
import unittest

from scripts.check_addon import check_addon


ADDON = Path(__file__).resolve().parents[1] / "examples" / "WoWAddonEngineerSmoke"


class SmokeAddonTests(unittest.TestCase):
    def test_toc_and_recursive_xml_load_order(self):
        report = check_addon(ADDON)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["warnings"], [])
        self.assertEqual(report["load_order"], [
            "Core.lua", "Smoke.xml", "Runtime.xml", "Runtime.lua",
        ])

    def test_saved_data_commands_and_event_binding_in_real_lua(self):
        executable = os.environ.get("WAE_LUA") or shutil.which("lua")
        if not executable:
            self.skipTest("Lua interpreter unavailable; set WAE_LUA to an existing executable")
        result = subprocess.run([executable, "-", str(ADDON)], input=LUA_CHECKS,
                                text=True, capture_output=True, timeout=15, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SMOKE_LUA_OK", result.stdout)


LUA_CHECKS = r'''
local directory = assert(arg[1])
local namespace = {}
assert(loadfile(directory .. "/Core.lua"))("WoWAddonEngineerSmoke", namespace)
local core = namespace.Core
local defaults = assert(core.Migrate(nil))
assert(defaults.schemaVersion == 2 and defaults.enabled == true)
assert(core.Migrate(false).enabled == true)
assert(defaults.loads == 0 and defaults.logins == 0 and defaults.reloads == 0)
local marker = { keep = "original" }
local old = { schemaVersion = 1, showMessages = false, loads = 7, custom = marker }
assert(core.Migrate(old) == old)
assert(old.enabled == false and old.showMessages == false and old.loads == 7)
assert(old.custom == marker and old.schemaVersion == 2)
assert(core.Migrate(old) == old and old.loads == 7 and old.custom == marker)
local current = { schemaVersion = 2, enabled = false, logins = 4, extra = marker }
core.Migrate(current)
assert(current.enabled == false and current.logins == 4 and current.extra == marker)
for _, invalid in ipairs({ -1, 0.5, "4", false, math.huge, 0 / 0 }) do
    local fixed = assert(core.Migrate({ loads = invalid, enabled = "invalid" }))
    assert(fixed.loads == 0 and fixed.enabled == true)
end
local future = { schemaVersion = 3, enabled = false, loads = 8, custom = marker }
local state, problem = core.Start(future)
assert(state == nil and type(problem) == "string")
assert(future.schemaVersion == 3 and future.loads == 8 and future.logins == nil)
assert(future.enabled == false and future.custom == marker)
state = assert(core.Start(old))
assert(state.db == old and old.loads == 8)
assert(core.Status(state):find("combat=unknown", 1, true))
assert(core.Status(state):find("messages=off", 1, true))
core.Event(state, "PLAYER_LOGIN")
core.Event(state, "PLAYER_LOGIN")
core.Event(state, "PLAYER_ENTERING_WORLD", false, true)
core.Event(state, "PLAYER_ENTERING_WORLD", false, true)
assert(old.logins == 1 and old.reloads == 1)
assert(core.Event(state, "PLAYER_REGEN_DISABLED") == nil and state.combat == true)
assert(core.Command(state, " TOGGLE ") == "automatic messages: on")
assert(core.Event(state, "PLAYER_REGEN_DISABLED") == "combat: started")
assert(core.Status(state):find("combat=yes", 1, true))
assert(core.Event(state, "PLAYER_REGEN_ENABLED") == "combat: ended")
assert(state.combat == false)
assert(core.Command(state, "status"):find("load=8 login=1 reload=1", 1, true))
assert(core.Command(state, "unknown") == core.Command(state, "help"))
assert(core.Command(state, nil) == core.Command(state, "help"))
local loads, logins, reloads, enabled = old.loads, old.logins, old.reloads, old.enabled
assert(core.Command(state, "test"):find("test: PASS", 1, true))
assert(old.loads == loads and old.logins == logins and old.reloads == reloads)
assert(old.enabled == enabled and old.custom == marker)
local nextSession = assert(core.Start(old))
core.Event(nextSession, "PLAYER_LOGIN")
core.Event(nextSession, "PLAYER_ENTERING_WORLD", true, false)
assert(old.loads == 9 and old.logins == 2 and old.reloads == 1)
local outputs, registrations = {}, {}
local callback, frameMutationCount = nil, 0
CreateFrame = function(kind, ...)
    assert(kind == "Frame" and select("#", ...) == 0)
    local frame = {}
    function frame:RegisterEvent(event)
        registrations[event] = true
        frameMutationCount = frameMutationCount + 1
        return true
    end
    function frame:SetScript(kind, handler)
        assert(kind == "OnEvent")
        callback = handler
        frameMutationCount = frameMutationCount + 1
    end
    return setmetatable(frame, { __index = function(_, key) error("unexpected frame operation: " .. key) end })
end
local createFrame = CreateFrame
SlashCmdList = { existing = "preserved" }
DEFAULT_CHAT_FRAME = { AddMessage = function(_, message, red, green, blue)
    assert(type(message) == "string" and red == 0.8 and green == 0.9 and blue == 1)
    outputs[#outputs + 1] = message
end }
GetBuildInfo = function() return "1.60.1", "70532", "test fixture", 16001, "", "" end
WoWAddonEngineerSmokeDB = nil
local function loadBindings()
    assert(loadfile(directory .. "/Runtime.lua"))("WoWAddonEngineerSmoke", namespace)
end
local function fire(event, ...) callback(nil, event, ...) end
loadBindings()
assert(SLASH_WOWADDONENGINEERSMOKE1 == "/waesmoke" and SlashCmdList.existing == "preserved")
assert(registrations.ADDON_LOADED and registrations.PLAYER_LOGIN and registrations.PLAYER_ENTERING_WORLD)
assert(registrations.PLAYER_REGEN_DISABLED and registrations.PLAYER_REGEN_ENABLED)
fire("PLAYER_LOGIN")
fire("ADDON_LOADED", "AnotherAddon", false)
assert(WoWAddonEngineerSmokeDB == nil)
fire("ADDON_LOADED", "WoWAddonEngineerSmoke", false)
local live = WoWAddonEngineerSmokeDB
assert(live.loads == 1)
fire("ADDON_LOADED", "WoWAddonEngineerSmoke", false)
assert(live.loads == 1)
fire("PLAYER_LOGIN")
fire("PLAYER_ENTERING_WORLD", false, true)
SlashCmdList.WOWADDONENGINEERSMOKE("status")
assert(outputs[#outputs]:find("client=1.60.1 build=70532 Interface=16001", 1, true))
assert(outputs[#outputs]:find("load=1 login=1 reload=1", 1, true))
SlashCmdList.WOWADDONENGINEERSMOKE("toggle")
assert(live.enabled == false)
local outputCount, mutationCount = #outputs, frameMutationCount
fire("PLAYER_REGEN_DISABLED")
fire("PLAYER_REGEN_ENABLED")
assert(#outputs == outputCount and frameMutationCount == mutationCount)
SlashCmdList.WOWADDONENGINEERSMOKE("status")
assert(outputs[#outputs]:find("combat=no", 1, true))
SlashCmdList.WOWADDONENGINEERSMOKE("test")
assert(outputs[#outputs]:find("test: PASS", 1, true))
assert(live.loads == 1 and live.logins == 1 and live.reloads == 1 and live.enabled == false)
WoWAddonEngineerSmokeDB = future
loadBindings()
fire("ADDON_LOADED", "WoWAddonEngineerSmoke", false)
assert(WoWAddonEngineerSmokeDB == future and future.schemaVersion == 3 and future.loads == 8)
SlashCmdList.WOWADDONENGINEERSMOKE("status")
assert(outputs[#outputs]:find("future schema", 1, true))
CreateFrame = nil
local priorCommand = SlashCmdList.WOWADDONENGINEERSMOKE
loadBindings()
assert(SlashCmdList.WOWADDONENGINEERSMOKE == priorCommand)
CreateFrame = createFrame
print("SMOKE_LUA_OK: migration, preservation, defaults, commands, event ordering, API bindings")
'''


if __name__ == "__main__":
    unittest.main()
