from itertools import groupby

from frappe import _

from pulse_gestor.patrimonio.report.utils import asset_columns, build_summary, fetch_assets


def execute(filters=None):
	assets = fetch_assets(filters)
	assets.sort(key=lambda r: (r.empresa or "", r.localizacao or "", r.nome_do_bem or "", r.ativo))

	# One row per location (with count and amounts), followed by its assets.
	data, totals = [], []
	for (company, location), group in groupby(assets, key=lambda r: (r.empresa, r.localizacao)):
		group = list(group)
		group_key = f"{company}::{location or ''}"
		name = location or _("Sem localização")
		data.append(
			{
				"id": group_key,
				"parent": None,
				"indent": 0,
				"descricao": name,
				"empresa": company,
				"quantidade": len(group),
				"valor_aquisicao": sum(r.valor_aquisicao or 0 for r in group),
				"valor_contabil": sum(r.valor_contabil or 0 for r in group),
			}
		)
		totals.append((name, len(group)))
		for row in group:
			row.update(id=row.ativo, parent=group_key, indent=1, descricao=row.nome_do_bem, quantidade=1)
			data.append(row)

	extra = [{"label": _("Localizações"), "value": len(totals), "datatype": "Int", "indicator": "Blue"}]
	return get_columns(), data, None, get_chart(totals), build_summary(assets, extra)


def get_chart(totals):
	if not totals:
		return None
	largest = sorted(totals, key=lambda t: t[1], reverse=True)[:15]
	return {
		"data": {
			"labels": [name for name, _count in largest],
			"datasets": [{"name": _("Ativos"), "values": [count for _name, count in largest]}],
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
		*asset_columns(),
	]
