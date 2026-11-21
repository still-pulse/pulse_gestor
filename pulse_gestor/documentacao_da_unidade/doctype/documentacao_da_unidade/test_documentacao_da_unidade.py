# Copyright (c) 2026, StillPulse Tecnologia LTDA and contributors
# For license information, please see license.txt

from frappe.tests.utils import FrappeTestCase

from pulse_gestor.utils import calculate_days_to_expiry, calculate_status, is_pdf


class TestDocumentacaodaUnidade(FrappeTestCase):
	def test_status_no_expiry(self):
		self.assertEqual(calculate_status(0, "2026-01-01", "2026-08-17"), "Sem validade")

	def test_status_valid(self):
		self.assertEqual(calculate_status(1, "2026-12-31", "2026-08-17"), "Válido")

	def test_status_expired(self):
		self.assertEqual(calculate_status(1, "2026-01-01", "2026-08-17"), "Vencido")

	def test_status_expiring_today_is_still_valid(self):
		self.assertEqual(calculate_status(1, "2026-08-17", "2026-08-17"), "Válido")

	def test_days_to_expiry(self):
		self.assertEqual(calculate_days_to_expiry(1, "2026-08-27", "2026-08-17"), 10)
		self.assertIsNone(calculate_days_to_expiry(0, "2026-08-27", "2026-08-17"))

	def test_is_pdf(self):
		self.assertTrue(is_pdf("/private/files/alvara.pdf"))
		self.assertTrue(is_pdf("documento.PDF"))
		self.assertFalse(is_pdf("/files/scan.png"))
		self.assertFalse(is_pdf(""))
