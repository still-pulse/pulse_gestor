import frappe
from frappe import _
from frappe.model.document import Document


class TipodeComissao(Document):
	def validate(self):
		self.nome_tipo = (self.nome_tipo or "").strip()
		if not self.nome_tipo:
			frappe.throw(_("Informe o nome do tipo de comissão."))
