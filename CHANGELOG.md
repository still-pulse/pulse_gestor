# Changelog

Reconstructed from `git tag` and `git log` (read-only) and checked against the app files. Limits of what git allows:

- **Start of history:** the first commit is from 2026-08-17 (v0.1.0). The repository has **two roots**: the old
  branch's (`e1d6111`) and that of commit `2fa98f2` ("Merge pull request #3", 2026-09-28, no parent), a snapshot that
  recreated `main`. The snapshot line (`f17bb23` onwards) only joined the old branch (v0.10.0) through merge `f515085`
  (v0.10.2). Therefore `git merge-base` between the two lines does not exist.
- **Tags outside the history:** none. All tags are contained in HEAD (`git tag --no-merged HEAD` is empty). v0.10.0 is
  on the old branch, before the merge.
- **Out-of-order tags:** v0.1.5 (2026-09-21) was created after v0.2.9, on another line of work (Unit Documentation).
  v0.9.2 points to the same commit as v0.9.1.
- **Versions without a tag:** v0.2.4 and v0.2.5 (numbering jumps from v0.2.3 to v0.2.6); their entries come from the
  text of the old CHANGELOG, delivered in the v0.2.6 commit. Commits without a tag go in the entry of the next tag.
- **Dates:** those of the tags (or of the commit, when the tag is lightweight). Entries already in the previous
  CHANGELOG were kept, with the heading changed from the old format (`## [date] — version`) to the current one; those of
  v0.1.5, v0.2.8, v0.2.9, v0.9.2, v0.9.4 and v0.9.5, which were missing, were added from the subject and diff of the
  commits only.
- **Numbering inconsistencies:**
  - `__version__` (in `pulse_gestor/__init__.py`) differs from `app_version` (in `hooks.py`) in four tags: v0.1.5
    (0.1.4), v0.9.4 and v0.9.5 (0.9.3) and v0.10.1 (0.9.3, `chore: versão 0.10.1` only touched `hooks.py`). v0.10.2 and
    v0.11.0 carry both equal to the tag. On the v0.11 line: v0.11.1 and v0.11.2 (both 0.10.0); v0.11.3 (`__version__`
    0.11.3, hooks 0.10.0); v0.11.4 to v0.11.6 (`__version__` equal to the tag, hooks 0.11.0). Only v0.11.7 aligns both.
  - Patches use the `vX_Y_Z_` prefix only in part (`v0_2_6_*`, `v0_4_0_*`, `v0_9_0_*`, `v0_9_2_*`; the
    `rename_configuracoes_documentos_da_unidade` has no version), **do not follow the app version** and were not
    renumbered. New patches follow `sNN_<action_in_snake_case>`.
  - There are no patches for the v0.10 and v0.11 lines: the Workspace, print format and Template adjustments are done
    in `after_migrate` (`setup/install.py`).
- There are no `rc/*` tags in this repository.

## Unreleased

### Changed
- Naming and language standardization (Phase 1): identifiers, comments, docstrings and documentation in English. Python
  modules `telefone.py` and `assinatura.py` became `phone.py` and `signature_profiles.py`; functions, constants and
  profile classes were renamed (e.g. `PerfilReuniaoDeComissao` → `CommitteeMeetingProfile`, `PerfilTermoDoAtivo` →
  `AssetTermProfile`, `PerfilTermoDeMovimentacao` → `AssetMovementTermProfile`); the whitelisted methods
  `buscar_membros`, `convocar`, `buscar_protocolo_e_niveis`, `buscar_vigencia_e_especialidades` and the committee
  dashboard methods now have English names (JS callers and Number Cards updated). DocType names, fieldnames, roles,
  stored strings and user-facing texts are unchanged.
- Metadata: publisher `StillPulse Tecnologia LTDA`, proprietary license (`license.txt`, `app_license = "Proprietary"`),
  copyright headers without the client brand.
- ADR files renamed to English slugs (numbering kept).
- New ADR-004 recording the language and naming standardization; `tests/site_setup.py` function renamed to `create_asset_custom_fields` (and its `ci.yml` call).

### Added
- `docs/dependencies.md` mapping the strong and weak dependencies; the `integracoes_customizadas` use in the meeting
  convocation is now guarded by `get_installed_apps()`.

## v1.0.2 — WhatsApp enabled by default in signatures · 2026-11-20

- Follows `assinatura_eletronica` v0.3.9: the committee member no longer provides `aceita_whatsapp` (the engine default
  is enabled; without a phone the engine skips the channel) and the seeded Signature Template is born with
  `exigir_aceite_whatsapp = 1` ("Respect the disabling of WhatsApp sending"). Templates already created are adjusted by
  the engine's patch.

