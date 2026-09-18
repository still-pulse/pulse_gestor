import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt, getdate

from pulse_gestor.indicadores.doctype.unidade_protocolo_vigencia.unidade_protocolo_vigencia import (
	periodos_se_sobrepoem,
)


def validar_setor_unidade(unidade, setor):
	if not unidade or not setor:
		frappe.throw(_("Informe a unidade e o setor."))
	if frappe.db.get_value("Department", setor, "company") != unidade:
		frappe.throw(_("O setor selecionado não pertence à unidade informada."))


class UnidadeEspecialidadeVigencia(Document):
	def validate(self):
		validar_setor_unidade(self.unidade, self.setor)
		if not self.data_inicio_vigencia:
			frappe.throw(_("Informe o início da vigência."))
		if self.data_fim_vigencia and getdate(self.data_fim_vigencia) < getdate(self.data_inicio_vigencia):
			frappe.throw(_("O fim da vigência não pode ser anterior ao início."))
		if not self.especialidades:
			frappe.throw(_("Inclua pelo menos uma especialidade."))

		vistas = set()
		for linha in self.especialidades:
			if not linha.especialidade:
				frappe.throw(_("Informe a especialidade em todas as linhas."))
			if linha.especialidade in vistas:
				frappe.throw(_("A especialidade {0} foi informada mais de uma vez.").format(linha.especialidade))
			vistas.add(linha.especialidade)
			if flt(linha.meta_quantidade) != cint(linha.meta_quantidade) or cint(linha.meta_quantidade) < 0:
				frappe.throw(_("A meta da especialidade {0} deve ser um inteiro não negativo.").format(linha.especialidade))
			if linha.periodicidade_meta not in ("Mensal", "Anual"):
				frappe.throw(_("Informe a periodicidade da meta de {0}.").format(linha.especialidade))

		for periodo in frappe.get_all(
			"Unidade Especialidade Vigencia",
			filters={"unidade": self.unidade, "setor": self.setor, "name": ["!=", self.name or ""]},
			fields=["name", "data_inicio_vigencia", "data_fim_vigencia"],
		):
			if periodos_se_sobrepoem(
				self.data_inicio_vigencia,
				self.data_fim_vigencia,
				periodo.data_inicio_vigencia,
				periodo.data_fim_vigencia,
			):
				frappe.throw(
					_("Já existe uma vigência para esta unidade e setor no período ({0}).").format(periodo.name)
				)
