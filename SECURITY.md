# Security Policy

Folder Sync operates on local files and intentionally has no network or telemetry features.

## Supported version

Security fixes target the latest version on the default branch.

## Reporting

Please avoid publishing sensitive filesystem paths, real manifests, credentials, or personal data in public issues. Report reproducible security concerns with sanitized paths and minimal test data through an appropriate private GitHub contact channel when available.

## Security boundaries

- Preview is the default; writes require `--apply`.
- Destination-only deletion additionally requires `--delete`.
- Symbolic links are skipped.
- Nested roots are rejected.
- Planned source/deletion hashes are checked again at execution.
- Copy/update uses a temporary sibling file and atomic replacement.
- Post-copy SHA-256 verification is enabled by default.

This utility cannot provide filesystem snapshot isolation and is not a substitute for versioned backups.

Maintainer: **Radwan Abdulhadi Ahmed / رضوان عبدالهادي أحمد / @rad03i2**
