# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

import json
import unicodedata

import frappe
from frappe.tests.utils import FrappeTestCase

from pulse_gestor import hooks

ESPERADOS = {
	"Location-custom_empresa": ("Location", "Link", "Company"),
	"Asset-custom_número_de_controle_bhcl": ("Asset", "Data", None),
	"Asset-custom_número_patrimônio_prefeitura": ("Asset", "Data", None),
	"Asset-custom_utilização": ("Asset", "Select", "\nEm uso\nOcioso\nEm manutenção\nInservível"),
	"Asset-custom_estado_de_conservação": (
		"Asset",
		"Select",
		"\nExcelente\nBom\nRegular\nRuim\nPéssimo",
	),
}


def _fixture_do_hook():
	return next(f for f in hooks.fixtures if f.get("dt") == "Custom Field")


class TestFixturesDePatrimonio(FrappeTestCase):
	def test_filtro_de_fixture_lista_os_cinco_campos(self):
		self.assertEqual(set(_fixture_do_hook()["filters"][0][2]), set(ESPERADOS))

	def test_arquivo_de_fixture_traz_exatamente_os_campos_do_filtro(self):
		caminho = frappe.get_app_path("pulse_gestor", "fixtures", "custom_field.json")
		with open(caminho, encoding="utf-8") as arquivo:
			dados = json.load(arquivo)
		self.assertEqual({d["name"] for d in dados}, set(ESPERADOS))
		for d in dados:
			with self.subTest(campo=d["name"]):
				self.assertEqual(d["doctype"], "Custom Field")
				self.assertEqual(d["name"], f"{d['dt']}-{d['fieldname']}")
				# nada de dados voláteis ou de pessoas no arquivo versionado
				for chave in ("owner", "creation", "modified", "modified_by", "idx", "docstatus"):
					self.assertNotIn(chave, d)

	def test_campos_existem_no_site_a_partir_das_fixtures(self):
		for nome, (doctype, fieldtype, options) in ESPERADOS.items():
			with self.subTest(campo=nome):
				# o nome pode estar em NFC ou NFD conforme a origem: compara normalizado
				existentes = {
					unicodedata.normalize("NFC", n): n
					for n in frappe.get_all("Custom Field", filters={"dt": doctype}, pluck="name")
				}
				self.assertIn(unicodedata.normalize("NFC", nome), existentes)
				campo = frappe.get_doc("Custom Field", existentes[unicodedata.normalize("NFC", nome)])
				self.assertEqual(campo.fieldtype, fieldtype)
				self.assertEqual(campo.options or None, options)
