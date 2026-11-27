import frappe
from frappe import _


def validar_custodiante(doc, method=None):
	"""O custodiante precisa ser colaborador da empresa do ativo (como o ERPNext já exige na movimentação)."""
	if not doc.custodian or not doc.company:
		return
	empresa = frappe.db.get_value("Employee", doc.custodian, "company")
	if empresa != doc.company:
		frappe.throw(
			_("O custodiante {0} não pertence à empresa {1}.").format(doc.custodian, doc.company),
			title=_("Custodiante de outra empresa"),
		)
