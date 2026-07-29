# Changelog

All notable changes to this repository are recorded here.

---

## [0.5.2] - 2026-07-29 — Short Commit Hash Support

### Fixed

- Fixed `/recheck` command ignoring comments that use a short (7-character) commit hash — GitHub's default link format. Both 7- and 40-character hashes are now accepted in `milestone-recheck.yml` and `_milestone-evaluate.yml`.
- Updated user-facing bot messages to remove the "40-character hash" instruction so builders are not asked to manually expand GitHub's default short hash.

---

## [0.5.1] - 2026-07-21 — Navbar Consistency

### Fixed

- Added missing Changelog nav link to `progress.html` and `ai-guide.html` so all four pages share an identical navigation bar.

---

## [0.5.0] - 2026-07-21 — Workflow Architecture Improvements

### Added

- Added `notify-reviewer.yml` — dedicated workflow that fires the Discord reviewer alert on the `ready-for-review` label event, replacing the inline Discord call in the evaluation pipeline.

### Changed

- Changed Discord notification to trigger from a label event rather than from inside the evaluation step — a Discord API failure can no longer affect evaluation state.
- Changed `milestone-repair.yml` excluded-issue list from a hardcoded `Set([60])` to an auditable `exclude_issues` workflow dispatch input (default `"60"`).
- Refactored `milestone-verdict.yml` — both verdict jobs now use a local `removeLabels` helper instead of repeating the try/catch removal loop inline.
- Documented `_milestone-evaluate.yml` monolith as an intentional architectural decision in `CONTEXT.md` (splitting deferred until submission volume justifies the job-overhead cost).

### Fixed

- Added cross-reference comments between `_milestone-evaluate.yml` and `milestone_policy.py` so the shared field-extraction regex cannot drift silently between the workflow JS and the Python test suite.

---

## [0.4.1] - 2026-07-21 — Reviewer Verdict & Site Updates

### Fixed

- Fixed reviewer `passed` verdict being stripped by the bot — reviewer verdict is now always final and overrides all automation guards.

### Added

- Added standalone changelog page at `docs/changelog.html` linked from the site nav.

---

## [0.4.0] - 2026-07-16 — Submission System Hardening

### Added

- Added reusable `_milestone-evaluate.yml` shared workflow — all evaluation logic (initial check and recheck) now delegates to a single callable workflow, eliminating duplicated code.
- Added `milestone-verdict.yml` — triggers on label events; handles `passed` (closes issue, unblocks waiting next-milestone submission) and `needs-improvement` (normalizes state labels).
- Added `milestone-repair.yml` — maintainer-only dry-run/apply workflow for consolidating and re-evaluating historical gate-blocked submissions in bulk.
- Added `milestone_policy.py` — pure Python helpers for deadline classification, milestone sequencing, recheck command parsing, and state decisions; independently testable with no GitHub API calls.
- Added `test_milestone_policy.py` — regression tests for all policy helpers.
- Added `waiting-on-prerequisite` label and state — submissions waiting for a previous milestone to pass now stay open and are re-evaluated automatically when the prerequisite is marked `passed`.
- Added `ready-for-review` label — replaces `auto-check-pending` as the post-check signal for reviewers; Discord notification fires only on transition to this state.
- Added `late-submission` label — informational metadata applied when a submission is created after the milestone target deadline; does not block evaluation or review.
- Added automatic duplicate detection — if a builder opens a second issue for the same milestone, the duplicate is closed and the builder is directed back to the canonical issue.
- Added `/recheck <hash>` command format — builders can now comment `/recheck <40-char-hash>` in addition to the legacy bare-hash format.
- Added concurrency groups per issue number to prevent race conditions between simultaneous workflow runs.
- Added pull request template covering context, issue linkage, testing, rollout, screenshots, documentation, and privacy checks.
- Added plain-language milestone pipeline guide (`docs/MILESTONE_PIPELINE_MENTOR_GUIDE.md`) for cohort mentors.

