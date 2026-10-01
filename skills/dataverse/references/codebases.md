# Relevant codebases and local conventions

These are integration sources, not bundled dependencies or authorization to run their workflows. Resolve paths from the active workspace/known sibling checkouts. If missing, use the upstream documentation or ask for the relevant location rather than cloning unrelated projects. Read applicable `AGENTS.md` and actual implementation before adapting anything. Preserve the user's repositories; make task-specific adaptations in a working output directory.

## Dataverse recipes

Local: `dataverse-recipes/`. Upstream: [gdcc/dataverse-recipes](https://github.com/gdcc/dataverse-recipes).

Use the smallest relevant recipe as an implementation example, then isolate only the requested operation. Several scripts create sample datasets/collections, publish them, delete them, or call administrative endpoints. Never execute an entire demonstration merely because one function is useful.

| Staff task | Source within `dataverse-recipes/` | How to reuse |
| --- | --- | --- |
| Draft metadata structure/editing | `dvcli/datasets/bodies/dataset.json`, `bodies/edit.json`, `dataset_metadata.sh`, `edit_dataset.sh` | Inspect schema/command shapes; use the real destination's metadata requirements. |
| Upload/replacement semantics | `dvcli/datasets/create_upload_publish_dataset.sh`, `directory_upload.sh`, `dvcli/files/replace_file.sh` | Extract operation examples only. Large/bulk transfers use DVUploader. |
| Review/version relationships | `dvcli/datasets/reviews.sh`, `link.sh`, `locks.sh` | Inspect normal staff calls; never copy unlock/admin behavior. |
| Collection examples | `dvcli/collections/collection.json`, `create_publish_delete_collection.sh` | Reuse structure after removing demonstration publication/deletion. |
| Downloads/exports | `shell/download/dv_downloader.sh`, `python/download_draft_croissant/`, `dvcli/datasets/download.sh`, `exporters.sh` | Inspect credentials, target version, output and execution scope first. |
| Metadata-block discovery | `js/metadatablocks/README.md`, `list.ts` | Inspect supported runtime and target; use current instance definitions. |
| Spreadsheet-driven draft preparation | `python/create_datasets_from_excel/create_datasets_from_excel.py` | Reuse mapping ideas only; validate all rows and payloads before creation, keep per-row PIDs/checkpoints, and reconcile partial runs. |
| Python client examples | `python/create_croissant_client_side/create_croissant_client_side.py` | Inspect version and published/draft behavior; see `python-clients.md`. |
| S3 protocol background | `shell/s3_direct_upload/README.md`, `s3_direct_upload.sh` | Diagnose phases only; use DVUploader for the transfer. |

The S3 shell recipe has Harvard/example PID and source-folder defaults, `.nc` selection and MIME/path assumptions, a single-PUT design, hardcoded credential setup, weak HTTP-success checks, and continuation after failures. Its “success” output cannot establish success. `dvcli/datasets/direct_upload.sh` also includes LocalStack/admin storage configuration; it is not a staff upload command. Exclude upgrades, backup/restore, storage-driver setup, host mounts, and server configuration examples.

The spreadsheet recipe hardcodes worksheet/column mapping, institution/contact/license defaults and demonstration credentials, and creates records before complete validation. Do not treat it as a safe batch importer. The draft Croissant recipe's `--ugly` path needs inspection/repair before use; check exporter support and Python syntax compatibility rather than running it blindly.

## JHU Fargate deployment

Local: `jhu-dataverse-deployment/`. Upstream: [JHU deployment repository](https://github.com/jhu-sheridan-libraries/jhu-dataverse-deployment).

Use `README.md`, `docker/dataverse/Dockerfile`, `config/proxy/httpd.conf`, and non-secret deployment documentation as **read-only diagnostic context**. The documented request path is Cloudflare → ALB/WAF → Apache/Shibboleth proxy → Dataverse/Payara; file storage is S3. Direct S3 upload can move file bytes off the application/proxy path when enabled for the dataset. Do not equate a Dataverse API error with an S3 PUT failure.

At skill design time the app image is pinned to `6.10.1-noble`, and proxy source includes `RequestReadTimeout` and `ProxyTimeout 600`. These do not establish live version, effective edge limits, or the cause of a timeout. Some checked-in guide links are older. The LocalStack test compose disables upload/download redirects; it cannot prove production direct-upload capability. Inspect current user-visible behavior or a supported staff API response.

`config/dataverse/Bundle.properties.overrides` contains JHU depositor-facing messages directing users to create a draft and await staff contact/upload. This is evidence of a local staff-mediated deposit convention; check current policy before quoting timelines or researcher-facing directions. It does not prevent staff using DVUploader.

The [JHRDR deposit policy](https://dataservices.library.jhu.edu/data-sharing/deposit-policy/) is the institution's policy source. At design time it requires mediated deposits and documentation including a README, describes an open-access repository rather than a controlled-access service, and asks depositors to consult Data Services for uncompressed datasets above 1 TB. Recheck for the current task. Dataverse restriction/embargo capabilities do not establish that JHRDR accepts protected data; do not propose restrictions as a workaround for ineligible content. An accommodation threshold in this policy is not an API transfer-size limit.

Do not execute build/deploy/database/bootstrap scripts or change deployment files while assisting a staff deposit. Do not retrieve SSM secrets, AWS credentials, or use private service URLs/ECS exec to bypass the public interface. A suspected proxy, IAM, bucket/CORS, or application configuration defect becomes an evidence-backed handoff.

## DVUploader

Use the [official project](https://github.com/GlobalDataverseCommunityConsortium/dataverse-uploader) and [usage wiki](https://github.com/GlobalDataverseCommunityConsortium/dataverse-uploader/wiki/DVUploader,-a-Command-line-Bulk-Uploader-for-Dataverse). Discover a trusted installed executable JAR and Java runtime; source code, an old wiki version, and an installed release may differ. Obtain the supported client if needed for an authorized upload; do not install server components. Read `large-uploads.md` for setup, commands, verification, and troubleshooting. Do not substitute the recipes' bespoke S3 uploader for DVUploader.

## JHU repositories MCP

Local: `jh-repositories-mcp/`. Upstream: [JHU repositories MCP](https://github.com/jhu-library-devops/jh-repositories-mcp). Relevant sources: `src/models/schemas.ts`, `src/models/identifiers.ts`, `src/adapters/jhrdr/dataverse-client.ts`, `docs/adr/ADR-008-anonymous-read-only-v1.md`, and `test/fixtures/jhrdr/`.

Use a connected `search_items`/`get_item` capability for public dataset discovery only after tool discovery confirms it exists. A checkout is not a callable MCP connection. Read actual tool schemas; do not invent arguments or endpoints. The JHRDR adapter is anonymous/latest-published only: it cannot inspect drafts, upload, edit, or show restricted content. Not-found cannot prove that a non-public dataset does not exist.

Its normalized record omits some metadata (including author identifiers/repeated descriptions) and limits public file summaries. Do not use it as a complete curation record or a round-trip metadata-edit payload. Its sanitized dataset fixture is a read-response test example, not a deposit template. Use the selected Dataverse instance's canonical authenticated state for staff work. Nearby AWS/OpenTofu repositories contribute architecture context only; their executable workflows are outside this skill.
