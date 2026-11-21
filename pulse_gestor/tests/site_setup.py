# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

"""Prepara um site novo (CI) com os Custom Fields de Patrimônio, que em produção foram criados à mão.

Não é chamado por hook: o app não cria esses campos em sites de produção. Idempotente.
"""

from __future__ import annotations

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CAMPOS = {
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


def criar_campos_de_patrimonio():
	campos = {
		doctype: [{"fieldtype": "Data", **campo} for campo in lista] for doctype, lista in CAMPOS.items()
	}
	create_custom_fields(campos, update=False)
	frappe.db.commit()
