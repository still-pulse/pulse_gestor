import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt, getdate, now_datetime

from pulse_gestor.indicadores.doctype.unidade_especialidade_vigencia.unidade_especialidade_vigencia import (
	validar_setor_unidade,
)


def obter_vigencia_e_especialidades(unidade, setor, data):
	if not unidade or not setor or not data:
		return None
	validar_setor_unidade(unidade, setor)
	vigencias = frappe.db.sql(
		"""
		SELECT name FROM `tabUnidade Especialidade Vigencia`
		WHERE unidade = %s AND setor = %s AND data_inicio_vigencia <= %s
			AND (data_fim_vigencia IS NULL OR data_fim_vigencia >= %s)
		LIMIT 2
		""",
		(unidade, setor, data, data),
		as_dict=True,
	)
	if not vigencias:
		frappe.throw(_("Não há especialidades vigentes para esta unidade e setor na data informada."))
	if len(vigencias) > 1:
		frappe.throw(_("Há mais de uma vigência para esta unidade e setor na data informada."))
	vigencia = vigencias[0].name
	linhas = frappe.get_all(
		"Vigencia Especialidade",
		filters={"parent": vigencia, "parenttype": "Unidade Especialidade Vigencia"},
		fields=["especialidade", "meta_quantidade", "periodicidade_meta"],
		order_by="idx asc",
	)
	if not linhas:
		frappe.throw(_("A vigência não possui especialidades."))
	return {"vigencia": vigencia, "especialidades": [dict(linha) for linha in linhas]}


@frappe.whitelist()
def buscar_vigencia_e_especialidades(unidade, setor, data):
	if not frappe.has_permission("Atendimento Diario", "create"):
		frappe.throw(_("Sem permissão para criar atendimentos diários."), frappe.PermissionError)
	return obter_vigencia_e_especialidades(unidade, setor, data)


class AtendimentoDiario(Document):
	def before_insert(self):
		self.lancado_por = frappe.session.user
		self.criado_em = now_datetime()

	def validate(self):
		validar_setor_unidade(self.unidade, self.setor)
		if not self.data:
			frappe.throw(_("Informe a data do atendimento."))
		anterior = self.get_doc_before_save() if not self.is_new() else None
		if anterior:
			self.lancado_por = anterior.lancado_por
			self.criado_em = anterior.criado_em
		self._validar_lancamento_unico()
		resolvido = obter_vigencia_e_especialidades(self.unidade, self.setor, self.data)
		self.vigencia = resolvido["vigencia"]
		especialidades = resolvido["especialidades"]
		if not self.especialidades and self.is_new():
			for item in especialidades:
				self.append("especialidades", item)
		linhas = self.especialidades or []
		if [linha.especialidade for linha in linhas] != [item["especialidade"] for item in especialidades]:
			frappe.throw(_("As especialidades devem corresponder, na mesma ordem, à vigência da unidade, setor e data."))
		mesmo_contexto = (
			anterior
			and anterior.unidade == self.unidade
			and anterior.setor == self.setor
			and getdate(anterior.data) == getdate(self.data)
			and anterior.vigencia == self.vigencia
		)
		total = 0
		for indice, linha in enumerate(linhas):
			origem = anterior.especialidades[indice] if mesmo_contexto else None
			linha.meta_quantidade = origem.meta_quantidade if origem else especialidades[indice]["meta_quantidade"]
			linha.periodicidade_meta = origem.periodicidade_meta if origem else especialidades[indice]["periodicidade_meta"]
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
			"Atendimento Diario",
			{
				"unidade": self.unidade,
				"setor": self.setor,
				"data": getdate(self.data),
				"docstatus": ["<", 2],
				"name": ["!=", self.name or ""],
			},
		)
		if outro:
			frappe.throw(_("Já existe um atendimento para esta unidade, setor e data ({0}).").format(outro))
