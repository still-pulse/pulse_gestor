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

		ordens = set()
		for nivel in self.niveis:
			nivel.nome_nivel = cstr(nivel.nome_nivel).strip()
			if not nivel.nome_nivel:
				frappe.throw(_("Informe o nome de todos os níveis."))
			if not nivel.ordem or nivel.ordem < 1:
				frappe.throw(_("A ordem dos níveis deve ser maior que zero."))
			if nivel.ordem in ordens:
				frappe.throw(_("A ordem {0} está repetida no protocolo.").format(nivel.ordem))
			ordens.add(nivel.ordem)
			if nivel.tempo_maximo_espera_min is None or nivel.tempo_maximo_espera_min < 0:
				frappe.throw(_("O tempo máximo de espera não pode ser negativo."))
