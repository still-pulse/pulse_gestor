# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

from types import SimpleNamespace
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from pulse_gestor.tasks import enviar_avisos_vencimento_documentos


class TestConfiguracoesDocumentosdaUnidade(FrappeTestCase):
	def test_destinatarios_exigem_modelo_e_emails_validos(self):
		settings = frappe.get_single("Configuracoes Documentos da Unidade")
		settings.modelo_email_vencimento = None
		settings.set("destinatarios_vencimento", [])
		settings.append("destinatarios_vencimento", {"company": "Empresa A", "emails": "a@example.com"})
		with self.assertRaises(frappe.ValidationError):
			settings.validate()

		settings.modelo_email_vencimento = "Modelo"
		settings.destinatarios_vencimento[0].emails = "endereco-invalido"
		with self.assertRaises(frappe.ValidationError):
			settings.validate()

		settings.destinatarios_vencimento[0].emails = "a@example.com, b@example.com"
		settings.validate()
		self.assertEqual(settings.destinatarios_vencimento[0].emails, "a@example.com\nb@example.com")

	def test_avisos_usam_empresa_e_modelo_configurados(self):
		settings = SimpleNamespace(
			modelo_email_vencimento="Modelo",
			dias_alerta_vencimento=30,
			destinatarios_vencimento=[SimpleNamespace(company="Empresa A", emails="a@example.com\nb@example.com")],
		)
		template = SimpleNamespace(get_formatted_email=lambda context: {"subject": "Assunto", "message": "Corpo"})
		documento = SimpleNamespace(as_dict=lambda: {"name": "DOC-1"})
		with (
			patch("pulse_gestor.tasks.frappe.get_single", return_value=settings),
			patch("pulse_gestor.tasks.frappe.get_all", return_value=[SimpleNamespace(name="DOC-1", company="Empresa A")]) as get_all,
			patch("pulse_gestor.tasks.frappe.get_doc", side_effect=[template, documento]),
			patch("pulse_gestor.tasks.frappe.db.exists", return_value=False),
			patch("pulse_gestor.tasks.frappe.sendmail") as sendmail,
		):
			enviar_avisos_vencimento_documentos()

		self.assertEqual(get_all.call_args.kwargs["filters"]["company"], ["in", ["Empresa A"]])
		sendmail.assert_called_once_with(
			recipients=["a@example.com", "b@example.com"],
			subject="Assunto",
			message="Corpo",
			reference_doctype="Documentacao da Unidade",
			reference_name="DOC-1",
		)
