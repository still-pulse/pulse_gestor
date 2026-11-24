# ADR-004: Language and naming standardization (Phase 1)

## Status

Accepted (2026-11-24).

## Context

The 10 Frappe apps of the set (`bhcl_site`, `rh_brasil`, `busca_cnpj`, `integracoes_customizadas`,
`assinatura_eletronica`, `clm`, `pdf_ocr`, `pulse_gestor`, `pulse_finance`, `pulse_process`) are being unified and
migrated from Frappe v15 to v16. Until now each app followed its own convention: documentation, comments and
identifiers in Portuguese, mixed ownership metadata (publisher, license and copyright citing a client brand) and
heterogeneous `required_apps`. The target standard is `clm/docs/naming-conventions.md` and
`clm/docs/fixtures-and-migrations.md` (in the `clm` repository). This ADR records what Phase 1 changed in
`pulse_gestor` and what was deliberately left for Phase 2. Phase 1 is limited to names and language; it changes no
behavior, no persisted data and no user-facing text.

## Decision

1. **English** for documentation, comments, docstrings, identifiers (functions, modules, variables, files) and commit
   messages. snake_case; classes PascalCase.
2. **pt-BR only for user-facing text**: `label`, messages passed to `_()` and `translations/pt-BR.csv`.
3. **ASCII-only names** for Reports, Print Formats and Workspaces (accents only in `label`). All existing ones already
   comply.
4. **Metadata**: publisher `StillPulse Tecnologia LTDA`; license `Proprietary` (`license.txt` shared with the other
   apps, `app_license = "Proprietary"`); copyright header `StillPulse Tecnologia LTDA and contributors`; the client
   brand BHCL is removed from metadata, copyright and docs.
5. **`required_apps`** as a uniform list of `org/repo@branch` strings (here `frappe/frappe@version-15`,
   `frappe/erpnext@version-15`, `still-pulse/clm@main`; already compliant).
6. **Rules for new code** are in `AGENTS.md` / `CLAUDE.md` ("Language and naming"): app prefix on new DocTypes and
   roles, Custom Fields on core DocTypes as `custom_pulse_gestor_<meaning>`, new patches as
   `sNN_<action_in_snake_case>`.
7. **Persisted names are not touched in Phase 1** (DocTypes, fieldnames, roles, record names, Custom Field names,
   stored strings): changing them needs idempotent patches and is Phase 2.

## What changed in this repository

### Modules

| Old | New |
| --- | --- |
| `pulse_gestor/telefone.py` | `pulse_gestor/phone.py` |
| `pulse_gestor/assinatura.py` | `pulse_gestor/signature_profiles.py` |
| `tests/test_email_vencimento.py` | `tests/test_expiry_email.py` |
| `tests/test_termo_responsabilidade.py` | `tests/test_responsibility_term.py` |

### Functions and constants (main ones)

| Old | New |
| --- | --- |
| `formatar_telefone`, `normalizar_telefone`, `validar_e_formatar_linhas` | `format_phone`, `normalize_phone`, `validate_and_format_rows` |
| `calcular_status`, `calcular_dias_para_vencimento`, `eh_pdf` | `calculate_status`, `calculate_days_to_expiry`, `is_pdf` |
| `STATUS_VALIDO` / `STATUS_VENCIDO` / `STATUS_SEM_VALIDADE` (names only; values unchanged) | `STATUS_VALID` / `STATUS_EXPIRED` / `STATUS_NO_EXPIRY` |
| `tasks.atualizar_status_documentos` | `tasks.update_document_statuses` |
| `tasks.enviar_avisos_vencimento_documentos` | `tasks.send_expiry_notices` |
| `tasks.corpo_email_vencimento` | `tasks.build_expiry_email_body` |
| `patrimonio.asset.validar_custodiante` | `patrimonio.asset.validate_custodian` |
| `buscar_membros`, `convocar(name, canal)` (whitelisted) | `fetch_members(members_doc)`, `send_convocation(name, channel)` |
| `obter_/buscar_protocolo_e_niveis(unidade, data)` | `resolve_/fetch_protocol_and_levels(unit, date)` |
| `obter_/buscar_vigencia_e_especialidades(unidade, data)` | `resolve_/fetch_validity_and_specialties(unit, date)` |
| `periodos_se_sobrepoem` | `periods_overlap` |
| `patrimonio.report.utils.buscar_ativos`, `colunas_do_ativo`, `resumo` | `fetch_assets`, `asset_columns`, `build_summary` |
| `setup.install.sincronizar_dias_alerta` | `sync_alert_days` |
| `setup.install.ensure_classificacao_import_permissions` | `ensure_classification_import_permissions` |
| `setup.install.backfill_cores_/tempos_classificacao_diaria` | `backfill_daily_classification_colors` / `_times` |
| `setup.install.ensure_ascii_indicadores_report` | `ensure_ascii_indicators_report` |
| `setup.install.ensure_comissoes_custom_blocks` | `ensure_committees_custom_blocks` |
| `signature_profiles.ensure_modelos_assinatura`, `ensure_modelo_convocacao` | `ensure_signature_templates`, `ensure_convocation_template` |
| `tests/site_setup.criar_campos_de_patrimonio` (and its `ci.yml` call, one line) | `create_asset_custom_fields` |
| Install constants (`INDICADORES_RELATORIO`, `COMISSOES_*`, `TOPO_NUMBER_CARDS`, ...) | `INDICATORS_REPORT`, `COMMITTEES_*`, `TOP_NUMBER_CARDS`, ... |

### Classes (signature profiles; `hooks.py` updated)

| Old | New |
| --- | --- |
| `PerfilReuniaoDeComissao` | `CommitteeMeetingProfile` |
| `PerfilTermoDoAtivo` | `AssetTermProfile` |
| `PerfilTermoDeMovimentacao` | `AssetMovementTermProfile` |
| `destinatario_membro` (recipient hook) | `member_recipient` |

