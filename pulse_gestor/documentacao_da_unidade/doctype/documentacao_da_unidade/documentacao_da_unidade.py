# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

from pulse_gestor.utils import calcular_dias_para_vencimento, calcular_status, eh_pdf


class DocumentacaodaUnidade(Document):
	def validate(self):
		self._validar_tipo_ativo()
		self._validar_vigencia()
		self._validar_pdf()
		self._atualizar_status()

	def _validar_tipo_ativo(self):
		if not self.tipo_documento:
			return
		ativo = frappe.db.get_value("Tipo de Documento da Unidade", self.tipo_documento, "ativo")
		if ativo is not None and not int(ativo):
			frappe.throw(_("O tipo de documento {0} está inativo.").format(self.tipo_documento))

	def _validar_vigencia(self):
		if not int(self.possui_validade or 0):
			self.data_inicio = None
			self.data_fim = None
			return

		if not self.data_inicio or not self.data_fim:
			frappe.throw(_("Informe o início e o fim da vigência."))

		if getdate(self.data_fim) < getdate(self.data_inicio):
			frappe.throw(_("O fim da vigência não pode ser anterior ao início."))

	def _validar_pdf(self):
		if not self.arquivo_pdf:
			frappe.throw(_("Anexe o arquivo PDF."))
		if not eh_pdf(self.arquivo_pdf):
			frappe.throw(_("O arquivo anexado precisa ser um PDF."))

	def _atualizar_status(self):
		hoje = nowdate()
		self.status = calcular_status(self.possui_validade, self.data_fim, hoje)
		self.dias_para_vencimento = calcular_dias_para_vencimento(
			self.possui_validade, self.data_fim, hoje
		)
