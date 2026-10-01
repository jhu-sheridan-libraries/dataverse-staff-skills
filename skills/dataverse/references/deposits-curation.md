# Deposits and curation

## Prepare a deposit

Use the depositor's supplied files and facts. Resolve the destination collection and whether the operation adds to an existing draft or starts a new dataset before preparing an API payload. For JHU staff-mediated deposits, check the local conventions in `codebases.md`; do not turn the depositor-facing upload message into a ban on staff uploading.

Make a manifest appropriate to the transfer: relative path, byte size, checksum algorithm/value, intended Dataverse path/label, file purpose, and restriction decision. Hash large files once when useful and reuse the results while files remain unchanged. Flag zero-byte or changing files, name/path collisions, duplicate content, accidental hidden files, and archive contents needing a decision. Do not automatically exclude legitimate dotfiles, rename research files, split a large scientific file, or transform data to fit a transfer limit.

Keep original data, accompanying code, README, and codebook/data dictionary distinguishable. Derive suggested README content from the supplied materials: what files contain, methods/provenance, units and missing values, software needed, relationships between files, and reproducibility instructions. Mark unresolved facts for the depositor. Never execute research code merely to curate it or claim an exhaustive confidentiality audit from a sample.

## Metadata and documentation review

Read the instance's current enabled metadata blocks, destination collection's required fields/templates, existing draft, and local deposit policy. Creation examples in recipes are structural aids, not an institution's complete requirements.

Check supplied evidence against title, author order/affiliations/identifiers, contacts, description, subjects and keywords, related publications and identifiers, funding, temporal/geographic coverage, methods, and domain-specific metadata. Verify identifier consistency; propose corrections without fabricating missing values. Retain repeated/compound fields and metadata blocks not involved in the requested change. Keep research-sensitive information out of publicly visible titles, abstracts, file names, and descriptions.

Assess whether documentation enables reuse and whether file labels/descriptions match their content. Record findings with the actual field/file, evidence, recommended correction, and whether it blocks the requested next step. Focus on material gaps rather than applying a fixed checklist to every dataset.

## File behavior that affects a deposit

The [Dataverse dataset guide](https://guides.dataverse.org/en/latest/user/dataset-management.html) describes installation-dependent upload limits and features. Check observed settings rather than borrowing another repository's limits. ZIPs may be unpacked; tabular ingest may produce a different representation. Agree on whether an archive should remain intact and whether original or ingested tabular bytes are the intended result. Review failed ingest separately from failed transfer.

For tabular questions, consult the version-matched [tabular ingest guide](https://guides.dataverse.org/en/latest/user/tabulardataingest/index.html). Compare observable row/column counts, variable names, encodings, dates, and missing-value definitions with the source where feasible. A UNF describes tabular content and is not a byte checksum. Direct S3 transfers may not perform the same file processing as uploads through the application; verify the actual resulting representation before promising ingest or previews.

## Access and release readiness

Use documented deposit policy and the rights holder's decisions for licenses, terms of use, restrictions, and embargoes. Propose unresolved choices instead of selecting a license or changing access by guesswork. Restricted files do not make published metadata private. If privacy/rights concerns cannot be resolved from available evidence, identify the affected fields/files and the policy decision needed.

Finish with the useful result for the request: prepared manifest/payload/documentation, verified draft edits, or a curation review. State outstanding facts and release blockers. Completing preparation does not itself publish the dataset; review and publication are covered in `staff-operations.md`.
