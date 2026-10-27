# Contributing

This repository adapts Caveman's automatic activation and ongoing reinforcement to Hermes. It is not a separate writing system or a replacement for Caveman's documentation.

## Keep Caveman upstream

- Preserve the upstream base writing rules in `skill/SKILL.md`. Keep the appended Hermes communication binding clearly separate.
- Propose changes to Caveman's writing behavior in the [upstream Caveman repository](https://github.com/JuliusBrussee/caveman), not as a competing ruleset here.
- Link to upstream for Caveman usage, examples, and general guidance. Do not duplicate its user guide or add alternative usage handling.
- Describe Hermes-specific differences honestly. Profile-wide settings and the local Ultra/Wenyan definitions are adaptations, not complete Claude Code parity.

## Scope integration changes

- `plugin/__init__.py`: native hooks, request-level recovery, and profile settings.
- `plugin/plugin.yaml`: plugin registration and declared capabilities.
- `skill/SKILL.md` and `skill/references/hermes-integration.md`: the Hermes binding and integration notes.
- `scripts/install.py` and `INSTALL.md`: explicit-profile installation and activation.
- `tests/test_communication.py` and `tests/test_install.py`: affected behavior and installation checks.

Preserve native skill disablement, trusted-project boundaries, profile isolation, user text, tool results, and stored history. Do not add proxies, response rewriting, extra model calls, workflow routing, or Hermes core patches. Additional Caveman features are separate work, not incidental integration cleanup.

## Write documentation for people

Explain the integration gap before implementation details. Describe restored behavior as a short bullet list naming its lifecycle point: conversation startup, before each turn, or before supported model requests. State the shared reason once: keep Caveman's writing guidance available throughout Hermes conversations without repeated manual loading.

Keep the README focused on that explanation, an accurate project tree, installation, and the Hermes functionality added. Put compatibility differences beside the relevant behavior. Avoid a second Caveman usage guide, internal deployment records, or navigation text written primarily for agents.

## Verify the affected change

For documentation-only changes, check accuracy, links, and the named files; a fresh model run is unnecessary. For executable changes, run the relevant native tests in disposable Hermes homes without inference credentials. Add a regression only for a distinct behavior or safety gap. See [verification](docs/VERIFICATION.md) for tested compatibility and limits.

Separate source review, automated tests, installation, and live gateway behavior. Do not claim full Claude Code parity, universal model adherence, or token savings from passing tests.

## Licensing and submissions

Contributions to this adapter use Apache-2.0. Preserve applicable upstream notices and identify changes to upstream material. Never include credentials, personal sessions, private logs, or machine-specific deployment files.

An upstream Caveman contribution is separate and follows its [contribution policy](https://github.com/JuliusBrussee/caveman/blob/main/CONTRIBUTING.md), including DCO requirements. Do not sign on someone else's behalf.
