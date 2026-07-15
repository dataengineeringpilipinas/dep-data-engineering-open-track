# Milestone Pipeline — Plain-Language Mentor Guide

Use this guide when a Builder asks what happened to their milestone submission or what they should do next.

> **Rollout note:** This guide describes the pipeline introduced by [PR #137](https://github.com/dataengineeringpilipinas/dep-data-engineering-open-track/pull/137). Until that PR is merged and the repair steps are run, older issues may still show the previous behavior.

## The One-Minute Explanation

1. The Builder opens **one milestone issue** before the deadline.
2. The system checks the exact repository commit written in the issue.
3. The issue receives a status explaining what happens next.
4. If changes are needed, the Builder fixes the project and comments `/recheck <full-commit-hash>` on the same issue.
5. When the automated checks pass, a human reviewer makes the final decision.

```text
Submit one issue
      ↓
Automated checks
      ↓
┌──────────────────────┬─────────────────────────┬──────────────────┐
│ needs-improvement    │ waiting-on-prerequisite │ ready-for-review │
│ Builder fixes work   │ Previous milestone waits│ Human reviews    │
└──────────────────────┴─────────────────────────┴──────────────────┘
      ↓                           ↓                         ↓
/recheck <commit-hash>   Releases automatically       passed or improve
```

## What Each Status Means

| Status | Simple meaning | Who acts next? |
|---|---|---|
| `auto-check-pending` | The first automated check has not finished yet. | Wait for the system. |
| `needs-improvement` | Something must be corrected. | The Builder fixes it and comments `/recheck <hash>`. |
| `waiting-on-prerequisite` | The submission is recorded, but the previous milestone has not passed. | Nobody needs to resubmit; the system waits. |
| `ready-for-review` | Automated checks passed. | A human reviewer reviews it. |
| `passed` | The milestone is complete. | The system releases the next waiting milestone, if one exists. |
| `late-submission` | The first issue was created after the deadline. | A maintainer reviews only an approved exception. |
| `duplicate` | Another issue is the official submission. | Continue only on the canonical issue named by the bot. |

## Common Questions and Answers

### “The initial check failed. How do I trigger another check?”

The Builder must fix the project, push the fix, and comment on the **same issue**:

```text
/recheck 0123456789abcdef0123456789abcdef01234567
```

The hash must be the full 40-character commit hash. Pushing a commit by itself does not trigger the milestone system.

### “The `auto-check-pending` label was removed. Is that a problem?”

No. That label only means the first check is still running, so it is normally removed when the check finishes.

Look for the replacement status: `needs-improvement`, `waiting-on-prerequisite`, or `ready-for-review`.

### “Do I need to open another issue after failing?”

No. The Builder should always continue on the same issue so the original deadline and review history are preserved.

### “I pushed a new commit. Why did nothing happen?”

The milestone repository cannot automatically see pushes in every Builder repository. The Builder must comment `/recheck <full-commit-hash>` on the original issue.

### “My previous milestone passed later. Do I need to trigger the next submission?”

No. An on-time issue marked `waiting-on-prerequisite` is checked again automatically after the previous milestone passes.

### “Automated checks passed. Am I done?”

Not yet. `ready-for-review` means the submission is waiting for a human reviewer to apply `passed` or `needs-improvement`.

### “Why does M0 still need a reviewer?”

The automated system only checks basic repository structure. A human must confirm that the problem, audience, and data source make sense.

### “Will a recheck be rejected after the deadline?”

An on-time original issue keeps its deadline eligibility. The Builder may post a corrected commit on that same issue after the deadline.

### “The bot closed my old on-time issue. Should I open a new one?”

No. This may be an issue created under the old pipeline, so a maintainer should restore and reevaluate the original on-time submission.

### “The issue has no clear status or bot response.”

Do not ask the Builder to open another issue. Send the issue to a maintainer for one manual evaluation so the correct status can be applied.

## Copy-Ready Mentor Replies

### When the Builder needs to fix something

> Please fix the items listed by the bot, push your changes, and comment `/recheck <full-40-character-commit-hash>` on this same issue. Do not open another submission issue.

### When the previous milestone is still pending

> Your submission is recorded and keeps its original submission time. You do not need to resubmit; it will move forward automatically after the previous milestone passes.

### When automated checks passed

> Your automated checks passed, and the issue is now waiting for human review. No Builder action is needed unless the reviewer requests changes.

### When an old issue was closed by the previous pipeline

> Please do not open another issue. We will ask a maintainer to restore and reevaluate your original on-time submission.

## What Mentors Should and Should Not Do

### Do

- Point the Builder to the bot's latest comment and current status label.
- Remind the Builder to use the same issue and a full 40-character commit hash.
- Tell the Builder when no action is required and the reviewer or maintainer must act.
- Escalate old closed issues, missing statuses, or approved deadline exceptions to a maintainer.

### Do not

- Tell the Builder to create a replacement issue.
- Tell the Builder that pushing a commit automatically triggers a recheck.
- Apply `passed` before the issue reaches `ready-for-review`.
- Promise a deadline exception or manually change a terminal verdict.

## When to Escalate

Ask a maintainer to inspect the issue when:

- An old on-time submission was closed by the previous pipeline.
- The issue has no clear status after the automated run finishes.
- `/recheck <hash>` was posted correctly but no workflow started.
- A duplicate or late-submission decision appears incorrect.
- A `passed` label was applied or removed by mistake.

For milestone requirements and reviewer criteria, use the [Milestone Checklist](MILESTONE_CHECKLIST.md). For volunteer responsibilities and review timing, use the [Volunteer Guide](VOLUNTEER_GUIDE.md).
