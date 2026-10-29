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
	}
	# O protocolo já é resolvido pela vigência ao gravar cada lançamento diário.
	# Agrupar também pelo tempo guardado na linha separa mudanças posteriores do alvo.
	data = frappe.db.sql(
		"""
		SELECT diario.protocolo, linha.idx AS ordem, linha.nivel,
			CASE WHEN linha.tempo_snapshot_preenchido = 1
				THEN linha.tempo_maximo_espera_min END AS tempo_maximo_espera_min,
			SUM(linha.qtd_pacientes_classificados) AS qtd_pacientes_classificados,
			SUM(diario.total_classificados) AS total_classificados
		FROM `tabClassificacao de Risco Diaria` diario
		JOIN `tabClassificacao Diaria Nivel` linha
			ON linha.parent = diario.name AND linha.parenttype = 'Classificacao de Risco Diaria'
		WHERE diario.unidade = %(unidade)s
			AND diario.data BETWEEN %(data_inicio)s AND %(data_fim)s
			AND diario.docstatus = 1
		GROUP BY diario.protocolo, linha.idx, linha.nivel,
			linha.tempo_snapshot_preenchido, linha.tempo_maximo_espera_min
		ORDER BY diario.protocolo, linha.idx, linha.tempo_snapshot_preenchido,
			linha.tempo_maximo_espera_min
		""",
		params,
		as_dict=True,
	)
	for row in data:
		row.percentual_classificacao = (
			100 * row.qtd_pacientes_classificados / row.total_classificados
			if row.total_classificados
			else 0
		)

	total = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(total_classificados), 0)
		FROM `tabClassificacao de Risco Diaria`
		WHERE unidade = %(unidade)s
			AND data BETWEEN %(data_inicio)s AND %(data_fim)s
			AND docstatus = 1
		""",
		params,
	)[0][0]
	summary = [
		{
			"label": _("Total classificados no período"),
			"value": int(total),
			"datatype": "Int",
			"indicator": "Blue",
		}
	]
	return get_columns(), data, None, get_chart(data, params), summary


def get_chart(data, params):
	por_nivel = {}
	for row in data:
		por_nivel[row.nivel] = por_nivel.get(row.nivel, 0) + row.qtd_pacientes_classificados

	if not any(por_nivel.values()):
		return None

	# A cor pode mudar entre protocolos ou lançamentos; vale a mais recente registrada no período.
	cores = {}
	for row in frappe.db.sql(
		"""
		SELECT linha.nivel, linha.cor
		FROM `tabClassificacao de Risco Diaria` diario
		JOIN `tabClassificacao Diaria Nivel` linha
			ON linha.parent = diario.name AND linha.parenttype = 'Classificacao de Risco Diaria'
		WHERE diario.unidade = %(unidade)s
			AND diario.data BETWEEN %(data_inicio)s AND %(data_fim)s
			AND diario.docstatus = 1
			AND linha.cor IS NOT NULL AND linha.cor != ''
		ORDER BY diario.data DESC, diario.name DESC
		""",
		params,
		as_dict=True,
	):
		cores.setdefault(row.nivel, row.cor)

	cores_padrao = ["#7cd6fd", "#5e64ff", "#ff5858", "#ffa00a", "#36b37e"]
	return {
		"data": {
			"labels": list(por_nivel),
			"datasets": [{"name": _("Classificados"), "values": list(por_nivel.values())}],
		},
		"type": "donut",
		"colors": [cores.get(nivel) or cores_padrao[i % len(cores_padrao)] for i, nivel in enumerate(por_nivel)],
		"height": 300,
	}


def get_columns():
	return [
		{
			"fieldname": "protocolo",
			"label": _("Protocolo"),
			"fieldtype": "Link",
			"options": "Protocolo de Triagem",
			"width": 220,
		},
		{"fieldname": "nivel", "label": _("Nível"), "fieldtype": "Data", "width": 150},
		{
			"fieldname": "tempo_maximo_espera_min",
			"label": _("Tempo máximo de espera (min)"),
			"fieldtype": "Int",
			"width": 210,
		},
		{
			"fieldname": "qtd_pacientes_classificados",
			"label": _("Classificados no nível"),
			"fieldtype": "Int",
			"width": 180,
		},
		{
			"fieldname": "total_classificados",
			"label": _("Total classificados na escala"),
			"fieldtype": "Int",
			"width": 200,
		},
		{
			"fieldname": "percentual_classificacao",
			"label": _("% Classificação"),
			"fieldtype": "Percent",
			"width": 160,
		},
	]
