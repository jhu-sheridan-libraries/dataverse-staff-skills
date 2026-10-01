# S3 sideload and registration fallback

Use this procedure when supported DVUploader recovery has failed, when the user explicitly requests sideloading, or when a completed S3 object needs registration. DVUploader remains the normal large-transfer client. Sideloading separates byte transfer from the Dataverse write; it does not bypass deposit policy, size/quota checks, or draft permissions.

## Choose the route from evidence

| Available state/capability | Recovery route |
| --- | --- |
| DVUploader's byte transfer completed, but registration failed or its response was lost | Reconcile the draft and confirm the completed object; register the same storage identifier if genuinely absent. Do not transfer again. |
| Dataverse can issue direct-upload URLs, but the uploader cannot complete the transfer | Use the returned single/multipart protocol with a compatible client, then register the returned storage identifier. This route uses temporary signed URLs and does not require a staff AWS account. |
| AWS CLI can place files in the dataset's configured S3 store and out-of-band upload is already enabled | Use the installation's established sideload convention and scoped AWS access, then register through the staff Native API. If AWS CLI is missing, guide its installation and sign-in using `aws-cli-setup.md`. |
| Required capability, exact object mapping, or approved storage access is missing | Prepare the payload/manifest and a specific administrator handoff. Do not enable the capability, borrow the ECS task role, or use a different bucket as a workaround. |

