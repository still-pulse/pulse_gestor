import frappe
from frappe.tests.utils import FrappeTestCase

from pulse_gestor.patrimonio.report.ativos_por_localizacao.ativos_por_localizacao import (
	execute as ativos_por_localizacao,
)
from pulse_gestor.patrimonio.report.relacao_de_ativos.relacao_de_ativos import execute as relacao_de_ativos

EMPRESA_A = "Empresa A de Teste"
EMPRESA_B = "Empresa B de Teste"


def criar_localizacao(nome, empresa):
	"""Cria a Location sem exigir a Company real: os relatórios só comparam o nome gravado."""
	local = frappe.get_doc({"doctype": "Location", "location_name": nome, "custom_empresa": empresa})
	local.flags.ignore_links = True
	return local.insert(ignore_permissions=True)


def criar_ativo(nome, empresa, localizacao):
	"""Grava um Asset submetido direto na tabela, sem a cadeia contábil do ERPNext (não é o foco do teste)."""
	ativo = frappe.get_doc(
		{
			"doctype": "Asset",
			"name": nome,
			"asset_name": nome,
			"company": empresa,
			"location": localizacao,
			"status": "Submitted",
			"docstatus": 1,
			"gross_purchase_amount": 100,
		}
	)
	ativo.set_user_and_timestamp()
	ativo.db_insert()
	return ativo


class TestRelatoriosDePatrimonio(FrappeTestCase):
	def setUp(self):
		super().setUp()
		self.local_a = criar_localizacao("Local A de Teste", EMPRESA_A).name
		self.local_b = criar_localizacao("Local B de Teste", EMPRESA_B).name
		criar_ativo("PAT-TESTE-A", EMPRESA_A, self.local_a)
		criar_ativo("PAT-TESTE-B", EMPRESA_B, self.local_b)

	def test_filtra_por_empresa(self):
		dados = relacao_de_ativos({"empresa": EMPRESA_A})[1]
		self.assertEqual([r.ativo for r in dados], ["PAT-TESTE-A"])
		self.assertTrue(all(r.empresa == EMPRESA_A for r in dados))

	def test_localizacao_de_outra_empresa_e_recusada(self):
		with self.assertRaises(frappe.ValidationError):
			relacao_de_ativos({"empresa": EMPRESA_B, "localizacao": self.local_a})

	def test_localizacao_da_mesma_empresa_e_aceita(self):
		dados = relacao_de_ativos({"empresa": EMPRESA_A, "localizacao": self.local_a})[1]
		self.assertEqual([r.ativo for r in dados], ["PAT-TESTE-A"])

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
