# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

from types import SimpleNamespace

from clm.clm.services.email_layout import is_branded, render_email
from frappe.tests.utils import FrappeTestCase

from pulse_gestor.tasks import corpo_email_vencimento


class TestEmailVencimento(FrappeTestCase):
	def test_email_template_vai_no_layout_institucional(self):
		html = corpo_email_vencimento(
			{"subject": "[Documentação] Vence em 30 dia(s)", "message": "<p>Alvará</p>"},
			SimpleNamespace(name="DOC-0001"),
		)
		self.assertTrue(is_branded(html))
		self.assertIn("<p>Alvará</p>", html)
		self.assertIn("Abrir documento", html)

	def test_template_ja_institucional_nao_e_envolvido_de_novo(self):
		corpo = render_email("Titulo", "<p>x</p>")
		self.assertEqual(
			corpo_email_vencimento({"subject": "s", "message": corpo}, SimpleNamespace(name="D")), corpo
		)
