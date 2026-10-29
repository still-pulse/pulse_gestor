import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

from pulse_gestor.indicadores.doctype.unidade_protocolo_vigencia.unidade_protocolo_vigencia import (
	periodos_se_sobrepoem,
)


class UnidadeEspecialidadeVigencia(Document):
	def validate(self):
		if not self.unidade or not self.data_inicio_vigencia:
			frappe.throw(_("Informe a unidade e o início da vigência."))
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

		for periodo in frappe.get_all(
			"Unidade Especialidade Vigencia",
			filters={"unidade": self.unidade, "name": ["!=", self.name or ""]},
			fields=["name", "data_inicio_vigencia", "data_fim_vigencia"],
		):
			if periodos_se_sobrepoem(
				self.data_inicio_vigencia,
				self.data_fim_vigencia,
				periodo.data_inicio_vigencia,
				periodo.data_fim_vigencia,
			):
				frappe.throw(_("A unidade já possui uma vigência de especialidades nesse período ({0}).").format(periodo.name))
