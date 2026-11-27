# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

"""Métodos whitelisted precisam de type hints (regra missing-argument-type-hint do semgrep do Frappe)."""

import inspect

from frappe.tests.utils import FrappeTestCase

from pulse_gestor.comissoes import dashboard
from pulse_gestor.comissoes.doctype.reuniao_de_comissao import reuniao_de_comissao
from pulse_gestor.indicadores.doctype.atendimento_medico_diario import atendimento_medico_diario
from pulse_gestor.indicadores.doctype.classificacao_de_risco_diaria import classificacao_de_risco_diaria

METODOS = (
	dashboard.cartao_reunioes_proximas,
	dashboard.cartao_mandatos_a_vencer,
	dashboard.cartao_comissoes_sem_reuniao,
	dashboard.cartao_presenca_media,
	dashboard.proximas_reunioes,
	reuniao_de_comissao.buscar_membros,
	reuniao_de_comissao.convocar,
	atendimento_medico_diario.buscar_vigencia_e_especialidades,
	classificacao_de_risco_diaria.buscar_protocolo_e_niveis,
)


class TestArgumentosWhitelist(FrappeTestCase):
	def test_todos_os_argumentos_tem_type_hint(self):
		for metodo in METODOS:
			funcao = inspect.unwrap(metodo)
			for nome, parametro in inspect.signature(funcao).parameters.items():
				with self.subTest(metodo=funcao.__qualname__, argumento=nome):
					self.assertIsNot(parametro.annotation, inspect.Parameter.empty)

	def test_cartoes_aceitam_filtros_como_texto_json_ou_dict(self):
		# O Frappe envia `filters` do Number Card como string JSON; chamadas internas podem passar dict.
		for filtros in (None, "{}", {}):
			with self.subTest(filtros=filtros):
				self.assertIn("value", dashboard.cartao_presenca_media(filters=filtros))
				self.assertIn("value", dashboard.cartao_comissoes_sem_reuniao(filters=filtros))

	def test_proximas_reunioes_aceita_limite_vindo_da_requisicao_como_texto(self):
		self.assertLessEqual(len(dashboard.proximas_reunioes(limite="3")), 3)
		self.assertIsInstance(dashboard.proximas_reunioes(limite=2), list)