## v1.0.1 — frappe pinned in required_apps · 2026-11-02

- `required_apps` becomes `frappe/frappe@version-15`: the bare `"frappe"` resolved to the local app and made `bench
  get-app --resolve-deps` fail ("Invalid frappe path").

## v1.0.0 — Pinned dependencies · 2026-11-02

- `required_apps` becomes `["frappe", "frappe/erpnext@version-15", "still-pulse/clm@main"]` (`clm` without an org was
  looked up in `frappe/clm`).
- README: installation order with ERPNext on `version-15` and `clm` before the app.

## v0.11.7 — version alignment · 2026-10-29

Merge `d02b9d8` of `feature/configuracoes-documentos-unidade` into `main`, with commit `d63d20f`: the hooks'
`app_version` aligned with `__version__` (0.11.7) after the merge of the unit-document settings feature.

## v0.11.6 — Frappe check tools · 2026-10-28

Commit `e2d1488`: commitlint, linter and CI (`ci: ferramentas de checagem do Frappe`). No functional change.

## v0.11.5 — merge of the indicators and the expiry notice · 2026-10-28

Commit `3d6d5dd` ("merge das features de indicadores e aviso de vencimento em main"), which follows merge `9f090ea` of
`feature/indicadores-protocolos-triagem` and commit `c90856d` (expiry notice test adjusted to the institutional e-mail
layout).

## v0.11.4 — `__version__` and expiry notice version · 2026-10-28

Commit `2f0eac8` ("aligns `__version__` with tag v0.11.3 and versions the e-mail expiry notice"), preceded by `1591510`
("app_version 0.1.5 in the Unit Documentation hooks"), and merge `876224c` of branch `feature/bump-versao-0-11-4`.

## v0.11.3 — expiry e-mail notice in the clm layout · 2026-10-28

Commit `3b2a354` ("aligns `__version__` with tag v0.11.2"). The range includes commits `5e02f94` and `4d9e2e7`
(2026-10-24, "expiry e-mail notice in the clm institutional layout"): change in `tasks.py` and new test
`tests/test_email_vencimento.py`.

## v0.11.2 — clears the Desk cache when injecting the card · 2026-10-20

Commit `93da1d4`: `setup/settings_workspace.py` clears the Desk cache when injecting the card into ERPNext Settings.

## v0.11.1 — shortcut to the document settings in ERPNext Settings · 2026-10-20

Commit `ab6823d`: new `setup/settings_workspace.py` and call in `setup/install.py` for the shortcut to the document
settings in ERPNext Settings.

## v0.11.0 — Asset Reports and Responsibility Term · 2026-10-17

### Added
- "Relação de Ativos" and "Ativos por Localização" reports (Script Reports of the Patrimonio module, "Relatórios de Patrimônio" card in the Gestor Workspace). Filters by company and by location linked to the company (`Location.custom_empresa`), including sublocations, plus category, status, usage and condition. The by-location report groups the assets in a tree, with count, amounts and a chart of the locations with the most assets
- "Termo de Responsabilidade do Ativo" (Asset, signed by the custodian at initial custody) and "Termo de Responsabilidade de Movimentacao" (Asset Movement, signed by each employee in "Para Funcionário", who sees only their own assets), in the institutional standard and with the record of the signature evidence
- Profiles `PerfilTermoDoAtivo` and `PerfilTermoDeMovimentacao` in the `assinatura_eletronica` engine and Signature Templates seeded for Asset and Asset Movement (parallel, after submit, electronic acceptance, receipt in the Term format). The automatic receipt (Receipt) is refused on movement: initial custody is signed on the Asset itself
- Asset custodian filtered by active employees of the asset's company, with server-side validation

### Changed
- The "Term date" of the Asset Term and the issue date use the Asset's creation date
- `registro_assinaturas` uses its own date label in the finished-process card (it was fixed as "Data da reunião")
- `ensure_modelo_assinatura` became `ensure_modelos_assinatura`, with the templates in `MODELOS`

## v0.10.2 — Integration of the v0.10.0 line into main · 2026-10-16

### Changed
- Integrates the v0.10.0 line (Patrimonio module and print formats) into `main`, which had been recreated from a snapshot with no shared history. Minutes and Convocation keep the v0.10.0 macros (`commission_name`, `meeting_card`, `agenda_card`, `participants_card`), plus the electronic signature record of the minutes (`registro_assinaturas`: evidence when a finished Signature Process exists; otherwise, the standard card with the meeting date)

