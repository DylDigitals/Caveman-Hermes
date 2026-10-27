# Caveman Hermes

A standalone adapter that brings [Caveman](https://github.com/JuliusBrussee/caveman)'s communication guidance to [Hermes Agent](https://github.com/NousResearch/hermes-agent) through native hooks and request middleware. This is not a fork of Caveman or Hermes.

## What it does

- Loads the full Caveman writing skill through native Hermes skill resolution.
- Reinforces the active profile's communication mode before each turn.
- Restores missing rules on qualified model requests without rewriting responses or invoking another model.
- Honors global/platform skill disablement and keeps trusted project overrides within their native lookup scope.

Plugin version: **1.1.1**. The adapter changes communication guidance, not tools, permissions, model routing, or task execution. Instruction delivery cannot guarantee model adherence or token savings.

## Layout

```text
plugin/     Native Hermes plugin and manifest
skill/      Complete writing rules, upstream license, integration notes
tests/      Native integration and isolated installer tests
scripts/    Explicit-target installer (preflight by default)
docs/       Integration explanation, verification, and contribution notes
```

Repository development does not automatically update installed profiles. Installation and gateway activation are separate steps.

## Modes

`/caveman` and `/caveman status` report state. Explicit `/caveman <mode>` changes the whole active profile, including its other sessions.

Available modes: `full`, `lite`, `ultra`, `wenyan-lite`, `wenyan-full`, `wenyan-ultra`, and `off`. Legacy `manual` is inactive. `/ultracave` selects `ultra`; `/megacave` selects `wenyan-full`.

This implements the startup-rule and per-prompt-reinforcement pattern, not complete Claude Code plugin parity. Profile-wide modes, local Ultra/Wenyan definitions, and native Hermes usage reporting are deliberate differences. It does not import per-session mode files, project-local Caveman mode settings, one-shot workflow restoration, or SessionEnd statistics.

## Install

Apache-2.0 licensed, with upstream notices preserved. This is an independent community adapter, not an official Caveman or Hermes release.

Clone the repository, then select an existing Hermes profile:

```bash
git clone https://github.com/DylDigitals/Caveman-Hermes.git
cd Caveman-Hermes
python3 scripts/install.py --home "$HOME/.hermes/profiles/coder"
python3 scripts/install.py --home "$HOME/.hermes/profiles/coder" --apply
```

The first command checks the target. The second installs the native plugin and complete skill, preserves existing auto-loaded skills, enables the adapter, and verifies configuration. Existing copies are refused, not overwritten. No core edits, network downloads, or gateway restart are performed.

Read [INSTALL.md](INSTALL.md) for requirements, activation, existing-installation handling, and removal boundaries. Read [what we added](docs/HERMES-INTEGRATION.md) for the Claude Code lifecycle comparison and official Hermes documentation.

## Verify

Use an existing compatible Hermes environment. The plugin has no independent third-party runtime dependencies; native tests also use PyYAML supplied by that environment.

```bash
export HERMES_SOURCE=/absolute/path/to/hermes-agent
export HERMES_PYTHON=/absolute/path/to/hermes-python
export HERMES_EXECUTABLE=/absolute/path/to/hermes
export HERMES_HOME="$(mktemp -d)"
PYTHONPATH="$HERMES_SOURCE" PYTHONDONTWRITEBYTECODE=1 \
  "$HERMES_PYTHON" -m unittest discover -s tests -v
"$HERMES_PYTHON" "$HERMES_SOURCE/hermes_cli/main.py" plugins doctor plugin --ci
"$HERMES_PYTHON" "$HERMES_SOURCE/hermes_cli/main.py" plugins validate plugin --json
```

Tests create disposable profile homes. Set `HERMES_EXECUTABLE` or the three installer tests are explicitly skipped. These checks do not run provider inference. CI performs syntax and package-presence checks only, not native-host integration or paid inference.

Request recovery currently accepts only explicit `chat_completions` and `codex_responses` API modes. Other native payloads are left unchanged; startup loading and the pre-turn reminder remain independent. The one-entry body cache reloads when native project lookup scope changes; same-scope file changes require a plugin reload. Alternating scopes can cause extra reads.

See [verification](docs/VERIFICATION.md), [licensing and attribution](LICENSING.md), and [the integration explanation](docs/HERMES-INTEGRATION.md).
