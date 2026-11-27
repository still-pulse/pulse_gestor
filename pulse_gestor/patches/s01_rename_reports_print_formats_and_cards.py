"""Phase 2, wave 2: English prefixed names for the Reports, Print Formats and Number Cards of the app.

Runs in [pre_model_sync] so the standard files (already moved to the new names) sync onto the renamed records instead of
creating duplicates. ``frappe.rename_doc`` rewrites the links (Has Role, Workspace links and number cards, Custom DocPerm);
it does not rewrite Property Setter values: the default Print Format of a DocType comes from the DocType JSON on sync.
Idempotent: a step runs only when the old name exists exactly (the database comparison ignores accents and case) and the
new one does not.
"""

import frappe

RENAMES = (
	("Report", "Apuracao de Classificacao de Risco", "Gestor Risk Classification Tally"),
	("Report", "Atividades de Comissao", "Gestor Committee Activities"),
	("Report", "Ativos por Localizacao", "Gestor Assets by Location"),
	("Report", "Relacao de Ativos", "Gestor Asset List"),
	("Report", "Relatorio de Atendimentos por Periodo", "Gestor Visits by Period"),
	("Print Format", "Ata de Reuniao de Comissao", "Gestor Committee Meeting Minutes"),
	("Print Format", "Convocacao para Reuniao de Comissao", "Gestor Committee Meeting Notice"),
	("Print Format", "Ficha de Movimentacao de Ativos", "Gestor Asset Movement Sheet"),
	("Print Format", "Ficha do Ativo Imobilizado", "Gestor Fixed Asset Sheet"),
	("Print Format", "Termo de Responsabilidade de Movimentacao", "Gestor Movement Responsibility Form"),
	("Print Format", "Termo de Responsabilidade do Ativo", "Gestor Asset Responsibility Form"),
	("Number Card", "Comissoes sem Reuniao Recente", "Gestor Committees Without Recent Meeting"),
	("Number Card", "Mandatos Vigentes", "Gestor Active Mandates"),
	("Number Card", "Mandatos a Vencer", "Gestor Mandates Expiring"),
	("Number Card", "PG Documentos Validos", "Gestor Valid Documents"),
	("Number Card", "PG Documentos Vencidos", "Gestor Expired Documents"),
	("Number Card", "PG Total Documentos", "Gestor Total Documents"),
	("Number Card", "Presenca Media", "Gestor Average Attendance"),
	("Number Card", "Reunioes no Mes", "Gestor Meetings This Month"),
	("Number Card", "Reunioes nos Proximos 7 Dias", "Gestor Meetings Next 7 Days"),
)


def _exact(doctype, name):
	row = frappe.db.sql(f"select name from `tab{doctype}` where name = %s collate utf8mb4_bin", name)
	return bool(row)


def execute():
	for doctype, old, new in RENAMES:
		if _exact(doctype, old) and not frappe.db.exists(doctype, new):
			frappe.rename_doc(doctype, old, new, force=True, ignore_if_exists=True, show_alert=False)
