import frappe
from frappe import _

# Custom Fields on Asset (created on the site, with accents in their names).
CONTROL_NUMBER_FIELD = "custom_número_de_controle_bhcl"
MUNICIPAL_ASSET_NUMBER_FIELD = "custom_número_patrimônio_prefeitura"
USAGE_FIELD = "custom_utilização"
CONDITION_FIELD = "custom_estado_de_conservação"


def fetch_assets(filters):
	"""Non-cancelled assets filtered by company, location (including sublocations) and status."""
	filters = frappe._dict(filters or {})
	params = {}
	conditions = ["ativo.docstatus < 2"]

	if filters.empresa:
		conditions.append("ativo.company = %(empresa)s")
		params["empresa"] = filters.empresa

	if filters.localizacao:
		location = frappe.db.get_value(
			"Location", filters.localizacao, ["lft", "rgt", "custom_empresa"], as_dict=True
		)
		if not location:
			frappe.throw(_("Localização {0} não encontrada.").format(filters.localizacao))
		if filters.empresa and location.custom_empresa != filters.empresa:
			frappe.throw(
				_("A localização {0} não está vinculada à empresa {1}.").format(
					filters.localizacao, filters.empresa
				)
			)
		conditions.append("local.lft >= %(lft)s AND local.rgt <= %(rgt)s")
		params.update(lft=location.lft, rgt=location.rgt)

	for filter_name, column in (
		("categoria", "ativo.asset_category"),
		("status", "ativo.status"),
		("utilizacao", f"ativo.`{USAGE_FIELD}`"),
		("conservacao", f"ativo.`{CONDITION_FIELD}`"),
	):
		if filters.get(filter_name):
			conditions.append(f"{column} = %({filter_name})s")
			params[filter_name] = filters[filter_name]

	assets = frappe.db.sql(
		f"""
		SELECT ativo.name AS ativo, ativo.asset_name AS nome_do_bem,
			ativo.`{CONTROL_NUMBER_FIELD}` AS controle_bhcl,
			ativo.`{MUNICIPAL_ASSET_NUMBER_FIELD}` AS patrimonio_prefeitura,
			ativo.asset_category AS categoria, ativo.item_code AS item,
			ativo.company AS empresa, ativo.location AS localizacao,
			ativo.custodian AS custodiante, colaborador.employee_name AS nome_custodiante,
			ativo.department AS departamento,
			ativo.`{USAGE_FIELD}` AS utilizacao, ativo.`{CONDITION_FIELD}` AS conservacao,
			ativo.status, ativo.purchase_date AS data_aquisicao,
			ativo.gross_purchase_amount AS valor_aquisicao,
			IF(ativo.calculate_depreciation, ativo.value_after_depreciation,
				COALESCE(NULLIF(ativo.total_asset_cost, 0), ativo.gross_purchase_amount)) AS valor_contabil
		FROM `tabAsset` ativo
		LEFT JOIN `tabLocation` local ON local.name = ativo.location
		LEFT JOIN `tabEmployee` colaborador ON colaborador.name = ativo.custodian
		WHERE {" AND ".join(conditions)}
		ORDER BY ativo.company, ativo.location, ativo.asset_name, ativo.name
		""",
		params,
		as_dict=True,
	)
	for row in assets:
		row.custodiante = row.nome_custodiante or row.custodiante
	return assets


def asset_columns():
	return [
		{"label": _("Controle BHCL"), "fieldname": "controle_bhcl", "fieldtype": "Data", "width": 110},
		{
			"label": _("Patrimônio Prefeitura"),
			"fieldname": "patrimonio_prefeitura",
			"fieldtype": "Data",
			"width": 130,
		},
		{
			"label": _("Categoria"),
			"fieldname": "categoria",
			"fieldtype": "Link",
			"options": "Asset Category",
			"width": 160,
		},
		{"label": _("Utilização"), "fieldname": "utilizacao", "fieldtype": "Data", "width": 110},
		{"label": _("Estado de conservação"), "fieldname": "conservacao", "fieldtype": "Data", "width": 120},
		{"label": _("Situação"), "fieldname": "status", "fieldtype": "Data", "width": 130},
		{"label": _("Custodiante"), "fieldname": "custodiante", "fieldtype": "Data", "width": 180},
		{"label": _("Data de aquisição"), "fieldname": "data_aquisicao", "fieldtype": "Date", "width": 110},
		{
			"label": _("Valor de aquisição"),
			"fieldname": "valor_aquisicao",
			"fieldtype": "Currency",
			"width": 130,
		},
		{"label": _("Valor contábil"), "fieldname": "valor_contabil", "fieldtype": "Currency", "width": 130},
	]


def build_summary(assets, extra=None):
	return [
		{"label": _("Ativos"), "value": len(assets), "datatype": "Int", "indicator": "Blue"},
		*(extra or []),
		{
			"label": _("Valor de aquisição"),
			"value": sum(r.valor_aquisicao or 0 for r in assets),
			"datatype": "Currency",
			"indicator": "Green",
		},
		{
			"label": _("Valor contábil"),
			"value": sum(r.valor_contabil or 0 for r in assets),
			"datatype": "Currency",
			"indicator": "Green",
		},
	]
