# FreshSend founder note — 2026-09-20

## Today’s problem

People select a file for an AI chat, email, ticket, or upload and later discover that a newer file with the same name was sitting in the workspace. The mistake is easy to make because the receiving tool usually shows “attached” but not whether the selected artifact is the latest local copy.

## First user

Developers, students, and support teams who repeatedly attach exported reports, logs, screenshots, prompts, or configuration files to an AI chat or issue tracker.

## Four candidate questions

| Candidate | Confirmed fact | Innovation hypothesis | One difference | 7-day experiment | Score / 50 |
| --- | --- | --- | --- | --- | ---: |
| FreshSend | AI tools can lose explicit file-selection control and users report wrong or stale context. | A pre-send local freshness check can prevent the mistake without owning the chat provider. | It checks the artifact at the hand-off boundary, not the model’s answer. | Ask 10 developers to run `freshsend check` before their next upload and count prevented stale sends. | 44 |
| ContextRot Lens | Long coding sessions can retain stale context and drift into old tasks. | A repo-local freshness score for instruction/context files could flag risky memory. | It would audit context artifacts, not file attachments. | Run against 20 repos and manually label whether each warning is useful. | 38 |
| AttachGate | File attachment systems can reject files or attach the wrong/unsupported kind, breaking a conversation. | A browser-side attachment preflight could show type, size, and hash before submit. | It sits in the browser UI and blocks invalid attachments. | Test a Chromium proof-of-concept on two chat sites with five file types. | 36 |
| ClipboardExpiry | Copy/paste workflows silently carry old text and citations into new conversations. | A local clipboard receipt with age and source could reduce stale paste errors. | It guards clipboard transitions rather than files. | Log 20 copy events locally and ask users whether the receipt changed behavior. | 34 |

## Selection

FreshSend wins because the pain is concrete, the MVP is safe to build today, and the result is immediately visible: `STALE` with the exact newer path. ContextRot Lens is close to GhostSweep and risks becoming another abstract dashboard. AttachGate depends on browser-extension permissions and provider-specific UI. ClipboardExpiry overlaps SourceStamp and would need persistent monitoring before it becomes useful.

## Business hypothesis

- Free/open source: local CLI and CI check for individuals and small teams.
- Possible paid path: team policy bundles, signed upload receipts, or integrations; not validated and not required for the MVP.
- First ten users: local-AI and coding-assistant communities, issue reporters who work with logs/configs, and developers who already use preflight scripts.

## Evidence reviewed

- GitHub Copilot documentation says chat uses conversation history, selected files, and tool results as context: <https://docs.github.com/en/copilot/tutorials/optimize-chat-usage>
- Codex users reported loss of explicit file selection and loss of control over which files enter context: <https://github.com/openai/codex/issues/9978>
- Codex users reported context compaction causing task drift and stale requests to be acted on: <https://github.com/openai/codex/issues/11315>
- VS Code users reported wrong file/session context being included across active chat sessions: <https://github.com/microsoft/vscode/issues/316051>
- OpenAI API users reported uploaded files being inaccessible or the wrong file being selected: <https://github.com/openai/openai-openapi/issues/222>

## Portfolio check

The account had 31 public repositories at the start of this run: 3 stars, 0 forks, 1 watcher, 0 open issues, 1 open pull request, and 27 latest releases reported by the GitHub CLI. Traffic views/clones were unavailable. FreshSend is separate from existing selection, provenance, clipboard, answer-completeness, and phantom-session tools.
