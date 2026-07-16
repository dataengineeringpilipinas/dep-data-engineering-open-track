# Changelog

All notable curriculum-documentation changes in this repo should be recorded here.

## Unreleased

### Added

- Added explicit milestone workflow states for submissions waiting on prerequisites or ready for review, plus non-blocking late-submission metadata.
- Added automatic release of an M1–M6 submission when the same builder's previous milestone receives a human `passed` verdict.
- Added a maintainer dry-run/apply workflow for repair of historical gate-blocked submissions.
- Added policy tests for deadline boundaries, repository normalization, milestone sequencing, recheck commands, and state decisions.
- Added a default pull request template covering context, issue linkage, testing, rollout, screenshots, documentation, and privacy checks.
- Added a plain-language milestone pipeline guide so cohort mentors can answer common submission, recheck, prerequisite, and review-status questions consistently.

### Changed

- Changed milestone deadlines from a hard rejection gate to a visible `late-submission` indicator; late issues remain open and follow the normal evaluation and review path.
- Changed prerequisite gates to preserve and validate submissions instead of closing them; revisions now stay on the canonical issue through `/recheck <commit-hash>`.
- Changed milestone identity matching from repository URL text to the submitting GitHub account so repository renames do not break progression.
- Changed M0 to require a human verdict after structural checks instead of automatically applying `passed`.
- Updated the public submission tracker to include evaluated late submissions in queues and totals with a separate Late badge, while continuing to exclude duplicates and legacy late-only closures.

### Fixed

- Fixed the deadline conflict that rejected replacement issues after an on-time submission was auto-closed for a pending prerequisite.
- Fixed structural-check failures that instructed builders to recheck without adding the `needs-improvement` state required to trigger the recheck workflow.
- Fixed duplicate milestone attempts by directing builders back to one canonical issue per milestone.

## [0.3.0] - 2026-07-08 - Builder Cohort Dashboard and Timeline

### Added

- Added a public, sanitized builder cohort section to the GitHub Pages onboarding site with aggregate stats, status and phase distributions, milestone summary, and a searchable builder directory powered by `docs/data/builders.json`.
- Limited the builder directory preview to 10 cards by default, added an expand/collapse control, and changed empty aggregate progress metrics to subtle dash placeholders.
- Documented the Python local static-server command for previewing the GitHub Pages onboarding site without `file://` fetch issues.
- Added a milestone deadline timeline to the builder cohort dashboard with a current-date marker, Philippine-time deadline labels, and a live millisecond clock.

## [0.2.0] - CI Milestone Check Deadlines

### Added

- **Hard deadline enforcement**: All milestones now have hard deadlines configured in `.github/milestone-deadlines.json`. Submissions created past the deadline are auto-rejected with a clear message. Resubmissions (rechecks) also check the original issue's creation date against the deadline. Deadlines are enforced at the workflow level — no date-based logic exists in the milestone check scripts.

## [0.1.0] - CI Milestone Check fixes

### Fixed

- **Gate URL matching in milestone-check.yml**: Normalizes repo URLs to base `owner/repo` before comparing. Previously, if a builder pasted a blob/tree URL (e.g. `.../blob/main/file`) in the "GitHub Repo URL" field, the gate check would fail to find their passed M0 submission because the substring match used the raw (wrong) URL.
- **Clone URL normalization in milestone-recheck.yml**: Same normalization applied to repo URLs on resubmission so `git clone` works even when the original issue body has a blob/file URL.

### Added

- **URL pattern validation on all milestone issue templates (M0-M6)**: The "GitHub Repo URL" field now rejects blob/tree/file URLs with a clear mismatch message, guiding builders to enter the repo root URL.
- **Auto-apply `passed` label for M0**: When all M0 structural checks pass, the `passed` label is applied automatically. M0 checks are purely structural (README existence and content length), so no subjective review is needed — this removes the manual bottleneck before builders can proceed to M1.

## [0.0.7] - Organizing Team Pictures

### Added

- Added volunteer profile photos to the Organizing Team section in [docs/index.html](docs/index.html): 23 circular avatars (56 px) for 23 team members, sourced from `/Users/zeraphim/Desktop/Volunteer Pics` and served from `docs/assets/volunteers/`. Photos appear next to each name in their respective team-group cards with a hover accent effect matching the gold design tokens.

## [0.0.6] - Organizing Team update 

### Changed

- Updated the onboarding site registration CTAs to reflect that registration is closed, including the navbar button and hero button, plus a disabled/closed visual treatment in [docs/index.html](docs/index.html) and [docs/assets/site.css](docs/assets/site.css).
- Aligned the team section in [docs/index.html](docs/index.html) added Myk Ogbinar (Founder, DEP), Simonee Ezequiel (Communications), and Bea Lambitco (Content Curator). Renamed groups to Content Curators, Squad Team, and Mentors Team. Corrected role titles across Ops, Communications, Squad, and Mentors. Rebuilt the Admissions panel to match the documented crossover (Katherine Bulac, James David Bradly Carballo, Anam Iqbal). Removed Vanie Bermudez and Renan Matthew Fajardo.
- Further team adjustments: added Jomai Hizon and Kim Audrey Magan to Ops; removed Yui Otsuka and Renzi Vidal from Mentors Team; swapped Zierd Ethan for Vanie Bermudez in Squad Team; renamed Community to Moderators and added Renan Matthew Fajardo.
- Added Zierd Ethan and Andrei Marcus to Curriculum; removed Simonee Ezequiel from Communications.

