# ADR-005 — Phase 2, wave 2: names of Reports, Print Formats and Number Cards

Status: proposed (merge needs L5).

## Decision

English names with the domain prefix `Gestor`, ASCII only; the pt-BR labels come from `translations/pt-BR.csv`.

| Kind | Old | New |
|---|---|---|
| Report | Apuracao de Classificacao de Risco | Gestor Risk Classification Tally |
| Report | Atividades de Comissao | Gestor Committee Activities |
| Report | Ativos por Localizacao | Gestor Assets by Location |
| Report | Relacao de Ativos | Gestor Asset List |
| Report | Relatorio de Atendimentos por Periodo | Gestor Visits by Period |
| Print Format | Ata de Reuniao de Comissao | Gestor Committee Meeting Minutes |
| Print Format | Convocacao para Reuniao de Comissao | Gestor Committee Meeting Notice |
| Print Format | Ficha de Movimentacao de Ativos | Gestor Asset Movement Sheet |
| Print Format | Ficha do Ativo Imobilizado | Gestor Fixed Asset Sheet |
| Print Format | Termo de Responsabilidade de Movimentacao | Gestor Movement Responsibility Form |
| Print Format | Termo de Responsabilidade do Ativo | Gestor Asset Responsibility Form |
| Number Card | Comissoes sem Reuniao Recente | Gestor Committees Without Recent Meeting |
| Number Card | Mandatos Vigentes | Gestor Active Mandates |
| Number Card | Mandatos a Vencer | Gestor Mandates Expiring |
| Number Card | PG Documentos Validos | Gestor Valid Documents |
| Number Card | PG Documentos Vencidos | Gestor Expired Documents |
| Number Card | PG Total Documentos | Gestor Total Documents |
| Number Card | Presenca Media | Gestor Average Attendance |
| Number Card | Reunioes no Mes | Gestor Meetings This Month |
| Number Card | Reunioes nos Proximos 7 Dias | Gestor Meetings Next 7 Days |

Patch `pulse_gestor.patches.s01_rename_reports_print_formats_and_cards` (`[pre_model_sync]`, idempotent) renames with
`frappe.rename_doc`, matching the old name exactly (the database collation ignores accents and case). The standard folders
and files of Reports and Print Formats follow `scrub(name)`. The default Print Format of `Asset` and `Asset Movement`
(a Property Setter) is rewritten by `print_formats.ensure_default_print_formats`; the DocType JSON of `Reuniao de Comissao`
carries its own default.

## Compatibility

No other repository of the set (nor `pulse_mobile`) references these names (grep). Saved Reports, Workflows, Server Scripts,
Notification templates and bookmarks of a site are not rewritten by `rename_doc`: check them on staging. Report URLs change
(`/app/query-report/<name>`).

## Verification (faithful baseline: production code migrated to `develop` plus this change)

- [x] L0 ruff check/format, compileall, JSON parse.
- [x] L2 new site with the repo's CI prep: 56 tests OK (3 skipped), same count as before.
- [x] L3 all 20 objects: old name gone, new name present; Has Role of each Report preserved (4 each); default Print Formats of
  `Asset` and `Asset Movement` point to the new names.
- [x] L4 second migrate identical; restore of the baseline backup identical to "before".
- [ ] L5 staging: **not executed**. The production Workspace links to these Reports/cards (`setup/gestor_links.json`) were not
  present on the baseline site, so their migration was not observed.
