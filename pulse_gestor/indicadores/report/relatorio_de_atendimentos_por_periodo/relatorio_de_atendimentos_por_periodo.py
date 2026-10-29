import frappe
from frappe import _
from frappe.utils import getdate


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.unidade or not filters.data_inicio or not filters.data_fim:
		frappe.throw(_("Informe unidade, data início e data fim."))
	if getdate(filters.data_inicio) > getdate(filters.data_fim):
		frappe.throw(_("A data início não pode ser posterior à data fim."))

	params = {
		"unidade": filters.unidade,
		"data_inicio": filters.data_inicio,
		"data_fim": filters.data_fim,
		"especialidade": filters.especialidade,
	}
	# Só entram lançamentos enviados; a linha guarda a especialidade vigente na data do lançamento.
	data = frappe.db.sql(
		"""
		SELECT linha.especialidade,
			SUM(linha.quantidade) AS quantidade,
			COUNT(DISTINCT CASE WHEN linha.quantidade > 0 THEN diario.data END) AS dias_com_atendimento,
			COUNT(DISTINCT diario.data) AS dias_lancados
		FROM `tabAtendimento Medico Diario` diario
		JOIN `tabAtendimento Medico Diario Especialidade` linha
			ON linha.parent = diario.name AND linha.parenttype = 'Atendimento Medico Diario'
		WHERE diario.unidade = %(unidade)s
			AND diario.data BETWEEN %(data_inicio)s AND %(data_fim)s
			AND diario.docstatus = 1
			AND (%(especialidade)s IS NULL OR %(especialidade)s = '' OR linha.especialidade = %(especialidade)s)
		GROUP BY linha.especialidade
		ORDER BY quantidade DESC, linha.especialidade
		""",
		params,
		as_dict=True,
	)
	total = sum(row.quantidade or 0 for row in data)
	for row in data:
		row.quantidade = row.quantidade or 0
		row.percentual = 100 * row.quantidade / total if total else 0
		row.media_por_dia = row.quantidade / row.dias_lancados if row.dias_lancados else 0

	dias_lancados = frappe.db.sql(
		"""
		SELECT COUNT(DISTINCT data) FROM `tabAtendimento Medico Diario`
		WHERE unidade = %(unidade)s AND data BETWEEN %(data_inicio)s AND %(data_fim)s AND docstatus = 1
		""",
		params,
	)[0][0]
	summary = [
		{"label": _("Total de atendimentos"), "value": int(total), "datatype": "Int", "indicator": "Blue"},
		{"label": _("Dias com lançamento"), "value": int(dias_lancados), "datatype": "Int", "indicator": "Green"},
		{
			"label": _("Média diária"),
			"value": round(total / dias_lancados, 1) if dias_lancados else 0,
			"datatype": "Float",
			"indicator": "Orange",
		},
	]
	return get_columns(), data, None, get_chart(data), summary


def get_chart(data):
	if not any(row.quantidade for row in data):
		return None
	return {
		"data": {
			"labels": [row.especialidade for row in data],
			"datasets": [{"name": _("Atendimentos"), "values": [row.quantidade for row in data]}],
		},
		"type": "bar",
		"height": 300,
	}


def get_columns():
	return [
		{
			"fieldname": "especialidade",
			"label": _("Especialidade"),
			"fieldtype": "Link",
			"options": "Especialidade",
			"width": 240,
		},
		{"fieldname": "quantidade", "label": _("Atendimentos"), "fieldtype": "Int", "width": 130},
		{"fieldname": "percentual", "label": _("% do total"), "fieldtype": "Percent", "width": 120},
		{
			"fieldname": "dias_com_atendimento",
			"label": _("Dias com atendimento"),
			"fieldtype": "Int",
			"width": 160,
		},
		{"fieldname": "dias_lancados", "label": _("Dias lançados"), "fieldtype": "Int", "width": 130},
		{"fieldname": "media_por_dia", "label": _("Média por dia lançado"), "fieldtype": "Float", "precision": 1, "width": 170},
	]
