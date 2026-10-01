# Large uploads on AWS ECS Fargate with DVUploader

## Tool and execution context

Use DVUploader for large/bulk uploads and resumed transfers. Work from an authorized staff workstation or an already approved client execution environment with access to the source data. Do not transfer files into an ECS container or a server filesystem. Avoid moving research data to a new service merely to improve upload performance.

Discover the Java runtime and exact executable JAR. Check its help/version or version-matched source and the [official usage wiki](https://github.com/GlobalDataverseCommunityConsortium/dataverse-uploader/wiki/DVUploader,-a-Command-line-Bulk-Uploader-for-Dataverse). The [v1.4.0 tagged build](https://github.com/GlobalDataverseCommunityConsortium/dataverse-uploader/blob/v1.4.0/pom.xml) targets Java 21; the wiki's Java 8+ statement covers an older artifact. Match the actual release, rather than assuming either requirement universally. Never assume a wildcard JAR selection chooses the correct binary.

Documented CLI options include `-listonly`, `-verify`, `-recurse`, `-limit`, `-maxlockwait`, `-uploadviaserver`, and `-singlefile`. The latter changes registration batching; it does not mean S3 single-part upload. Use only supported options and only those the task needs. Do not use `-trustall` to fix production TLS failures. Coordinate one writer per dataset; parallel uploader processes and concurrent staff writes can invalidate comparison/registration state.

## Prepare and inspect

1. Resolve instance base URL (no dataset page path), stage/production, dataset PID, current draft and edit permission. Read existing files and locks. Check user-visible upload-size/count/quota constraints and the intended access policy. No universal “large file limit” comes from Fargate alone.
2. Select explicit files or a deliberate source directory. Record paths, counts, byte sizes, and local fixity. Keep the JAR, API payloads, logs and manifests outside that directory. Reconcile prior uploader directory labels with DVUploader's preview before calling a file absent: the S3 recipe uses `data/netcdf`, while a new explicit-file selection may use a different label. Explain expected labels when recursion is used; the client may retain the selected top-level directory name. Preserve an already registered file and transfer only the genuinely outstanding input.
3. Check available local resources for checksum calculation and the installed client's multipart buffering/staging behavior. Do not assume a whole-file memory requirement or a particular temporary-disk requirement without observing the client.
4. Run a supported dry run and inspect its selected files, existing-file comparisons, target and totals. `-listonly` avoids upload, but can still query Dataverse and write local logs. For uncertain behavior, start with a small explicitly selected file/batch within the already authorized upload scope; do not create or publish a throwaway production dataset.

The following is an invocation pattern, not a command with populated credentials. Bind these task-specific variables locally through the user's existing credential mechanism. The `-key` argument can appear in process arguments and some versions' output; keep output private and redact it before exposing it. Preserve actual argument boundaries and quote paths.

```bash
java -jar "$DVUPLOADER_JAR" \
  "-server=$DATAVERSE_BASE_URL" "-did=$DATASET_PID" \
  "-key=$DATAVERSE_API_TOKEN" -listonly -verify "$SOURCE_PATH"
```

Choose upload-mode flags after inspecting the preview. In the [v1.4.0 implementation](https://github.com/GlobalDataverseCommunityConsortium/dataverse-uploader/blob/v1.4.0/src/main/java/org/sead/uploader/dataverse/DVUploader.java), existing-file matching uses path/name; `-verify` adds checksum comparison, and a mismatch can become a new upload candidate rather than an explicit replacement. Ingested originals can lack comparable original checksums. Do not simply remove `-listonly` from a verification command and upload every reported difference. Resolve mismatches/unknowns, use explicit file selections, and handle intended replacements separately.

For the authorized upload, remove `-listonly` from the reconciled transfer invocation and use `-verify` only where comparison is appropriate. Add `-recurse` only when subdirectories belong in the deposit. Run from a private working directory outside the upload tree: [AbstractUploader](https://github.com/GlobalDataverseCommunityConsortium/dataverse-uploader/blob/v1.4.0/src/main/java/org/sead/uploader/AbstractUploader.java) creates its own local log there even for a dry run. Capture output privately, redact before display, and check canonical draft state. Do not put a literal token in a reusable script or shared command.

## Direct upload and failure phases

Keep DVUploader responsible for transfer and registration. Use its logs to identify the phase; raw S3/API recipes explain the protocol, not a replacement transfer workflow.

The [Dataverse direct-upload guide](https://guides.dataverse.org/en/6.10.1/developers/s3-direct-upload-api.html) describes initiation, byte transfer, multipart completion where needed, and registration. Initiation uses the actual byte size and returns either one URL or numbered part URLs, `partSize`, a storage identifier and completion/abort links. Preserve returned links rather than reconstructing them. Multipart completion uses collected part ETags; ETags are not general-purpose file checksums. Registration requires the corresponding storage identifier and file metadata/fixity. Check the running version's guide for protocol differences.

Treat a presigned URL as a temporary credential; do not alter, decode/re-encode, or share its query string. Dataverse's API token belongs on the Dataverse requests, not S3 PUTs. Successful transfer alone is not a registered dataset file. An initiation/cancel/completion request is an external operation even where its HTTP method is GET.

Do not assume direct upload is enabled because S3 is configured. Confirm the observed client's initiation response. If unavailable, DVUploader's documented `-uploadviaserver` fallback still sends bytes through the application/proxy chain. For large files, establish that the route supports the size/duration before using it. Do not silently fall back to an already failing route or enable direct upload yourself.

## Diagnose and recover

Record the failure phase, UTC timestamp/duration, file byte size, client/runtime versions, HTTP/API or S3 error code, safe request IDs, and completed files/parts if available. Read a small redacted log excerpt, not an unrestricted dump. Correlate the public/API request and S3 response independently. A 403 is not enough to blame the Dataverse token or bucket policy.

| Observed symptom | Staff action and limit |
| --- | --- |
| Dataverse 401/403 or login HTML | Verify chosen host, staff account/token validity, draft permission, and response origin. Do not expose the token or retry another environment with it. |
| Dataverse size/quota/file-count rejection | Check the explicit rejected constraint and manifest. Propose supported packaging only when scientifically appropriate; request a policy/configuration handoff if the limit must change. |
| S3 expired token/signature mismatch/403 | Check whether the signed URL expired or was altered and whether required headers match the client's supported protocol; verify local clock and proxy interference. A fresh attempt is appropriate only after reconciliation. Persistent denied access needs a handoff. |
| S3 501/length or part-completion error | Inspect exact-byte `Content-Length`, part sizes, recorded part results and client compatibility. Preserve the source bytes; do not patch scientific files or guess a completion endpoint. |
| 413, connection reset, 502/504/edge timeout | Establish whether bytes went to S3 or through the proxy; correlate request ID and elapsed time. Use a supported DVUploader direct route if available. Do not change ALB/WAF/proxy timeouts or infer a live limit from checked-in configuration. |
| Dataset lock or ingest failure | Read lock/status and wait within a chosen client bound if processing is active. `-maxlockwait` changes client patience, not server limits. Stalled processing needs a handoff; do not force unlock or promise re-ingest. |
| Local Java/memory/disk/TLS failure | Confirm runtime/JAR compatibility and client staging/buffering requirements. Adjust only justified client settings or use an approved client environment; do not disable certificate checks. |
| Transfer finished, file absent from draft | Check registration and multipart-completion results. Treat uncertain registration as possibly committed; reconcile file IDs/path/size/checksum before rerunning. Do not upload a duplicate just because the last response was lost. |

For a transient client/network failure, permit one controlled retry after state inspection and correction. If the same failure recurs, stop blind attempts, preserve progress, and choose a different *supported DVUploader configuration* only if the evidence justifies it; otherwise prepare a handoff. Authentication, policy, or unsupported-capability errors need resolution before retrying.

Rerun DVUploader first in list-only mode on the unchanged intended input, inspect skip/upload decisions, then transfer only reconciled outstanding files. Resume means reconciling dataset files; do not promise in-place multipart resume without proof that the installed release preserves that session. Where an abandoned client session has a documented cancel operation, cancel only that operation within its supported workflow after checking uncertain completion. Raw bucket deletion, multipart cleanup policy, and Dataverse `cleanStorage` are outside scope.

## Verify the deposit and leave a handoff when needed

Reconcile every intended file against authenticated draft file IDs, relative labels, sizes, algorithm/value pairs, restriction flags and ingest status. The [AWS multipart guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html) explains why a multipart ETag is not an MD5 checksum. Client-supplied fixity stored during registration and a DVUploader comparison against that metadata do not independently prove S3 bytes were checked; state what was verified. Use an authorized original-byte download/checksum comparison or an existing server verification result when stronger evidence is required; do not automatically redownload a huge dataset.

Report per-file uploaded/registered/verified/failed status, including any unverified items. Do not call the deposit complete because the client prints “all files processed.” Do not publish as part of upload unless publication was also requested.

If infrastructure intervention is necessary, prepare a redacted handoff naming the instance/PID, file sizes, request/transfer phase, observed errors/request IDs/times, client versions, verified progress, attempted client fix, and specific administrator check needed. Do not include tokens, signed URLs, preview links, private data contents, or an unproven root cause. Sending the handoff requires a request to send it.
