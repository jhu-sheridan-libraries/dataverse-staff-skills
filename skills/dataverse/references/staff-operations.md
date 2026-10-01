# Staff repository operations

## Canonical state and API edits

Use an authenticated account with the permissions for the requested object. Resolve PID to the correct instance; database dataset/file IDs belong to that instance and must not be carried between stage and production. Get the current version and affected metadata/files before a write. For multi-record work, establish the explicit target list and preserve per-record results.

The [Native API guide](https://guides.dataverse.org/en/latest/api/native-api.html) is the endpoint authority. Common reads include `/api/info/version`, dataset versions addressed by persistent ID, metadata block definitions, and dataset locks. URL-encode PIDs and query parameters. Use `X-Dataverse-key` with Dataverse requests. Inspect HTTP status and API status; an HTML login/proxy page is not a successful JSON response.

Read-response JSON, export JSON, creation bodies, full version updates, and partial metadata-edit payloads serve different purposes. Use the documented write schema rather than reposting a response envelope. Build valid JSON with a serializer; read fresh state before full updates so unrelated fields and other staff's edits are preserved. After a timeout, check whether the change already committed before sending it again. For replacement, identify the intended file ID and preserve its version relationship; delete-and-add is not a routine substitute.

## Review, publication, and versions

When asked to submit for review, verify the draft and submit using available staff permissions. When asked to review, inspect files, metadata, rights/access, and outstanding ingest/locks, then prepare findings or use an authorized return-to-author operation with an actionable reason. Do not send a separate email/message unless requested.

When publication is requested and authorized, summarize the exact draft/version and access consequences, resolve blocking findings, and use the supported publish operation. Validate the resulting public landing page/citation and file access after release. [Dataverse's version guidance](https://guides.dataverse.org/en/latest/user/dataset-management.html#dataset-versions) explains that edits create a draft and file additions/removals require a major release; observe the offered version choices. Publication cannot simply be undone to restore draft-only status. Do not promise that deaccession removes every copy.

Deaccession or destructive deletion needs a specifically requested target, reason, and applicable repository policy. If unrequested, provide a proposal only. Infrastructure-level purge/cleanup remains outside this skill.

## Access and preview links

Distinguish dataset editing/review roles from access to individual restricted files. Verify effective/inherited permissions and the exact user/group/file set before an authorized grant or removal. Changes to a parent collection can affect many records. Restriction changes and guestbook questions should reflect approved policy, not replace it.

Preview/private URLs can expose draft files to anyone with the link, including restricted/embargoed files in supported versions. Create them only for an authorized sharing request and handle them as secrets. Verify the recipient's view and any anonymization before distribution; do not equate anonymized metadata with anonymized file content. Consult the [preview URL guidance](https://guides.dataverse.org/en/latest/user/dataset-management.html#preview-url-to-review-unpublished-dataset) for the running version.

## Collections, discovery, and exports

Within the staff member's delegated role, support collection descriptions, metadata-field selection, templates, guestbooks, and role assignments. Review scope and inheritance before a collection-wide change. Consult [collection management](https://guides.dataverse.org/en/latest/user/dataverse-management.html); creating a collection does not imply publishing it or changing default access. Limits requiring superuser access are outside scope even if they appear on a collection/dataset endpoint.

Use public discovery tools only for public discovery; read `codebases.md` for the JHU MCP's limitations. For citation/export requests, specify the dataset version and export format, and inspect the exported content. Confirm whether the chosen exporter covers the published version or an authenticated draft; do not describe a latest-published export as the draft. For downloads, reconcile files and fixity within the user's access rights and intended size/scope; use the [Data Access API](https://guides.dataverse.org/en/latest/api/dataaccess.html) for original versus derived representations.
