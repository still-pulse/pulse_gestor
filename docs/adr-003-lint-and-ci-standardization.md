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

1. **Python 3.11 floor** (`target-version = "py311"`, `requires-python = ">=3.11"`), kept due to a production
   constraint. Production and staging are confirmed on **Python 3.12**; `ci.yml` now runs 3.12 to reflect
   production (the previous 3.14 is incompatible with Frappe v15: `freezegun`, used by the ERPNext tests, breaks at
   collection with `AttributeError: module 'uuid' has no attribute '_load_system_functions'`, which left Run Tests red
   on `main`). `linter.yml` stays on 3.11 (the floor). The Frappe v16 migration target is `>=3.13`
   (`target-version = "py313"`, `requires-python = ">=3.13"`, with `linter.yml` and `ci.yml` consistent), to be done
   at the migration, not before.
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

## Semgrep exception

`pulse_gestor/patches/v0_2_6_rename_indicadores_doctypes.py` gets `# nosemgrep: frappe-monkey-patching-not-allowed` on
the `import` line (semgrep reports the match from the import up to the assignment). It is a one-off historical patch
that temporarily swaps `builder.TABLE_NAME_PATTERN` to rename DocTypes with accents and restores the value in
`finally`; Frappe 15 offers no hook for this. Approved by the repository owner. The finding only appeared because
`semgrep ci` is diff-aware and `ruff --fix`/`format` rewrote the file.

### `frappe-sql-format-injection` findings in patches

`patches/v0_2_6_remove_triagem_fields.py` and `patches/v0_9_0_remove_metas_e_setor_especialidades.py` build
`ALTER TABLE ... DROP COLUMN` with an f-string and `frappe.db.sql`. The table and column names are constants of the
patch itself (no external input) and SQL identifiers do not accept parameters, so the finding is a false positive.
Decision: keep `frappe.db.sql` as in `main` and suppress with `# nosemgrep: frappe-sql-format-injection` on the line
immediately before the call, with a comment giving the justification. Replacing it with `frappe.db.sql_ddl` was
discarded: it would only work around the rule, without reducing risk, and would add an explicit commit to the patch.
The `has_column` guard keeps it idempotent. Semgrep with `frappe/semgrep-rules`: 2 findings without the suppression,
0 with it.

### Asset tests in CI

`install-app` does not run `after_migrate`; `after_install` now also calls `ensure_print_formats`, which sets the
default format of `Asset` and `Asset Movement` on new sites. The Asset Custom Fields (`custom_empresa` on `Location`
and four fields on `Asset`) exist only in production, created by hand; `ci.yml` creates them on the test site through
`pulse_gestor.tests.site_setup`, without changing production behavior.

## Open items

- Migrate to Python `>=3.13` together with v16 and review the prettier/eslint versions when preparing for v16/v17.
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