### Changed

- Changed milestone deadlines from hard rejection to a visible `late-submission` informational indicator — late issues remain open and follow the normal evaluation and review path.
- Changed prerequisite gates to preserve and validate submissions instead of closing them; revisions stay on the canonical issue via `/recheck`.
- Changed milestone identity matching from repository URL substring to the submitting GitHub account login — repository renames no longer break progression.
- Changed `passed` verdict to auto-close the issue as `completed` and automatically trigger re-evaluation of any waiting next-milestone submission from the same builder.

### Fixed

- Fixed the deadline conflict that rejected replacement issues opened after an on-time submission was auto-closed for a pending prerequisite.
- Fixed structural-check failures that instructed builders to recheck without adding the `needs-improvement` label required to trigger the recheck workflow.
- Fixed duplicate milestone attempts by directing builders back to one canonical issue per milestone instead of silently closing new ones.

---

## [0.3.1] - 2026-07-13 — Accessibility & Site Shell

### Added

- Added `docs/ai-guide.html` — styled standalone page for responsible AI guidance, linked from site nav.

### Changed

- Rebuilt `docs/progress.html` submission tracker on the shared site shell (shared nav, CSS, and JS assets) to match the main site design.
- Improved accessibility across the site: contrast ratios, keyboard navigation, ARIA labels, milestone clock behavior, and form semantics.
- Improved timeline marker and shared navigation across pages.

---

## [0.3.0] - 2026-07-08 — Builder Cohort Dashboard and Timeline

### Added

- Added public builder cohort section to the GitHub Pages site with aggregate stats, status and phase distributions, milestone summary, and a searchable builder directory powered by `docs/data/builders.json`.
- Added milestone deadline timeline with a current-date marker, Philippine-time deadline labels, and a live millisecond clock.
- Added `docs/data/milestone-deadlines.json` for deadline data shared between the site and CI.
- Limited the builder directory preview to 10 cards by default with an expand/collapse control.

---

## [0.2.0] - 2026-07-06 — CI Milestone Deadlines

### Added

- Added hard deadline enforcement via `.github/milestone-deadlines.json`; submissions created after the deadline are auto-rejected with a clear message referencing the deadline in Philippine time.
- Added deadline validation to the recheck workflow — resubmissions also check the original issue's creation date against the deadline.

---

## [0.1.0] - 2026-07-06 — CI Milestone Check Fixes

### Fixed

- Fixed gate URL matching in `milestone-check.yml` — normalizes repo URLs to `owner/repo` before comparing so blob/tree/file URLs no longer break prerequisite checks.
- Fixed clone URL normalization in `milestone-recheck.yml` — same normalization applied on resubmission so `git clone` succeeds even when the original issue body contains a non-root GitHub URL.

### Added

- Added URL pattern validation on all M0–M6 issue templates — the "GitHub Repo URL" field rejects blob/tree/file URLs with a clear mismatch message.

---

## [0.0.8] - 2026-07-05 — Submission System Improvements

### Added

- Added `enrolled-participants.json` allowlist with 33 confirmed GitHub usernames for cohort 2026-A.
- Added enrollment filter to Discord webhook notifications in both `milestone-check.yml` and `milestone-recheck.yml` — only enrolled participants trigger reviewer alerts.
- Added Non-Enrolled toggle to `docs/progress.html` dashboard so operators can view submissions from outside the enrolled cohort.
- Added behavioral test suite for `milestone_check.py` covering M0–M6 pass and fail cases.

### Changed

- Changed cohort field on all M0–M6 issue templates from free-text to a dropdown with `2026-A` and `Open Track` options to prevent freeform inconsistencies.
- Rewrote starter kit `README.md` Step 1 with beginner-friendly options: GUI upload (Option A) and Git command line (Option B).

### Fixed

