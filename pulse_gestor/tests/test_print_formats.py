"""Guarda do padrao institucional dos Print Formats do Pulse Gestor (apps/clm/docs/brand-manifesto.md)."""

import re
from unittest.mock import patch

import frappe
from clm.clm.services.pdf_engine import PDF_ENGINE_MODULES, generate_pdf
from frappe.tests.utils import FrappeTestCase
from frappe.www.printview import get_rendered_template

from pulse_gestor.print_formats import DEFAULT_PRINT_FORMATS, LEGACY_PRINT_FORMATS

BASE_TEMPLATE = "clm/templates/print/clm_base.html"
FORMATS = ("Ata de Reuniao de Comissao", "Convocacao para Reuniao de Comissao")
ASSET_FORMATS = ("Ficha do Ativo Imobilizado", "Ficha de Movimentacao de Ativos")
TERMO_FORMATS = ("Termo de Responsabilidade do Ativo", "Termo de Responsabilidade de Movimentacao")


def format_html(name):
	module = frappe.db.get_value("Print Format", name, "module")
	folder = frappe.scrub(name)
	path = frappe.get_app_path("pulse_gestor", frappe.scrub(module), "print_format", folder, f"{folder}.html")
	return frappe.utils.get_html_format(path)


def new_doc(doctype, **kwargs):
	doc = frappe.new_doc(doctype)
	doc.name = "TEST-001"
	doc.update(kwargs)
	return doc


def meeting(**kwargs):
	return new_doc("Reuniao de Comissao", **kwargs)


def render(print_format, doc):
	with patch("frappe.www.printview.validate_print_permission"):
		return get_rendered_template(
			doc, print_format=frappe.get_doc("Print Format", print_format), no_letterhead=True
		)


def visible_text(html):
	return re.sub(r"<style.*?</style>|<[^>]+>", "", html, flags=re.S)


class TestComissoesPrintFormats(FrappeTestCase):
	def test_every_format_follows_the_institutional_standard(self):
		for name in FORMATS + ASSET_FORMATS + TERMO_FORMATS:
			with self.subTest(print_format=name):
				self.assertTrue(name.isascii())
				doc = frappe.get_doc("Print Format", name)
				self.assertIn(doc.module, PDF_ENGINE_MODULES)
				self.assertTrue(doc.custom_format)
				self.assertEqual(doc.print_format_type, "Jinja")
				self.assertEqual(
					(doc.margin_top, doc.margin_bottom, doc.margin_left, doc.margin_right), (4, 4, 20, 20)
				)
				html = format_html(name)
				self.assertIn(BASE_TEMPLATE, html)
				self.assertNotIn("<style", html)
				self.assertIsNone(re.search(r"font-family|@page|#[0-9a-fA-F]{3,6}\b", html))

	def test_meeting_declares_the_minutes_as_default_format(self):
		self.assertEqual(frappe.get_meta("Reuniao de Comissao").default_print_format, FORMATS[0])

	def test_blank_meeting_renders_without_missing_values(self):
		for name in FORMATS:
			with self.subTest(print_format=name):
				html = render(name, meeting())
				self.assertIn("clm-pdf-meta", html)
				self.assertIsNone(re.search(r"\bNone\b|\bnull\b|\bundefined\b", visible_text(html)))
				self.assertTrue(generate_pdf(name, html, pdf_generator="weasyprint").startswith(b"%PDF"))

	def test_minutes_list_attendees_and_their_signatures(self):
		doc = meeting(data_reuniao="2026-10-14 09:30:00", local_reuniao="Sala <1>")
		for nome, status in (
			("Ana", "Presente"),
			("Bruno", "Ausente"),
			("Carla", "Presente"),
			("Davi", "Presente"),
		):
			doc.append("participantes", {"nome": nome, "funcao": "Membro", "status_presenca": status})
		html = render(FORMATS[0], doc)
		text = visible_text(html)
		self.assertIn("14/10/2026", text)
		self.assertIn("às 09:30", text)
		self.assertIn("Sala &lt;1&gt;", html)
		self.assertIn("com a presença de 3 de 4 participantes", text)
		# 3 presentes em linhas de 2: a segunda linha e completada por uma celula vazia, sem filete.
		self.assertEqual(html.count('class="clm-signatures"'), 2)
		self.assertEqual(html.count("clm-signature-line clm-signature-empty"), 1)
		self.assertNotIn("BRUNO", text.upper().split("ASSINATURAS DOS PRESENTES")[-1])
		self.assertIn("clm-tag-bad", html)

	def test_asset_doctypes_use_the_institutional_formats_by_default(self):
		for doctype, print_format in DEFAULT_PRINT_FORMATS.items():
			with self.subTest(doctype=doctype):
				self.assertEqual(frappe.get_meta(doctype).default_print_format, print_format)

	def test_legacy_asset_formats_are_disabled(self):
		for old in LEGACY_PRINT_FORMATS:
			if frappe.db.get_value("Print Format", old) == old:
				with self.subTest(print_format=old):
					self.assertEqual(frappe.db.get_value("Print Format", old, "disabled"), 1)

	def test_new_formats_are_not_retired_through_accent_insensitive_names(self):
		for name in ASSET_FORMATS:
			self.assertEqual(frappe.db.get_value("Print Format", name, "disabled"), 0)

	def test_blank_asset_documents_render_without_missing_values(self):
		for name, doctype in zip(ASSET_FORMATS, ("Asset", "Asset Movement"), strict=True):
			with self.subTest(print_format=name):
				html = render(name, new_doc(doctype))
				self.assertIn("clm-pdf-meta", html)
				self.assertIn("data:image/png;base64,", html)
				self.assertNotIn("api.qrserver.com", html)
				self.assertIsNone(re.search(r"\bNone\b|\bnull\b|\bundefined\b", visible_text(html)))
				self.assertTrue(generate_pdf(name, html, pdf_generator="weasyprint").startswith(b"%PDF"))

	def test_asset_sheet_shows_the_bhcl_control_number_as_reference(self):
		html = render(
			ASSET_FORMATS[0],
			new_doc("Asset", asset_name="Monitor", **{"custom_número_de_controle_bhcl": "BH-42"}),
		)
		self.assertIn('data-ref="Controle BHCL nº BH-42"', html)
		self.assertIn("ID: TEST-001", html)

	def test_blank_custody_terms_render_without_missing_values(self):
		for name, doctype in zip(TERMO_FORMATS, ("Asset", "Asset Movement"), strict=True):
			with self.subTest(print_format=name):
				html = render(name, new_doc(doctype))
				self.assertIn("Termo de Responsabilidade", html)
				self.assertIsNone(re.search(r"\bNone\b|\bnull\b|\bundefined\b", visible_text(html)))
				self.assertTrue(generate_pdf(name, html, pdf_generator="weasyprint").startswith(b"%PDF"))

	def test_movement_term_groups_assets_by_custodian(self):
		employees = frappe.get_all("Employee", pluck="name", limit=2)
		if len(employees) < 2:
			self.skipTest("Sem colaboradores suficientes")
		doc = new_doc("Asset Movement", purpose="Transfer")
		for asset_name, employee in (("Mesa", employees[0]), ("Cadeira", employees[1]), ("Monitor", None)):
			doc.append("assets", {"asset_name": asset_name, "to_employee": employee})
		html = render(TERMO_FORMATS[1], doc)
		self.assertEqual(html.count("Bens sob responsabilidade de "), 2)
		self.assertNotIn("Monitor", visible_text(html))
