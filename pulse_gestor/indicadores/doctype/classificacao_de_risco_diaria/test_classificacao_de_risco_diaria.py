from uuid import uuid4

import frappe
from frappe.tests.utils import FrappeTestCase

from pulse_gestor.indicadores.doctype.classificacao_de_risco_diaria.classificacao_de_risco_diaria import (
	obter_protocolo_e_niveis,
)
from pulse_gestor.setup.install import (
	backfill_cores_classificacao_diaria,
	backfill_tempos_classificacao_diaria,
)


class TestClassificacaoDeRiscoDiaria(FrappeTestCase):
	def test_manager_pode_importar_e_viewer_nao(self):
		usuarios = {}
		for role in ("Pulse Gestor Manager", "Pulse Gestor Viewer"):
			usuario = frappe.get_doc(
				{
					"doctype": "User",
					"email": f"teste-importacao-{uuid4().hex[:12]}@example.com",
					"first_name": "Teste Importação",
					"user_type": "System User",
					"send_welcome_email": 0,
					"roles": [{"role": role}],
				}
			).insert(ignore_permissions=True)
			usuarios[role] = usuario.name

		anterior = frappe.session.user
		try:
			frappe.set_user(usuarios["Pulse Gestor Manager"])
			self.assertTrue(frappe.get_meta("Classificacao de Risco Diaria").allow_import)
			self.assertTrue(frappe.has_permission("Classificacao de Risco Diaria", "import"))
			self.assertTrue(frappe.has_permission("Data Import", "create"))
			importacao = frappe.get_doc(
				{
					"doctype": "Data Import",
					"reference_doctype": "Classificacao de Risco Diaria",
					"import_type": "Insert New Records",
				}
			).insert()
			self.assertTrue(importacao.name)

			frappe.set_user(usuarios["Pulse Gestor Viewer"])
			self.assertFalse(frappe.has_permission("Classificacao de Risco Diaria", "import"))
			self.assertFalse(frappe.has_permission("Data Import", "create"))
		finally:
			frappe.set_user(anterior)

	def test_resolucao_linhas_total_e_envio(self):
		unidade = frappe.get_all("Company", fields=["name"], order_by="name asc", limit=1)[0].name
		protocolo = frappe.get_doc(
			{
				"doctype": "Protocolo de Triagem",
				"nome_protocolo": f"Teste diário {uuid4().hex[:10]}",
				"niveis": [
					{
						"ordem": 1,
						"nome_nivel": "Vermelho",
						"cor": "#CB2929",
						"tempo_maximo_espera_min": 0,
					},
					{
						"ordem": 2,
						"nome_nivel": "Amarelo",
						"cor": "#ECAD4B",
						"tempo_maximo_espera_min": 60,
					},
				],
			}
		).insert()
		frappe.get_doc(
			{
				"doctype": "Unidade Protocolo Vigencia",
				"unidade": unidade,
				"protocolo": protocolo.name,
				"data_inicio_vigencia": "2099-01-01",
				"data_fim_vigencia": "2099-01-31",
			}
		).insert()

		resolvido = obter_protocolo_e_niveis(unidade, "2099-01-31")
		self.assertEqual(resolvido["protocolo"], protocolo.name)
		self.assertEqual(
			resolvido["niveis"],
			[
				{"nivel": "Vermelho", "cor": "#CB2929", "tempo_maximo_espera_min": 0},
				{"nivel": "Amarelo", "cor": "#ECAD4B", "tempo_maximo_espera_min": 60},
			],
		)
		with self.assertRaises(frappe.ValidationError):
			obter_protocolo_e_niveis(unidade, "2099-02-01")

		lancamento = frappe.get_doc(
			{"doctype": "Classificacao de Risco Diaria", "unidade": unidade, "data": "2099-01-31"}
		).insert()
		self.assertEqual(lancamento.protocolo, protocolo.name)
		self.assertEqual([linha.nivel for linha in lancamento.niveis_classificados], ["Vermelho", "Amarelo"])
		self.assertEqual([linha.cor for linha in lancamento.niveis_classificados], ["#CB2929", "#ECAD4B"])
		self.assertEqual(
			[linha.tempo_maximo_espera_min for linha in lancamento.niveis_classificados], [0, 60]
		)
		self.assertEqual(lancamento.total_classificados, 0)
		self.assertEqual(lancamento.status, "Rascunho")
		self.assertTrue(lancamento.lancado_por)
		self.assertTrue(lancamento.criado_em)

		lancamento.niveis_classificados[0].nivel = "Azul"
		with self.assertRaises(frappe.ValidationError):
			lancamento.save()
		lancamento.reload()

		lancamento.niveis_classificados[0].qtd_pacientes_classificados = 4
		lancamento.niveis_classificados[0].qtd_pacientes_classificados = -1
		with self.assertRaises(frappe.ValidationError):
			lancamento.save()
		lancamento.reload()
		lancamento.niveis_classificados[0].qtd_pacientes_classificados = 4
		lancamento.niveis_classificados[1].qtd_pacientes_classificados = 2
		lancamento.save()
		self.assertEqual(lancamento.total_classificados, 6)

		frappe.db.set_value(
			"Classificacao Diaria Nivel",
			lancamento.niveis_classificados[0].name,
			"cor",
			None,
			update_modified=False,
		)
		backfill_cores_classificacao_diaria()
		lancamento.reload()
		self.assertEqual(lancamento.niveis_classificados[0].cor, "#CB2929")
		frappe.db.set_value(
			"Classificacao Diaria Nivel",
			lancamento.niveis_classificados[1].name,
			{"tempo_maximo_espera_min": 0, "tempo_snapshot_preenchido": 0},
			update_modified=False,
		)
		backfill_tempos_classificacao_diaria()
		lancamento.reload()
		self.assertEqual(lancamento.niveis_classificados[1].tempo_maximo_espera_min, 60)

		protocolo.niveis[0].cor = "#4463F0"
		protocolo.save()
		backfill_cores_classificacao_diaria()
		lancamento.reload()
		self.assertEqual(lancamento.niveis_classificados[0].cor, "#CB2929")
		lancamento.niveis_classificados[0].cor = "#000000"
		lancamento.save()
		self.assertEqual(lancamento.niveis_classificados[0].cor, "#CB2929")

		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{"doctype": "Classificacao de Risco Diaria", "unidade": unidade, "data": "2099-01-31"}
			).insert()

		lancamento.submit()
		lancamento.reload()
		self.assertEqual(lancamento.status, "Enviado")
		lancamento.niveis_classificados[0].qtd_pacientes_classificados = 6
		with self.assertRaises(frappe.ValidationError):
			lancamento.save()
