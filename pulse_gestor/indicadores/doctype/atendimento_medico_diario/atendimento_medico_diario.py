import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt, getdate, now_datetime


def resolve_validity_and_specialties(unit, date):
	"""Resolve the unit's validity period on the date, including its first and last day."""
	if not unit or not date:
		return None
	validities = frappe.db.sql(
		"""
		SELECT name FROM `tabUnidade Especialidade Vigencia`
		WHERE unidade = %s AND data_inicio_vigencia <= %s
			AND (data_fim_vigencia IS NULL OR data_fim_vigencia >= %s)
		LIMIT 2
		""",
		(unit, date, date),
		as_dict=True,
	)
	if not validities:
		frappe.throw(_("Não há especialidades vigentes para esta unidade na data informada."))
	if len(validities) > 1:
		frappe.throw(_("Há mais de uma vigência para esta unidade na data informada."))
	validity = validities[0].name
	rows = frappe.get_all(
		"Vigencia Especialidade",
		filters={"parent": validity, "parenttype": "Unidade Especialidade Vigencia"},
		fields=["especialidade"],
		order_by="idx asc",
	)
	if not rows:
		frappe.throw(_("A vigência não possui especialidades."))
	return {"vigencia": validity, "especialidades": [dict(row) for row in rows]}


@frappe.whitelist()
def fetch_validity_and_specialties(unit, date):
	if not frappe.has_permission("Atendimento Medico Diario", "create"):
		frappe.throw(_("Sem permissão para criar atendimentos médicos diários."), frappe.PermissionError)
	return resolve_validity_and_specialties(unit, date)


class AtendimentoMedicoDiario(Document):
	def before_insert(self):
		self.lancado_por = frappe.session.user
		self.criado_em = now_datetime()

	def validate(self):
		if not self.unidade or not self.data:
			frappe.throw(_("Informe a unidade e a data do atendimento."))
		previous = self.get_doc_before_save() if not self.is_new() else None
		if previous:
			self.lancado_por = previous.lancado_por
			self.criado_em = previous.criado_em
		self._validar_lancamento_unico()
		resolved = resolve_validity_and_specialties(self.unidade, self.data)
		self.vigencia = resolved["vigencia"]
		specialties = resolved["especialidades"]
		if not self.especialidades and self.is_new():
			for item in specialties:
				self.append("especialidades", item)
		rows = self.especialidades or []
		if [row.especialidade for row in rows] != [item["especialidade"] for item in specialties]:
			frappe.throw(
				_("As especialidades devem corresponder, na mesma ordem, à vigência da unidade na data.")
			)
		total = 0
		for row in rows:
			quantity = row.quantidade or 0
			if flt(quantity) != cint(quantity) or cint(quantity) < 0:
				frappe.throw(
					_("A quantidade da especialidade {0} deve ser um inteiro não negativo.").format(
						row.especialidade
					)
				)
			total += cint(quantity)
		self.total_dia = total
		self.status = "Rascunho" if self.docstatus == 0 else "Enviado"

	def before_submit(self):
		self.status = "Enviado"

	def _validate_unique_entry(self):
		other = frappe.db.exists(
			"Atendimento Medico Diario",
			{
				"unidade": self.unidade,
				"data": getdate(self.data),
				"docstatus": ["<", 2],
				"name": ["!=", self.name or ""],
			},
		)
		if other:
			frappe.throw(_("Já existe um atendimento médico para esta unidade e data ({0}).").format(other))
