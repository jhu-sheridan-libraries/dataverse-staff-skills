# AWS CLI setup for staff sideloading

Use AWS CLI v2 on the staff workstation or approved client environment. If it is missing, guide the user through installation and sign-in rather than treating installation as an administrator-only Dataverse task. This setup does not grant AWS access or enable out-of-band upload. Return to [s3-sideload.md](s3-sideload.md) once the client and appropriate staff identity are ready.

## Discover and install

Check `aws --version` and the workstation OS/architecture. If an installed v2 works, use it. If only v1 is found, inspect its installation/PATH before introducing v2; preserve existing profiles and unrelated tooling. If missing, give the user the relevant steps below, one meaningful action at a time when guiding interactively. Do not require installation when the task only needs registration of an already completed object through Dataverse.

Use the current [official AWS CLI v2 installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html), selecting the workstation OS and architecture:

| Workstation | Guided installation |
| --- | --- |
| macOS | Download the official [AWSCLIV2.pkg](https://awscli.amazonaws.com/AWSCLIV2.pkg), open it and follow the installer. The guide also provides a current-user installation if needed. |
| Windows 64-bit | Download and run [AWSCLIV2-User.msi](https://awscli.amazonaws.com/AWSCLIV2-User.msi) for the current user, or the all-users MSI when that is the workstation's established installation method. |
| Linux x86_64 / aarch64 | Follow the guide's matching official installer and package-signature procedure; use its current-user option or writable install/bin directories when system installation is unavailable. |

Keep installer files outside the upload source directory. Use the user's workstation installation method when provided. If managing the installation directly, use ordinary local permission mechanisms; leave password prompts to the user. Do not install through ECS exec or change server images. After installation, reopen the terminal if necessary and run `aws --version`; confirm it reports `aws-cli/2`. If it fails or still reports v1, resolve the executable/PATH using the install guide rather than reinstalling blindly. Provide only the commands for the user's platform.

## Configure granted staff access

Reuse a suitable existing named profile, supplied role/account and region. `aws configure list-profiles` can identify profile names without displaying secrets. A missing profile can be configured with the institution's existing sign-in method; do not assume JHU uses IAM Identity Center or invent a role/region.

When IAM Identity Center/SSO is the granted method, guide the [official SSO setup](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html) using the supplied start/issuer URL, SSO region, account and role:

```bash
aws configure sso --profile "$SIDELOAD_AWS_PROFILE"
aws sso login --profile "$SIDELOAD_AWS_PROFILE"
```

The user completes sign-in in their own browser. For a profile already configured for SSO, use login without reconfiguration. For another institution-provided credential process or temporary-credential workflow, follow that workflow locally; do not ask the user to paste access keys, session tokens or device authorization codes into chat, and do not create long-lived keys as a shortcut.

Verify the selected identity with the read-only [caller-identity operation](https://docs.aws.amazon.com/cli/latest/reference/sts/get-caller-identity.html):

```bash
aws --profile "$SIDELOAD_AWS_PROFILE" sts get-caller-identity
```

Compare account/role with the approved sideload destination; keep unnecessary identity details private. This proves which identity is active, not S3 write/HEAD/KMS permission. Do not probe other buckets, try broader roles, print credential files/environment variables, or retrieve deployment/SSM/task-role credentials. If access has not been granted, continue preparing the manifest/registration payload and explain the specific access the operator must supply.

Once ready, use this named profile explicitly on the one-file S3 dry run and transfer in `s3-sideload.md`. On an expired SSO session, renew sign-in and reconcile transfer/registration progress before any retry. No IAM, bucket, lifecycle, KMS-policy or Dataverse configuration change is part of client setup.
