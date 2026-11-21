# Pulse Gestor (`pulse_gestor`)

Frappe/ERPNext app for unit management, with four areas: **Unit Documentation** (Documentação da Unidade),
**Indicators** (triage and medical visits), **Committees** (Comissões) and **Assets** (Patrimônio: asset printouts and
reports). In all of them, the *unit* is ERPNext's `Company` DocType. Registries and reports live in the **Gestor**
Workspace.

Repository: [still-pulse/pulse_gestor](https://github.com/still-pulse/pulse_gestor)

Current version: **1.0.2** (`pulse_gestor/__init__.py` and `hooks.py`). History in [CHANGELOG.md](CHANGELOG.md).

## Features

### Unit Documentation

- **Tipo de Documento da Unidade** (unit document type): registry of the document types required from units.
- **Documentacao da Unidade**: a document per unit, with a PDF attachment and optional validity. The status is
  `Válido` (valid), `Vencido` (expired) or `Sem validade` (no expiry), with a count of days to expiry.
- **Daily jobs**: recompute the status and days to expiry and queue e-mail notices at the configured lead time. The
  e-mail body uses the institutional layout of `clm` (`clm.clm.services.email_layout`), with the "Abrir documento"
  (open document) button, unless the Email Template already comes in that layout (`is_branded`).
- **Configuracoes Documentos da Unidade** (settings): alert days, e-mail template and recipients per company. A
  "Pulse Gestor" card in the **ERPNext Settings** Workspace leads to them (`setup/settings_workspace.py`, applied in
  `after_migrate`; the Gestor Workspace is restricted, ERPNext Settings is not).
- `Documento da Unidade a Vencer` and `Documento da Unidade Vencido` Notifications, and Number Cards (total, valid and
  expired) in the Workspace.

### Indicators

- **Triage**: **Protocolo de Triagem** (triage protocol) with levels (color and time of each scale, child table
  *Protocolo Nivel*) and **Unidade Protocolo Vigencia**, which associates each unit with a protocol per period. End
  dates are inclusive, an empty end date means an open-ended period and periods of the same unit cannot overlap.
- **Classificacao de Risco Diaria** (daily risk classification): entry of patients classified by level, per unit and
  date. The server resolves the protocol in force, requires one row per level in protocol order and recalculates the
  total. Allows **bulk import** through Data Import.
- **Medical visits**: **Especialidade**, **Unidade Especialidade Vigencia** (specialties served by the unit in a
  period) and **Atendimento Medico Diario** (quantity per specialty, submittable, one non-cancelled entry per unit and
  date).
- **Reports**: *Apuracao de Classificacao de Risco* and *Relatorio de Atendimentos por Periodo* (totals per specialty,
  percentage, days with visits, daily average per entered day and chart). Only submitted entries count in the tallies.

### Committees

- **Categoria de Comissao**, **Tipo de Comissao** (company, bylaws with change history and a mandatory reason when
  changing) and **Mandato de Comissao** (period and status).
- **Membros de Comissao** per term and **Reuniao de Comissao** with agenda, participants and attendance, resolutions
  and referrals; the participant list can be copied from the members.
- **Convocation** through the meeting's *Convocar membros* button, by WhatsApp, e-mail or both, according to each
  participant's preferred channel. Requires the `integracoes_customizadas` app (see *Requirements*).
- **Signable minutes**: with the `assinatura_eletronica` app, the present participants sign the minutes through the
  signature engine (`CommitteeMeetingProfile` profile, Signature Template seeded in `after_migrate`). When a finished
  Signature Process exists, the minutes print the evidence record.
- **Print formats** in the institutional standard: *Convocacao para Reuniao de Comissao* and *Ata de Reuniao de
  Comissao* (the DocType default).
- **Report** *Atividades de Comissao* (meetings per period, attendance and optional agenda).
- **Management panel** in the Workspace: meetings in the next 7 days, terms expiring in 60 days, committees without a
  meeting for more than 90 days, terms in force, meetings in the month and average attendance, plus the blocks
  *Próximas reuniões* and *Comissões que exigem atenção*.

### Assets (Patrimonio)

The **Patrimonio** module creates no DocTypes: it extends ERPNext's `Asset` and `Asset Movement`.

- **Print formats** (institutional standard, WeasyPrint engine): *Ficha do Ativo Imobilizado* and *Ficha de
  Movimentacao de Ativos*, set as the DocTypes' default in `after_migrate`; *Termo de Responsabilidade do Ativo* and
  *Termo de Responsabilidade de Movimentacao*, used as the signature receipt. The record's QR Code is generated
  locally (Jinja method `qr_data_uri`).
- **Reports** (Script Reports on `Asset`): *Relacao de Ativos* and *Ativos por Localizacao* (assets grouped in a tree,
  with count, amounts and chart). They filter by company, location (including sublocations), category, status, usage
  and condition. The location's company comes from the `custom_empresa` field of `Location`, a Custom Field created on
  the site, which is **not** in the app's fixtures.
- **Custodian**: on the `Asset`, only active employees of the asset's company (filter in `public/js/asset.js`), with
  server-side validation (`validate_custodian`, `validate` event).
- **Electronically signed terms**: with the `assinatura_eletronica` app, the custodian signs the Term at initial
  custody, on the `Asset` itself (`AssetTermProfile`), and each employee in *Para Funcionário* signs the Term of the
  `Asset Movement` (`AssetMovementTermProfile`). The receipt (`Receipt`) created by ERPNext when submitting the Asset is
  refused on movement, so the signature is not duplicated.

### Gestor Workspace

The app's cards live in a single Workspace, **Gestor**: Unit Documentation, Triage, Visits, Indicator Reports,
Committees, Committee Settings, Committee Reports and Asset Reports, plus the management panel on top. The links come
from `pulse_gestor/setup/gestor_links.json` and are applied by `after_migrate` (`ensure_pulse_gestor_workspace`), which
also deletes the old Workspaces `Pulse Gestor`, `Indicadores`, `Comissoes` and `Documentacao da Unidade`. The `Gestor`
Workspace is **not created by this app**: if it does not exist on the site, nothing is applied.

## Roles and permissions

| Role | Access |
| --- | --- |
| `Pulse Gestor Manager` | Registration, editing and bulk import |
| `Pulse Gestor Viewer` | Read-only |
| `System Manager` / `Administrator` | Full access to DocTypes and Workspaces |

## Requirements

- Frappe v15 and ERPNext v15.
- `clm` app: `required_apps = ["frappe/frappe@version-15", "frappe/erpnext@version-15", "still-pulse/clm@main"]`. The
  print formats extend `clm/templates/print/clm_base.html` (macros, brand manifesto in `clm/docs/brand-manifesto.md`)
  and the PDF comes from the `clm` engine, which only serves the modules listed in `PDF_ENGINE_MODULES`
  (`apps/clm/clm/clm/services/pdf_engine.py`). `Comissoes` and `Patrimonio` are already on that list. Install `clm`
  before `pulse_gestor`.
- Existing `Gestor` Workspace on the site (see *Gestor Workspace*).
- E-mail queue configured for the expiry notices.
- **Optional, not declared in `required_apps`** (map in [docs/dependencies.md](docs/dependencies.md)):
  - `assinatura_eletronica`: signature of the minutes and the Responsibility Terms. `signature_profiles.py` imports the
    app inside `try`; without it, the profiles are not defined and nothing is seeded.
  - `integracoes_customizadas`: WhatsApp/e-mail convocation (`Modelo WhatsApp`) and phone normalization. The imports
    stay inside functions and are guarded by `get_installed_apps()`; without the app, *Convocar membros* answers with an
    error.

## Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app erpnext --branch version-15
bench get-app still-pulse/clm --branch main
bench get-app still-pulse/pulse_gestor --branch main
bench --site <site> install-app erpnext clm pulse_gestor
bench --site <site> migrate
```

Assign the **Pulse Gestor Manager** or **Pulse Gestor Viewer** role to users. Then, in *Configuracoes Documentos da
Unidade*, set the alert days, the e-mail template and the recipients.

## Usage: daily medical visits

1. **Especialidade**: register each specialty once.
2. **Unidade Especialidade Vigencia**: choose the unit, the period and the specialties served in it.
3. **Atendimento Medico Diario**: enter unit and date; the app loads the specialties in force and you only fill in the
   **Quantidade**. Use **Submit** to finish the entry.

## Usage: bulk import of the risk classification

In the **Classificacao de Risco Diaria** list, use **Import** and download the Data Import template. Enter **Unidade**
and **Data** on the first row of each entry and fill the **Níveis classificados** table with one row per level, in the
order of the protocol in force. Check **Submit after import** to include the entries in the tallies.

## Development

Counts from `git ls-files`: 23 DocTypes (14 standalone, 1 of them Single, and 9 child tables), 5 Script Reports, 6 print
formats, 6 Committee Number Cards (`comissoes/number_card`) and 3 Documentation ones (`fixtures/number_card.json`),
2 daily jobs, 7 patches and 46 tests in 11 files.

```text
pulse_gestor/
├── hooks.py · modules.txt · patches.txt
├── documentacao_da_unidade/   # 4 DocTypes (1 Single, 1 child)
├── indicadores/               # 10 DocTypes, 2 reports
├── comissoes/                 # 9 DocTypes, report, 2 formats, Number Cards, custom_blocks (panel)
├── patrimonio/                # 2 reports (and report/utils.py), 4 formats, asset.py (custodian)
├── signature_profiles.py      # assinatura_eletronica engine profiles, seeded Templates (optional)
├── print_formats.py           # default and legacy formats, qr_data_uri
├── phone.py                   # phone mask and validation
├── tasks.py                   # scheduled jobs (daily)
├── utils.py                   # status and expiry calculation
├── setup/                     # install.py (after_install/after_migrate), settings_workspace.py, gestor_links.json
├── public/js/asset.js         # custodian filter
├── templates/print/           # comissoes_macros.html, patrimonio_macros.html
├── patches/ · fixtures/ · translations/pt-BR.csv
└── tests/                     # print formats, status, terms, expiry e-mail
```

Project conventions (language and naming, ASCII technical identifiers, Workspaces and migration) are in
[AGENTS.md](AGENTS.md). After changing metadata or Workspaces, run `bench --site <site> migrate`.

### Tests

From the bench root:

```bash
bench --site <site> run-tests --app pulse_gestor
```

There are 13 test modules (`git ls-files`): 4 in `pulse_gestor/tests/` and the rest next to the DocTypes and reports.
The repository also has `.github/workflows/` (`ci.yml` runs the tests; `linter.yml` runs commitlint, pre-commit and
Semgrep, on PRs only), `.pre-commit-config.yaml`, `.eslintrc` and `commitlint.config.js` (conventional messages).

## Documentation

- [CHANGELOG.md](CHANGELOG.md): version history and git limits.
- [AGENTS.md](AGENTS.md): conventions, Workspace, Responsibility Terms and dependencies.
- [docs/dependencies.md](docs/dependencies.md): strong and weak dependencies of the app.
- [docs/adr-001-minimum-read-access-on-linked-doctypes.md](docs/adr-001-minimum-read-access-on-linked-doctypes.md):
  guaranteed minimum read access for the app's roles on DocTypes of other modules referenced by Link.
- [docs/adr-002-log-quality-and-readability.md](docs/adr-002-log-quality-and-readability.md):
  log standard for external integrations (structured context, no secrets in clear text, error classification,
  grouping per run).
- [docs/adr-003-lint-and-ci-standardization.md](docs/adr-003-lint-and-ci-standardization.md): lint and CI decisions.

## License

Proprietary — StillPulse Tecnologia LTDA (see [license.txt](license.txt)).
