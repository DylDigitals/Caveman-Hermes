# What this adds to Caveman's Hermes support

## The missing behavior

Installing a writing skill makes its instructions available. It does not, by itself, arrange automatic activation or repeat the active mode on later turns.

Caveman's Claude Code integration registers `SessionStart`, `SubagentStart`, `UserPromptSubmit`, and `SessionEnd` hooks.[7]

By contrast, the inspected `installHermes()` skill-installer path copies skill directories; that function does not install equivalent lifecycle hooks.[8] This comparison concerns that specific path, not a claim that every Caveman CLI or gateway integration lacks Hermes hooks.

We built this adapter to bring the automatic activation and ongoing reinforcement pattern to ordinary Hermes conversations, without sending requests through a proxy or another model.

## What we added

- **Automatic full-rule loading:** native `skills.auto_load` supplies the complete Caveman skill at startup.
- **Per-turn reinforcement:** `pre_llm_call` supplies the profile's current mode reminder.
- **Missing-rule recovery:** `llm_request` restores missing writing guidance on supported provider requests, including synthetic tool-loop and post-compaction shapes covered by tests.
- **Persistent controls:** explicit `/caveman <mode>` commands update one profile setting. Existing and new sessions consume it on their next turn; bare `/caveman` and `/caveman status` are read-only.

Existing user text, raw tool results, stored history, model choice, permissions, and task execution remain unchanged. No response filter, additional inference call, or Hermes core patch is required.

## Why Hermes needs a different implementation

A Hermes profile is a persistent home for configuration, skills, memory, and sessions; it is not one conversation.[3]

Skills supply instruction documents, while native plugins provide hooks and commands.[4][5]

Hermes request middleware can modify outgoing provider kwargs before execution.[6] We use that boundary only to append absent communication guidance, preserving existing content.

## Deliberate differences and limits

Modes are profile-wide, not Claude-style session-local. Ultra/Wenyan definitions are local adaptations. We do not reproduce Claude's statusline, SessionEnd statistics, natural-language mode persistence, or one-shot skill restoration.

Request recovery is qualified for `chat_completions` and `codex_responses` only. Other formats remain unchanged. Native skill disablement and trusted-project boundaries still apply. These mechanisms deliver instructions; they do not guarantee compliance or measured token savings.

See [installation](../INSTALL.md) and [verification](VERIFICATION.md). This is a candidate enhancement for maintainer review, not a claim of full Claude Code parity or upstream endorsement.

## Sources

[3] https://hermes-agent.nousresearch.com/docs/user-guide/profiles
[4] https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
[5] https://hermes-agent.nousresearch.com/docs/developer-guide/plugins
[6] https://hermes-agent.nousresearch.com/docs/developer-guide/middleware
[7] https://github.com/JuliusBrussee/caveman/blob/9b68f7ed12b05e7efaff18e65c5a3fc2849fd0a4/.claude-plugin/plugin.json
[8] https://github.com/JuliusBrussee/caveman/blob/9b68f7ed12b05e7efaff18e65c5a3fc2849fd0a4/installer/install.js