## v0.10.1 — Committee Print Formats in the institutional standard · 2026-10-16

### Changed
- `Ata de Reuniao de Comissao` and `Convocacao para Reuniao de Comissao` now extend `clm_base.html` (manifesto `apps/clm/docs/brand-manifesto.md`): cards, tables with a `teal_dark` header, attendance tags, reference "Committee · Meeting of dd/mm/yyyy" and footer with ID
- Minutes signature: with a finished Signature Process, prints the evidence record (OTP, IP, location, integrity and QR); otherwise, the standard `signature_block` card with the "Meeting date" box. The convocation uses the standard card with the "Convocation date"
- Own macros in `templates/print/comissoes_macros.html`; format folders renamed to `scrub(name)` (a Frappe requirement)
- `required_apps` includes `clm`

### Added (same commit, f17bb23)
- Signable minutes: profile `PerfilReuniaoDeComissao` in the `assinatura_eletronica` engine (the present participants sign) and `Comissao Membro` as recipient; Signature Template seeded in `after_migrate`. Optional dependency: `assinatura.py` imports the app inside `try`
- Convocation of participants through the *Convocar membros* button of the Reuniao de Comissao (WhatsApp, e-mail or both, with a seeded WhatsApp Template), via `integracoes_customizadas`; `telefone.py` applies the mask and validates the phones of member and participant rows

### Changed (same commit, f17bb23): everything in the Gestor Workspace
- The Indicadores, Comissoes, Documentacao da Unidade and Pulse Gestor Workspaces were removed; their cards (Unit Documentation, Triage, Visits, Indicator Reports, Committees, Committee Settings, Committee Reports) and the management panel now live in the Gestor Workspace
- App links versioned in `setup/gestor_links.json`; `ensure_pulse_gestor_workspace` (after_migrate) applies them to Gestor without changing the rest of the content and deletes the old Workspaces

## v0.10.0 — Assets and print formats in the institutional standard · 2026-10-14

> Tag outside the `main` line until v0.10.2: the commit belongs to the old branch, which was only joined to `main` by merge `f515085`.

### Added
- Patrimonio module with Print Formats in the institutional standard (`clm_base.html`, WeasyPrint engine): "Ficha do Ativo Imobilizado" (Asset) and "Ficha de Movimentacao de Ativos" (Asset Movement), set as the DocTypes' default through a Property Setter in after_migrate; the record's QR Code generated locally (Jinja method `qr_data_uri`), with no external service
- Standard and render tests of the Print Formats (`tests/test_print_formats.py`)

### Changed
- "Ata de Reuniao de Comissao" and "Convocacao para Reuniao de Comissao" rewritten on top of `clm_base.html` and the CLM macros (header, footer, cards, tables, attendance tags and standard signature card); the Minutes become the default format of Reuniao de Comissao
- The app now requires `clm` (`required_apps`), which provides the print base and the PDF engine (clm v0.1.95 or later)
- The old asset sheets, which existed only in the database ("Ficha de Ativo Imobilizado" and "Ficha de Movimentação de Ativos"), are disabled without being deleted; the accented one is renamed to "Ficha de Movimentacao de Ativos (antiga)" in before_migrate, because the database collation would confuse it with the new format

## v0.9.5 — README rewrite · 2026-10-13

### Changed
- Documentation only: `README.md` rewritten (commit `ec05776`). `__version__` stayed at 0.9.3.

## v0.9.4 — Version ranges in `pyproject.toml` · 2026-10-08

### Changed
- `[tool.bench.frappe-dependencies]` limits `frappe` and `erpnext` to `>=15.0.0,<16.0.0` and `pyproject.toml` gains comments about the bench-managed dependencies (commit `dd071d3`; lightweight tag, no annotation). `__version__` stayed at 0.9.3.

## v0.9.3 — Visits report renamed · 2026-09-28

### Changed
- Report "Atendimentos Medicos por Periodo" renamed to "Relatorio de Atendimentos por Periodo" (title "Relatório de Atendimentos por Período" via pt-BR.csv); the old record is removed by a patch
- The Indicadores Workspace gets the "Relatórios" card, with the Risk Classification Tally and the Visits Report by Period, which leave the Triage and Visits cards (idempotent adjustment in after_migrate)

### Fixed
- Classificacao de Risco Diaria: `atualizar_total` used the non-existent variable `line`, causing a ReferenceError when editing a quantity

## v0.9.2 · 2026-09-28

The tag points to the same commit as v0.9.1 (`ef699ce`, `__version__` 0.9.1); it carries no change of its own. Patch `v0_9_2_renomeia_relatorio_de_atendimentos` came out with v0.9.3.

