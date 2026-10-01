---
name: dataverse
license: Apache-2.0
description: "Assist repository staff with Dataverse deposits, metadata and file curation, review, access permissions, versions, and collection operations on the JHU AWS ECS Fargate stack. Use DVUploader for large or bulk uploads and transfer troubleshooting, drawing on Dataverse recipes and relevant codebases. Excludes system administration and on-premises workflows."
---

# Dataverse Staff

Help staff complete a deposit or repository operation with an inspectable result: correct files and metadata in the intended dataset/version, appropriate access, and evidence of what succeeded. The deployment is AWS ECS Fargate with S3 storage. Use **DVUploader for large or bulk file transfers**, including recovery after transfer failures.

Invoke as `/dataverse` in clients with skill slash commands, `$dataverse` in Codex's skill mention interface, or `Use the dataverse skill`. For a guided introduction, invoke `dataverse-tutorial`. For client-specific discovery and invocation, read [references/clients.md](references/clients.md). Keep the workflow independent of any particular agent's tool names: use its available browser, HTTP, filesystem and shell capabilities, and state missing capabilities rather than inventing them.

## Scope

Support deposit preparation, draft creation and edits, metadata and documentation review, file uploads/replacements, ingest checks, review submission/return, publication when requested, dataset/file permissions, embargoes where supported, exports, citations, and ordinary collection management. A Dataverse collection's Administrator role is a repository role; it does not authorize installation administration.

Exclude infrastructure provisioning, deployments, ECS exec, AWS IAM/bucket policies/lifecycle changes, proxy/WAF/ALB changes, application or database configuration, Solr/reindexing, upgrades, backups/restores, admin/superuser APIs, forced lock removal, and raw storage cleanup. Exclude SSH/rsync, server filesystem/mount workflows, and other on-premises architectures. When the next repair requires these capabilities, prepare a specific handoff with the evidence gathered; do not perform that repair.

## Establish the operation

Infer the target from the user's links and workspace before asking. Resolve only missing essentials: instance base URL and stage/production, dataset PID or collection alias, source files, desired operation, staff identity/permissions, and applicable deposit/access policy. Distinguish permission to edit a draft from permission to publish or broaden access. Continue actions already authorized; do not ask again for the same operation. A general curation request permits preparation and review, but does not itself authorize publication, deletion/deaccession, new access grants, or new preview URLs. Prepare a concrete proposal before requesting any missing authorization.

Use the authenticated Dataverse browser or Native API for canonical draft state. A public search result or normalized discovery record cannot establish draft completeness. Read the relevant local conventions and current metadata schema; do not invent institution policy, dataset facts, author identifiers, licenses, or unavailable features.

Identify the running Dataverse version through public instance information/UI when possible. A Docker image pin, old guide link, or checked-in setting is evidence about a checkout, not proof of the live deployment. Match API/client guidance to observed versions and capabilities.

## Choose the reference needed

- For tools, recipes, local JHU conventions, or implementation examples, read [references/codebases.md](references/codebases.md). Inspect relevant source before executing or adapting it; recipes can bundle create/publish/delete/admin actions.
- For Python automation or existing pyDataverse/python-dvuploader code, read [references/python-clients.md](references/python-clients.md). These are distinct clients with version-dependent interfaces; keep DVUploader as the established large-transfer default.
- For a local file manifest or comparison with a saved canonical draft response, read [references/inventory.md](references/inventory.md) and use the bundled Python helper. It performs no network requests or repository writes.
- For deposit preparation and curation, read [references/deposits-curation.md](references/deposits-curation.md).
- For large/bulk uploads, interrupted transfers, HTTP/S3 errors, or Fargate-specific transfer diagnosis, read [references/large-uploads.md](references/large-uploads.md). Keep DVUploader as the transfer tool.
- For review, publication, access, collections, versions, exports, or authenticated API edits, read [references/staff-operations.md](references/staff-operations.md).

Load only references relevant to the request. Follow links to official version-matched documentation when behavior or options need verification.

## Execute and verify

For writes, establish the current draft, exact affected files/fields, and intended change first. Keep payloads, manifests, and logs outside upload source directories. Scope bulk operations to a reviewed file/record list; do not silently expand a directory selection. Preserve originals and existing metadata unless alteration is requested.

Keep API credentials in the user's existing secure mechanism. Do not put tokens in source, payloads, chat, or URLs. DVUploader versions may expose credentials in process arguments or output: capture output privately and redact tokens, presigned URL query strings, and preview links before displaying/sharing it. Do not send the Dataverse token to an S3 host or disable TLS verification to make a transfer work.

Verify state through Dataverse after an operation, rather than relying on a script's last message or process exit alone. For files, reconcile the intended manifest with draft file IDs, paths, sizes, reported checksums, access flags, and ingest status. A stored client-supplied checksum is not independent proof of remote-byte integrity; state the verification method and any remaining uncertainty.

After an ambiguous write failure, inspect current state before retrying. Stop repeated writes that could duplicate files or overwrite another staff member's work. For transfer recovery, use the bounded retry and reconciliation guidance in the large-upload reference.

Report the target instance/PID/version, completed change, verification evidence, remaining failures or blockers, and useful artifact/log paths. Clearly distinguish uploaded bytes, registered draft files, reviewed content, and published content. If interrupted or blocked, leave a resumable record of verified progress.
