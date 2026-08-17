# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

from frappe.tests.utils import FrappeTestCase

from pulse_gestor.utils import calcular_dias_para_vencimento, calcular_status, eh_pdf


class TestDocumentacaodaUnidade(FrappeTestCase):
	def test_status_sem_validade(self):
		self.assertEqual(calcular_status(0, "2026-01-01", "2026-08-17"), "Sem validade")

	def test_status_valido(self):
		self.assertEqual(calcular_status(1, "2026-12-31", "2026-08-17"), "Válido")

	def test_status_vencido(self):
		self.assertEqual(calcular_status(1, "2026-01-01", "2026-08-17"), "Vencido")

	def test_status_vence_hoje_ainda_valido(self):
		self.assertEqual(calcular_status(1, "2026-08-17", "2026-08-17"), "Válido")

	def test_dias_para_vencimento(self):
		self.assertEqual(calcular_dias_para_vencimento(1, "2026-08-27", "2026-08-17"), 10)
		self.assertIsNone(calcular_dias_para_vencimento(0, "2026-08-27", "2026-08-17"))

	def test_eh_pdf(self):
		self.assertTrue(eh_pdf("/private/files/alvara.pdf"))
		self.assertTrue(eh_pdf("documento.PDF"))
		self.assertFalse(eh_pdf("/files/scan.png"))
		self.assertFalse(eh_pdf(""))
