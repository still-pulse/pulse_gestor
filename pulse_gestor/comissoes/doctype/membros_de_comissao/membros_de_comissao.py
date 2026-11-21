from frappe.model.document import Document

from pulse_gestor.phone import validate_and_format_rows


class MembrosdeComissao(Document):
	def validate(self):
		validate_and_format_rows(self.membros)
