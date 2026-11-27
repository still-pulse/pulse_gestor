import frappe
from frappe.tests.utils import FrappeTestCase

from pulse_gestor.patrimonio.report.gestor_asset_list.gestor_asset_list import execute as asset_list
from pulse_gestor.patrimonio.report.gestor_assets_by_location.gestor_assets_by_location import (
	execute as assets_by_location,
)


class TestAssetReports(FrappeTestCase):
	def test_filters_by_company(self):
		company = frappe.db.get_value("Asset", {"docstatus": 1}, "company")
		if not company:
			self.skipTest("Sem ativos no site")
		rows = asset_list({"empresa": company})[1]
		self.assertTrue(rows)
		self.assertTrue(all(r.empresa == company for r in rows))

	def test_location_of_another_company_is_rejected(self):
		location = frappe.db.get_value(
			"Location", {"custom_empresa": ("is", "set")}, ["name", "custom_empresa"], as_dict=True
		)
		other_company = frappe.db.get_value("Company", {"name": ("!=", location and location.custom_empresa)})
		if not location or not other_company:
			self.skipTest("Sem localizações e empresas suficientes")
		with self.assertRaises(frappe.ValidationError):
			asset_list({"empresa": other_company, "localizacao": location.name})

	def test_groups_assets_under_location(self):
		rows = assets_by_location({})[1]
		groups = {r["id"]: r for r in rows if r["indent"] == 0}
		for row in rows:
			if row["indent"] == 1:
				self.assertIn(row["parent"], groups)
		self.assertEqual(
			sum(g["quantidade"] for g in groups.values()),
			sum(1 for r in rows if r["indent"] == 1),
		)
