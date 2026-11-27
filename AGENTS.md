# Project memory of pulse_gestor

## Language and naming

Source of truth: [`clm/docs/naming-conventions.md`](https://github.com/still-pulse/clm/blob/main/docs/naming-conventions.md)
and [`clm/docs/fixtures-and-migrations.md`](https://github.com/still-pulse/clm/blob/main/docs/fixtures-and-migrations.md).

- Identifiers (functions, modules, variables, files), comments, docstrings, documentation and commit messages are
  written in **English** (snake_case; classes PascalCase). User-facing labels and messages stay pt-BR and are
  translated through `translations/`.
- New DocTypes carry the app prefix (`Pulse Gestor `), with the folder in snake_case. Roles created by the app are
  prefixed with the app name (`Pulse Gestor Manager`, `Pulse Gestor Viewer`).
- Reports, Print Formats and Workspaces have **ASCII-only** names (accents only in `label`).
- Custom Fields on `Employee`/`Designation` (and other core DocTypes) are `custom_pulse_gestor_<meaning>`.
- New patches are named `sNN_<action_in_snake_case>` in `pulse_gestor/patches/` (next free number), idempotent,
  registered in `patches.txt`; existing patches are never renamed or edited.
- Renames of persisted names (DocTypes, fieldnames, roles, record names, Custom Fields) are Phase 2 work and need
  their own patch. Today the legacy DocTypes, fieldnames and the Custom Fields on `Asset`/`Location` are still in
  Portuguese.

## App memory

- In this app, the unit is the ERPNext `Company` DocType. The `unidade` field of `Unidade Protocolo Vigencia` points to it.
- `Protocolo Nivel` is a child table of `Protocolo de Triagem`; it gets no navigation link of its own in the Workspace.
- A link card in a Workspace needs **two** parts: `Card Break` and `Link` rows in `links`, and a `type: "card"` block in
  `content` whose `card_name` equals the `Card Break` label. Shortcuts in `shortcuts` do not create the card.
- New navigable DocTypes must include full `System Manager` and `Administrator` permissions. In Workspaces with role
  restrictions, include both in `roles`. Child tables inherit the permissions of the parent DocType.
- After changing metadata or the Workspace, run `bench --site dev migrate` on the bench and check the record on the site.
  Isolated JSON files do not show up in the UI before migration.
- On already installed Workspaces, migration may keep the old `content` even when the app's JSON changed. For new
  required blocks, use an idempotent adjustment in `after_migrate` (like `ensure_pulse_gestor_workspace`) and check
  the `content` directly on the site.
- The Query Builder of this Frappe 15 validates DocType names as ASCII only; the names of the indicator DocTypes must
  stay free of accents.
- All technical identifiers of DocTypes, Reports and routes must use ASCII only, with no accents, cedilla or other
  special characters. This includes `name`/`report_name`, `frappe.query_reports` keys, `link_to` in the Workspace and
  directory names. Labels visible to the user may have accents. Check this rule before migrating new metadata.
- `Classificacao de Risco Diaria` resolves the protocol by the unit's validity period on the date and requires one row
  per level, in protocol order. The server recalculates the total and validates the quantities; the screen only
  anticipates the filling.
- `Protocolo Nivel` and `Classificacao Diaria Nivel` use `editable_grid=1`. The color is stored on the daily row when
  the entry is generated, and migration fills old rows without color using the protocol available at that moment.
- The Frappe grid reserves a final cell for each row's action, aligned with the settings icon in the header. When hiding
  the expand action, keep that cell empty; removing it misaligns the columns. For the colored strip, use an inner
  shadow instead of a border so the row width does not change.
- The Patrimonio reports (`Relacao de Ativos`, `Ativos por Localizacao`) use the `custom_empresa` field of `Location`, a
  Custom Field created on the site (not in the app's fixtures). The common query lives in `patrimonio/report/utils.py`;
  the location filter includes sublocations (lft/rgt).
- Custodian Responsibility Term: profiles `AssetTermProfile` (Asset, signed by the `custodian`) and
  `AssetMovementTermProfile` (Asset Movement, signed by each `to_employee`) in `signature_profiles.py`, with Templates
  seeded in `TEMPLATES`. The `Receipt` created by ERPNext when submitting the Asset is refused on movement: the initial
  custody is signed on the Asset itself. The Sheets (Fichas) remain the standard format; the Terms are the receipt format.

## Dependencies, version and documentation

- `required_apps = ["frappe/frappe@version-15", "frappe/erpnext@version-15", "still-pulse/clm@develop"]`. The Committees and
  Assets formats extend `clm_base.html`; the `Comissoes` and `Patrimonio` modules must remain in `PDF_ENGINE_MODULES`
  of `clm` (`clm/clm/services/pdf_engine.py`) and follow `docs/brand-manifesto.md` of `clm`.
- **Undeclared (weak) dependencies**: `assinatura_eletronica` (optional; `signature_profiles.py` imports inside `try`) and
  `integracoes_customizadas` (`phone.py` and the committee meeting import inside functions, guarded by
  `get_installed_apps()`). Full map: [docs/dependencies.md](docs/dependencies.md).
- `__version__` in `pulse_gestor/__init__.py` must match the tag (currently 1.0.2; no git tag exists in this checkout).
  Patches written before the `sNN_` convention use the `vX_Y_Z_` prefix and do not follow the app version.
- **A `feature/*` branch uses the `main` major + 1** (in force since 2026-11-01). Minor and patch run normally inside
  it: with `main` at `vX.Y.Z`, the feature starts at `v(X+1).0.0` and continues `v(X+1).0.1`, `v(X+1).1.0`... while on
  the branch. If `main` bumps its major, the feature bumps with it. Check the `main` version
  (`git show main:pulse_gestor/__init__.py`) and `git tag` before tagging, and never reuse an existing number.
- A request limited to README/CHANGELOG that says "do not commit" prevails over any commit and tag rule. Dependencies
  between apps and documentation progress: `../../CLAUDE.md`.

## Lint and pre-commit

- Run `pre-commit install` once after cloning the repository.
- CI (`.github/workflows/linter.yml`) runs pre-commit, semgrep and pip-audit on pull requests.
- Lint and CI decisions: [docs/adr-003-lint-and-ci-standardization.md](docs/adr-003-lint-and-ci-standardization.md).
