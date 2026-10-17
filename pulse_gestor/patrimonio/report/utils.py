import frappe
from frappe import _

# Campos customizados do Asset (criados no site, com acento no nome).
CONTROLE_BHCL = "custom_número_de_controle_bhcl"
PATRIMONIO_PREFEITURA = "custom_número_patrimônio_prefeitura"
UTILIZACAO = "custom_utilização"
CONSERVACAO = "custom_estado_de_conservação"


def buscar_ativos(filters):
	"""Ativos não cancelados filtrados por empresa, localização (com sublocais) e situação."""
	filters = frappe._dict(filters or {})
	params = {}
	condicoes = ["ativo.docstatus < 2"]

	if filters.empresa:
		condicoes.append("ativo.company = %(empresa)s")
		params["empresa"] = filters.empresa

	if filters.localizacao:
		local = frappe.db.get_value(
			"Location", filters.localizacao, ["lft", "rgt", "custom_empresa"], as_dict=True
		)
		if not local:
			frappe.throw(_("Localização {0} não encontrada.").format(filters.localizacao))
		if filters.empresa and local.custom_empresa != filters.empresa:
			frappe.throw(
				_("A localização {0} não está vinculada à empresa {1}.").format(
					filters.localizacao, filters.empresa
				)
			)
		condicoes.append("local.lft >= %(lft)s AND local.rgt <= %(rgt)s")
		params.update(lft=local.lft, rgt=local.rgt)

	for filtro, coluna in (
		("categoria", "ativo.asset_category"),
		("status", "ativo.status"),
		("utilizacao", f"ativo.`{UTILIZACAO}`"),
		("conservacao", f"ativo.`{CONSERVACAO}`"),
	):
		if filters.get(filtro):
			condicoes.append(f"{coluna} = %({filtro})s")
			params[filtro] = filters[filtro]

	ativos = frappe.db.sql(
		f"""
		SELECT ativo.name AS ativo, ativo.asset_name AS nome_do_bem,
			ativo.`{CONTROLE_BHCL}` AS controle_bhcl,
			ativo.`{PATRIMONIO_PREFEITURA}` AS patrimonio_prefeitura,
			ativo.asset_category AS categoria, ativo.item_code AS item,
			ativo.company AS empresa, ativo.location AS localizacao,
			ativo.custodian AS custodiante, colaborador.employee_name AS nome_custodiante,
			ativo.department AS departamento,
			ativo.`{UTILIZACAO}` AS utilizacao, ativo.`{CONSERVACAO}` AS conservacao,
			ativo.status, ativo.purchase_date AS data_aquisicao,
			ativo.gross_purchase_amount AS valor_aquisicao,
			IF(ativo.calculate_depreciation, ativo.value_after_depreciation,
				COALESCE(NULLIF(ativo.total_asset_cost, 0), ativo.gross_purchase_amount)) AS valor_contabil
		FROM `tabAsset` ativo
		LEFT JOIN `tabLocation` local ON local.name = ativo.location
		LEFT JOIN `tabEmployee` colaborador ON colaborador.name = ativo.custodian
		WHERE {" AND ".join(condicoes)}
		ORDER BY ativo.company, ativo.location, ativo.asset_name, ativo.name
		""",
		params,
		as_dict=True,
	)
	for row in ativos:
		row.custodiante = row.nome_custodiante or row.custodiante
	return ativos


def colunas_do_ativo():
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


def resumo(ativos, extra=None):
	return [
		{"label": _("Ativos"), "value": len(ativos), "datatype": "Int", "indicator": "Blue"},
		*(extra or []),
		{
			"label": _("Valor de aquisição"),
			"value": sum(r.valor_aquisicao or 0 for r in ativos),
			"datatype": "Currency",
			"indicator": "Green",
		},
		{
			"label": _("Valor contábil"),
			"value": sum(r.valor_contabil or 0 for r in ativos),
			"datatype": "Currency",
			"indicator": "Green",
		},
	]
