# Volunteer Guide

> Volunteers don't teach. They enable.

The program runs on milestones, not lectures. Your job is to create the conditions for Builders to learn — not to spoon-feed answers.

---

## Roles

### Content Curators
Find and organize learning resources (videos, articles, docs) for each week. You don't need to create content — you curate it.

**Tasks:**
- Add resource links to week folders in this repo
- Keep resources free, accessible, and practical
- Flag outdated or broken links

### Milestone Reviewers
Review Builder submissions using the checklist in [MILESTONE_CHECKLIST.md](MILESTONE_CHECKLIST.md). Give a Pass or Improve verdict.

**Tasks:**
- Check submissions within 3–5 days of the deadline
- Use the checklist — don't improvise criteria
- Leave one specific, actionable comment when marking Improve
- Review issues labeled `ready-for-review`; issues labeled `waiting-on-prerequisite` are recorded but not yet ready for a verdict
- Apply `passed` only after the full human checklist is satisfied, including M0; applying it closes the issue and releases the builder's next queued milestone
- Apply `needs-improvement` when revisions are required. Do not remove a terminal `passed` label directly; escalate an accidental verdict to the Systems Lead for an audited correction

### Community Moderators
Keep the Discord healthy. Answer questions async. Encourage progress.

**Tasks:**
- Respond to questions within 24–48 hours (async is fine)
- Redirect to resources before giving direct answers
- Surface common questions to the program lead

### Squad Guides *(Optional)*
Paired with stuck Builders. Limited slots. Only for Builders who are blocked, not those who are slow.

**Tasks:**
- One check-in per week (async DM is fine)
- Help unblock — don't do the work for them
- Escalate to program lead if a Builder is at risk of dropping out

---

## Operating Rhythm

| Cadence | Activity |
|---------|---------|
| Weekly | Moderators check community channels |
| Per milestone | Reviewers process submissions |
| Monthly | Optional team sync / retrospective |
| End of cohort | Showcase + featured projects update |

---

## Review Escalation Policy

A builder should never be blocked on a milestone for more than 7 days due to reviewer unavailability.

| Day | Who acts | Action |
|-----|----------|--------|
| Day 1–5 | Milestone Reviewer | Review the submission and apply `passed` or `needs-improvement` |
| Day 5 | Community Moderator | Ping the assigned reviewer in the volunteer channel if no verdict yet |
| Day 7 | System Lead | Step in directly — either review it or reassign to another available reviewer |

The day-5 and day-7 reminders are automated: `sla-nag.yml` runs daily, comments on overdue `ready-for-review` issues, and mirrors the ping to Discord. It also nudges builders whose `needs-improvement` issues have been idle for 7 days. The clock starts when the issue enters its current state, so a resubmission is never counted against the previous review round.

The prerequisite queue protects builders from reviewer timing. A next-milestone issue must stay open while the previous review is pending. Deadline classification uses the issue's original creation time, remains informational, and does not block its release.

**If you cannot review a submission you've been assigned:**

- Post in the volunteer channel as early as possible so someone else can pick it up
- Do not leave it silent — a delayed handoff is better than a missed deadline

**For builders:** If your submission has been waiting more than 7 days with no verdict, post in the Discord community channel and tag your moderator.

---

## What Volunteers Do NOT Do

- Run live lectures or synchronous sessions
- Write code for Builders
- Remove a valid `late-submission` indicator or bypass the normal review checklist
- Ask builders to open replacement milestone issues; revisions belong on the canonical issue as `/recheck <40-character-hash>`
- Make unilateral changes to the curriculum repo

For curriculum changes, open a PR. For policy questions, raise it with the program lead.

---

*Systems Lead: Ray Cancino — for GitHub/infrastructure issues*
