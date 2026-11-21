import frappe


def execute():
	# A migração do Frappe remove o metadado, mas preserva colunas antigas.
	for doctype, column in (
		("Protocolo Nivel", "meta_conformidade_pct"),
		("Classificacao Diaria Nivel", "qtd_atendidos_dentro_do_tempo"),
	):
		if frappe.db.has_column(doctype, column):
			frappe.db.sql_ddl(f"ALTER TABLE `tab{doctype}` DROP COLUMN `{column}`")
