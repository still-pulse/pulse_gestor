# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

"""Print Formats institucionais do Pulse Gestor (padrao BHCL, ver apps/clm/docs/brand-manifesto.md).

Os formatos sao standard (JSON + HTML em ``<modulo>/print_format/``) e estendem
``clm/templates/print/clm_base.html``. Este modulo define o formato padrao dos DocTypes do ERPNext que
ganharam formato proprio e retira os formatos antigos que existiam so no banco do site.
"""

from __future__ import annotations

import frappe
import pyqrcode
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

# DocType (Core) -> Print Format padrao
DEFAULT_PRINT_FORMATS = {
	"Asset": "Ficha do Ativo Imobilizado",
	"Asset Movement": "Ficha de Movimentacao de Ativos",
}

# Formatos antigos (standard=No, so no banco) substituidos -> novo formato. Sao apenas desabilitados,
# para nao perder o conteudo.
LEGACY_PRINT_FORMATS = {
	"Ficha de Ativo Imobilizado": "Ficha do Ativo Imobilizado",
	"Ficha de Movimentacao de Ativos (antiga)": "Ficha de Movimentacao de Ativos",
}

# A collation do banco ignora acentos: o formato antigo acentuado e o novo em ASCII seriam o mesmo registro e a
# importacao do standard sobrescreveria o antigo. Antes da sincronizacao (before_migrate) o antigo e renomeado.
ACCENTED_LEGACY_NAMES = {
	"Ficha de Movimentação de Ativos": "Ficha de Movimentacao de Ativos (antiga)",
}


def _exact(name):
	"""Print Format com exatamente este nome (a comparacao do banco ignora acentos e caixa)."""
	row = frappe.db.get_value("Print Format", name, ["name", "standard"], as_dict=True)
	return row if row and row.name == name else None


def preserve_accented_legacy_print_formats():
	for old, new in ACCENTED_LEGACY_NAMES.items():
		row = _exact(old)
		if row and row.standard == "No" and not frappe.db.exists("Print Format", new):
			frappe.rename_doc("Print Format", old, new, force=True, show_alert=False, rebuild_search=False)
			frappe.db.set_value("Print Format", new, "disabled", 1)
	frappe.db.commit()


def ensure_default_print_formats():
	"""Define o formato do Pulse Gestor como padrao de cada DocType, idempotente.

	So troca o padrao quando ele esta vazio ou aponta para um formato antigo substituido; uma escolha
	explicita de outro formato feita pelo usuario e preservada.
	"""
	for doctype, print_format in DEFAULT_PRINT_FORMATS.items():
		if not frappe.db.exists("DocType", doctype) or not frappe.db.exists("Print Format", print_format):
			continue
		current = frappe.get_meta(doctype).default_print_format
		replaceable = {*LEGACY_PRINT_FORMATS, *ACCENTED_LEGACY_NAMES}
		if current == print_format or (current and current not in replaceable):
			continue
		make_property_setter(
			doctype,
			None,
			"default_print_format",
			print_format,
			"Data",
			for_doctype=True,
			validate_fields_for_doctype=False,
		)


def retire_legacy_print_formats():
	"""Desabilita os formatos antigos cujo substituto ja existe."""
	for old, new in LEGACY_PRINT_FORMATS.items():
		row = _exact(old)
		if row and row.standard == "No" and frappe.db.exists("Print Format", new):
			frappe.db.set_value("Print Format", old, "disabled", 1)


def qr_data_uri(content: str, scale: int = 4) -> str:
	"""QR Code em PNG (data URI), gerado localmente; exposto como metodo Jinja."""
	if not content:
		return ""
	return "data:image/png;base64," + pyqrcode.create(content, error="M").png_as_base64_str(
		scale=scale, quiet_zone=1
	)
