# Copyright (c) 2026, StillPulse Tecnologia LTDA and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

from pulse_gestor.utils import calculate_days_to_expiry, calculate_status, is_pdf


class DocumentacaodaUnidade(Document):
	def validate(self):
		self._validar_tipo_ativo()
		self._validar_vigencia()
		self._validar_pdf()
		self._atualizar_status()

	def _validate_type_active(self):
		if not self.tipo_documento:
			return
		is_active = frappe.db.get_value("Tipo de Documento da Unidade", self.tipo_documento, "ativo")
		if is_active is not None and not int(is_active):
			frappe.throw(_("O tipo de documento {0} está inativo.").format(self.tipo_documento))

	def _validate_validity(self):
		if not int(self.possui_validade or 0):
			self.data_inicio = None
			self.data_fim = None
			return

		if not self.data_inicio or not self.data_fim:
			frappe.throw(_("Informe o início e o fim da vigência."))

		if getdate(self.data_fim) < getdate(self.data_inicio):
			frappe.throw(_("O fim da vigência não pode ser anterior ao início."))

	def _validate_pdf(self):
		if not self.arquivo_pdf:
			frappe.throw(_("Anexe o arquivo PDF."))
		if not is_pdf(self.arquivo_pdf):
			frappe.throw(_("O arquivo anexado precisa ser um PDF."))

	def _update_status(self):
		today = nowdate()
		self.status = calculate_status(self.possui_validade, self.data_fim, today)
		self.dias_para_vencimento = calculate_days_to_expiry(self.possui_validade, self.data_fim, today)
