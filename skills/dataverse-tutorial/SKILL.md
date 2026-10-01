---
name: dataverse-tutorial
license: Apache-2.0
description: "Launch an interactive, one-step-at-a-time introduction to the dataverse staff skill when the user requests a Dataverse tutorial, guided practice, or /dataverse-tutorial. Teach deposit preparation, curation, DVUploader transfers and failure recovery on AWS ECS Fargate. Use synthetic local examples by default."
---

# Dataverse Tutorial

Teach staff to use the companion `dataverse` skill through a short conversation with one meaningful step at a time. Begin the tutorial immediately when invoked; do not respond with an offer to start or deliver the entire course in one answer.

Read the companion [dataverse skill](../dataverse/SKILL.md) and the relevant references as the learner needs them. Resolve sibling paths relative to this skill's directory, rather than depending on a client-specific home path. If the companion is missing, explain that dependency and teach from [references/walkthrough.md](references/walkthrough.md) without claiming its tools are installed.

## First interaction

Briefly explain that the skill helps staff prepare, upload, curate and manage Dataverse content on AWS Fargate, and uses DVUploader for large files. State that practice begins with synthetic local examples. Then present **one** choice:

- Guided deposit practice (default): files → metadata → transfer → verification → next operation.
- Large-upload recovery: work through a failed transfer, recover with DVUploader, and practice S3 sideload/registration when needed.
- My own task: explain an actual deposit/curation request, starting with read-only preparation.

Use a choice tool if the client has one, or a plain question otherwise. Wait for the learner's answer. If their invocation already names a track or task, use it and start its first substantive step instead of asking the same question again. Do not request API keys or private datasets for the tutorial.

## Interactive pacing

Read [references/walkthrough.md](references/walkthrough.md) for the chosen track. Each turn should name the current step, explain the useful concept in a few sentences, give one concrete action/choice, and pause for the answer. Build on what the learner did, rather than displaying every future step. Accept `next`, `back`, `skip`, `explain`, `switch track`, and free-text answers. Do not grade or force a quiz when the user wants demonstration.

Remember the track, current step, completed artifacts and unresolved questions in the conversation. On resume, state the current step briefly and continue. Do not schedule follow-ups or create additional chats. If the learner asks for all steps at once, honor that preference.

## Practice boundaries and completion

Use the bundled [sample deposit](assets/sample-deposit/) and [synthetic draft response](assets/sample-draft.json) for local practice. Copy examples to a temporary working folder before edits or manifest creation. Never alter the installed examples, put generated logs/manifests inside the sample upload tree, or imply the synthetic PID is a real dataset. No production API call, upload, publication or access change is part of the default tutorial.

For an actual task, the tutorial is not permission to mutate a live dataset. Gather the target/source information without credentials in chat, explain the prepared next action, and follow the companion skill's existing authorization boundaries. Once the learner requests execution, work within that request; do not repeatedly ask permission for already authorized steps.

At the end, briefly identify what the learner practiced and what they can ask next. Offer useful ready-to-copy requests such as `/dataverse help prepare this deposit` or `Use the dataverse skill to recover this interrupted DVUploader upload`. Explain the host client's actual invocation syntax when known; do not promise that every client natively registers the same slash alias. The portable fallback is `Use the dataverse skill` or `Use the dataverse-tutorial skill`.
