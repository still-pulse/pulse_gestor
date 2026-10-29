from uuid import uuid4

import frappe
from frappe.model.rename_doc import rename_doc
from frappe.tests.utils import FrappeTestCase

from pulse_gestor.indicadores.report.apuracao_de_classificacao_de_risco.apuracao_de_classificacao_de_risco import (
	execute,
)
from pulse_gestor.setup.install import (
	INDICADORES_RELATORIO,
	INDICADORES_RELATORIO_ANTIGO,
	ensure_ascii_indicadores_report,
)


class TestApuracaoDeClassificacaoDeRisco(FrappeTestCase):
	def test_renomeia_relatorio_legado_com_collation_sem_acentos(self):
		temporario = f"Teste Renomear Relatorio {uuid4().hex[:10]}"
		for origem, destino in (
			(INDICADORES_RELATORIO, temporario),
			(temporario, INDICADORES_RELATORIO_ANTIGO),
		):
			rename_doc(
				"Report", origem, destino,
				force=True, ignore_permissions=True, show_alert=False, rebuild_search=False,
			)
		ensure_ascii_indicadores_report()
		self.assertEqual(
			frappe.db.sql("SELECT name FROM `tabReport` WHERE BINARY name = %s", INDICADORES_RELATORIO)[0][0],
			INDICADORES_RELATORIO,
		)
		self.assertFalse(
			frappe.db.sql(
				"SELECT name FROM `tabReport` WHERE BINARY name = %s", INDICADORES_RELATORIO_ANTIGO
			)
		)

	def test_periodo_com_duas_escalas_e_total_do_card(self):
		unidade = frappe.get_all("Company", fields=["name"], order_by="name asc", limit=1)[0].name
		protocolos = []
		for inicio, fim, alvo, cor_vermelho, cor_amarelo in (
			("2098-01-01", "2098-01-15", 30, "#ff0000", "#ffff00"),
			("2098-01-16", "2098-01-31", 60, "#cc0000", "#eeee00"),
		):
			protocolo = frappe.get_doc(
				{
					"doctype": "Protocolo de Triagem",
					"nome_protocolo": f"Teste apuração {uuid4().hex[:10]}",
					"niveis": [
						{"ordem": 1, "nome_nivel": "Vermelho", "cor": cor_vermelho, "tempo_maximo_espera_min": 0},
						{"ordem": 2, "nome_nivel": "Amarelo", "cor": cor_amarelo, "tempo_maximo_espera_min": alvo},
					],
				}
			).insert()
			frappe.get_doc(
				{
					"doctype": "Unidade Protocolo Vigencia",
					"unidade": unidade,
					"protocolo": protocolo.name,
					"data_inicio_vigencia": inicio,
					"data_fim_vigencia": fim,
				}
			).insert()
			protocolos.append(protocolo)

		def lancar(data, vermelho, amarelo, enviar=True):
			doc = frappe.get_doc(
				{
					"doctype": "Classificacao de Risco Diaria",
					"unidade": unidade,
					"data": data,
				}
			).insert(set_name=f"CRD-TEST-{uuid4().hex[:12]}")
			doc.niveis_classificados[0].qtd_pacientes_classificados = vermelho
			doc.niveis_classificados[1].qtd_pacientes_classificados = amarelo
			doc.save()
			if enviar:
				doc.submit()
			return doc

		lancar("2098-01-02", 2, 3)
		lancar("2098-01-03", 1, 2)
		lancar("2098-01-04", 0, 0)
		lancar("2098-01-16", 8, 2)
		lancar("2098-01-17", 99, 1, enviar=False)

		columns, rows, _, chart, summary = execute(
			{"unidade": unidade, "data_inicio": "2098-01-01", "data_fim": "2098-01-31"}
		)
		self.assertEqual(len(columns), 6)
		self.assertEqual(summary[0]["value"], 18)
		self.assertEqual(chart["type"], "donut")
		self.assertEqual(chart["data"]["labels"], ["Vermelho", "Amarelo"])
		self.assertEqual(chart["data"]["datasets"][0]["values"], [11, 7])
		self.assertEqual(chart["colors"], ["#cc0000", "#eeee00"])
		self.assertEqual(len(rows), 4)
		by_key = {(row.protocolo, row.nivel): row for row in rows}
		primeiro = by_key[(protocolos[0].name, "Vermelho")]
		self.assertEqual(primeiro.qtd_pacientes_classificados, 3)
		self.assertEqual(primeiro.total_classificados, 8)
		self.assertAlmostEqual(primeiro.percentual_classificacao, 37.5)
		self.assertEqual(by_key[(protocolos[0].name, "Amarelo")].tempo_maximo_espera_min, 30)
		self.assertEqual(by_key[(protocolos[1].name, "Amarelo")].tempo_maximo_espera_min, 60)
		self.assertEqual(by_key[(protocolos[1].name, "Vermelho")].percentual_classificacao, 80)
		_, sem_pacientes, _, chart, summary = execute(
			{"unidade": unidade, "data_inicio": "2098-01-04", "data_fim": "2098-01-04"}
		)
		self.assertEqual(summary[0]["value"], 0)
		self.assertIsNone(chart)
		self.assertTrue(all(row.percentual_classificacao == 0 for row in sem_pacientes))

		protocolos[1].niveis[1].tempo_maximo_espera_min = 90
		protocolos[1].niveis[1].cor = "#dddd00"
		protocolos[1].save()
		_, rows, _, chart, _ = execute(
			{"unidade": unidade, "data_inicio": "2098-01-16", "data_fim": "2098-01-16"}
		)
		self.assertEqual(next(row for row in rows if row.nivel == "Amarelo").tempo_maximo_espera_min, 60)
		self.assertEqual(chart["colors"], ["#cc0000", "#eeee00"])

		lancar("2098-01-18", 5, 5)
		_, rows, _, chart, summary = execute(
			{"unidade": unidade, "data_inicio": "2098-01-16", "data_fim": "2098-01-18"}
		)
		amarelos = [row for row in rows if row.nivel == "Amarelo"]
		self.assertEqual({row.tempo_maximo_espera_min for row in amarelos}, {60, 90})
		self.assertEqual({row.total_classificados for row in amarelos}, {10})
		self.assertEqual(summary[0]["value"], 20)
		self.assertEqual(chart["data"]["datasets"][0]["values"], [13, 7])
		self.assertEqual(chart["colors"], ["#cc0000", "#dddd00"])

	def test_periodo_vazio_e_datas_invertidas(self):
		unidade = frappe.get_all("Company", fields=["name"], order_by="name asc", limit=1)[0].name
		_, rows, _, chart, summary = execute(
			{"unidade": unidade, "data_inicio": "2199-01-01", "data_fim": "2199-01-31"}
		)
		self.assertEqual(rows, [])
		self.assertIsNone(chart)
		self.assertEqual(summary[0]["value"], 0)
		with self.assertRaises(frappe.ValidationError):
			execute({"unidade": unidade, "data_inicio": "2199-02-01", "data_fim": "2199-01-31"})
