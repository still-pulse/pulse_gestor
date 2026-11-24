# Copyright (c) 2026, StillPulse Tecnologia LTDA and contributors
# For license information, please see license.txt

import unittest
from datetime import date

from pulse_gestor.utils import calculate_days_to_expiry, calculate_status, is_pdf


class TestCalculateStatus(unittest.TestCase):
	def test_no_expiry(self):
		self.assertEqual(calculate_status(0, date(2026, 1, 1), date(2026, 8, 17)), "Sem validade")

	def test_valid(self):
		self.assertEqual(calculate_status(1, "2026-12-31", "2026-08-17"), "Válido")

	def test_expired(self):
		self.assertEqual(calculate_status(1, "2026-01-01", "2026-08-17"), "Vencido")

	def test_expiring_today_remains_valid(self):
		self.assertEqual(calculate_status(1, "2026-08-17", "2026-08-17"), "Válido")

	def test_positive_and_negative_days(self):
		self.assertEqual(calculate_days_to_expiry(1, "2026-08-27", "2026-08-17"), 10)
		self.assertEqual(calculate_days_to_expiry(1, "2026-08-07", "2026-08-17"), -10)

	def test_pdf_detection(self):
		self.assertTrue(is_pdf("/private/files/alvara.pdf"))
		self.assertFalse(is_pdf("foto.jpg"))


if __name__ == "__main__":
	unittest.main()