DocType controller classes keep their names: Frappe requires them to match the DocType name.

### Number Card and dashboard methods (`comissoes/dashboard.py`)

| Old | New |
| --- | --- |
| `cartao_reunioes_proximas` | `card_upcoming_meetings` |
| `cartao_mandatos_a_vencer` | `card_expiring_terms` |
| `cartao_comissoes_sem_reuniao` | `card_committees_without_meeting` |
| `cartao_presenca_media` | `card_average_attendance` |
| `proximas_reunioes(limite)` | `upcoming_meetings(limit)` |
| `comissoes_em_atencao` | `committees_needing_attention` |

The four `method` values in `comissoes/number_card/*/*.json` and the JS callers (custom blocks, form scripts) were
updated accordingly.

### Documentation and metadata

- README, CHANGELOG, AGENTS.md, CLAUDE.md and the ADRs were translated to English; ADR files were renamed to English
  slugs keeping their numbers (`adr-001-minimum-read-access-on-linked-doctypes.md`,
  `adr-002-log-quality-and-readability.md`, `adr-003-lint-and-ci-standardization.md`).
- New `docs/dependencies.md` maps strong and weak dependencies.
- Publisher, license, `pyproject` and copyright headers aligned with the decision above.
- `send_convocation` now guards `integracoes_customizadas` with `frappe.get_installed_apps()` before importing it.

## Contracts kept in Portuguese (owned by other apps)

- `assinatura_eletronica` profile API: base class `PerfilAssinatura`, `Signatario`, `Destinatario`, methods
  `conteudo`, `signatarios`, `validar_solicitacao`, `resumo_publico`, `dados_verificacao`, `contexto_mensagem`,
  attributes `prefixo_arquivo`, `situacoes`, kwarg `aceita_eletronica`, and the hook keys
  `assinatura_eletronica_perfis` / `assinatura_eletronica_destinatarios`.
- `integracoes_customizadas`: `whatsapp.modelos.enviar_modelo(..., telefone=, email=, canal=, extra=)` and
  `whatsapp.conector.normalizar_numero_br`.
- Data contracts: the keys returned by `content()` of the profiles (persisted in the signature hash, including
  `controle_bhcl`), report filter and column fieldnames, and the `vermelho`/`amarelo`/`azul` severity values of the
  committees dashboard.

These change only in a coordinated change with the owning app.

## Risks

- **Bench not run.** No bench was available while doing this work. Validation was static: `ruff check`,
  `ruff format --check`, `compileall`, prettier on the JS, and `tests/test_static_references.py` (plain unittest: `self.x()`
  calls resolve to class members, every dotted `pulse_gestor...` string in hooks, Number Card JSON, JS and Python
  resolves, keyword arguments match in-repo signatures). The first pass only checked imports and hooks and missed
  internal method calls; a Graphify review found the orphan calls (`self._validar_lancamento_unico()` and similar),
  fixed afterwards together with this test. `tests/test_validate_flows.py` (validate() smoke tests of four
  controllers and the minutes signature content) was written but **not executed**, like the rest of the suite and
  `bench migrate`.
- **Number Card methods in the database.** The `method` of the four Committee Number Cards is stored in the database;
  the new values only reach it after `bench --site <site> migrate` (standard module files are re-synced). Until then,
  the cards call methods that no longer exist.
- **Renamed whitelisted methods** (`fetch_members`, `send_convocation`, `fetch_*_and_*`) have new argument names
  (`members_doc`, `channel`, `unit`, `date`, `limit`). Any external caller of the old paths breaks; none exists in the
  repositories of the set, but check custom Client Scripts or integrations on the sites.
- **Scheduler**: the daily job paths changed (`update_document_statuses`, `send_expiry_notices`); Frappe re-syncs
  Scheduled Job Types on migrate.

### Deployment plan

1. Deploy to staging, run `bench --site <site> migrate`, then `bench --site <site> run-tests --app pulse_gestor`.
2. Check manually: the four Committee Number Cards render; *Convocar membros* works; *Buscar Participantes*; the daily
   classification and daily visit forms load protocol/specialties; the Committees panel blocks; Asset print formats.
3. Production: back up, deploy, `bench migrate`, repeat the checks.
4. Rollback: revert the merge and run `bench migrate` again (no data or schema changed, so no data restore is needed).

## Phase 2 (out of scope here)

- DocTypes, modules and roles are in Portuguese and without the app prefix (e.g. `Reuniao de Comissao`,
  `Comissao Membro`, `Documentacao da Unidade`, `Classificacao de Risco Diaria`; modules `Documentacao da Unidade`,
  `Indicadores`, `Comissoes`, `Patrimonio`), as are their fieldnames and the folders derived from them. Renaming needs
  `pre_model_sync` patches with `frappe.rename_doc`, following the `clm` precedent.
- Report, Print Format and Workspace names are ASCII but in Portuguese and without a `Pulse Gestor` prefix.
- The five Custom Fields on `Asset`/`Location`, created by hand on the sites, do not follow
  `custom_pulse_gestor_<meaning>` and have accented fieldnames: `custom_número_de_controle_bhcl`,
  `custom_número_patrimônio_prefeitura`, `custom_utilização`, `custom_estado_de_conservação` and `custom_empresa`. The
  first two **contain BHCL in the name**. Renaming them needs a business decision (the number is a client concept)
  and a data-migrating patch; the code that reads them (reports, print formats, signature profiles, tests, CI
  `site_setup`) must change together.
- Stored strings, seeded Templates, Notification and Number Card names, and CSS classes (`pg-*`) remain in Portuguese.
