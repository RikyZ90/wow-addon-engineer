local _, namespace = ...
local Core = {}
namespace.Core = Core

local function counter(value)
    return type(value) == "number" and value >= 0 and value < math.huge and value % 1 == 0
end

function Core.Migrate(saved)
    local db = type(saved) == "table" and saved or {}
    if type(db.schemaVersion) == "number" and db.schemaVersion > 2 then
        return nil, "future schema: data preserved, addon inactive"
    end
    -- Version 1 used showMessages; retain it and every unowned field.
    if db.enabled == nil and type(db.showMessages) == "boolean" then
        db.enabled = db.showMessages
    end
    if type(db.enabled) ~= "boolean" then
        db.enabled = true
    end
    for _, key in ipairs({ "loads", "logins", "reloads" }) do
        if not counter(db[key]) then
            db[key] = 0
        end
    end
    db.schemaVersion = 2
    return db
end

function Core.Start(saved)
    local db, problem = Core.Migrate(saved)
    if not db then
        return nil, problem
    end
    db.loads = db.loads + 1
    return { db = db, loginSeen = false, worldSeen = false }
end

function Core.Event(state, event, _, isReloadingUi)
    if event == "PLAYER_LOGIN" and not state.loginSeen then
        state.loginSeen = true
        state.db.logins = state.db.logins + 1
    elseif event == "PLAYER_ENTERING_WORLD" and not state.worldSeen then
        state.worldSeen = true
        if isReloadingUi == true then
            state.db.reloads = state.db.reloads + 1
        end
    elseif event == "PLAYER_REGEN_DISABLED" then
        state.combat = true
        return state.db.enabled and "combat: started" or nil
    elseif event == "PLAYER_REGEN_ENABLED" then
        state.combat = false
        return state.db.enabled and "combat: ended" or nil
    end
end

function Core.Status(state)
    local db = state.db
    local combat = "unknown"
    if state.combat ~= nil then
        combat = state.combat and "yes" or "no"
    end
    return string.format("schema=%d messages=%s load=%.0f login=%.0f reload=%.0f combat=%s",
        db.schemaVersion, db.enabled and "on" or "off", db.loads, db.logins, db.reloads, combat) .. (state.clientInfo or "")
end

function Core.SelfTest()
    local marker = {}
    local db = { schemaVersion = 1, showMessages = false, custom = marker, loads = 4 }
    assert(Core.Migrate(db) == db and db.enabled == false and db.custom == marker)
    assert(Core.Migrate(db) == db and db.loads == 4 and db.schemaVersion == 2)
    local state = assert(Core.Start(db))
    Core.Event(state, "PLAYER_LOGIN")
    Core.Event(state, "PLAYER_LOGIN")
    Core.Event(state, "PLAYER_ENTERING_WORLD", false, true)
    Core.Event(state, "PLAYER_ENTERING_WORLD", false, true)
    assert(db.loads == 5 and db.logins == 1 and db.reloads == 1)
    Core.Event(state, "PLAYER_REGEN_DISABLED")
    assert(state.combat == true and db.enabled == false)
    Core.Event(state, "PLAYER_REGEN_ENABLED")
    assert(state.combat == false and db.custom == marker)
end

function Core.Command(state, message)
    local command = (message or ""):match("^%s*(.-)%s*$"):lower()
    if command == "status" then
        return Core.Status(state)
    elseif command == "toggle" then
        state.db.enabled = not state.db.enabled
        return "automatic messages: " .. (state.db.enabled and "on" or "off")
    elseif command == "test" then
        local ok = pcall(Core.SelfTest)
        return ok and "test: PASS (Lua only; secure execution and Secret Values unverified)"
            or "test: FAIL (local Lua logic)"
    end
    return "/waesmoke help | status | test | toggle"
end
