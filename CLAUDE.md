# Claude Code instructions for this repo

## After every commit

Always update the changelog immediately after staging and committing changes:

1. Add a new version entry to **`CHANGELOG.md`** at the top (below the header, above the previous version).
2. Add the matching HTML block to **`docs/changelog.html`** — insert it before the previous version's `<!-- x.y.z -->` comment.
3. Include the new changelog files in the same commit, or commit them immediately after.

### Version number convention

- **Patch** (0.x.Y): bug fixes, wording changes, minor corrections
- **Minor** (0.X.0): new features, new workflows, new pages, meaningful behaviour changes
- **Major** (X.0.0): breaking changes to the submission flow that require builder action

### Entry format (CHANGELOG.md)

```markdown
## [x.y.z] - YYYY-MM-DD — Short Title

### Added
- …

### Changed
- …

### Fixed
- …
```

Omit sections that have no entries.

### Entry format (docs/changelog.html)

Copy the pattern of the entry directly above. Use `cl-group-label added/changed/fixed` for each section. Insert before the previous version's `<!-- x.y.z -->` comment and add a `<hr class="cl-divider" />` between versions.

---

## General

- Never add `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>` (or any Claude co-author line) to any commit message.
- Prefer editing existing files to creating new ones.
- Do not push to remote unless the user explicitly asks.
