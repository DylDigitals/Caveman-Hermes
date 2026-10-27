# Install the Hermes communication adapter

The package is licensed under Apache-2.0 with upstream notices preserved. No GitHub account is required to download the public repository.

Clone the repository, then run the commands below from its root:

```bash
git clone https://github.com/DylDigitals/Caveman-Hermes.git
cd Caveman-Hermes
```

For repeatable deployment, check out the exact commit you reviewed before installation. Never put a GitHub token in the clone URL.

## Requirements

- An existing Hermes installation and configured profile.
- Python 3.10 or later for the installer; no additional installer packages.
- Hermes with native `pre_llm_call`, `llm_request`, plugin commands, and `skills.auto_load` support. See [verified compatibility](docs/VERIFICATION.md).
- No existing discoverable skill named `caveman` or plugin named `caveman-communication` in that profile. The installer refuses replacement rather than overwriting another installation.

## Install

Run from this package's root. Choose the exact profile home: `~/.hermes` for default, or `~/.hermes/profiles/<name>` for a named profile. Hermes documents these independent profile homes in its [profiles guide](https://hermes-agent.nousresearch.com/docs/user-guide/profiles).

```bash
# Example: an existing profile named coder.
python3 scripts/install.py --home "$HOME/.hermes/profiles/coder"

# After checking the printed destination:
python3 scripts/install.py --home "$HOME/.hermes/profiles/coder" --apply
```

The first command checks the destination without copying the adapter or changing its settings. Hermes itself may create normal diagnostic/cache files when its CLI runs. The second command:

1. Copies `plugin/` into the selected home's `plugins/caveman-communication/`.
2. Copies the complete `skill/` package into `skills/caveman/`.
3. Adds `caveman` to the existing `skills.auto_load` list, preserving other entries.
4. Sets the communication mode and enables the plugin through native Hermes CLI commands, then reads the settings back.

Use `--mode lite`, `--mode ultra`, a documented Wenyan mode, or `--mode off` to choose another initial mode. Use `--hermes /path/to/hermes` if the intended executable is not on `PATH`. The installer confirms that Hermes resolves the exact requested profile's config file.

It does not change your provider, tools, permissions, gateway service, or Hermes application source. Do not run it while another process is editing that profile's configuration. Installation is not transactional: a failed apply can leave copied files or partial settings; inspect the reported target rather than rerunning with force.

## Activate and check

Start a new Hermes CLI process for that profile. An already-running gateway must be reloaded or restarted through its normal owner; the installer never does this automatically. For a gateway serving multiple profiles, coordinate that shared lifecycle explicitly.

In the selected profile's chat:

```text
/caveman status
/caveman lite
/caveman off
/caveman full
```

Status should report the selected mode and `profile-wide`. A mode change applies to existing and new sessions on their next turn. Ask a normal question to check visible style; status proves configuration, not guaranteed model adherence.

## Existing installations, upgrades, and removal

If an upstream skill-only installation already supplies `caveman`, keep it intact. Review its owner and local changes before replacing it, or try this adapter in a separate profile. This fresh-install script deliberately has no force, automatic migration, upgrade, or deletion mode.

To suspend the style, use `/caveman off`. To disable the plugin itself, use the native `hermes plugins disable caveman-communication` command with `HERMES_HOME` set to the same selected home. The auto-loaded writing skill is separate: remove only `caveman` from `skills.auto_load` through Hermes configuration management if retiring both components. Do not replace the entire list or delete user-modified skill files blindly.
