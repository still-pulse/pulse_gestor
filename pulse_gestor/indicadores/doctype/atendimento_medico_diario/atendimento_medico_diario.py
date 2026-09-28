import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt, getdate, now_datetime


def obter_vigencia_e_especialidades(unidade, data):
	"""Resolve a vigência da unidade na data, inclusive no primeiro e no último dia."""
	if not unidade or not data:
		return None
	vigencias = frappe.db.sql(
		"""
		SELECT name FROM `tabUnidade Especialidade Vigencia`
		WHERE unidade = %s AND data_inicio_vigencia <= %s
			AND (data_fim_vigencia IS NULL OR data_fim_vigencia >= %s)
		LIMIT 2
		""",
		(unidade, data, data),
		as_dict=True,
	)
	if not vigencias:
		frappe.throw(_("Não há especialidades vigentes para esta unidade na data informada."))
	if len(vigencias) > 1:
		frappe.throw(_("Há mais de uma vigência para esta unidade na data informada."))
	vigencia = vigencias[0].name
	linhas = frappe.get_all(
		"Vigencia Especialidade",
		filters={"parent": vigencia, "parenttype": "Unidade Especialidade Vigencia"},
		fields=["especialidade"],
		order_by="idx asc",
	)
	if not linhas:
		frappe.throw(_("A vigência não possui especialidades."))
	return {"vigencia": vigencia, "especialidades": [dict(linha) for linha in linhas]}


@frappe.whitelist()
def buscar_vigencia_e_especialidades(unidade, data):
	if not frappe.has_permission("Atendimento Medico Diario", "create"):
		frappe.throw(_("Sem permissão para criar atendimentos médicos diários."), frappe.PermissionError)
	return obter_vigencia_e_especialidades(unidade, data)


class AtendimentoMedicoDiario(Document):
	def before_insert(self):
		self.lancado_por = frappe.session.user
		self.criado_em = now_datetime()

	def validate(self):
		if not self.unidade or not self.data:
			frappe.throw(_("Informe a unidade e a data do atendimento."))
		anterior = self.get_doc_before_save() if not self.is_new() else None
		if anterior:
			self.lancado_por = anterior.lancado_por
			self.criado_em = anterior.criado_em
		self._validar_lancamento_unico()
		resolvido = obter_vigencia_e_especialidades(self.unidade, self.data)
		self.vigencia = resolvido["vigencia"]
		especialidades = resolvido["especialidades"]
		if not self.especialidades and self.is_new():
			for item in especialidades:
				self.append("especialidades", item)
		linhas = self.especialidades or []
		if [linha.especialidade for linha in linhas] != [item["especialidade"] for item in especialidades]:
			frappe.throw(_("As especialidades devem corresponder, na mesma ordem, à vigência da unidade na data."))
		total = 0
		for linha in linhas:
			quantidade = linha.quantidade or 0
			if flt(quantidade) != cint(quantidade) or cint(quantidade) < 0:
				frappe.throw(_("A quantidade da especialidade {0} deve ser um inteiro não negativo.").format(linha.especialidade))
			total += cint(quantidade)
		self.total_dia = total
		self.status = "Rascunho" if self.docstatus == 0 else "Enviado"

	def before_submit(self):
		self.status = "Enviado"

	def _validar_lancamento_unico(self):
		outro = frappe.db.exists(
			"Atendimento Medico Diario",
			{
				"unidade": self.unidade,
				"data": getdate(self.data),
				"docstatus": ["<", 2],
				"name": ["!=", self.name or ""],
			},
		)
		if outro:
			frappe.throw(_("Já existe um atendimento médico para esta unidade e data ({0}).").format(outro))
