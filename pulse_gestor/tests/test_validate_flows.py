# Copyright (c) 2026, StillPulse Tecnologia LTDA and contributors
# For license information, please see license.txt

"""Smoke tests of `validate()` of the main controllers and of the minutes signature context.

They exist to catch broken internal calls after renames (a `validate()` that calls a method that no longer
exists). Meant to run under `bench run-tests --app pulse_gestor`.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

try:
	from pulse_gestor.signature_profiles import CommitteeMeetingProfile
except ImportError:  # assinatura_eletronica (optional) not installed
	CommitteeMeetingProfile = None

CLASSIFICATION_MODULE = (
	"pulse_gestor.indicadores.doctype.classificacao_de_risco_diaria.classificacao_de_risco_diaria"
)
VISIT_MODULE = "pulse_gestor.indicadores.doctype.atendimento_medico_diario.atendimento_medico_diario"


class TestValidateFlows(FrappeTestCase):
	def test_unit_documentation_validate_sets_status(self):
		doc = frappe.new_doc("Documentacao da Unidade")
		doc.update({"possui_validade": 0, "arquivo_pdf": "/private/files/alvara.pdf"})
		doc.validate()
		self.assertEqual(doc.status, "Sem validade")

	def test_committee_type_validate_records_bylaws_history(self):
		doc = frappe.new_doc("Tipo de Comissao")
		doc.update({"nome_tipo": " Teste unitario ", "regimento": "<p>Texto</p>"})
		with patch("frappe.db.exists", return_value=None):
			doc.validate()
		self.assertEqual(doc.nome_tipo, "Teste unitario")
		self.assertEqual(len(doc.historico_regimento), 1)
		self.assertEqual(doc.historico_regimento[0].versao, 1)

	def test_daily_classification_validate_loads_levels_and_totals(self):
		resolved = {
			"protocolo": "PROTO-1",
			"niveis": [
				{"nivel": "Vermelho", "cor": "#ff0000", "tempo_maximo_espera_min": 0},
				{"nivel": "Verde", "cor": "#00ff00", "tempo_maximo_espera_min": 120},
			],
		}
		doc = frappe.new_doc("Classificacao de Risco Diaria")
		doc.update({"unidade": "Unidade Teste", "data": "2099-01-31"})
		with (
			patch(f"{CLASSIFICATION_MODULE}.resolve_protocol_and_levels", return_value=resolved),
			patch("frappe.db.exists", return_value=None),
		):
			doc.validate()
		self.assertEqual(doc.protocolo, "PROTO-1")
		self.assertEqual(len(doc.niveis_classificados), 2)
		self.assertEqual(doc.total_classificados, 0)
		self.assertEqual(doc.status, "Rascunho")

	def test_daily_visit_validate_loads_specialties_and_totals(self):
		resolved = {"vigencia": "VIG-1", "especialidades": [{"especialidade": "Clinica"}]}
		doc = frappe.new_doc("Atendimento Medico Diario")
		doc.update({"unidade": "Unidade Teste", "data": "2098-01-31"})
		with (
			patch(f"{VISIT_MODULE}.resolve_validity_and_specialties", return_value=resolved),
			patch("frappe.db.exists", return_value=None),
		):
			doc.validate()
		self.assertEqual(doc.vigencia, "VIG-1")
		self.assertEqual(len(doc.especialidades), 1)
		self.assertEqual(doc.total_dia, 0)


@unittest.skipUnless(CommitteeMeetingProfile, "assinatura_eletronica ausente")
class TestMinutesSignatureContext(FrappeTestCase):
	def test_minutes_content_lists_only_present_participants(self):
		participants = [
			SimpleNamespace(membro_origem="MEM-B", status_presenca="Presente", funcao="Membro"),
			SimpleNamespace(membro_origem="MEM-A", status_presenca="Ausente", funcao="Membro"),
			SimpleNamespace(membro_origem="MEM-C", status_presenca="Presente", funcao=None),
		]
		doc = SimpleNamespace(
			tipo_comissao="TPCOM-1",
			mandato_comissao="MAND-1",
			data_reuniao="2026-10-14 09:30:00",
			local_reuniao="Sala 1",
			pauta=[SimpleNamespace(assunto="Item 1")],
			deliberacoes="<p>Ok</p>",
			encaminhamentos_conclusoes="",
			participantes=participants,
		)
		profile = CommitteeMeetingProfile()
		with patch("frappe.db.get_value", return_value="Comissao de Teste"):
			content = profile.conteudo(doc)
		self.assertEqual(content["presentes"], ["MEM-B", "MEM-C"])
		self.assertEqual(content["comissao"], "Comissao de Teste")
		self.assertEqual([s.parte for s in profile.signatarios(doc)], ["MEM-B", "MEM-C"])
