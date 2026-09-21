# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import validate_email_address


class ConfiguracoesDocumentosdaUnidade(Document):
	def validate(self):
		if int(self.dias_alerta_vencimento or 0) < 0:
			frappe.throw(_("Os dias de alerta não podem ser negativos."))

		companies = set()
		for row in self.destinatarios_vencimento:
			if row.company in companies:
				frappe.throw(_("A empresa {0} foi informada mais de uma vez.").format(row.company))
			companies.add(row.company)
			emails = [
				email.strip()
				for email in (row.emails or "").replace(",", "\n").splitlines()
				if email.strip()
			]
			if not emails or any(not validate_email_address(email) for email in emails):
				frappe.throw(_("Informe e-mails válidos para a empresa {0}.").format(row.company))
			row.emails = "\n".join(dict.fromkeys(emails))
		if self.destinatarios_vencimento and not self.modelo_email_vencimento:
			frappe.throw(_("Selecione o modelo de e-mail para o aviso de vencimento."))

	def on_update(self):
		from pulse_gestor.setup.install import sincronizar_dias_alerta

		sincronizar_dias_alerta()
