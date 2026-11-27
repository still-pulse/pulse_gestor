import frappe
from frappe.tests.utils import FrappeTestCase

from pulse_gestor.patrimonio.report.ativos_por_localizacao.ativos_por_localizacao import (
	execute as ativos_por_localizacao,
)
from pulse_gestor.patrimonio.report.relacao_de_ativos.relacao_de_ativos import execute as relacao_de_ativos


class TestRelatoriosDePatrimonio(FrappeTestCase):
	def test_filtra_por_empresa(self):
		empresa = frappe.db.get_value("Asset", {"docstatus": 1}, "company")
		if not empresa:
			self.skipTest("Sem ativos no site")
		dados = relacao_de_ativos({"empresa": empresa})[1]
		self.assertTrue(dados)
		self.assertTrue(all(r.empresa == empresa for r in dados))

	def test_localizacao_de_outra_empresa_e_recusada(self):
		local = frappe.db.get_value(
			"Location", {"custom_empresa": ("is", "set")}, ["name", "custom_empresa"], as_dict=True
		)
		outra = frappe.db.get_value("Company", {"name": ("!=", local and local.custom_empresa)})
		if not local or not outra:
			self.skipTest("Sem localizações e empresas suficientes")
		with self.assertRaises(frappe.ValidationError):
			relacao_de_ativos({"empresa": outra, "localizacao": local.name})

	def test_agrupa_ativos_sob_a_localizacao(self):
		dados = ativos_por_localizacao({})[1]
		grupos = {r["id"]: r for r in dados if r["indent"] == 0}
		for row in dados:
			if row["indent"] == 1:
				self.assertIn(row["parent"], grupos)
		self.assertEqual(
			sum(g["quantidade"] for g in grupos.values()),
			sum(1 for r in dados if r["indent"] == 1),
		)
