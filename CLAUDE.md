# pulse_gestor

The rest of the repository instructions is in `AGENTS.md` (including the "Language and naming" section). Versioning rule:

- **A `feature/*` branch uses the `main` major + 1** (in force since 2026-11-01). Minor and patch run normally inside
  it: with `main` at `vX.Y.Z`, the feature starts at `v(X+1).0.0` and continues `v(X+1).0.1`, `v(X+1).1.0`... while on
  the branch. If `main` bumps its major, the feature bumps with it. Check the `main` version
  (`git show main:pulse_gestor/__init__.py`) and `git tag` before tagging, and never reuse an existing number.

## Language and naming

Source of truth: [`clm/docs/naming-conventions.md`](https://github.com/still-pulse/clm/blob/main/docs/naming-conventions.md).

- Identifiers, documentation, comments, docstrings and commit messages in **English**; user-facing labels in pt-BR
  (`label`, `translations/`).
- DocTypes carry the app prefix; Reports, Print Formats and Workspaces use ASCII-only names.
- Custom Fields on `Employee`/`Designation` (and other core DocTypes) are `custom_pulse_gestor_<meaning>`.
- New patches are `sNN_<action_in_snake_case>`, registered in `patches.txt`; roles created by the app carry the app prefix.

## Git tags in cloud agent sessions

Agents running in a Claude Code cloud session cannot push git tags: the egress proxy answers `HTTP 403` (verified
2026-11-26; branch pushes work). It is a policy denial: do not retry or route around it. Commit and push the branch,
update `__version__` only when the task asks, and report once that the tag is pending. A human creates the tag
(`git tag vX.Y.Z && git push origin vX.Y.Z` from a normal machine, or a GitHub release). Details:
`pulse_platform/docs/handoff-dev-data.md`.
