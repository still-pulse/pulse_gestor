import frappe
from frappe import _
from frappe.utils import cint, formatdate, getdate

MEETING_FIELDS = (
	"reuniao",
	"data_reuniao",
	"local_reuniao",
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

	include_agenda = cint(filters.incluir_pauta)
	params = {"data_inicio": filters.data_inicio, "data_fim": filters.data_fim}
	conditions = ["DATE(reuniao.data_reuniao) BETWEEN %(data_inicio)s AND %(data_fim)s"]
	for field in ("empresa", "tipo_comissao"):
		if filters.get(field):
			conditions.append(f"reuniao.{field} = %({field})s")
			params[field] = filters[field]

	# With the agenda, the report has one row per item; meetings without an agenda appear
	# once, with an empty subject. Without the agenda, it is one row per meeting.
	agenda_select = "pauta.assunto AS assunto," if include_agenda else ""
	agenda_join = (
		"""LEFT JOIN `tabComissao Pauta Item` pauta
			ON pauta.parent = reuniao.name AND pauta.parenttype = 'Reuniao de Comissao'"""
		if include_agenda
		else ""
	)
	agenda_order = ", pauta.idx" if include_agenda else ""

	data = frappe.db.sql(
		f"""
		SELECT reuniao.name AS reuniao, reuniao.data_reuniao, reuniao.local_reuniao, reuniao.data_convocacao,
			reuniao.empresa, categoria.nome_categoria AS categoria,
			tipo.nome_tipo AS comissao, mandato.data_inicio_mandato,
			mandato.status_mandato,
			{agenda_select}
			(SELECT COUNT(*) FROM `tabComissao Reuniao Participante` p
				WHERE p.parent = reuniao.name AND p.parenttype = 'Reuniao de Comissao'
				AND p.status_presenca = 'Presente') AS presentes,
			(SELECT COUNT(*) FROM `tabComissao Reuniao Participante` p
				WHERE p.parent = reuniao.name AND p.parenttype = 'Reuniao de Comissao') AS convocados
		FROM `tabReuniao de Comissao` reuniao
		LEFT JOIN `tabTipo de Comissao` tipo ON tipo.name = reuniao.tipo_comissao
		LEFT JOIN `tabCategoria de Comissao` categoria ON categoria.name = tipo.categoria_comissao
		LEFT JOIN `tabMandato de Comissao` mandato ON mandato.name = reuniao.mandato_comissao
		{agenda_join}
		WHERE {" AND ".join(conditions)}
		ORDER BY reuniao.data_reuniao, reuniao.empresa, reuniao.tipo_comissao, reuniao.name{agenda_order}
		""",
		params,
		as_dict=True,
	)

	meetings = {row.reuniao for row in data}
	seen = set()
	for row in data:
		row.mandato = (
			f"{formatdate(row.data_inicio_mandato)} ({row.status_mandato})" if row.data_inicio_mandato else ""
		)
		# With the agenda, the meeting data appears only on the first row.
		if row.reuniao in seen:
			for field in MEETING_FIELDS:
				row[field] = None
		seen.add(row.reuniao)
	summary = [
		{
			"label": _("Reuniões no período"),
			"value": len(meetings),
			"datatype": "Int",
			"indicator": "Blue",
		}
	]
	return get_columns(include_agenda), data, None, None, summary


def get_columns(include_agenda):
	columns = [
		{
			"label": _("Reunião"),
			"fieldname": "reuniao",
			"fieldtype": "Link",
			"options": "Reuniao de Comissao",
			"width": 130,
		},
		{
			"label": _("Data e hora da reunião"),
			"fieldname": "data_reuniao",
			"fieldtype": "Datetime",
			"width": 150,
		},
		{"label": _("Local"), "fieldname": "local_reuniao", "fieldtype": "Data", "width": 160},
		{"label": _("Data da convocação"), "fieldname": "data_convocacao", "fieldtype": "Date", "width": 120},
		{
			"label": _("Empresa"),
			"fieldname": "empresa",
			"fieldtype": "Link",
			"options": "Company",
			"width": 260,
		},
		{"label": _("Categoria"), "fieldname": "categoria", "fieldtype": "Data", "width": 150},
		{"label": _("Comissão"), "fieldname": "comissao", "fieldtype": "Data", "width": 220},
		{"label": _("Mandato"), "fieldname": "mandato", "fieldtype": "Data", "width": 170},
		{"label": _("Presentes"), "fieldname": "presentes", "fieldtype": "Int", "width": 80},
		{"label": _("Participantes"), "fieldname": "convocados", "fieldtype": "Int", "width": 100},
	]
	if include_agenda:
		columns.append({"label": _("Pauta"), "fieldname": "assunto", "fieldtype": "Small Text", "width": 350})
	return columns
