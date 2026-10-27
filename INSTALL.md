# Install into Hermes

## 1. Choose a profile

Use an existing, configured Hermes installation with the [supported integration interfaces](docs/VERIFICATION.md). The installer needs Python 3.10 or later and a `hermes` executable; it installs no dependencies.

On Linux/macOS, the default profile is `$HOME/.hermes`; a named profile is `$HOME/.hermes/profiles/<name>`. See [Hermes profiles](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) for host-specific paths. Pass the exact home directory to the installer; do not use the Hermes application/source directory.

The examples below use an existing profile named `coder`. Do not run installation while another process is editing that profile's configuration.

## 2. Download and preflight

```bash
git clone https://github.com/DylDigitals/Caveman-Hermes.git
cd Caveman-Hermes
python3 scripts/install.py --home "$HOME/.hermes/profiles/coder"
```

For repeatable deployment, check out the commit you reviewed before running the installer. Preflight prints the selected home, plugin, skill, and initial mode, then asks you to repeat with `--apply`. It does not copy adapter files or change configuration, although Hermes CLI may create ordinary cache files.

If Hermes is not on PATH, append `--hermes /absolute/path/to/hermes` to both installer commands. If preflight refuses an existing installation, follow the conflict section below instead of deleting files.

## 3. Apply

```bash
python3 scripts/install.py --home "$HOME/.hermes/profiles/coder" --apply
```

The installer copies `plugin/` to `plugins/caveman-communication/` and `skill/` to `skills/caveman/` inside that home. It adds `caveman` to the existing auto-load list, sets the initial profile mode, enables the plugin through Hermes, and reads the settings back. Other auto-loaded skills remain intact.

Expected final message: `Installed and configuration verified. Start a new Hermes process; check /caveman status.` This confirms files and settings, not activation in an already-running gateway.

## 4. Activate and verify

Start a new CLI process for the same profile:

```bash
hermes -p coder chat
```

Enter `/caveman status`. It should report `full` and `profile-wide` after the default installation. If the command is unavailable, confirm you opened the selected profile and a new process. General Caveman usage belongs in the [upstream documentation](https://github.com/JuliusBrussee/caveman); this status check verifies the adapter installation.

For a messaging gateway, use its normal owner-managed restart/reload procedure after draining active work. A shared gateway may serve several profiles. The installer never restarts it, and this guide does not prescribe an unconditional service restart.

## If Caveman is already installed

Automatic replacement, migration, and upgrades are not supported. Preflight rejects an existing plugin directory or any discoverable `caveman` skill, including a copy outside the profile's immediate skill directory. Inspect without changing anything:

```bash
hermes -p coder skills list
hermes -p coder config get skills.external_dirs --json
hermes -p coder config get skills.auto_load --json
```

The supported way to try the adapter without replacing that installation is a separate profile. Choose a new profile name, configure it, then preflight that exact home:

```bash
hermes profile create cavemandemo --no-skills
hermes -p cavemandemo setup
python3 scripts/install.py --home "$HOME/.hermes/profiles/cavemandemo"
```

If that preflight passes, repeat it with `--apply` and start `hermes -p cavemandemo chat`. These commands create a separate profile; they do not migrate existing settings or conversations. Do not remove a shared or locally modified skill just to satisfy preflight.

## If apply fails partway through

Apply is not transactional. Copied files or some settings may remain even when the command reports failure. Stop; do not rerun with force or delete the profile.

Inspect the exact target's plugin list and settings:

```bash
hermes -p coder plugins list
hermes -p coder config get plugins.entries.caveman-communication.settings.mode --json
hermes -p coder config get skills.auto_load --json
```

If this attempt enabled the plugin and you want to prevent it loading in the next process, run `hermes -p coder plugins disable caveman-communication`. Disabling the plugin does not remove the separately auto-loaded writing skill or unload an existing process. Record what changed and resolve that specific failed command before retrying. Ask for help with the error and synthetic reproduction, never credentials or private transcripts.

There is no automatic uninstall. Retiring both components requires disabling the plugin and removing only `caveman` from the existing auto-load list through Hermes configuration management. Preserve other entries and user-modified files. See [SECURITY.md](SECURITY.md) for sensitive reports.