- Fixed `milestone-check.yml` to auto-close the issue when the builder's repo cannot be cloned instead of prompting the builder to reopen.
- Fixed misleading clone-error message that suggested a resubmit path that does not exist for clone failures.

---

## [0.0.7] - 2026-06-23 — Submission Tracker Dashboard

### Added

- Added `docs/progress.html` — internal submission tracker dashboard reading the GitHub Issues API; shows pending, needs-improvement, and all-submissions tables with stats cards and milestone progress grid.
- Added search, milestone filter, status filter, and sortable column headers to the dashboard.
- Added days-waiting column with SLA breach indicators (⚠️ 3d, 🔴 5d).
- Added enrolled/all toggle button with dynamic cohort label sourced from `enrolled-participants.json`.
- Added mobile responsive layout for the dashboard.
- Added Discord webhook alerts to `#open-builders` when all auto-checks pass on a new submission.
- Added sequential milestone gate enforcement — M(n-1) must have `passed` label before M(n) is reviewed.
- Added recheck workflow (`milestone-recheck.yml`) for builder resubmissions via comment.
- Added volunteer profile photos (24 avatars) to the Organizing Team section.

---

## [0.0.6] - 2026-06-19 — Registration Closed

### Changed

- Updated site registration CTAs to reflect that registration is closed — navbar button and hero button show a disabled/closed visual treatment.

---

## [0.0.5] - 2026-06-14 — Site General Improvements

### Changed

- Refreshed GitHub Pages site styling: stronger editorial hierarchy, subtler canvas texture, layered card shadows, branded hero panel, and DEP logo usage.
- Replaced the redundant hero fact panel with cohort-focused notes; improved output-card contrast; widened the FAQ layout.
- Updated FAQ to align with the full question list.

---

## [0.0.4] - 2026-06-04 — Submission System Design

### Added

- Added `CONTEXT.md` defining domain terms and the full participant submission flow.
- Added M0–M6 GitHub issue templates with `auto-check-pending` label applied on open.
- Added `milestone-check.yml` GitHub Actions workflow for automated structural checks on submission.
- Added `milestone_check.py` with per-milestone check definitions (M0–M6).
- Added starter kit scaffold (`cohorts/starter-kit/`) with README, scripts, dashboard template, and GitHub Pages deployment workflow.

### Changed

- Restructured phase layout: Phase 3 expanded to weeks 7–12; SQL and data modeling moved from Phase 2.
- Updated phase READMEs with revised milestone timing, pass criteria, and gate enforcement.
- Rewrote Phase 5 as a conditional dual-path: Path A (predictive/ML) and Path B (advanced EDA and stakeholder track).
- Updated `docs/MILESTONE_CHECKLIST.md` with hard gate notes and separate Path A/B criteria for M5.

---

## [0.0.3] - 2026-05-29 — Static Site

### Added

- Added dependency-free GitHub Pages onboarding site at `docs/index.html` with sections for registration, program positioning, selection and onboarding flow, expected outputs, responsible AI, organizing team, and FAQs.

---

## [0.0.2] - 2026-05-29 — AI Guide

### Added

- Added `docs/AI_GUIDE.md` as a cohort-facing reference for responsible AI use, example prompts, and assessment support.
- Added AI support notes to `01-foundations/README.md` and `docs/FAQ.md`.
- Added week-specific sample AI prompts to Foundations week READMEs (weeks 1–4).

---

## [0.0.1] - 2026-05-26 — Learner Support Templates

### Added

- Added learner support blocks to all 24 weekly curriculum files (weeks 1–24) with Starter Script, How To Adapt, Definition of Done, Common Mistakes, and If You're Stuck sections.
- Added ingestion scaffolds for API, scraping, and manual-download paths.
- Added notebook outlines for summary statistics, charting, inference, and insight writing.
- Added dashboard planning, deployment, documentation-polish, QA, and demo-script support for Phase 6.
- Restructured curriculum phases and populated all week READMEs with revised content, tech stack diagram, and DEP branding.
