# Verification

## Installer and release preparation

The package was tested with Python 3.11 against an unmodified Git archive of the public Hermes commit `614f11d3f6a0eddc381f05f5c4dd759d0f752be4`. Its upstream existence was confirmed through the GitHub API. The run reused an existing Hermes dependency environment; it was not a fresh dependency installation or a claim of compatibility with every Hermes release.

Executed from the standalone package:

- Native integration plus installer suite: **10 tests passed** (7 communication tests and 3 installer tests).
- Plugin Doctor: passed discovery, parsing, import, and registration.
- Manifest validation: passed, including declared middleware and security scan.
- Installer checks: preflight leaves target configuration and adapter files untouched; apply preserves unrelated settings; paths with spaces work; existing copies, duplicate native skill names, and symlinked installation boundaries are refused.

The same 10 tests also passed against the current, modified local Hermes host. No inference credentials, paid provider requests, live profile installation, gateway restart, or base-Hermes edits were used for these checks. Synthetic request restoration is tested; actual model-driven compaction and universal model adherence are not certified.

The installer supports fresh installation only. No force-overwrite, automatic upgrade, migration, or removal flow is claimed. Apache-2.0 licensing and applicable upstream notices are included. Public distribution remains pending.
