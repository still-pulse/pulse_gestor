import frappe
from frappe import _
from frappe.model.document import Document


class CategoriadeComissao(Document):
	def validate(self):
		self.nome_categoria = (self.nome_categoria or "").strip()
		if not self.nome_categoria:
			frappe.throw(_("Informe o nome da categoria de comissão."))
