# Contributing to FreshSend

Small, reproducible changes are welcome.

1. Open an issue describing the user problem and the smallest safe behavior.
2. Keep all path access explicit and read-only.
3. Add a test before changing behavior.
4. Run `python -m pytest`, `ruff check .`, `mypy src`, `python -m build`, `pip-audit --path dist`, and `git diff --check`.
5. Explain any platform-specific behavior, especially Windows symlink behavior.

Please do not add telemetry, silent uploads, background watchers, or provider-specific credentials without a separate design discussion.
