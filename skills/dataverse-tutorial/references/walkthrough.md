# Interactive walkthrough

Deliver the selected track incrementally. The descriptions below are teaching notes, not text to dump into the first response.

## Guided deposit practice

1. **Name the task.** Distinguish the Dataverse installation, collection, dataset PID, draft and published version. Use the synthetic sample; ask the learner whether the goal is preparation, upload, curation or publication. Explain that an upload does not publish.
2. **Prepare files.** Copy `assets/sample-deposit/` into a temporary practice folder. Inspect its small synthetic CSV and README. Use the companion's `deposit_inventory.py manifest` helper when available, saving output outside the file tree. Explain explicit file selection, labels, checksums and documentation. Ask the learner to identify which files belong in the deposit or to review the manifest.
3. **Curate metadata.** Read the synthetic draft response, which is an exercise artifact rather than a real API result. Discuss title/description, supplied author/contact information, local requirements and rights choices. Ask for one supported correction or a question; prepare that correction locally without posting it. Keep unknown facts unresolved rather than filling them with plausible text.
4. **Choose transfer.** Show a DVUploader invocation using unpopulated local variables and a list-only preview. Explain instance/PID selection, direct multipart transfer for large files, registration and the private working directory for logs. Do not run a client against the synthetic PID or invent a dry-run transcript. Ask the learner what to check before changing a preview to a transfer.
5. **Verify the draft.** Use `deposit_inventory.py reconcile` with the practice manifest and bundled synthetic draft response. Align the prefix with `data` so path matching is explicit. Explain matched/missing/unexpected files and checksum uncertainty, including how ingest can change the representation. Invite the learner to remove a file from a *copied* saved draft JSON and rerun to see missing-file detection. Do not pretend metadata comparison independently verifies S3 bytes.
6. **Choose the next operation.** Show the difference between review submission, a curator's publication decision and a new version. Explain staff roles versus system administration, and JHU policy versus platform capability. Ask which real task they want to try next, or finish with two concise invocation examples.

## Large-upload recovery

Use this scenario without generating enormous files or contacting a repository: two 24 GiB NetCDF files were attempted with an old S3 recipe; a transfer returned 403, the script said “All files processed,” and one file is visible in the draft.

1. **Locate the failure.** Present only that scenario. Ask what evidence the learner would gather. Explain the difference between initiation, S3 byte transfer, multipart completion and Dataverse registration; do not identify the cause from 403 alone.
2. **Reconcile progress.** Discuss the authenticated draft list, exact file paths/labels, sizes/checksums, locks and private logs. Explain why the existing file must be checked before rerunning both files. The old recipe's `data/netcdf` label may differ from DVUploader's selection-relative paths.
3. **Prepare DVUploader.** Discover or discuss the actual JAR/runtime and supported flags. Show a list-only pattern; match client/version guidance and explain source selection, one writer per dataset and credential redaction. Keep all execution offline in this scenario.
4. **Recover the outstanding file.** Explain fresh initiation, supported multipart transfer and registration with the selected DVUploader release. Reconcile a lost registration response before another write. Ask the learner whether the given failure evidence supports one corrected retry or an administrator handoff; accept a reasoned answer rather than forcing a single guessed root cause.
5. **Verify and hand off.** Compare manifest against canonical draft results, distinguish reported-checksum checks from independent byte checks, and prepare a short redacted handoff for infrastructure blockers. Explain why changing ECS, bucket/IAM, proxy settings or force-unlocking is outside the staff skill. Finish with an example real recovery request.

## Learner's own task

Ask only for missing non-secret context needed for the next step. Reuse the relevant section of the companion skill, keep explanations tied to the learner's task, and begin with inspection/local preparation. Explicitly distinguish tutorial demonstration from requested live execution. A request to execute the prepared staff operation can transition into the `dataverse` workflow without restarting intake.
