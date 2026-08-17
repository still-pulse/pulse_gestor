# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

import unittest
from datetime import date

from pulse_gestor.utils import calcular_dias_para_vencimento, calcular_status, eh_pdf


class TestCalcularStatus(unittest.TestCase):
	def test_sem_validade(self):
		self.assertEqual(calcular_status(0, date(2026, 1, 1), date(2026, 8, 17)), "Sem validade")

	def test_valido(self):
		self.assertEqual(calcular_status(1, "2026-12-31", "2026-08-17"), "Válido")

	def test_vencido(self):
		self.assertEqual(calcular_status(1, "2026-01-01", "2026-08-17"), "Vencido")

	def test_vence_hoje_continua_valido(self):
		self.assertEqual(calcular_status(1, "2026-08-17", "2026-08-17"), "Válido")

	def test_dias_positivos_e_negativos(self):
		self.assertEqual(calcular_dias_para_vencimento(1, "2026-08-27", "2026-08-17"), 10)
		self.assertEqual(calcular_dias_para_vencimento(1, "2026-08-07", "2026-08-17"), -10)

	def test_pdf(self):
		self.assertTrue(eh_pdf("/private/files/alvara.pdf"))
		self.assertFalse(eh_pdf("foto.jpg"))


if __name__ == "__main__":
	unittest.main()
