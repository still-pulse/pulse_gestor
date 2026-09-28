import frappe
from frappe import _
from frappe.utils import cint, formatdate, getdate

CAMPOS_DA_REUNIAO = (
	"reuniao",
	"data_reuniao",
	"data_convocacao",
	"empresa",
	"categoria",
	"comissao",
	"mandato",
	"presentes",
	"convocados",
)


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.data_inicio or not filters.data_fim:
		frappe.throw(_("Informe data início e data fim."))
	if getdate(filters.data_inicio) > getdate(filters.data_fim):
		frappe.throw(_("A data início não pode ser posterior à data fim."))

	incluir_pauta = cint(filters.incluir_pauta)
	params = {"data_inicio": filters.data_inicio, "data_fim": filters.data_fim}
	condicoes = ["reuniao.data_reuniao BETWEEN %(data_inicio)s AND %(data_fim)s"]
	for campo in ("empresa", "tipo_comissao"):
		if filters.get(campo):
			condicoes.append(f"reuniao.{campo} = %({campo})s")
			params[campo] = filters[campo]

	# Com a pauta, o relatório traz uma linha por item; reuniões sem pauta aparecem
	# uma vez, com o assunto vazio. Sem a pauta, é uma linha por reunião.
	pauta_select = "pauta.assunto AS assunto," if incluir_pauta else ""
	pauta_join = (
		"""LEFT JOIN `tabComissao Pauta Item` pauta
			ON pauta.parent = reuniao.name AND pauta.parenttype = 'Reuniao de Comissao'"""
		if incluir_pauta
		else ""
	)
	pauta_order = ", pauta.idx" if incluir_pauta else ""

	data = frappe.db.sql(
		f"""
		SELECT reuniao.name AS reuniao, reuniao.data_reuniao, reuniao.data_convocacao,
			reuniao.empresa, categoria.nome_categoria AS categoria,
			tipo.nome_tipo AS comissao, mandato.data_inicio_mandato,
			mandato.status_mandato,
			{pauta_select}
			(SELECT COUNT(*) FROM `tabComissao Reuniao Participante` p
				WHERE p.parent = reuniao.name AND p.parenttype = 'Reuniao de Comissao'
				AND p.status_presenca = 'Presente') AS presentes,
			(SELECT COUNT(*) FROM `tabComissao Reuniao Participante` p
				WHERE p.parent = reuniao.name AND p.parenttype = 'Reuniao de Comissao') AS convocados
		FROM `tabReuniao de Comissao` reuniao
		LEFT JOIN `tabTipo de Comissao` tipo ON tipo.name = reuniao.tipo_comissao
		LEFT JOIN `tabCategoria de Comissao` categoria ON categoria.name = tipo.categoria_comissao
		LEFT JOIN `tabMandato de Comissao` mandato ON mandato.name = reuniao.mandato_comissao
		{pauta_join}
		WHERE {" AND ".join(condicoes)}
		ORDER BY reuniao.data_reuniao, reuniao.empresa, reuniao.tipo_comissao, reuniao.name{pauta_order}
		""",
		params,
		as_dict=True,
	)

	reunioes = {row.reuniao for row in data}
	vistas = set()
	for row in data:
		row.mandato = (
			f"{formatdate(row.data_inicio_mandato)} ({row.status_mandato})" if row.data_inicio_mandato else ""
		)
		# Com a pauta, os dados da reunião aparecem só na primeira linha.
		if row.reuniao in vistas:
			for campo in CAMPOS_DA_REUNIAO:
				row[campo] = None
		vistas.add(row.reuniao)
	summary = [
		{
			"label": _("Reuniões no período"),
			"value": len(reunioes),
			"datatype": "Int",
			"indicator": "Blue",
		}
	]
	return get_columns(incluir_pauta), data, None, None, summary


def get_columns(incluir_pauta):
	columns = [
		{"label": _("Reunião"), "fieldname": "reuniao", "fieldtype": "Link", "options": "Reuniao de Comissao", "width": 130},
		{"label": _("Data da reunião"), "fieldname": "data_reuniao", "fieldtype": "Date", "width": 110},
		{"label": _("Data da convocação"), "fieldname": "data_convocacao", "fieldtype": "Date", "width": 120},
		{"label": _("Empresa"), "fieldname": "empresa", "fieldtype": "Link", "options": "Company", "width": 260},
		{"label": _("Categoria"), "fieldname": "categoria", "fieldtype": "Data", "width": 150},
		{"label": _("Comissão"), "fieldname": "comissao", "fieldtype": "Data", "width": 220},
		{"label": _("Mandato"), "fieldname": "mandato", "fieldtype": "Data", "width": 170},
		{"label": _("Presentes"), "fieldname": "presentes", "fieldtype": "Int", "width": 80},
		{"label": _("Participantes"), "fieldname": "convocados", "fieldtype": "Int", "width": 100},
	]
	if incluir_pauta:
		columns.append({"label": _("Pauta"), "fieldname": "assunto", "fieldtype": "Small Text", "width": 350})
	return columns
