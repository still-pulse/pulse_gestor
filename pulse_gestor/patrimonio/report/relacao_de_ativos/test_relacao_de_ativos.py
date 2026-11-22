import frappe
from frappe.tests.utils import FrappeTestCase

from pulse_gestor.patrimonio.report.ativos_por_localizacao.ativos_por_localizacao import (
	execute as ativos_por_localizacao,
)
from pulse_gestor.patrimonio.report.relacao_de_ativos.relacao_de_ativos import execute as relacao_de_ativos
from pulse_gestor.patrimonio.report.utils import (
	CONSERVACAO,
	CONTROLE_BHCL,
	PATRIMONIO_PREFEITURA,
	SQL_ATIVOS,
	UTILIZACAO,
	buscar_ativos,
)

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
	@classmethod
	def setUpClass(cls):
		# FrappeTestCase só desfaz o banco no fim da classe, não entre testes: criar uma vez aqui evita
		# DuplicateEntryError (nomes fixos) a partir do segundo teste.
		super().setUpClass()
		cls.local_a = criar_localizacao("Local A de Teste", EMPRESA_A).name
		cls.local_b = criar_localizacao("Local B de Teste", EMPRESA_B).name
		criar_ativo("PAT-TESTE-A", EMPRESA_A, cls.local_a)
		criar_ativo("PAT-TESTE-B", EMPRESA_B, cls.local_b)

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


class TestConsultaDeAtivosEstatica(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		local = criar_localizacao("Local Filtros de Teste", EMPRESA_A).name
		for nome, categoria, status, utilizacao, conservacao in (
			("PAT-FILTRO-1", "Cat Teste 1", "Submitted", "Em uso", "Bom"),
			("PAT-FILTRO-2", "Cat Teste 2", "In Location", "Ocioso", "Ruim"),
		):
			ativo = frappe.get_doc(
				{
					"doctype": "Asset",
					"name": nome,
					"asset_name": nome,
					"company": EMPRESA_A,
					"location": local,
					"asset_category": categoria,
					"status": status,
					"docstatus": 1,
					"gross_purchase_amount": 100,
					UTILIZACAO: utilizacao,
					CONSERVACAO: conservacao,
				}
			)
			ativo.set_user_and_timestamp()
			ativo.db_insert()

	def nomes(self, **filtros):
		return sorted(r.ativo for r in buscar_ativos({"empresa": EMPRESA_A, **filtros}))

	def test_cada_filtro_restringe_o_resultado(self):
		self.assertEqual(self.nomes(), ["PAT-FILTRO-1", "PAT-FILTRO-2"])
		self.assertEqual(self.nomes(categoria="Cat Teste 2"), ["PAT-FILTRO-2"])
		self.assertEqual(self.nomes(status="Submitted"), ["PAT-FILTRO-1"])
		self.assertEqual(self.nomes(utilizacao="Ocioso"), ["PAT-FILTRO-2"])
		self.assertEqual(self.nomes(conservacao="Bom"), ["PAT-FILTRO-1"])

	def test_filtros_combinados_e_vazios(self):
		self.assertEqual(self.nomes(categoria="Cat Teste 1", conservacao="Ruim"), [])
		self.assertEqual(self.nomes(categoria="", status="", utilizacao="", conservacao=""), self.nomes())

	def test_constantes_dos_campos_estao_na_consulta(self):
		for nome in (CONTROLE_BHCL, PATRIMONIO_PREFEITURA, UTILIZACAO, CONSERVACAO):
			self.assertIn(f"`{nome}`", SQL_ATIVOS)
		self.assertNotIn("{", SQL_ATIVOS)
