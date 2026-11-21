# Copyright (c) 2026, StillPulse Tecnologia LTDA and contributors
# For license information, please see license.txt

from types import SimpleNamespace

from clm.clm.services.email_layout import is_branded, render_email
from frappe.tests.utils import FrappeTestCase

from pulse_gestor.tasks import build_expiry_email_body


class TestExpiryEmail(FrappeTestCase):
	def test_email_template_uses_institutional_layout(self):
		html = build_expiry_email_body(
			{"subject": "[Documentação] Vence em 30 dia(s)", "message": "<p>Alvará</p>"},
			SimpleNamespace(name="DOC-0001"),
		)
		self.assertTrue(is_branded(html))
		self.assertIn("<p>Alvará</p>", html)
		self.assertIn("Abrir documento", html)

	def test_branded_template_is_not_wrapped_again(self):
		body = render_email("Titulo", "<p>x</p>")
		self.assertEqual(
			build_expiry_email_body({"subject": "s", "message": body}, SimpleNamespace(name="D")), body
		)