## [0.0.5] - Site General Improvements

### Changed

- Refreshed the GitHub Pages onboarding site styling in [docs/](docs/): stronger editorial hierarchy, subtler canvas texture, layered card shadows, branded hero panel treatment, and DEP logo usage in the header.
- Expanded the visual language further with a dark hero, gold/navy accents, animated glow layers, and scroll-reveal cards across the onboarding page.
- Replaced the redundant hero fact panel with cohort-focused notes, improved output-card contrast, and widened the FAQ so questions no longer feel clipped.

## [0.0.4] - Submission System Design & Curriculum Restructure

### Added

- Added [CONTEXT.md](CONTEXT.md) defining domain terms and the full participant submission flow: Starter Kit, Milestone Submission (GitHub Issue), Auto-Check (GitHub Action), Milestone Reviewer verdict (`passed` / `needs-improvement`), and Resubmission model.

### Changed

- Restructured phase layout: Phase 2 trimmed to weeks 5–6; Phase 3 expanded to weeks 7–12 (SQL and data modeling moved from Phase 2).
- Moved `week-07` and `week-08` from `02-data-collection/` into `03-data-processing/`.
- Populated all 24 week READMEs with topics, primary and optional resources, build tasks, and deliverables.
- Rewrote Phase 5 as a conditional dual-path: Path A (predictive/ML) and Path B (advanced EDA and stakeholder track).
- Updated all phase READMEs with revised milestone timing, pass criteria, and gate enforcement.
- Updated `docs/MILESTONE_CHECKLIST.md` with hard gate notes on M0 and M1, revised milestone timing, and separate Path A / Path B criteria for M5.
- Updated tech stack diagram (SVG) with corrected week ranges, SQL added to Phase 3, scikit-learn added to Phase 5.
- Updated [README.md](README.md) to reflect Program Overview: added Program Design section (duration, weekly rule, design principles, resource rule, tool stack), split Phase 5 into separate Path A and Path B rows in the curriculum table, added analysis notebook to primary outputs, and fixed Starter Kit link to point to [cohorts/starter-kit/](cohorts/starter-kit/).
- Fixed [06-deployment/week-23/README.md](06-deployment/week-23/README.md) milestone label from `Milestone 5 / 6` to `Milestone 5` — week 24 is the sole M6 deliverable.

## [0.0.3] - Static Site Preliminary

### Added

- Added a dependency-free GitHub Pages onboarding site under [docs/index.html](docs/index.html), with static CSS and JavaScript assets in [docs/assets/](docs/assets/).
- Added cohort-facing sections for registration, program positioning, selection and onboarding flow, expected outputs, responsible AI use, organizing team, and FAQs.

## [0.0.2] - Leveraging AI Guide

### Added

- Added [docs/AI_GUIDE.md](docs/AI_GUIDE.md) as a cohort-facing reference for responsible AI use, example prompts, and assessment support.

### Changed

- Added AI support notes to [01-foundations/README.md](01-foundations/README.md) and [docs/FAQ.md](docs/FAQ.md).
- Added week-specific sample AI prompts to [01-foundations/week-01/README.md](01-foundations/week-01/README.md) through [01-foundations/week-04/README.md](01-foundations/week-04/README.md).

## [0.0.1] - Learner Support / Reference templates

### Added

- Added learner-facing guidance blocks to all weekly curriculum files from Week 1 through Week 24.
- Added a consistent `Learner Support` section structure to each weekly README:
  - `Starter Script / Template`
  - `How To Adapt This To Your Project`
  - `Definition of Done`
  - `Common Mistakes`
  - `If You're Stuck After 2 Hours`

### Changed

- Expanded [01-foundations/week-01/README.md](01-foundations/week-01/README.md) and [01-foundations/week-02/README.md](01-foundations/week-02/README.md) with problem-framing and data-source documentation templates.
- Expanded [01-foundations/week-03/README.md](01-foundations/week-03/README.md) with repo setup, folder structure, and first-commit guidance.
- Expanded [01-foundations/week-04/README.md](01-foundations/week-04/README.md), [02-data-collection/week-05/README.md](02-data-collection/week-05/README.md), and [02-data-collection/week-06/README.md](02-data-collection/week-06/README.md) with ingestion scaffolds for API, scraping, and manual-download paths.
- Expanded [03-data-processing/week-07/README.md](03-data-processing/week-07/README.md) through [03-data-processing/week-12/README.md](03-data-processing/week-12/README.md) with schema, SQL, transform, validation, and pipeline-run-order guidance.
- Expanded [04-analysis-and-insights/week-13/README.md](04-analysis-and-insights/week-13/README.md) through [04-analysis-and-insights/week-16/README.md](04-analysis-and-insights/week-16/README.md) with notebook outlines for summary statistics, charting, inference, and insight writing.
- Expanded [05-project-packaging/week-17/README.md](05-project-packaging/week-17/README.md) through [05-project-packaging/week-20/README.md](05-project-packaging/week-20/README.md) with learner scaffolds for both Path A (predictive) and Path B (non-predictive).
- Expanded [06-deployment/week-21/README.md](06-deployment/week-21/README.md) through [06-deployment/week-24/README.md](06-deployment/week-24/README.md) with dashboard planning, deployment, documentation-polish, QA, and demo-script support.

### Notes

- The added examples are scaffold-level only and use placeholders such as `<your_source_url>` and `<your_kpi_name>` so learners are guided without being handed finished project answers.
