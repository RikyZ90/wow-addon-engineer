# Behavioral evals

[The scenarios](cases.json) cover target ambiguity, invented APIs, combat restrictions, Secret Values, data preservation, performance evidence, missing tools, licensing/release boundaries, untrusted logs, and MCP provider identity.

Give a fresh agent only the named installed skill, linked references, prompt, and necessary raw fixtures. Do not give the expected answer. Isolate side effects: the cases need no game access, downloads, external mutation, or paid API runner.

Save actual output, host/model/version, date, context, and observed tool calls. Score every "must" expectation and confirm every "must_not" remains absent. All conditions must hold to pass. Report unexecuted cases as unexecuted. Matching skill text is not a behavioral evaluation.

Offline CI checks definitions and routing only. All ten independent response scenarios have [recorded assessments](results-2026-10-21.json). Missing-context responses are evaluated for appropriate reasoning and boundaries, not as completed addon operations. See [verification](../docs/verification.md) for separate host, implementation, integration and runtime evidence.