## v0.9.1 — Specialties grid aligned · 2026-09-28

### Fixed
- The specialties grid of Atendimento Medico Diario was misaligned with the header: the final row-action cell is now kept empty, as in the other Indicators grids

## v0.9.0 — Daily medical visits by validity period · 2026-09-28

### Added
- Report "Atendimentos Medicos por Periodo": submitted visits per specialty in a period, with percentage, days with visits, daily average per entered day, summary and chart; link in the Visits card of the Indicadores Workspace

### Changed
- "Atendimento Diario" (and its child table) renamed to "Atendimento Medico Diario" by a pre-sync patch
- The specialties validity period now maps the specialties served by the unit in a period, like the triage protocol validity: the Sector field left the validity and the visit, and the lookup and entry uniqueness use only unit and date

### Removed
- Definition of goals per specialty (quantity and periodicity) in the validity and the visit; the old columns, including Sector, are removed from the database on migrate

## v0.8.1 — Committees panel without charts · 2026-09-28

### Removed
- Charts "Reuniões por mês", "Mandatos por status" and "Reuniões por unidade" of the Committees panel (also removed from the database on migrate)

## v0.8.0 — Committees management panel · 2026-09-28

### Added
- Management panel at the top of the Comissoes Workspace: cards (meetings in the next 7 days, terms expiring in 60 days, committees without a meeting for more than 90 days, terms in force, meetings in the month and average attendance of the last 90 days) and two blocks: "Próximas reuniões" and "Comissões que exigem atenção"
- Standard Number Cards and Dashboard Charts in comissoes/number_card and comissoes/dashboard_chart; data computed in comissoes/dashboard.py
- Custom HTML Blocks created/updated idempotently in after_migrate (source in comissoes/custom_blocks)

## v0.7.0 — Meeting date, time and place · 2026-09-28

### Added
- "Meeting place" field in the Reuniao de Comissao

### Changed
- "Meeting date" becomes "Meeting date and time" (Datetime); already registered meetings stay at 00:00
- Convocation and minutes print the time and place (the time is omitted when 00:00)
- The "Atividades de Comissão" report shows date and time and the place, and the period filter considers the whole day of the end date

## v0.6.0 — Meeting convocation and minutes · 2026-09-28

### Added
- Print formats of the Reuniao de Comissao: "Convocacao para Reuniao de Comissao" (date, time and place to fill in, agenda and summoned members) and "Ata de Reuniao de Comissao" (participants with attendance, agenda, resolutions, referrals and signatures of those present)

## v0.5.1 — Friendly names in the Committees report · 2026-09-28

### Changed
- The "Atividades de Comissão" report shows the category name, the committee name and the term (start and status) instead of IDs
- With the agenda included, the meeting data appears only on the first row; the other items show only the subject

## v0.5.0 — Atividades de Comissão report · 2026-09-28

### Added
- "Atividades de Comissão" report (Comissoes): meetings per period, with company and committee filters, present/participants per meeting and the option to include the agenda (one row per item)
- "Relatórios" card in the Comissoes Workspace

## v0.4.0 — Committee category, company and bylaws · 2026-09-28

### Added
- Categoria de Comissao (Council, Committee, Nucleus, Working Group etc.), linked to the Tipo de Comissao
- Bylaws text in the Tipo de Comissao, with change history (version, date, person responsible, reason and previous text); the reason is mandatory when changing an already saved bylaw

### Changed
- The company is now registered on the Tipo de Comissao; the Mandato de Comissao receives it from the type, read-only
- Categoria and Tipo de Comissao named by ID (CATCOM-/TPCOM-), showing the friendly name in link fields; type uniqueness becomes by name and company
- Migration copies the company from the terms to the type when the origin is unique

## v0.3.0 — Committees module · 2026-09-28

### Added
- Committees module as a subworkspace of Gestor: Tipo de Comissao, Mandato de Comissao, Membros de Comissao and Reuniao de Comissao (agenda, participants with attendance, resolutions and referrals)
- Copy of the committee members into the meeting's participant list
- pt-BR translation of the Workspace title, keeping the route in ASCII

### Changed (commits without a tag since v0.2.9)
- Indicadores Workspace organized as a subworkspace of Gestor (commit `0c086f7`)

## v0.1.5 — Configuracoes Documentos da Unidade · 2026-09-21

> Tag out of numeric order (created after v0.2.9), on commit `e8c70c6`; `app_version` in `hooks.py` is 0.1.5, but `__version__` stayed at 0.1.4.

