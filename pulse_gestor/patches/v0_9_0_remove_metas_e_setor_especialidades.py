import frappe


def execute():
	# A migração do Frappe remove o metadado, mas preserva colunas antigas.
	for doctype, columns in (
		("Vigencia Especialidade", ("meta_quantidade", "periodicidade_meta")),
		("Atendimento Medico Diario Especialidade", ("meta_quantidade", "periodicidade_meta")),
		("Unidade Especialidade Vigencia", ("setor",)),
		("Atendimento Medico Diario", ("setor",)),
	):
		for column in columns:
			if frappe.db.has_column(doctype, column):
				frappe.db.sql(f"ALTER TABLE `tab{doctype}` DROP COLUMN `{column}`")
