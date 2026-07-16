# DEP Cohort 1 - CI Playbook

by: `JC Diamante`

# Milestone Pipeline — Plain-Language Mentor Guide

Use this guide when a Builder asks what happened to their milestone submission or what they should do next.

> **Historical note:** Older late submissions may still be closed under the previous hard-deadline behavior. The current pipeline does not reopen those issues automatically; send one to a maintainer if it needs reevaluation.

## The One-Minute Explanation

1. The Builder opens **one milestone issue**, ideally by the target deadline.
2. If it was created after the target deadline, the system adds `late-submission` and a deadline notice, but keeps the issue open.
3. The system checks the exact repository commit written in the issue.
4. The issue receives a workflow status explaining what happens next.
5. If changes are needed, the Builder fixes the project and comments `/recheck <full-commit-hash>` on the same issue.
6. When the automated checks pass, a human reviewer makes the final decision.

```text
Submit one issue
      ↓
Optional timing indicator: late-submission
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

The `late-submission` indicator may appear beside any workflow status below. It records timing only; it does not decide what happens next.

## Workflow Statuses

| Status | Simple meaning | Who acts next? |
|---|---|---|
| `auto-check-pending` | The first automated check has not finished yet. | Wait for the system. |
| `needs-improvement` | Something must be corrected. | The Builder fixes it and comments `/recheck <hash>`. |
| `waiting-on-prerequisite` | The submission is recorded, but the previous milestone has not passed. | Nobody needs to resubmit; the system waits. |
| `ready-for-review` | Automated checks passed. | A human reviewer reviews it. |
| `passed` | The milestone is complete. | The system releases the next waiting milestone, if one exists. |

## Additional Indicators

| Indicator | Simple meaning | Effect on the issue |
|---|---|---|
| `late-submission` | The issue was created after the target deadline. | None. The issue stays open and follows its normal workflow status. The indicator remains visible even after `passed`. |
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

### “My issue has `late-submission`. Was it rejected?”

No. The label records that the issue was created after the target deadline. The bot still checks the submitted commit, applies the normal workflow status, keeps the issue open, and allows the usual reviewer verdict flow.

Read the other status on the issue to determine the next action:

- `needs-improvement`: fix the work and use `/recheck <full-commit-hash>` on the same issue.
- `waiting-on-prerequisite`: wait for the previous milestone to pass.
- `ready-for-review`: wait for a human reviewer.
- `passed`: the milestone is complete; the issue closes as completed, not because it was late.

### “Do I need to open another issue after failing?”

No. The Builder should always continue on the same issue so the original submission time and review history are preserved.

### “I pushed a new commit. Why did nothing happen?”

The milestone repository cannot automatically see pushes in every Builder repository. The Builder must comment `/recheck <full-commit-hash>` on the original issue.

### “My previous milestone passed later. Do I need to trigger the next submission?”

No. An issue marked `waiting-on-prerequisite` is checked again automatically after the previous milestone passes.

### “Automated checks passed. Am I done?”

Not yet. `ready-for-review` means the submission is waiting for a human reviewer to apply `passed` or `needs-improvement`.

### “Why does M0 still need a reviewer?”

The automated system only checks basic repository structure. A human must confirm that the problem, audience, and data source make sense.

### “Will a recheck be rejected after the deadline?”

No. The deadline only determines whether the issue has a `late-submission` indicator. The Builder may post a corrected commit on the same issue, and the recheck follows the normal evaluation path.

### “Why is a late submission visible in the public tracker?”

Evaluated late submissions count in the same queues, milestone totals, and aggregate totals as other submissions. The tracker displays a separate **Late** badge beside the current workflow status. Historical issues that were closed by the old deadline-only rejection path remain excluded unless a maintainer reevaluates them.

### “The bot closed my old issue under the previous pipeline. Should I open a new one?”

No. A maintainer should inspect and, when appropriate, manually reevaluate the original issue. The current pipeline does not automatically reopen historical closures.

### “The issue has no clear status or bot response.”

Do not ask the Builder to open another issue. Send the issue to a maintainer for one manual evaluation so the correct status can be applied.

## Copy-Ready Mentor Replies

### When the Builder needs to fix something

> Please fix the items listed by the bot, push your changes, and comment `/recheck <full-40-character-commit-hash>` on this same issue. Do not open another submission issue.

### When the previous milestone is still pending

> Your submission is recorded and keeps its original submission time. You do not need to resubmit; it will move forward automatically after the previous milestone passes.

### When automated checks passed

> Your automated checks passed, and the issue is now waiting for human review. No Builder action is needed unless the reviewer requests changes.

### When the issue was submitted late

> The `late-submission` label records timing only. Your issue remains open and will continue through the normal checks and review process. Follow the other workflow status on the issue for your next action, and keep all revisions on this same issue.

### When an old issue was closed by the previous pipeline

> Please do not open another issue. We will ask a maintainer to inspect and, when appropriate, reevaluate your original submission.

## What Mentors Should and Should Not Do

### Do

- Point the Builder to the bot's latest comment and current status label.
- Read `late-submission` separately from the workflow status that determines the next action.
- Remind the Builder to use the same issue and a full 40-character commit hash.
- Tell the Builder when no action is required and the reviewer or maintainer must act.
- Escalate old closed issues, missing statuses, or an incorrect late indicator to a maintainer.

### Do not

- Tell the Builder to create a replacement issue.
- Tell the Builder that pushing a commit automatically triggers a recheck.
- Tell the Builder that `late-submission` requires an exception or blocks review.
- Apply `passed` before the issue reaches `ready-for-review`.
- Remove a valid late indicator or manually change a terminal verdict.

## When to Escalate

Ask a maintainer to inspect the issue when:

- An old submission was closed by the previous pipeline.
- The issue has no clear status after the automated run finishes.
- `/recheck <hash>` was posted correctly but no workflow started.
- A duplicate decision or `late-submission` indicator appears incorrect.
- A `passed` label was applied or removed by mistake.

For milestone requirements and reviewer criteria, use the [Milestone Checklist](MILESTONE_CHECKLIST.md). For volunteer responsibilities and review timing, use the [Volunteer Guide](VOLUNTEER_GUIDE.md).
