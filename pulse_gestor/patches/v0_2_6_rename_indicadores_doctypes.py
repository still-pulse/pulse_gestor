import re

import frappe
from frappe.model.rename_doc import rename_doc
from frappe.query_builder import builder  # nosemgrep: frappe-monkey-patching-not-allowed

RENAMES = (
	("Protocolo Nível", "Protocolo Nivel"),
	("Unidade Protocolo Vigência", "Unidade Protocolo Vigencia"),
	("Classificação Diária Nível", "Classificacao Diaria Nivel"),
	("Classificação de Risco Diária", "Classificacao de Risco Diaria"),
)


def execute():
	# Patch unico e historico: a troca do regex e temporaria (restaurada em `finally`) e o Frappe 15 nao oferece
	# hook para isso. O semgrep reporta o match desde o import, onde fica o nosemgrep.
	# O validador deste Frappe 15 rejeita os nomes antigos durante a renomeação.
	old_pattern = builder.TABLE_NAME_PATTERN
	builder.TABLE_NAME_PATTERN = re.compile(r"^[\w -]*$")
	try:
		for old, new in RENAMES:
			if _exists_exactly(old):
				if _exists_exactly(new):
					frappe.throw(f"Os DocTypes {old} e {new} existem simultaneamente.")
				rename_doc(
					"DocType", old, new, force=True, ignore_permissions=True, show_alert=False, validate=False
				)
	finally:
		builder.TABLE_NAME_PATTERN = old_pattern


def _exists_exactly(name):
	return bool(frappe.db.sql("SELECT 1 FROM `tabDocType` WHERE BINARY name = BINARY %s", name))
