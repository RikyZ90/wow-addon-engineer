# Usage examples

In Codex, ask in natural language to use the named skill from WoW Addon Engineer. Claude exposes the same skills under `/wow-addon-engineer:<skill-name>`. Supply an actual addon path and evidence for its target.

## First inspection

> Use WoW Addon Engineer / get-started for the addon at C:\Work\MyAddon. Inspect its TOCs, identify what target evidence is missing, and run doctor. Do not access a live game.

Expected: prerequisite report, target facts/unknowns, and a suitable workflow. Optional tools may be missing.

## Create

> Use wow-addon-create to add a small draggable settings window to this addon. Use its existing namespace and matching-build API documentation. Preserve saved settings; verify secure/combat restrictions.

Expected: scoped addon changes and explicit API evidence; no guessed Interface number or copied external framework.

## Debug

> Use wow-addon-debug with this stack and reproduction. The button fails after entering combat. Trace the first restricted change and propose the smallest fix. Do not attach to the client or send hotkeys.

Expected: load/event/secure-path investigation and a bounded reproduction; runtime gaps stay visible.

## Research and review

> Use wow-addon-research to verify this event's arguments for our exact build, then wow-addon-review to inspect the handler's allocation rate and saved-data migration. Cite the sources actually read.

Expected: a build-specific evidence ledger; measured findings distinguished from hypotheses.

## Test

> Use wow-addon-test. Run structural checks, then the installed wowlua_ls and StyLua in check mode. Do not install missing tools. Report simulation and real-client tests separately.

Expected: actual commands, exit statuses, diagnostics, and skips. Formatting is not a runtime proof.

## Prepare a release

> Use wow-addon-release to prepare a local ZIP for this addon. Inspect .pkgmeta and all TOCs, exclude secrets, include required notices, and report the archive hash. Do not upload, tag, commit, or push.

Expected: one addon root with intended runtime files, explicit license review, and honest target/runtime limits. This skill packages the user's addon, not WoW Addon Engineer.
