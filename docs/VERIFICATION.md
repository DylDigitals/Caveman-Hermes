# Tested compatibility

Adapter version: **1.1.1**.

## Recorded baseline

The release checks passed with Python 3.11 and an unmodified archive of [Hermes commit `614f11d3`](https://github.com/NousResearch/hermes-agent/commit/614f11d3f6a0eddc381f05f5c4dd759d0f752be4), using an existing dependency environment rather than a fresh dependency installation:

- 7 communication tests and 3 installer tests passed.
- Native Plugin Doctor and manifest validation passed.
- An anonymous checkout of the published adapter also passed the 10 tests with the available local Hermes environment.

This is one tested source baseline, not a minimum-version claim. Run the [contributor checks](../CONTRIBUTING.md#3-check-it) against the Hermes version you intend to support. CI alone checks syntax/package presence, not native behavior.

## Limits

- Request recovery accepts only `chat_completions` and `codex_responses`. Other payload formats remain unchanged.
- Skill disablement is checked per request. Cached skill content reloads when trusted-project lookup scope changes; changing the body within the same scope requires a plugin reload.
- The installer supports fresh installs, not automatic migration, upgrades, or removal.
- Tests cover synthetic tool-loop and missing-context requests. They do not certify real model-driven compaction, every gateway, every OS, model adherence, or token savings.

No provider credentials are needed for the documented native checks.
