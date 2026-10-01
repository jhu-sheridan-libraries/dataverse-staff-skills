# Dataverse staff skills

Portable agent skills for staff deposits, curation and ordinary repository operations on the JHU AWS ECS Fargate Dataverse stack.

- **`dataverse`** prepares and curates deposits, uses DVUploader for large or bulk uploads, diagnoses transfer failures, and supports authorized review, access and version operations.
- **`dataverse-tutorial`** introduces the workflow one step at a time, with synthetic local files and a large-upload recovery exercise.

System administration and on-premises workflows are outside scope. The skills draw on [Dataverse recipes](https://github.com/gdcc/dataverse-recipes), the [JHU deployment](https://github.com/jhu-sheridan-libraries/jhu-dataverse-deployment), [DVUploader](https://github.com/GlobalDataverseCommunityConsortium/dataverse-uploader), [pyDataverse](https://github.com/gdcc/pyDataverse), and [python-dvuploader](https://github.com/gdcc/python-dvuploader). Repository-specific policy is distinguished from platform capability. No credentials or client binaries are bundled.

## Install

Clone this repository or download a tagged release. Install both complete folders from `skills/` side by side; the tutorial uses the main skill's instructions and helper. Keep any existing same-name skill until you have reviewed how to update it. Do not merge a new copy into an existing folder blindly.

```bash
git clone https://github.com/thinkingsage/dataverse-staff-skills.git
cd dataverse-staff-skills
```

For **Codex**, copy `skills/dataverse/` and `skills/dataverse-tutorial/` into `~/.agents/skills/`. For **Claude Code**, use `~/.claude/skills/`. For **Kiro IDE/CLI**, use `~/.kiro/skills/` or import each GitHub skill-folder URL through Kiro's skill interface. Project-local equivalents are documented in the [client guide](skills/dataverse/references/clients.md). Codex and Claude also support symlinked skill folders for a single maintained checkout. Kiro can use full folder copies/imports.

Reload the client's skill list or start a fresh session if the new skills are not yet visible. Installing a skill does not install Java, DVUploader, optional Python libraries or a Dataverse connection.

## Invoke

| Client | Main workflow | Interactive introduction |
| --- | --- | --- |
| Codex desktop | Select `dataverse` in the `/` skill menu, or `$dataverse` | Select `dataverse-tutorial`, or `$dataverse-tutorial` |
| Codex CLI / IDE extension | `$dataverse` or select with `/skills` | `$dataverse-tutorial` or select with `/skills` |
| Claude Code | `/dataverse` | `/dataverse-tutorial` |
| Kiro IDE / CLI | `/dataverse` | `/dataverse-tutorial` |

Examples:

```text
/dataverse help prepare these files and metadata for a draft deposit
/dataverse recover an interrupted DVUploader upload without publishing
/dataverse-tutorial
```

Use the equivalent explicit skill mention in your client. `Use the dataverse skill` and `Use the dataverse-tutorial skill` are also portable requests when the host has discovered the folders. The tutorial starts with one track choice and waits for your answer; it does not upload or publish practice data.

## Embedded Python helper

`skills/dataverse/scripts/deposit_inventory.py` uses Python 3.9+ and the standard library. It creates streamed file manifests and compares them with saved canonical Dataverse **DRAFT** JSON. It has no network access and performs no upload or repository mutation.

```bash
python3 skills/dataverse/scripts/deposit_inventory.py --help
python3 -m unittest discover -s tests -v
```

Keep reports outside the selected upload tree. A saved-metadata checksum match does not independently verify remote bytes. See the [inventory guide](skills/dataverse/references/inventory.md) for commands and exit codes, and the [large-upload workflow](skills/dataverse/references/large-uploads.md) for transfer and recovery.

## Maintenance and distribution

This repository is the canonical source for both skills. Tag releases so staff can use a known version, update installed copies deliberately, and rerun the offline tests after helper changes. Check relevant upstream interfaces when revising client guidance; source snapshots in the Python reference record behavior that was actually inspected. Test substantive instruction changes with realistic offline deposit, metadata-edit and recovery requests.

Keep the deployment repository linked to this source rather than duplicating instructions there. A future client-specific plugin or marketplace package can wrap these same skill folders. Personal/project installations preserve the short command names; plugin packaging can introduce namespaces. The first release therefore distributes ordinary skill folders directly.

## License

Apache License 2.0, matching the [Dataverse project's license](https://github.com/IQSS/dataverse/blob/develop/LICENSE.md). See [LICENSE](LICENSE). Each independently installable skill includes a copy of the license. Referenced upstream projects retain their own licenses.
