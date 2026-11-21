# ADR-003: Lint and CI standardization

## Status

Accepted (2026-11-21).

## Context

The 10 Frappe apps of the set (`bhcl_site`, `rh_brasil`, `busca_cnpj`, `integracoes_customizadas`,
`assinatura_eletronica`, `clm`, `pdf_ocr`, `pulse_gestor` and the others) are being prepared for unification and for
the v15 -> v16/v17 migration. The apps diverged in lint and CI (Python version, ruff rules and versions, ignores,
pre-commit excludes, ESLint globals), which makes it harder to review and move code between them. This ADR records the
adopted standard, without changing logic or runtime behavior.

## Decision

1. **Python 3.11** in CI, `target-version = "py311"` and `requires-python = ">=3.11"` (target to be reviewed for v16).
2. **ruff pinned at v0.16.10** via `ruff-pre-commit`, rules `F, E, W, I, UP, B, RUF` and an `ignore` list identical to
   CLM's.
3. **pyupgrade covered by ruff's `UP` rule**, with no separate hook.
4. **F401 is not ignored**: dead imports are removed; re-exports and side-effect imports are kept with
   `# noqa: F401  # <reason>`. User-visible strings with an ambiguous unicode character get `# noqa: RUF001` instead of
   changing the text.
5. **prettier 2.7.1 and eslint 8.44.0 kept**: the upgrade was postponed so as not to mix it with the standardization;
   review when preparing for v16/v17.
6. **Pre-commit excludes** are always paths of the repository itself; dead entries were removed, without widening the
   ignored scope.
7. **ESLint globals** declared in `.eslintrc` with minimal scope. In this repo: `root_element` (variable injected by
   Frappe into a Custom HTML Block) as `readonly`, in `overrides` restricted to `**/custom_blocks/**/*.js`. No
   app-namespace global was needed.
8. **JS files with Jinja** are excluded from prettier/eslint by exact path. In this repo: none.
9. **JS formatted by prettier in a style-only commit.** In this repo: 5 files.
10. **pip-audit runs only in CI and audits only the `pyproject`**; the `erpnext`/`hrms` dependencies are commented
    out, so coverage is small (see Open items).
11. **commitlint kept** and `pre-commit install` documented in `AGENTS.md`.
12. **No tag or `__version__` change** in this standardization.

## Consequences

- Lint, formatting and CI behave the same across the apps, making unification easier.
- Dead imports are no longer tolerated; re-exports need an explicit justification in the `noqa`.
- Upgrades of prettier/eslint require a round of their own, with possible JS reformatting.
- The current pip-audit gives a false sense of coverage, since it does not audit the Frappe/ERPNext/HRMS dependencies.

## Open items

- Review the Python target (`py311`) and the prettier/eslint versions when preparing for v16/v17.
- Extend pip-audit to cover the dependencies actually installed (currently commented out in the `pyproject`).

## State of this repository

| Item | State |
| --- | --- |
| F401 | 0 occurrences removed or kept (`fix: corrigir erros do ruff check` only handled import ordering, `zip(strict=True)`, an unused variable and one `noqa: RUF001`) |
| Excludes changed | prettier and eslint: removed `pulse_gestor/public/dist`, `cypress`, `pulse_gestor/templates/includes` and `pulse_gestor/public/js/lib` (non-existent paths); kept `node_modules` and `boilerplate` |
| ESLint | `root_element` override in `**/custom_blocks/**/*.js` |
| JS with Jinja | none |
| JS formatted by prettier | 5 files |
| Final pre-commit result | all hooks pass (`SKIP=commitlint pre-commit run --all-files`) |
