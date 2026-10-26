#!/usr/bin/env python3
"""Install into one explicitly selected Hermes home using native config commands.

Fresh installs only. No network calls, force-overwrite, dependency installation,
gateway restart, or edits to the Hermes application source.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = "caveman-communication"
MODES = ("full", "lite", "ultra", "wenyan-lite", "wenyan-full", "wenyan-ultra", "off")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", required=True, type=Path, help="Exact profile home, never inferred")
    parser.add_argument("--hermes", default="hermes", help="Hermes executable (not a shell command)")
    parser.add_argument("--mode", choices=MODES, default="full")
    parser.add_argument("--apply", action="store_true", help="Copy files and enable; default only checks")
    args = parser.parse_args()
    home = args.home.expanduser().resolve()
    executable = shutil.which(args.hermes)
    if not executable:
        parser.error("Hermes executable not found; install Hermes first or use --hermes.")
    env = dict(os.environ, HERMES_HOME=str(home), PYTHONDONTWRITEBYTECODE="1")

    def cli(*parts):
        result = subprocess.run([executable, *parts], env=env, cwd=home if home.is_dir() else home.parent,
                                capture_output=True, text=True, timeout=60)
        if result.returncode:
            # Do not echo arbitrary host configuration or credential-bearing output.
            raise RuntimeError("Hermes command failed: " + " ".join(parts[:3]))
        return result.stdout.strip()

    def get(key):
        return json.loads(cli("config", "get", key, "--json"))

    try:
        if not home.is_dir() or not (home / "config.yaml").is_file():
            raise RuntimeError("Select an existing, configured Hermes profile home.")
        for path in (home / "config.yaml", home / "plugins", home / "skills"):
            if path.is_symlink():
                raise RuntimeError(f"Refusing symlinked installation boundary: {path.name}")
        target_config = Path(cli("config", "path")).expanduser().resolve()
        if target_config != home / "config.yaml":
            raise RuntimeError("Hermes resolved another profile; no files were copied.")
        destinations = [(ROOT / "plugin", home / "plugins" / PLUGIN),
                        (ROOT / "skill", home / "skills" / "caveman")]
        for source, dest in destinations:
            if not source.is_dir():
                raise RuntimeError(f"Incomplete package: {source.name}")
            if dest.exists() or dest.is_symlink():
                raise RuntimeError(f"Existing {dest.name} installation; automatic replacement is not supported.")
        # Native discovery includes external and disabled skills; reject ambiguous names.
        listed = cli("skills", "list")
        if re.search(r"(?<![\w-])caveman(?![\w-])", listed):
            raise RuntimeError("A caveman skill is already discoverable. Resolve that copy before installation.")
        autoload = get("skills.auto_load")
        if not isinstance(autoload, list) or not all(isinstance(x, str) for x in autoload):
            raise RuntimeError("skills.auto_load must be a list of skill names.")
        print(f"Target: {home}")
        print(f"Plugin: {PLUGIN}; skill: caveman; mode: {args.mode}")
        print("Existing auto-loaded skills are preserved. No gateway restart is performed.")
        if not args.apply:
            print("Preflight passed. Repeat with --apply to install.")
            return 0
        for source, dest in destinations:
            shutil.copytree(source, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        if "caveman" not in autoload:
            autoload.append("caveman")
        cli("config", "set", "skills.auto_load", json.dumps(autoload))
        cli("config", "set", f"plugins.entries.{PLUGIN}.settings.mode", args.mode)
        cli("plugins", "enable", PLUGIN, "--no-allow-tool-override")
        if get("skills.auto_load") != autoload or get(f"plugins.entries.{PLUGIN}.settings.mode") != args.mode:
            raise RuntimeError("Configuration readback did not match the requested installation.")
        enabled = get("plugins.enabled")
        if not isinstance(enabled, list) or PLUGIN not in enabled:
            raise RuntimeError("Plugin enablement was not confirmed.")
        print("Installed and configuration verified. Start a new Hermes process; check /caveman status.")
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"Installation stopped: {exc}", file=sys.stderr)
        if args.apply:
            print("An apply failure may leave copied files or partial settings. Inspect the target; do not force-overwrite.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
