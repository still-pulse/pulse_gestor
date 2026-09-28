import frappe
from frappe.model.rename_doc import rename_doc

RENAMES = (
	("Atendimento Diario", "Atendimento Medico Diario"),
	("Atendimento Diario Especialidade", "Atendimento Medico Diario Especialidade"),
)


def execute():
	# Antes da sincronização dos modelos, para preservar tabelas e lançamentos existentes.
	for old, new in RENAMES:
		if frappe.db.exists("DocType", old) and not frappe.db.exists("DocType", new):
			rename_doc("DocType", old, new, force=True, ignore_permissions=True, show_alert=False, validate=False)
