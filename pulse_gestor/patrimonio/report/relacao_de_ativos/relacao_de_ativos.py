from frappe import _

from pulse_gestor.patrimonio.report.utils import buscar_ativos, colunas_do_ativo, resumo


def execute(filters=None):
	ativos = buscar_ativos(filters)
	return get_columns(), ativos, None, None, resumo(ativos)


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
		*colunas_do_ativo(),
	]
