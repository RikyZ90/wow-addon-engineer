local addonName, namespace = ...
local Core = namespace.Core
local state, problem

local function output(message)
    if message and DEFAULT_CHAT_FRAME and type(DEFAULT_CHAT_FRAME.AddMessage) == "function" then
        DEFAULT_CHAT_FRAME:AddMessage("[WAESmoke] " .. message, 0.8, 0.9, 1)
    end
end

if type(CreateFrame) ~= "function" or type(SlashCmdList) ~= "table" then
    output("Startup APIs unavailable; check the client")
    return
end
local frame = CreateFrame("Frame")
if not frame or type(frame.RegisterEvent) ~= "function" or type(frame.SetScript) ~= "function" then
    output("Event frame unavailable; check the client")
    return
end

SLASH_WOWADDONENGINEERSMOKE1 = "/waesmoke"
SlashCmdList.WOWADDONENGINEERSMOKE = function(message)
    output(state and Core.Command(state, message) or problem or "starting up")
end

frame:SetScript("OnEvent", function(_, event, ...)
    if event == "ADDON_LOADED" then
        local loadedName = ...
        if loadedName ~= addonName or state or problem then
            return
        end
        state, problem = Core.Start(WoWAddonEngineerSmokeDB)
        if not state then
            output(problem)
            return
        end
        WoWAddonEngineerSmokeDB = state.db
        if type(GetBuildInfo) == "function" then
            local version, build, _, interface = GetBuildInfo()
            if type(version) == "string" and type(build) == "string" and type(interface) == "number" then
                state.clientInfo = string.format(" | client=%s build=%s Interface=%.0f", version, build, interface)
            end
        end
        if state.db.enabled then
            output("loaded; /waesmoke help")
        end
    elseif state then
        output(Core.Event(state, event, ...))
    end
end)

for _, event in ipairs({ "ADDON_LOADED", "PLAYER_LOGIN", "PLAYER_ENTERING_WORLD",
    "PLAYER_REGEN_DISABLED", "PLAYER_REGEN_ENABLED" }) do
    frame:RegisterEvent(event)
end
