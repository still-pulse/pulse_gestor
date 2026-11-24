# Copyright (c) 2026, StillPulse Tecnologia LTDA and contributors
# For license information, please see license.txt

"""Prepare a fresh (CI) site with the Asset Custom Fields, which were created by hand in production.

Not called by any hook: the app does not create these fields on production sites. Idempotent.
"""

from __future__ import annotations

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

FIELDS = {
	"Asset": [
		{"fieldname": "custom_número_de_controle_bhcl", "label": "Número de Controle BHCL"},
		{"fieldname": "custom_número_patrimônio_prefeitura", "label": "Número Patrimônio Prefeitura"},
		{"fieldname": "custom_utilização", "label": "Utilização"},
		{"fieldname": "custom_estado_de_conservação", "label": "Estado de Conservação"},
	],
	"Location": [
		{"fieldname": "custom_empresa", "label": "Empresa", "fieldtype": "Link", "options": "Company"}
	],
}


def create_asset_custom_fields():
	fields = {doctype: [{"fieldtype": "Data", **field} for field in rows] for doctype, rows in FIELDS.items()}
	create_custom_fields(fields, update=False)
	frappe.db.commit()
