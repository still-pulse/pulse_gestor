# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr


class TipodeDocumentodaUnidade(Document):
	def validate(self):
		self.tipo = cstr(self.tipo).strip()
		if not self.tipo:
			frappe.throw(_("Informe o tipo do documento."))
