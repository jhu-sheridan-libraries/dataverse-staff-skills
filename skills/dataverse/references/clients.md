# Portable skill discovery and invocation

The `dataverse` and `dataverse-tutorial` folders use the shared Agent Skills format: `SKILL.md` with `name`/`description`, relative resources, and ordinary Markdown instructions. Install the entire two folders side by side, including scripts and tutorial assets. `agents/openai.yaml` supplies optional Codex UI metadata and is not required by the other clients.

| Client | Personal skill directory | Main / tutorial invocation |
| --- | --- | --- |
| Codex desktop | `~/.agents/skills/` | Select `dataverse` or `dataverse-tutorial` from the `/` skill menu; `$dataverse` and `$dataverse-tutorial` are explicit skill mentions. |
| Codex CLI / IDE extension | `~/.agents/skills/` | `$dataverse`, `$dataverse-tutorial`, or select the skill through `/skills`. |
| Claude Code | `~/.claude/skills/` | `/dataverse` and `/dataverse-tutorial`. |
| Kiro IDE / CLI | `~/.kiro/skills/` | `/dataverse` and `/dataverse-tutorial`. |

Official references: [Codex skill discovery](https://learn.chatgpt.com/docs/build-skills), [Codex desktop slash commands](https://learn.chatgpt.com/docs/reference/slash-commands), [Claude Code skills](https://code.claude.com/docs/en/skills), [Kiro skills](https://kiro.dev/docs/skills/). Clients can also load project skills from their corresponding `.agents/skills`, `.claude/skills` or `.kiro/skills` directory. Keep one canonical source to maintain; Codex and Claude document symlinked skill folders, while a complete folder copy/import is the documented Kiro option. Preserve existing skill installations rather than overwriting a same-name skill blindly.

Codex installations already using `~/.codex/skills/` may retain that location; current public discovery guidance uses `.agents/skills`. Do not add deprecated custom prompt wrappers to emulate short aliases. Claude plugin packaging adds a namespace to slash commands, so personal/project skills preserve the requested short names. Kiro custom agents may require the skill resource in their configuration; do not rewrite unrelated agent settings automatically. Personal skill files do not automatically reach remote/cloud sessions.

After installation, check that the client discovers both skills; reload its skill list or start a fresh session if needed. Tool access, Java/DVUploader, optional Python libraries, source repository checkouts and staff authentication are runtime capabilities rather than bundled credentials or assumptions. Where skill commands are unavailable, the explicit text `Use the dataverse skill` / `Use the dataverse-tutorial skill` is the portable request; provide the skill path if that host has not discovered it.
