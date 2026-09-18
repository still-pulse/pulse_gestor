from uuid import uuid4

import frappe
from frappe.tests.utils import FrappeTestCase

from pulse_gestor.indicadores.doctype.atendimento_diario.atendimento_diario import (
	buscar_vigencia_e_especialidades,
	obter_vigencia_e_especialidades,
)


class TestAtendimentoDiario(FrappeTestCase):
	def preparar_cadastros(self):
		unidade = frappe.get_all("Company", fields=["name"], order_by="name asc", limit=1)[0].name
		setor = frappe.get_doc(
			{
				"doctype": "Department",
				"department_name": f"Atendimento Teste {uuid4().hex[:10]}",
				"company": unidade,
			}
		).insert()
		especialidades = [
			frappe.get_doc(
				{"doctype": "Especialidade", "nome_especialidade": f"Especialidade Teste {uuid4().hex[:10]}"}
			).insert()
			for _ in range(2)
		]
		return unidade, setor.name, especialidades

	def test_vigencia_resolucao_lancamento_e_envio(self):
		unidade, setor, especialidades = self.preparar_cadastros()
		vigencia = frappe.get_doc(
			{
				"doctype": "Unidade Especialidade Vigencia",
				"unidade": unidade,
				"setor": setor,
				"data_inicio_vigencia": "2098-01-01",
				"data_fim_vigencia": "2098-01-31",
				"especialidades": [
					{"especialidade": especialidades[0].name, "meta_quantidade": 40, "periodicidade_meta": "Mensal"},
					{"especialidade": especialidades[1].name, "meta_quantidade": 400, "periodicidade_meta": "Anual"},
				],
			}
		).insert()
		resolvido = obter_vigencia_e_especialidades(unidade, setor, "2098-01-31")
		self.assertEqual(resolvido["vigencia"], vigencia.name)
		self.assertEqual(
			[item["especialidade"] for item in resolvido["especialidades"]],
			[item.name for item in especialidades],
		)
		with self.assertRaises(frappe.ValidationError):
			obter_vigencia_e_especialidades(unidade, setor, "2098-02-01")
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Unidade Especialidade Vigencia",
					"unidade": unidade,
					"setor": setor,
					"data_inicio_vigencia": "2098-01-31",
					"especialidades": [
						{"especialidade": especialidades[0].name, "meta_quantidade": 1, "periodicidade_meta": "Mensal"}
					],
				}
			).insert()

		atendimento = frappe.get_doc(
			{"doctype": "Atendimento Diario", "unidade": unidade, "setor": setor, "data": "2098-01-31"}
		).insert()
		self.assertEqual(atendimento.vigencia, vigencia.name)
		self.assertEqual([linha.especialidade for linha in atendimento.especialidades], [e.name for e in especialidades])
		self.assertEqual([linha.meta_quantidade for linha in atendimento.especialidades], [40, 400])
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
		atendimento.especialidades[0].meta_quantidade = 999
		atendimento.especialidades[0].quantidade = 4
		atendimento.especialidades[1].quantidade = 2
		atendimento.save()
		self.assertEqual(atendimento.total_dia, 6)
		self.assertEqual(atendimento.especialidades[0].meta_quantidade, 40)
		vigencia.especialidades[0].meta_quantidade = 50
		vigencia.save()
		atendimento.especialidades[0].quantidade = 5
		atendimento.save()
		self.assertEqual(atendimento.total_dia, 7)
		self.assertEqual(atendimento.especialidades[0].meta_quantidade, 40)
		with self.assertRaises(frappe.ValidationError):
			frappe.get_doc(
				{"doctype": "Atendimento Diario", "unidade": unidade, "setor": setor, "data": "2098-01-31"}
			).insert()
		atendimento.submit()
		self.assertEqual(atendimento.status, "Enviado")

	def test_setor_de_outra_unidade_e_viewer_nao_pode_buscar(self):
		unidade, setor, especialidades = self.preparar_cadastros()
		outra = frappe.get_all("Company", filters={"name": ["!=", unidade]}, fields=["name"], limit=1)
		if outra:
			with self.assertRaises(frappe.ValidationError):
				frappe.get_doc(
					{
						"doctype": "Unidade Especialidade Vigencia",
						"unidade": outra[0].name,
						"setor": setor,
						"data_inicio_vigencia": "2098-01-01",
						"especialidades": [
							{"especialidade": especialidades[0].name, "meta_quantidade": 1, "periodicidade_meta": "Mensal"}
						],
					}
				).insert()
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
			self.assertFalse(frappe.has_permission("Atendimento Diario", "create"))
			with self.assertRaises(frappe.PermissionError):
				buscar_vigencia_e_especialidades(unidade, setor, "2098-01-01")
		finally:
			frappe.set_user(anterior)
