# Contributing

## 1. Choose the right change

Changes to Caveman's writing rules and general usage belong [upstream](https://github.com/JuliusBrussee/caveman). This repository owns the Hermes adapter:

- Hooks, request recovery, and profile commands: `plugin/__init__.py`.
- Native registration: `plugin/plugin.yaml`.
- Installation: `scripts/install.py` and `INSTALL.md`.
- Hermes-specific instruction binding: the separately headed section in `skill/SKILL.md`.
- Regression coverage: `tests/test_communication.py` and `tests/test_install.py`.

Keep the base Caveman rules intact. Preserve profile/project isolation, native disablement, user text, tool results, and stored history. Do not introduce a proxy, output rewriting, extra inference, or Hermes core changes as part of a documentation or integration fix.

## 2. Make the change

Create a working branch from the version you intend to change. Keep the patch focused and add a regression when executable behavior changes. Human documentation should have one owner: README explains why and what; INSTALL gives installation/recovery steps; this guide gives contribution steps. Link general Caveman usage upstream rather than reproducing it.

## 3. Check it

For prose-only changes, review the diff, verify referenced files and links, and check that installed skill documentation does not depend on the repository's original directory layout. Do not change runtime skill instructions merely to shorten a human guide.

For executable changes, use an existing compatible Hermes environment and its Python interpreter. The [tested baseline](docs/VERIFICATION.md) is evidence, not a promise that every version works. Set these three paths to that same environment:

```bash
export HERMES_SOURCE=/absolute/path/to/hermes-agent
export HERMES_PYTHON=/absolute/path/to/hermes-python
export HERMES_EXECUTABLE=/absolute/path/to/hermes
```

From this repository's root, run the native tests and plugin checks in a temporary home. The subprocess environment below deliberately excludes provider credentials and live profile settings:

```bash
"$HERMES_PYTHON" - <<'PY'
import os
from pathlib import Path
import subprocess
import tempfile

source = Path(os.environ["HERMES_SOURCE"]).resolve()
python = str(Path(os.environ["HERMES_PYTHON"]).absolute())
hermes = str(Path(os.environ["HERMES_EXECUTABLE"]).absolute())
with tempfile.TemporaryDirectory(prefix="caveman-check-") as directory:
    env = {key: os.environ[key] for key in ("PATH", "LANG", "SystemRoot") if key in os.environ}
    env.update(HOME=directory, HERMES_HOME=str(Path(directory) / "profile"),
               PYTHONPATH=str(source), PYTHONDONTWRITEBYTECODE="1",
               HERMES_EXECUTABLE=hermes)
    commands = [
        [python, "-m", "unittest", "discover", "-s", "tests", "-v"],
        [python, str(source / "hermes_cli/main.py"), "plugins", "doctor", "plugin", "--ci"],
        [python, str(source / "hermes_cli/main.py"), "plugins", "validate", "plugin", "--json"],
    ]
    for command in commands:
        subprocess.run(command, env=env, check=True)
PY
```

The current suite contains 10 tests. Without `HERMES_EXECUTABLE`, the three installer tests are skipped; a skipped installer check is not installation proof. CI runs only syntax/package checks. Report native results separately and never use real-provider inference to compensate for missing test setup.

## 4. Submit

Open a focused pull request describing the problem, the changed behavior or document, and the checks you ran. State the Hermes revision and any untested boundaries for executable changes. Do not include credentials, sessions, raw request logs, or local deployment paths.

Contributions use Apache-2.0; preserve upstream attribution and modification notices. A separate submission to Caveman follows its [contribution policy](https://github.com/JuliusBrussee/caveman/blob/main/CONTRIBUTING.md), including DCO requirements. Never sign for another contributor.
