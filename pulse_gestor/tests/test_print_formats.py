# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

"""Guarda do padrao institucional dos Print Formats de Comissoes (apps/clm/docs/brand-manifesto.md)."""

import re

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.www.printview import get_rendered_template

FORMATOS = ("Ata de Reuniao de Comissao", "Convocacao para Reuniao de Comissao")
BASE_TEMPLATE = "clm/templates/print/clm_base.html"


def formato_html(name):
	pasta = frappe.scrub(name)
	return frappe.utils.get_html_format(frappe.get_app_path("pulse_gestor", "comissoes", "print_format", pasta, f"{pasta}.html"))


def reuniao_de_teste():
	doc = frappe.new_doc("Reuniao de Comissao")
	doc.update({"empresa": "BHCL", "data_reuniao": "2026-10-20 14:00:00", "data_convocacao": "2026-10-16", "local_reuniao": "Sala 1"})
	doc.append("pauta", {"assunto": "Abertura"})
	doc.append("participantes", {"nome": "Maria Silva", "funcao": "Presidente", "status_presenca": "Presente"})
	doc.append("participantes", {"nome": "Joao Souza", "funcao": "Membro", "status_presenca": "Ausente"})
	doc.name = "RC-TESTE"
	return doc


class TestComissoesPrintFormats(FrappeTestCase):
	def test_formatos_seguem_o_padrao_institucional(self):
		for nome in FORMATOS:
			with self.subTest(print_format=nome):
				pf = frappe.get_doc("Print Format", nome)
				self.assertTrue(pf.custom_format)
				self.assertEqual(pf.print_format_type, "Jinja")
				self.assertEqual((pf.margin_top, pf.margin_bottom, pf.margin_left, pf.margin_right), (4, 4, 20, 20))
				html = formato_html(nome)
				self.assertIn(BASE_TEMPLATE, html)
				self.assertNotIn("<style", html)
				self.assertIsNone(re.search(r"font-family|@page|#[0-9a-fA-F]{3,6}\b", html))

	def test_render_usa_comissao_e_data_como_referencia(self):
		doc = reuniao_de_teste()
		for nome in FORMATOS:
			with self.subTest(print_format=nome):
				html = get_rendered_template(doc, print_format=frappe.get_doc("Print Format", nome), no_letterhead=1)
				self.assertIn("Reunião de 20/10/2026", html)
				self.assertIn("clm-signature", html)
				self.assertNotIn("None", html)
