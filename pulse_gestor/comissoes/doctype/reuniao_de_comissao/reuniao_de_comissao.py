import frappe
from frappe import _
from frappe.model.document import Document


@frappe.whitelist()
def buscar_membros(membros_comissao):
	if not frappe.has_permission("Reuniao de Comissao", "create"):
		frappe.throw(_("Sem permissão para criar reuniões de comissão."), frappe.PermissionError)
	return frappe.get_all(
		"Comissao Membro",
		filters={"parent": membros_comissao, "parenttype": "Membros de Comissao"},
		fields=["nome", "funcao", "email"],
		order_by="idx asc",
	)


class ReuniaodeComissao(Document):
	pass
