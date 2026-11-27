import frappe
from frappe.tests.utils import FrappeTestCase

from pulse_gestor.comissoes.report.atividades_de_comissao.atividades_de_comissao import execute


class TestAtividadesDeComissao(FrappeTestCase):
	def test_exige_periodo_valido(self):
		with self.assertRaises(frappe.ValidationError):
			execute({"data_inicio": "2026-02-01", "data_fim": "2026-01-01"})
		with self.assertRaises(frappe.ValidationError):
			execute({})

	def test_coluna_de_pauta_depende_do_filtro(self):
		periodo = {"data_inicio": "2026-01-01", "data_fim": "2026-12-31"}
		sem_pauta = [c["fieldname"] for c in execute(periodo)[0]]
		com_pauta = [c["fieldname"] for c in execute({**periodo, "incluir_pauta": 1})[0]]
		self.assertNotIn("assunto", sem_pauta)
		self.assertIn("assunto", com_pauta)


EMPRESA_X = "Empresa SQL de Teste X"
EMPRESA_Y = "Empresa SQL de Teste Y"
PERIODO = {"data_inicio": "2031-05-01", "data_fim": "2031-05-31"}


def criar_reuniao(nome, empresa, dia, pautas=(), presentes=0, ausentes=0):
	"""Grava a reunião e as linhas filhas direto na tabela (o relatório só lê os campos gravados)."""
	reuniao = frappe.get_doc(
		{
			"doctype": "Reuniao de Comissao",
			"name": nome,
			"empresa": empresa,
			"data_convocacao": f"2031-05-{dia:02d}",
			"data_reuniao": f"2031-05-{dia:02d} 10:00:00",
		}
	)
	reuniao.set_user_and_timestamp()
	reuniao.db_insert()
	filhas = [("Comissao Pauta Item", "pauta", {"assunto": assunto}) for assunto in pautas]
	filhas += [
		("Comissao Reuniao Participante", "participantes", {"nome": "P", "status_presenca": "Presente"})
	] * presentes
	filhas += [
		("Comissao Reuniao Participante", "participantes", {"nome": "A", "status_presenca": "Ausente"})
	] * ausentes
	for idx, (doctype, campo, valores) in enumerate(filhas, start=1):
		filha = frappe.get_doc(
			{
				"doctype": doctype,
				"name": frappe.generate_hash(length=10),
				"parent": nome,
				"parenttype": "Reuniao de Comissao",
				"parentfield": campo,
				"idx": idx,
				**valores,
			}
		)
		filha.set_user_and_timestamp()
		filha.db_insert()


class TestAtividadesDeComissaoConsulta(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		# FrappeTestCase só desfaz o banco no fim da classe: dados criados uma vez aqui.
		super().setUpClass()
		criar_reuniao("RC-SQL-X1", EMPRESA_X, 10, pautas=("Item 1", "Item 2"), presentes=2, ausentes=1)
		criar_reuniao("RC-SQL-X2", EMPRESA_X, 11)
		criar_reuniao("RC-SQL-Y1", EMPRESA_Y, 12, pautas=("Item Y",), presentes=1)

	def reunioes(self, **filtros):
		_, data, *_ = execute({**PERIODO, **filtros})
		return data

	def test_sem_pauta_traz_uma_linha_por_reuniao_e_sem_coluna_assunto(self):
		data = self.reunioes()
		self.assertEqual([r["reuniao"] for r in data], ["RC-SQL-X1", "RC-SQL-X2", "RC-SQL-Y1"])
		self.assertTrue(all("assunto" not in r for r in data))
		x1 = data[0]
		self.assertEqual((x1["presentes"], x1["convocados"]), (2, 3))

	def test_com_pauta_traz_uma_linha_por_item_e_reuniao_sem_pauta_uma_vez(self):
		data = self.reunioes(incluir_pauta=1)
		self.assertEqual([r["assunto"] for r in data], ["Item 1", "Item 2", None, "Item Y"])
		# dados da reunião só na primeira linha de cada reunião
		self.assertEqual([r["reuniao"] for r in data], ["RC-SQL-X1", None, "RC-SQL-X2", "RC-SQL-Y1"])

	def test_filtra_por_empresa(self):
		self.assertEqual([r["reuniao"] for r in self.reunioes(empresa=EMPRESA_Y)], ["RC-SQL-Y1"])

	def test_filtro_vazio_equivale_a_sem_filtro(self):
		self.assertEqual(len(self.reunioes(empresa="", tipo_comissao="")), 3)

	def test_periodo_fora_nao_traz_reunioes(self):
		_, data, *_ = execute({"data_inicio": "2031-06-01", "data_fim": "2031-06-30"})
		self.assertEqual(data, [])

	def test_consulta_nao_monta_sql_por_texto(self):
		from pulse_gestor.comissoes.report.atividades_de_comissao.atividades_de_comissao import SQL_REUNIOES

		self.assertNotIn("{", SQL_REUNIOES)
