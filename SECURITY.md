# Security

The plugin can inspect outgoing model requests and modify their instruction fields. Install only reviewed code from a trusted revision. The installer requires an explicit Hermes profile home and refuses automatic replacement of existing copies.

Never put credentials, session transcripts, or private request payloads in an issue. While the repository is private, report problems to its owner through the existing private repository channel. A public vulnerability-reporting channel must be configured before public launch.

The installer does not restart services or modify Hermes core. Its apply step is not transactional; a failed configuration command may leave copied files or partial settings. Inspect the target before recovery. Existing-file replacement, upgrades, and removal are not automated.
