# Caveman for Hermes

## Why this adapter exists

Caveman's Hermes integration is not built the same way as its Claude Code integration. Claude Code uses lifecycle hooks for automatic activation and ongoing reinforcement; Caveman's Hermes skill-installation path copies the skills without installing those same hooks.[7][8]

This adapter brings that activation and reinforcement pattern to native Hermes conversations. The shared reason is simple: keep the writing guidance available throughout a conversation without repeatedly asking the assistant to load it. This comparison concerns the skill-installation path, not every Caveman CLI or gateway integration.

The base Caveman writing rules are retained, with a separate Hermes binding appended. For Caveman usage and examples, read the **[upstream Caveman documentation](https://github.com/JuliusBrussee/caveman)**. This repository documents the Hermes adaptation only.

## Project layout

```text
Caveman-Hermes/
├── README.md
├── INSTALL.md                    Install, activate, and handle conflicts
├── CONTRIBUTING.md               Change, test, and submit the adapter
├── CHANGELOG.md
├── SECURITY.md
├── LICENSING.md
├── LICENSE / LICENSE-MIT / NOTICE
├── AGENTS.md                     Brief contributor boundaries
├── .gitignore
├── plugin/
│   ├── __init__.py               Hooks, request recovery, profile commands
│   ├── plugin.yaml               Native plugin registration
│   └── LICENSE
├── skill/
│   ├── SKILL.md                  Caveman rules + Hermes binding
│   ├── README.md                 Portable documentation links
│   └── LICENSE / LICENSE-MIT / NOTICE
├── scripts/
│   └── install.py                Explicit-profile installer
├── tests/
│   ├── test_communication.py
│   └── test_install.py
├── docs/
│   └── VERIFICATION.md           Tested baseline and compatibility limits
└── .github/workflows/
    └── checks.yml                Syntax and package checks
```

Hermes integrates one skill, `caveman`, and one plugin, `caveman-communication`. The installer copies the complete `skill/` and `plugin/` directories into the selected profile; separate Ultra/Wenyan skill packages are not required by this adapter.

## Installation

For an existing configured profile named `coder`:

```bash
git clone https://github.com/DylDigitals/Caveman-Hermes.git
cd Caveman-Hermes
python3 scripts/install.py --home "$HOME/.hermes/profiles/coder"
python3 scripts/install.py --home "$HOME/.hermes/profiles/coder" --apply
```

The first command after cloning is a preflight; `--apply` installs. Follow **[INSTALL.md](INSTALL.md)** to select another profile, activate the plugin, or handle an existing Caveman installation. The installer does not restart Hermes or modify its core.

## What we restored, and where

- **Conversation startup:** `skills.auto_load` supplies the complete writing rules.
- **Before each turn:** the plugin's `pre_llm_call` hook supplies the active mode reminder.
- **Before supported model requests:** `llm_request` restores missing guidance, including requests whose context no longer contains it.
- **Across conversations in a profile:** the plugin reads one persistent profile setting, keeping existing and new conversations aligned on their next turn.

Hermes profiles and skills provide the configuration and instruction layer.[3][4]

Native plugin hooks and request middleware supply the integration points.[5][6]

### Hermes-specific differences

Settings are profile-wide rather than Claude-style session-local. Bare mode/status commands are observational; persistent changes require an explicit mode command. Ultra/Wenyan definitions are local adaptations. Claude's statusline, session-end statistics, natural-language persistence, and one-shot restoration are not ported.

Request recovery supports `chat_completions` and `codex_responses`; other formats are unchanged. See the [tested baseline and limits](docs/VERIFICATION.md). Delivering instructions does not guarantee model adherence or token savings.

Independent community adapter, version **1.1.1**. [Apache-2.0 with upstream notices](LICENSING.md); no Caveman or Hermes endorsement is implied.

## Sources

[3] https://hermes-agent.nousresearch.com/docs/user-guide/profiles
[4] https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
[5] https://hermes-agent.nousresearch.com/docs/developer-guide/plugins
[6] https://hermes-agent.nousresearch.com/docs/developer-guide/middleware
[7] https://github.com/JuliusBrussee/caveman/blob/9b68f7ed12b05e7efaff18e65c5a3fc2849fd0a4/.claude-plugin/plugin.json
[8] https://github.com/JuliusBrussee/caveman/blob/9b68f7ed12b05e7efaff18e65c5a3fc2849fd0a4/installer/install.js
