import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr


class ProtocolodeTriagem(Document):
	def validate(self):
		self.nome_protocolo = cstr(self.nome_protocolo).strip()
		if not self.nome_protocolo:
			frappe.throw(_("Informe o nome do protocolo."))
		if not self.niveis:
			frappe.throw(_("Informe ao menos um nível de triagem."))

		orders = set()
		for level in self.niveis:
			level.nome_nivel = cstr(level.nome_nivel).strip()
			if not level.nome_nivel:
				frappe.throw(_("Informe o nome de todos os níveis."))
			if not level.ordem or level.ordem < 1:
				frappe.throw(_("A ordem dos níveis deve ser maior que zero."))
			if level.ordem in orders:
				frappe.throw(_("A ordem {0} está repetida no protocolo.").format(level.ordem))
			orders.add(level.ordem)
			if level.tempo_maximo_espera_min is None or level.tempo_maximo_espera_min < 0:
				frappe.throw(_("O tempo máximo de espera não pode ser negativo."))
