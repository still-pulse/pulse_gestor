import frappe
from frappe.model.rename_doc import rename_doc


def execute():
	old = "Configuracoes Pulse Gestor"
	new = "Configuracoes Documentos da Unidade"
	if frappe.db.exists("DocType", old) and not frappe.db.exists("DocType", new):
		rename_doc("DocType", old, new, force=True, ignore_permissions=True, show_alert=False)
