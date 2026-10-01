# Python clients

Use Python when it improves metadata preparation, repeatable staff API work, manifest construction, or analysis of existing client code. Keep large/bulk transfer work on the established DVUploader workflow in `large-uploads.md`. Java DVUploader and the Python package named `dvuploader` are distinct implementations; record the chosen client/version explicitly. Do not silently exchange them.

## pyDataverse

Source: [gdcc/pyDataverse](https://github.com/gdcc/pyDataverse). Documentation: [pyDataverse docs](https://gdcc.github.io/pyDataverse/).

Use pyDataverse for canonical dataset/collection/file reads, local metadata construction, and scoped draft operations supported by the installed release. Its interface is evolving: the current main branch documents a high-level `Dataverse` object, while many recipes/releases use `pyDataverse.api.NativeApi` and metadata models. Check the installed package version and matching documentation/source before composing calls. Do not combine examples from these interfaces or assume that main-branch features ship in the installed package.

Consult the current instance's metadata blocks and collection requirements, even when a library model validates a payload. Model validation cannot prove institutional completeness, rights, or correctness of research facts. Preserve compound/repeated fields and unrelated blocks when adapting model exports for writes.

Separate reads/local preparation from creation, updates, file writes, publication and deletion. High-level convenience examples may include `publish()`; omit it unless requested. Determine whether object construction/assignment is local or writes remotely from the version's implementation. The inspected [high-level metadata update](https://github.com/gdcc/pyDataverse/blob/1fb1ac6dd94e470d27aaf513b6a6b3816f5e7378/pyDataverse/dataverse/dataset.py) replaces metadata/license state; prefer a documented scoped edit for a narrow correction. Check returned HTTP/API results and reconcile ambiguous outcomes just as for raw Native API calls. A Python upload convenience method does not supersede the chosen DVUploader transfer route.

Local recipes worth inspecting include the Excel-to-datasets and client-side Croissant directories listed in `codebases.md`. Their hardcoded metadata, demo targets, version dependencies and published/draft assumptions must be replaced by the actual task context. For batch imports, validate the complete proposed row-to-field mapping first; record returned PIDs per row and inspect already-created drafts before rerunning a partial batch. Never retry an entire sheet blindly.

## python-dvuploader

Source/docs: [gdcc/python-dvuploader](https://github.com/gdcc/python-dvuploader). Python import/package name: `dvuploader`.

Relevant capabilities include `File` descriptions, explicit directory labels, a `DVUploader` orchestration object, streamed direct/multipart uploads and a CLI/config interface. Use these as knowledge for reviewing an existing Python workflow or preparing manifests. Consult the installed release's source for actual replacement, fallback, retries, cancellation and checkpoint semantics; the Java flags do not apply to the Python CLI.

Do not recommend unmodified Python transfer code based solely on the README. The inspected [uploader snapshot](https://github.com/gdcc/python-dvuploader/blob/9e9ce8b906c8b39e39598d73e8d002a82db211db/dvuploader/dvuploader.py) and [direct-upload snapshot](https://github.com/gdcc/python-dvuploader/blob/9e9ce8b906c8b39e39598d73e8d002a82db211db/dvuploader/directupload.py) have consequential behaviors: `replace_existing=True` by default, unsupported direct upload can fall back to application upload, success text is not per-file verification, and a direct PUT path passes the Dataverse API key to storage. Recheck the exact selected version before concluding these observations still apply. Do not execute a path that sends the Dataverse token to storage; use the established Java workflow while that remains unresolved.

If the user explicitly chooses a Python transfer workflow later, make that selection concrete and inspect its implementation first. Disable unintended replacement/fallback where supported, set concurrency/retries to a justified bound, preserve per-file state, confine credentials, and verify canonical registration/fixity. If the selected version cannot meet those requirements, explain the specific limitation and continue preparation using supported tools; do not patch an upstream uploader or change the server implicitly.
