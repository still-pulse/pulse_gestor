from frappe.model.document import Document

from pulse_gestor.telefone import validar_e_formatar_linhas


class MembrosdeComissao(Document):
	def validate(self):
		validar_e_formatar_linhas(self.membros)
