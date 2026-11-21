# Copyright (c) 2026, StillPulse Tecnologia LTDA and contributors
# For license information, please see license.txt

"""Scheduled jobs of Pulse Gestor."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_days, escape_html, get_url_to_form, nowdate, strip_html

from pulse_gestor.utils import calculate_days_to_expiry, calculate_status

DOCTYPE = "Documentacao da Unidade"


def update_document_statuses():
	"""Recompute the status and days to expiry of all documents."""
	today = nowdate()
	documents = frappe.get_all(
		DOCTYPE,
		fields=["name", "possui_validade", "data_fim", "status", "dias_para_vencimento"],
	)

	updated_count = 0
	for doc in documents:
		new_status = calculate_status(doc.possui_validade, doc.data_fim, today)
		new_days = calculate_days_to_expiry(doc.possui_validade, doc.data_fim, today)

		values = {}
		if doc.status != new_status:
			values["status"] = new_status
		if doc.dias_para_vencimento != new_days:
			values["dias_para_vencimento"] = new_days

		if not values:
			continue

		frappe.db.set_value(DOCTYPE, doc.name, values, update_modified=False)
		updated_count += 1

	if updated_count:
		frappe.db.commit()
		frappe.logger("pulse_gestor").info("Status updated on %s document(s).", updated_count)


def send_expiry_notices():
	"""Queue one notice per document at the configured lead time, for the matching company."""
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
		filters={
			"possui_validade": 1,
			"data_fim": target_date,
			"company": ["in", list(recipients_by_company)],
		},
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
			message=build_expiry_email_body(formatted, full_doc),
			reference_doctype=DOCTYPE,
			reference_name=doc.name,
		)


def build_expiry_email_body(formatted, doc):
	"""Email Template body inside the institutional clm layout (manifesto, section 6)."""
	from clm.clm.services.email_layout import is_branded, render_email

	if is_branded(formatted["message"]):
		return formatted["message"]
	return render_email(
		escape_html(strip_html(formatted["subject"] or "")),
		formatted["message"],
		action=(_("Abrir documento"), get_url_to_form(DOCTYPE, doc.name)),
	)
