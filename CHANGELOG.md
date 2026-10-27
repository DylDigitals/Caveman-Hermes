# Changelog

## 1.1.1

Initial standalone distribution of the native Hermes communication adapter.

- Automatic loading of the complete Caveman writing skill.
- Per-turn reminders and profile-wide mode commands.
- Missing-guidance recovery for Chat Completions and Codex Responses requests.
- Native skill disablement and trusted-project scope handling.
- An explicit-target, preflight-first installer that preserves other auto-loaded skills and refuses conflicting installations.
- Apache-2.0 licensing, upstream notices, installation guidance, and native integration tests.

This release does not provide automatic upgrades, a proxy, response rewriting, extra inference, or complete Claude Code plugin parity. See [verification](docs/VERIFICATION.md) for tested compatibility and limits.
