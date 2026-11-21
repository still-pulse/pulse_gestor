import frappe
from frappe import _


def validate_custodian(doc, method=None):
	"""The custodian must be an employee of the asset's company (as ERPNext already requires on movement)."""
	if not doc.custodian or not doc.company:
		return
	company = frappe.db.get_value("Employee", doc.custodian, "company")
	if company != doc.company:
		frappe.throw(
			_("O custodiante {0} não pertence à empresa {1}.").format(doc.custodian, doc.company),
			title=_("Custodiante de outra empresa"),
		)
