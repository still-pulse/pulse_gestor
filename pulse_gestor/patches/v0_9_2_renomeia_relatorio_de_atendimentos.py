import frappe


def execute():
	# O relatório antigo é padrão do app e o novo é criado pela sincronização; remover só o registro.
	if frappe.db.exists("Report", "Atendimentos Medicos por Periodo"):
		frappe.db.delete("Report", {"name": "Atendimentos Medicos por Periodo"})
