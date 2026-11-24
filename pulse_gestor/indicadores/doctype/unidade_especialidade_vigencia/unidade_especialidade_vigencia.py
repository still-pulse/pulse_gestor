import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

from pulse_gestor.indicadores.doctype.unidade_protocolo_vigencia.unidade_protocolo_vigencia import (
	periods_overlap,
)


class UnidadeEspecialidadeVigencia(Document):
	def validate(self):
		if not self.unidade or not self.data_inicio_vigencia:
			frappe.throw(_("Informe a unidade e o início da vigência."))
		if self.data_fim_vigencia and getdate(self.data_fim_vigencia) < getdate(self.data_inicio_vigencia):
			frappe.throw(_("O fim da vigência não pode ser anterior ao início."))
		if not self.especialidades:
			frappe.throw(_("Inclua pelo menos uma especialidade."))

		seen = set()
		for row in self.especialidades:
			if not row.especialidade:
				frappe.throw(_("Informe a especialidade em todas as linhas."))
			if row.especialidade in seen:
				frappe.throw(
					_("A especialidade {0} foi informada mais de uma vez.").format(row.especialidade)
				)
			seen.add(row.especialidade)

		for period in frappe.get_all(
			"Unidade Especialidade Vigencia",
			filters={"unidade": self.unidade, "name": ["!=", self.name or ""]},
			fields=["name", "data_inicio_vigencia", "data_fim_vigencia"],
		):
			if periods_overlap(
				self.data_inicio_vigencia,
				self.data_fim_vigencia,
				period.data_inicio_vigencia,
				period.data_fim_vigencia,
			):
				frappe.throw(
					_("A unidade já possui uma vigência de especialidades nesse período ({0}).").format(
						period.name
					)
				)
