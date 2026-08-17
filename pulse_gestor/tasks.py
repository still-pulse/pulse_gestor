# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

"""Jobs agendados do Pulse Gestor."""

from __future__ import annotations

import frappe
from frappe.utils import nowdate

from pulse_gestor.utils import calcular_dias_para_vencimento, calcular_status

DOCTYPE = "Documentacao da Unidade"


def atualizar_status_documentos():
	"""Recalcula status e dias para vencimento de todos os documentos."""
	hoje = nowdate()
	documentos = frappe.get_all(
		DOCTYPE,
		fields=["name", "possui_validade", "data_fim", "status", "dias_para_vencimento"],
	)

	atualizados = 0
	for doc in documentos:
		novo_status = calcular_status(doc.possui_validade, doc.data_fim, hoje)
		novos_dias = calcular_dias_para_vencimento(doc.possui_validade, doc.data_fim, hoje)

		valores = {}
		if doc.status != novo_status:
			valores["status"] = novo_status
		if doc.dias_para_vencimento != novos_dias:
			valores["dias_para_vencimento"] = novos_dias

		if not valores:
			continue

		frappe.db.set_value(DOCTYPE, doc.name, valores, update_modified=False)
		atualizados += 1

	if atualizados:
		frappe.db.commit()
		frappe.logger("pulse_gestor").info("Status atualizado em %s documento(s).", atualizados)
