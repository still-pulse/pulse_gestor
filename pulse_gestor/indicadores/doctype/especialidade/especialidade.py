import frappe
from frappe import _
from frappe.model.document import Document


class Especialidade(Document):
	def validate(self):
		self.nome_especialidade = (self.nome_especialidade or "").strip()
		if not self.nome_especialidade:
			frappe.throw(_("Informe o nome da especialidade."))