The [Dataverse file-storage configuration guide](https://guides.dataverse.org/en/6.10.1/installation/config.html#file-storage) distinguishes `dataverse.files.<id>.upload-redirect` (Dataverse-issued direct-upload URLs) from `dataverse.files.<id>.upload-out-of-band` (files placed through other tools). S3 storage alone proves neither is enabled. Completed signed-URL/DVUploader transfers can be registered through their enabled direct-upload route without separately enabling out-of-band upload; the approved AWS-client route requires the established out-of-band capability. Confirm the running version and enabled workflow through an existing runbook, authorized capability response, or administrator-provided information. Reading a checked-in setting does not establish live state; configuration changes remain outside this skill.

Ordinary staff authorization to upload to Dataverse covers the supported signed-URL workflow. Direct bucket writes additionally require established authorization for the specific store/prefix and an AWS CLI profile using the institution's granted staff access. Guide missing local CLI/profile setup; it is not a reason to reject an otherwise supported sideload. Reuse that authorization without repeatedly asking; do not discover deployment secrets, create IAM permissions, or broaden access to make the fallback work.

## Preserve per-file state before transferring

Record the target instance, dataset PID/draft, local path, intended directory label/name, bytes and local checksum, S3 bucket/key, full Dataverse storage identifier, transfer method, and completed/registered status. Keep signed URLs, session responses, payloads and logs private and outside the source tree. Preserve prior uploader records: a filename alone cannot identify an S3 object or prove that a transfer completed. Coordinate one writer per dataset.

Reconcile canonical draft file IDs/path/size/checksum and any prior registration response. A lost response may mean registration succeeded. Preserve existing files; a checksum mismatch is not permission to replace or overwrite them. Confirm that multipart completion succeeded before registering; uploaded parts by themselves are not a completed object. An authorized S3 `HeadObject` or the documented completion result can establish existence/size; a denied HEAD does not prove absence. Record available verification without demanding broader AWS permissions.

## Transfer using Dataverse-issued URLs

Follow the running version's [direct-upload protocol](https://guides.dataverse.org/en/6.10.1/developers/s3-direct-upload-api.html). Initiate with the actual byte size, preserve the returned storage identifier and URLs, and distinguish one URL from numbered part URLs plus `partSize` and complete/abort links. Use the returned endpoints rather than copying the guide's example paths or reconstructing signed URLs.

Send exact file/part bytes and appropriate `Content-Length`. Honor required signed headers and the store's established temporary-object tagging convention; do not blindly copy a tagging header from another installation. Send the Dataverse API token only to Dataverse, never to S3. Signed URLs already authorize their specific S3 operations; do not add an AWS profile or feed such a URL to `aws s3 cp`.

For multipart, retain each part number and returned ETag, complete using the returned Dataverse link and version-matched ETag payload, and inspect the actual result before registration. Do not upload a 24 GiB file with the recipe's single PUT. An expired URL needs a supported renewed transfer/session after reconciliation; do not invent refresh or persistent-resume capabilities. Cancel an abandoned session only through its documented abort workflow after checking uncertain completion. Bucket cleanup remains an administrator task.

## Transfer using AWS CLI

Obtain the dataset's actual storage-driver ID, bucket, exact dataset prefix, unique unregistered object key, and corresponding Dataverse storage identifier from the established runbook or prior authorized initiation/transfer record. In the [v6.10.1 S3 implementation](https://github.com/IQSS/dataverse/blob/v6.10.1/src/main/java/edu/harvard/iq/dataverse/dataaccess/S3AccessIO.java), the mapping is:

```text
Dataverse storageIdentifier: <store-id>://<bucket>:<opaque-file-id>
Physical S3 object key:      <authorityForFileStorage>/<identifierForFileStorage>/<opaque-file-id>
```

The file-storage authority/identifier can come from an alternate PID marked as the storage-location designator, so the current visible PID alone is insufficient for migrated datasets. A driver named `s3` is an example, not a universal default. Neither the original filename nor Dataverse's `directoryLabel` determines this physical key. Preserve the exact opaque ID from an existing transfer record; do not substitute the filename or a full `s3://bucket/path` URI for the API storage identifier.

Preserve a known completed object's mapping. For a new upload, use the deployment's supported unique-object naming convention and confirm the destination is unused through the available approved mechanism. In v6.10.1, S3 validation requires the configured bucket and an opaque ID beginning with 11 lowercase hexadecimal characters, a hyphen and 12 lowercase hexadecimal characters (with an optional suffix); enabling out-of-band does not admit arbitrary object names. Reuse a Dataverse-issued ID or the installation's verified generator rather than inventing one. Never overwrite an object referenced by Dataverse or reuse another dataset's object. Do not guess a key from a DOI string or strip components from a storage identifier without checking version-matched source/conventions. Registering an existing object requires the correct dataset/store mapping even if another tool uploaded it successfully.

Use **AWS CLI v2** for the out-of-band byte transfer. Check `aws --version`; if missing or unsuitable, guide installation, verification and the institution's granted sign-in/profile using [aws-cli-setup.md](aws-cli-setup.md). Do this on the staff workstation or approved client environment, never inside ECS. Check the installed version's help and [S3 transfer behavior](https://docs.aws.amazon.com/cli/latest/topic/s3-config.html); high-level transfers manage their own multipart upload and completion. Do not combine AWS-client multipart sessions with Dataverse-issued part/completion URLs. Preserve established encryption, ownership and tagging requirements; request missing information instead of choosing new storage settings.

This pattern assumes `S3_OBJECT_URI` is the reviewed physical destination and `SIDELOAD_AWS_PROFILE` is already authorized. It is not a bucket-discovery or credential-setup procedure:

```bash
aws --profile "$SIDELOAD_AWS_PROFILE" s3 cp \
  "$SOURCE_FILE" "$S3_OBJECT_URI" --no-follow-symlinks --dryrun
```

Inspect the exact one-file source/destination, then remove `--dryrun` for the authorized transfer and apply only the required, established transfer options. Prefer explicit files to broad `sync`/recursive operations. A dry run does not prove permissions or successful bytes. Capture the exit/result privately and, where existing permissions allow, check object length and recorded checksum information. AWS multipart ETags are not file MD5 values; do not put an ETag into Dataverse's checksum field. Do not change IAM, bucket policy/CORS, ACLs, lifecycle rules, or ECS configuration, and do not use `--no-verify-ssl` to resolve errors.

## Register the completed object

Use the ordinary staff Native API, with no file bytes attached. For one new file, the version-matched operation is `POST /api/datasets/:persistentId/add?persistentId=<encoded PID>` with multipart form field `jsonData`. For an explicitly requested replacement, use `POST /api/files/<existing file ID>/replace` and its replacement semantics instead of adding a duplicate. Multiple-file endpoints and partial results are version-dependent; prefer per-file checkpointing during recovery.

Build valid JSON locally with a JSON library, outside the source tree. Review `storageIdentifier`, `fileName`, `mimeType`, checksum, `directoryLabel`, description, categories, restriction and any applicable metadata/access requirements. The following is a shape only; replace every example value with established facts. The placeholder hash deliberately cannot be submitted as valid fixity:

```json
{
  "storageIdentifier": "<exact Dataverse storage identifier>",
  "fileName": "observations.nc",
  "mimeType": "application/x-netcdf",
  "directoryLabel": "data/netcdf",
  "description": "<supplied description>",
  "restrict": false,
  "checksum": {
    "@type": "SHA-256",
    "@value": "<checksum of the unchanged original file bytes>"
  }
}
```

The manifest helper can calculate a supported local checksum; map its field names into this API schema rather than sending the manifest itself. Preserve intended directory labels so a later DVUploader preview does not mistake this file for a missing one. Omit optional values unless supplied/required; an unrestricted example does not override the actual access policy.

Send `jsonData` from the reviewed JSON file as a **text form field**, for example curl's `--form-string "jsonData=$(cat "$REGISTRATION_JSON")"` after validating the file. Do not attach it as the scientific `file` upload, do not manually set multipart boundaries, and do not place credentials in that file or the request URL. Use the user's existing private HTTP credential mechanism for the Dataverse header. URL-encode the PID and retain HTTP status/body privately. A conceptual request is sufficient until actual instance, credentials and payload are available; do not run the example placeholders.

Check both HTTP success and API `status`, then the per-file result/file ID and authenticated draft state. An outer `OK` from a batch operation does not prove every file succeeded. Dataverse normally obtains the object length from storage; a supplied `fileSize` is not an override or verification substitute. Reconcile name/path, bytes, reported checksum, restriction and ingest status against the unchanged local manifest. A stored supplied checksum establishes metadata agreement, not independent verification of S3 bytes. Use existing server verification or an authorized byte comparison when stronger verification is requested.

In the v6.10.1 S3 finalization implementation, `removeTempTag()` deletes **all object tags**, not just `dv-state=temp`. Do not promise custom tags survive registration or add ad hoc tag-based retention logic. If the established sideload procedure depends on such tags, resolve that compatibility issue with the operator before registration; lifecycle configuration remains outside staff scope.

## Failure boundaries and handoff

After an ambiguous registration response, inspect the draft before retrying the same object. After a transient/correctable failure, allow one controlled retry of the affected phase following reconciliation; if the same error recurs, stop blind attempts and retain checkpoints. Registration 400/403, inaccessible/wrong-store objects, quotas or policy rejection are not solved by repeated byte uploads. Do not delete or rename S3 objects to cure registration errors, force-unlock the dataset, or silently start another upload route.

Report each file as transferred, completed, registered, metadata-verified and independently byte-verified only where supported by evidence. Preserve an unregistered completed object's bucket/key/storage identifier for follow-up and indicate lifecycle/cleanup uncertainty for the administrator. Prepare a redacted handoff when store enablement, AWS authorization or infrastructure repair is needed. Do not publish as part of recovery unless publication was requested.

## Implementation sources

- [Dataverse v6.10.1 dataset API source](https://github.com/IQSS/dataverse/blob/v6.10.1/src/main/java/edu/harvard/iq/dataverse/api/Datasets.java) and [S3 storage implementation](https://github.com/IQSS/dataverse/blob/v6.10.1/src/main/java/edu/harvard/iq/dataverse/dataaccess/S3AccessIO.java): inspect against the actual running release when resolving identifier validation, registration or store behavior.
- [AWS CLI copy reference](https://docs.aws.amazon.com/cli/latest/reference/s3/cp.html) and [S3 HeadObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_HeadObject.html): client options and existence/metadata checks depend on the installed client and granted access.
- `dataverse-recipes/shell/s3_direct_upload/`: useful initiation/registration shape, but its single-PUT, hardcoded defaults and weak failure checks make it unsuitable for unchanged large-file recovery. See `codebases.md`.
