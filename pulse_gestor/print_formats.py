# Copyright (c) 2026, StillPulse Tecnologia LTDA and contributors
# For license information, please see license.txt

"""Institutional Print Formats of Pulse Gestor (see apps/clm/docs/brand-manifesto.md).

The formats are standard (JSON + HTML in ``<module>/print_format/``) and extend
``clm/templates/print/clm_base.html``. This module sets the default format of the ERPNext DocTypes that
got their own format and retires the old formats that existed only in the site database.
"""

from __future__ import annotations

import frappe
import pyqrcode
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

# DocType (Core) -> default Print Format
DEFAULT_PRINT_FORMATS = {
	"Asset": "Ficha do Ativo Imobilizado",
	"Asset Movement": "Ficha de Movimentacao de Ativos",
}

# Legacy formats (standard=No, database only) that were replaced -> new format. They are only disabled,
# so that no content is lost.
LEGACY_PRINT_FORMATS = {
	"Ficha de Ativo Imobilizado": "Ficha do Ativo Imobilizado",
	"Ficha de Movimentacao de Ativos (antiga)": "Ficha de Movimentacao de Ativos",
}

# The database collation ignores accents: the old accented format and the new ASCII one would be the same record,
# and importing the standard would overwrite the old one. Before the sync (before_migrate) the old one is renamed.
ACCENTED_LEGACY_NAMES = {
	"Ficha de Movimentação de Ativos": "Ficha de Movimentacao de Ativos (antiga)",
}


def _exact(name):
	"""Print Format with exactly this name (the database comparison ignores accents and case)."""
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
	"""Set the Pulse Gestor format as the default of each DocType (idempotent).

	The default is replaced only when it is empty or points to a replaced legacy format; an explicit
	choice of another format made by the user is preserved.
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
	"""Disable legacy formats whose replacement already exists."""
	for old, new in LEGACY_PRINT_FORMATS.items():
		row = _exact(old)
		if row and row.standard == "No" and frappe.db.exists("Print Format", new):
			frappe.db.set_value("Print Format", old, "disabled", 1)


def qr_data_uri(content: str, scale: int = 4) -> str:
	"""QR Code as PNG (data URI), generated locally; exposed as a Jinja method."""
	if not content:
		return ""
	return "data:image/png;base64," + pyqrcode.create(content, error="M").png_as_base64_str(
		scale=scale, quiet_zone=1
	)
