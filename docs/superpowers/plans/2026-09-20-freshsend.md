# FreshSend implementation plan

## Goal

Build a read-only, zero-dependency Python CLI that warns when a file selected for an AI chat, email, or upload is older than another same-named file in an explicitly chosen folder.

## Safety boundary

- Read only; never rename, delete, upload, or edit files.
- Require an explicit candidate file and comparison directory.
- Reject symlink candidates and do not follow symlinked directories or files.
- Exit non-zero when a newer same-name file is found so scripts can stop before sending.

## Delivery steps

1. Define the package metadata and write failing freshness tests.
2. Run the focused test suite to record RED.
3. Implement deterministic file snapshots, safe directory walking, JSON output, text output, and exit codes.
4. Add README, example, license, security/contributing guidance, changelog, CI, and a verification record.
5. Run tests, typecheck, lint, build, package smoke test, dependency audit, diff checks, and a real-input demo.
6. Run the standard security scan, commit only verified files, push a new public repository, publish v0.1.0, and verify CI/release URLs.

## Acceptance criteria

- Fresh candidate returns exit code 0 and explains what was checked.
- Candidate with a newer same-name file returns exit code 1 and names the newer path.
- Invalid paths and symlink inputs fail safely with exit code 2.
- JSON is machine-readable and includes size, modification time, and SHA-256.
- No network call or filesystem mutation is needed to run the check.
