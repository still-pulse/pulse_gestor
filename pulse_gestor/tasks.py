# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

"""Jobs agendados do Pulse Gestor."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_days, escape_html, get_url_to_form, nowdate, strip_html

from pulse_gestor.utils import calcular_dias_para_vencimento, calcular_status

DOCTYPE = "Documentacao da Unidade"


def atualizar_status_documentos():
	"""Recalcula status e dias para vencimento de todos os documentos."""
	hoje = nowdate()
	documentos = frappe.get_all(
		DOCTYPE,
		fields=["name", "possui_validade", "data_fim", "status", "dias_para_vencimento"],
	)

	atualizados = 0
	for doc in documentos:
		novo_status = calcular_status(doc.possui_validade, doc.data_fim, hoje)
		novos_dias = calcular_dias_para_vencimento(doc.possui_validade, doc.data_fim, hoje)

		valores = {}
		if doc.status != novo_status:
			valores["status"] = novo_status
		if doc.dias_para_vencimento != novos_dias:
			valores["dias_para_vencimento"] = novos_dias

		if not valores:
			continue

		frappe.db.set_value(DOCTYPE, doc.name, valores, update_modified=False)
		atualizados += 1

	if atualizados:
		frappe.db.commit()
		frappe.logger("pulse_gestor").info("Status atualizado em %s documento(s).", atualizados)


def enviar_avisos_vencimento_documentos():
	"""Enfileira um aviso por documento no prazo configurado, para a empresa correspondente."""
	settings = frappe.get_single("Configuracoes Documentos da Unidade")
	if not settings.modelo_email_vencimento or not settings.destinatarios_vencimento:
		return

	recipients_by_company = {
		row.company: [email.strip() for email in row.emails.splitlines() if email.strip()]
		for row in settings.destinatarios_vencimento
	}
	template = frappe.get_doc("Email Template", settings.modelo_email_vencimento)
	target_date = add_days(nowdate(), int(settings.dias_alerta_vencimento or 0))
	for doc in frappe.get_all(
		DOCTYPE,
		filters={"possui_validade": 1, "data_fim": target_date, "company": ["in", list(recipients_by_company)]},
		fields=["name", "company"],
	):
		if frappe.db.exists(
			"Email Queue",
			{"reference_doctype": DOCTYPE, "reference_name": doc.name, "creation": [">=", nowdate()]},
		):
			continue
		full_doc = frappe.get_doc(DOCTYPE, doc.name)
		context = full_doc.as_dict()
		context["doc"] = full_doc
		formatted = template.get_formatted_email(context)
		frappe.sendmail(
			recipients=recipients_by_company[doc.company],
			subject=formatted["subject"],
			message=corpo_email_vencimento(formatted, full_doc),
			reference_doctype=DOCTYPE,
			reference_name=doc.name,
		)


def corpo_email_vencimento(formatted, doc):
	"""Corpo do Email Template dentro do layout institucional do clm (manifesto, seção 6)."""
	from clm.clm.services.email_layout import is_branded, render_email

	if is_branded(formatted["message"]):
		return formatted["message"]
	return render_email(
		escape_html(strip_html(formatted["subject"] or "")),
		formatted["message"],
		action=(_("Abrir documento"), get_url_to_form(DOCTYPE, doc.name)),
	)
