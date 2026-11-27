from itertools import groupby

from frappe import _

from pulse_gestor.patrimonio.report.utils import buscar_ativos, colunas_do_ativo, resumo


def execute(filters=None):
	ativos = buscar_ativos(filters)
	ativos.sort(key=lambda r: (r.empresa or "", r.localizacao or "", r.nome_do_bem or "", r.ativo))

	# Uma linha por localização (com quantidade e valores), seguida dos seus ativos.
	data, totais = [], []
	for (empresa, local), grupo in groupby(ativos, key=lambda r: (r.empresa, r.localizacao)):
		grupo = list(grupo)
		chave = f"{empresa}::{local or ''}"
		nome = local or _("Sem localização")
		data.append(
			{
				"id": chave,
				"parent": None,
				"indent": 0,
				"descricao": nome,
				"empresa": empresa,
				"quantidade": len(grupo),
				"valor_aquisicao": sum(r.valor_aquisicao or 0 for r in grupo),
				"valor_contabil": sum(r.valor_contabil or 0 for r in grupo),
			}
		)
		totais.append((nome, len(grupo)))
		for row in grupo:
			row.update(id=row.ativo, parent=chave, indent=1, descricao=row.nome_do_bem, quantidade=1)
			data.append(row)

	extra = [{"label": _("Localizações"), "value": len(totais), "datatype": "Int", "indicator": "Blue"}]
	return get_columns(), data, None, get_chart(totais), resumo(ativos, extra)


def get_chart(totais):
	if not totais:
		return None
	maiores = sorted(totais, key=lambda t: t[1], reverse=True)[:15]
	return {
		"data": {
			"labels": [nome for nome, _qtd in maiores],
			"datasets": [{"name": _("Ativos"), "values": [qtd for _nome, qtd in maiores]}],
		},
		"type": "bar",
		"title": _("Localizações com mais ativos"),
	}


def get_columns():
	return [
		{"label": _("Localização / bem"), "fieldname": "descricao", "fieldtype": "Data", "width": 320},
		{"label": _("Ativo"), "fieldname": "ativo", "fieldtype": "Link", "options": "Asset", "width": 140},
		{"label": _("Qtd."), "fieldname": "quantidade", "fieldtype": "Int", "width": 70},
		{
			"label": _("Empresa"),
			"fieldname": "empresa",
			"fieldtype": "Link",
			"options": "Company",
			"width": 240,
		},
		*colunas_do_ativo(),
	]
