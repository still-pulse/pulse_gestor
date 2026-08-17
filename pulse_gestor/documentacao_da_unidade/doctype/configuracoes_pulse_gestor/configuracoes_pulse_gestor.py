# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ConfiguracoesPulseGestor(Document):
	def validate(self):
		if int(self.dias_alerta_vencimento or 0) < 0:
			frappe.throw(_("Os dias de alerta não podem ser negativos."))

	def on_update(self):
		from pulse_gestor.setup.install import sincronizar_dias_alerta

		sincronizar_dias_alerta()