### Added
- Single DocType `Configuracoes Documentos da Unidade` (renamed from `Configuracoes Pulse Gestor` by patch `rename_configuracoes_documentos_da_unidade`) with alert days, e-mail template and child table `Destinatarios Vencimento Documento` (e-mails per company)
- Validation: non-negative alert days, no repeated company, valid e-mails and mandatory template when there are recipients

## v0.2.9 — Chart per level in the risk tally · 2026-09-21

### Added
- The risk classification tally report now returns a chart (donut) per level

## v0.2.8 — Specialties and daily visits · 2026-09-18

### Added
- DocTypes `Especialidade`, `Unidade Especialidade Vigencia` (and the validity child table), `Atendimento Diario` and `Atendimento Diario Especialidade` (renamed to Atendimento Medico Diario in v0.9.0), with tests and a README section
- In this version the validity and the entry still had a sector and goals per specialty, removed in v0.9.0

## v0.2.7 — Risk classification tally · 2026-09-18

### Added
- Risk classification tally report per unit and period, with separate scales per protocol and target time
- Card with the total of patients classified in the period

### Changed
- Maximum waiting time preserved on the daily rows; migration fills the previous entries with the value available in the protocol

### Fixed
- Report identifier and route in ASCII, with the link updated in the Workspace and migration of the legacy name

## v0.2.6 — Indicator DocTypes without accents · 2026-09-18

### Changed
- Names of the indicator DocTypes without accents
- Daily classification records only the quantity classified per level
- Protocol levels keep color and maximum waiting time

## v0.2.5 — Direct editing in the indicator grids · 2026-09-18

> No tag and no commit of its own: the text came together with the v0.2.6 commit (`67ecb49`).

### Changed
- Direct editing of the levels in the protocol and of the quantities in the daily classification, without opening the overlay row
- Row highlighting by the protocol color, with a soft background and a side strip
- Level color preserved in the daily entries and filled in the previous records during migration
- Alignment of the rows with the grid header when hiding the expand action

## v0.2.4 — Daily risk classification entry · 2026-09-18

> No tag and no commit of its own: the text came together with the v0.2.6 commit (`67ecb49`).

### Added
- Daily risk classification entry, with protocol and levels filled in from the unit's validity period
- Calculated total, quantity validation and a submit that blocks editing
- Link to the entry in the **Triagem** card of the **Indicadores** Workspace

### Fixed
- Read and write compatibility of the indicator DocTypes in this bench's Query Builder
- Ordering of the validity-overlap query

## v0.2.3 — Triage link card · 2026-09-18

### Added
- Link card for the triage registries in the **Indicadores** Workspace
- Idempotent synchronization of the card in already installed Workspaces
- Memory of the app conventions in `AGENTS.md`

## v0.2.2 — Validity list ordering · 2026-09-18

### Fixed
- Listing of validity periods per unit with ordering compatible with Frappe 15's SQL validator

## v0.2.1 — Indicadores Workspace visibility · 2026-09-18

### Fixed
- Visibility of the **Indicadores** Workspace after installation or migration
- Full `System Manager` and `Administrator` permissions on the indicator registries
- Explicit access of these roles to the **Indicadores** Workspace

## v0.2.0 — Indicators and triage protocols · 2026-09-18

### Added
- **Indicadores** Workspace with triage protocols and validity periods per unit
- Configurable levels with color and maximum waiting time
- Validation of overlapping periods for each unit (`Company`)

## v0.1.4 — Unit Documentation card separated · 2026-08-17

### Fixed
- Documentation links leave the Patrimônio card and go to the **Documentação da Unidade** card

## v0.1.3 — Card in the Modules section · 2026-08-17

### Changed
- **Documentação da Unidade** card in the Modules section of the Gestor Workspace

## v0.1.2 — Shortcuts in the Gestor Workspace · 2026-08-17

### Changed
- Unit Documentation shortcuts now live in the **Gestor** Workspace
- Pulse Gestor Workspace hidden in the sidebar

## v0.1.1 — Workspace name fix · 2026-08-17

### Fixed
- The Workspace stopped using the same name as the DocType (the New button opened a Workspace)

## v0.1.0 — Unit Documentation · 2026-08-17

### Added

- `pulse_gestor` app with the Unit Documentation module
- `Tipo de Documento da Unidade` DocType for registering the PDF types
- `Documentacao da Unidade` DocType linked to the unit (`Company`)
- Optional validity, PDF attachment and status badge (Válido / Vencido / Sem validade)
- Notification for upcoming expiry and on the expiry day
- Daily job to update the status
- Workspace and roles Pulse Gestor Manager / Viewer
