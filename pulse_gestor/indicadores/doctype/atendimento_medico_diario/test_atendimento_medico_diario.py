from uuid import uuid4

import frappe
from frappe.tests.utils import FrappeTestCase

from pulse_gestor.indicadores.doctype.atendimento_medico_diario.atendimento_medico_diario import (
	buscar_vigencia_e_especialidades,
	obter_vigencia_e_especialidades,
)
from pulse_gestor.indicadores.report.atendimentos_medicos_por_periodo.atendimentos_medicos_por_periodo import (
	execute as executar_relatorio,
)


class TestAtendimentoMedicoDiario(FrappeTestCase):
	def preparar_cadastros(self):
		unidade = frappe.get_all("Company", fields=["name"], order_by="name asc", limit=1)[0].name
		especialidades = [
			frappe.get_doc(
				{"doctype": "Especialidade", "nome_especialidade": f"Especialidade Teste {uuid4().hex[:10]}"}
			).insert()
			for _ in range(2)
		]
		return unidade, especialidades

	def criar_vigencia(self, unidade, especialidades, inicio, fim=None):
		return frappe.get_doc(
			{
				"doctype": "Unidade Especialidade Vigencia",
				"unidade": unidade,
				"data_inicio_vigencia": inicio,
				"data_fim_vigencia": fim,
				"especialidades": [{"especialidade": e.name} for e in especialidades],
			}
		).insert()

	def test_vigencia_resolucao_lancamento_e_envio(self):
		unidade, especialidades = self.preparar_cadastros()
		vigencia = self.criar_vigencia(unidade, especialidades, "2098-01-01", "2098-01-31")
		resolvido = obter_vigencia_e_especialidades(unidade, "2098-01-31")
		self.assertEqual(resolvido["vigencia"], vigencia.name)
		self.assertEqual(
			[item["especialidade"] for item in resolvido["especialidades"]],
			[item.name for item in especialidades],
		)
		with self.assertRaises(frappe.ValidationError):
			obter_vigencia_e_especialidades(unidade, "2098-02-01")
		with self.assertRaises(frappe.ValidationError):
			self.criar_vigencia(unidade, especialidades[:1], "2098-01-31")
		with self.assertRaises(frappe.ValidationError):
			self.criar_vigencia(unidade, [especialidades[0], especialidades[0]], "2098-03-01")

		atendimento = frappe.get_doc(
			{"doctype": "Atendimento Medico Diario", "unidade": unidade, "data": "2098-01-31"}
		).insert()
		self.assertEqual(atendimento.vigencia, vigencia.name)
		self.assertEqual([linha.especialidade for linha in atendimento.especialidades], [e.name for e in especialidades])
		self.assertEqual(atendimento.total_dia, 0)
		self.assertEqual(atendimento.status, "Rascunho")
		self.assertTrue(atendimento.lancado_por)
		self.assertTrue(atendimento.criado_em)

		atendimento.especialidades[0].quantidade = -1
		with self.assertRaises(frappe.ValidationError):
			atendimento.save()
		atendimento.reload()
		atendimento.especialidades[0].especialidade = especialidades[1].name
		with self.assertRaises(frappe.ValidationError):
			atendimento.save()
		atendimento.reload()
		atendimento.especialidades[0].quantidade = 4
		atendimento.especialidades[1].quantidade = 2
		atendimento.save()
		self.assertEqual(atendimento.total_dia, 6)
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{"doctype": "Atendimento Medico Diario", "unidade": unidade, "data": "2098-01-31"}
			).insert()
		atendimento.submit()
		self.assertEqual(atendimento.status, "Enviado")

	def test_relatorio_por_periodo(self):
		unidade, especialidades = self.preparar_cadastros()
		self.criar_vigencia(unidade, especialidades, "2097-01-01", "2097-12-31")
		for data, quantidades in (("2097-03-01", (10, 5)), ("2097-03-02", (20, 0)), ("2097-04-01", (99, 99))):
			atendimento = frappe.get_doc(
				{"doctype": "Atendimento Medico Diario", "unidade": unidade, "data": data}
			).insert()
			for linha, quantidade in zip(atendimento.especialidades, quantidades):
				linha.quantidade = quantidade
			atendimento.save()
			atendimento.submit()
		# Rascunho no período não entra na apuração.
		frappe.get_doc({"doctype": "Atendimento Medico Diario", "unidade": unidade, "data": "2097-03-03"}).insert()

		filtros = {"unidade": unidade, "data_inicio": "2097-03-01", "data_fim": "2097-03-31"}
		colunas, linhas, _msg, grafico, resumo = executar_relatorio(filtros)
		por_especialidade = {linha.especialidade: linha for linha in linhas}
		primeira, segunda = (por_especialidade[e.name] for e in especialidades)
		self.assertEqual((primeira.quantidade, segunda.quantidade), (30, 5))
		self.assertEqual((primeira.dias_com_atendimento, segunda.dias_com_atendimento), (2, 1))
		self.assertEqual(primeira.dias_lancados, 2)
		self.assertAlmostEqual(primeira.percentual, 100 * 30 / 35)
		self.assertEqual(resumo[0]["value"], 35)
		self.assertEqual(resumo[1]["value"], 2)
		self.assertTrue(grafico)

		_c, filtradas, *_r = executar_relatorio({**filtros, "especialidade": especialidades[1].name})
		self.assertEqual([linha.especialidade for linha in filtradas], [especialidades[1].name])
		with self.assertRaises(frappe.ValidationError):
			executar_relatorio({**filtros, "data_inicio": "2097-04-01"})

	def test_viewer_nao_pode_buscar(self):
		unidade, _especialidades = self.preparar_cadastros()
		usuario = frappe.get_doc(
			{
				"doctype": "User",
				"email": f"teste-atendimento-{uuid4().hex[:12]}@example.com",
				"first_name": "Teste Atendimento",
				"user_type": "System User",
				"send_welcome_email": 0,
				"roles": [{"role": "Pulse Gestor Viewer"}],
			}
		).insert(ignore_permissions=True)
		anterior = frappe.session.user
		try:
			frappe.set_user(usuario.name)
			self.assertFalse(frappe.has_permission("Atendimento Medico Diario", "create"))
			with self.assertRaises(frappe.PermissionError):
				buscar_vigencia_e_especialidades(unidade, "2098-01-01")
		finally:
			frappe.set_user(anterior)
