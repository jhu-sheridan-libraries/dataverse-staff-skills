# Local deposit inventory helper

Use [scripts/deposit_inventory.py](../scripts/deposit_inventory.py) for repeatable file inventories and comparison with a saved canonical Dataverse draft response. It requires Python 3.9+ and only the standard library. It never contacts Dataverse, reads credentials, uploads, or modifies source files.

`manifest` includes **every regular file** below the explicitly selected directory, including hidden files. Review the selection first; do not point it at an unrelated project tree. Symlinks/special files and detected changes during hashing are refused. SHA-256 is the default; choose the draft's supported checksum algorithm for a comparable verification pass. `--prefix` sets the intended Dataverse directory label before relative source paths, not a local directory. Align it with the actual DVUploader preview or prior upload's labels.

Bind the paths locally. Save generated output in a working folder outside the selected upload tree; shell output redirection inside that tree would itself add a file to the inventory.

```bash
python3 "$SKILL_DIR/scripts/deposit_inventory.py" manifest "$SOURCE_ROOT" \
  --checksum sha256 --prefix "$DATAVERSE_PATH_PREFIX" \
  > "$WORK_DIR/manifest.json"

python3 "$SKILL_DIR/scripts/deposit_inventory.py" reconcile \
  --manifest "$WORK_DIR/manifest.json" --draft-json "$WORK_DIR/draft.json" \
  > "$WORK_DIR/reconciliation.json"
```

The manifest records relative/intended paths, byte sizes and streamed checksums. Its `review` section flags hidden/empty files, duplicate content and path/case collisions for staff decisions; it does not remove or rename them. Reuse a manifest only while its inputs remain unchanged.

`reconcile` accepts saved Native API version responses or dataset responses containing `latestVersion`, requires `versionState: DRAFT`, and compares the full file list. Public MCP summaries/exports and published responses are not substitutes. It reports matched file IDs, missing/unexpected paths, size/checksum differences, incomparable algorithms and ingested-original uncertainty. Unexpected files can be legitimate existing draft content; do not infer permission to delete them. It does not compare restriction flags or assess content/metadata quality; check those separately.

Exit **0** means an inventory was created (review its flags), or a complete saved-metadata match. Exit **1** means manifest path/case collisions or incomplete reconciliation. Exit **2** means invalid input or a filesystem/read/change/symlink error. JSON goes to stdout; `--help` explains the commands. A zero exit does not prove current live state, independent remote-byte integrity or publication readiness. A checksum algorithm mismatch calls for an appropriate comparable manifest or verification method, not a claim of corruption.
