from frappe import _

from pulse_gestor.patrimonio.report.utils import asset_columns, build_summary, fetch_assets


def execute(filters=None):
	assets = fetch_assets(filters)
	return get_columns(), assets, None, None, build_summary(assets)


def get_columns():
	return [
		{"label": _("Ativo"), "fieldname": "ativo", "fieldtype": "Link", "options": "Asset", "width": 140},
		{"label": _("Nome do bem"), "fieldname": "nome_do_bem", "fieldtype": "Data", "width": 240},
		{
			"label": _("Empresa"),
			"fieldname": "empresa",
			"fieldtype": "Link",
			"options": "Company",
			"width": 260,
		},
		{
			"label": _("Localização"),
			"fieldname": "localizacao",
			"fieldtype": "Link",
			"options": "Location",
			"width": 220,
		},
		*asset_columns(),
	]
