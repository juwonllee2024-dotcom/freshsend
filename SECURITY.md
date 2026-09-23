# Security policy

## Supported version

The latest release on the default branch is the supported version.

## Scope

FreshSend is intentionally small and local. It reads only the explicit candidate and the explicit comparison directory. It must not upload data, execute commands, mutate files, follow symlinks, or silently widen the scan scope.

## Reporting a vulnerability

Please do not open a public issue for a path traversal, unintended file disclosure, command execution, dependency, or data-exfiltration vulnerability. Use GitHub's private security advisory flow for this repository and include:

1. the released version or commit;
2. exact reproduction steps with synthetic files only;
3. expected versus actual behavior; and
4. a safe contact method for follow-up.

Do not include secrets or private user files in a report.
