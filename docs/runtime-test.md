# Manual client smoke test

Original addon: `examples/WoWAddonEngineerSmoke`, version `0.1.1`, no dependencies.
Previously authorized local installation target: `C:\Games\World of Warcraft\_forever_\Interface\AddOns\WoWAddonEngineerSmoke`.
Do not overwrite other folders or existing SavedVariables. Installation and any archive are handled separately; translating this repository does not update the installed copy.

Detected local target: product `wowf`, `1.60.1.70532`. The available, inspected API source is **1.60.1.70450**, Interface `16001`, Gethe commit `172a387e3ab85b26e6640d3058d5ec1e6ccd4c63` (October 16, 2026). This difference requires a manual test; the source evidence alone does not certify compatibility with 70532 or every Forever client.

1. Start the client manually, enable **WoW Addon Engineer Smoke** in the addon list, and enter the world with a character.
2. `/waesmoke help`: expect the list `help | status | test | toggle`.
3. `/waesmoke status`: record the entire line with `schema`, `messages`, `load`, `login`, `reload`, `combat`, and the actual client version, build, and Interface. `login` counts `PLAYER_LOGIN` events, including after a reload; `combat=unknown` remains until a combat event arrives.
4. `/waesmoke test`: expect `test: PASS (Lua only; secure execution and Secret Values unverified)`. The test uses temporary data and does not change saved settings.
5. `/waesmoke toggle`: set automatic messages to `off`; if it shows `on`, repeat the command. `/waesmoke status` must still work.
6. Run `/reload` manually. `/waesmoke status`: the off setting is preserved; `load` and `login` each increase by 1, and `reload` increases by 1. The `reload` counter uses only the `isReloadingUi` flag from `PLAYER_ENTERING_WORLD`; it does not count zone changes.
7. `/waesmoke toggle` to enable messages again. Enter and then leave combat in a situation you choose: expect `combat: started` and `combat: ended`. `/waesmoke status` must show `combat=yes` during combat and `combat=no` afterward.
8. Log out normally and log in again. The setting is preserved; `load` and `login` increase, while `reload` stays unchanged for a normal login. Do not delete SavedVariables to repeat the test.

Report the actual version/build/Interface, the status lines before and after reloading and logging in again, the results of test/toggle/combat checks, and the complete text of any Lua errors. If a step does not produce the expected result, identify the step and do not mark it as passed.

The sample registers events, updates its own data, and writes chat messages. It does not create buttons, secure templates, macros, actions, or attribute/layout changes in combat. It does not read potentially secret game values and **does not verify Secret Values, protected action correctness, taint, or the absence of errors in other addons**.

Earlier real-client checks: **confirmed by the user on October 21, 2026**. The screenshot shows 1.60.1 build 70532, Interface 16001, schema 2, counters, and toggle output from the earlier Italian-language revision. The rest of that procedure was confirmed by the user rather than observed automatically. This English-language revision has not been retested in the game client. Static and Lua test results are recorded in the development report; a PASS from `/waesmoke test` covers local logic only.
