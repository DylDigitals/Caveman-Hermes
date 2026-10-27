# Security

The plugin can inspect outgoing model requests and modify their instruction fields. Install only reviewed code from a trusted revision. The installer requires an explicit Hermes profile home and refuses automatic replacement of existing copies.

Report vulnerabilities through [GitHub private vulnerability reporting](https://github.com/DylDigitals/Caveman-Hermes/security/advisories/new). Never post credentials, session transcripts, private request payloads, or exploit details in a public issue. Include the affected commit and a minimal reproduction with synthetic data.

The installer does not restart services or modify Hermes core. Its apply step is not transactional; a failed configuration command may leave copied files or partial settings. Inspect the target before recovery. Existing-file replacement, upgrades, and removal are not automated.
