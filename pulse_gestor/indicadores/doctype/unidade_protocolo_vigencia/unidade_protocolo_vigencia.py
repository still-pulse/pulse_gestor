import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


def periods_overlap(start_a, end_a, start_b, end_b):
	"""End dates are inclusive; a missing end means an open-ended period."""
	start_a, start_b = getdate(start_a), getdate(start_b)
	end_a = getdate(end_a) if end_a else None
	end_b = getdate(end_b) if end_b else None
	return (end_a is None or start_b <= end_a) and (end_b is None or start_a <= end_b)


class UnidadeProtocoloVigencia(Document):
	def validate(self):
		if not self.unidade or not self.protocolo or not self.data_inicio_vigencia:
			frappe.throw(_("Informe unidade, protocolo e início da vigência."))
		if self.data_fim_vigencia and getdate(self.data_fim_vigencia) < getdate(self.data_inicio_vigencia):
			frappe.throw(_("O fim da vigência não pode ser anterior ao início."))

		previous = self.get_doc_before_save() if not self.is_new() else None
		if not previous or previous.protocolo != self.protocolo:
			if not int(frappe.db.get_value("Protocolo de Triagem", self.protocolo, "ativo") or 0):
				frappe.throw(_("Selecione um protocolo de triagem ativo."))

		for period in frappe.get_all(
			"Unidade Protocolo Vigencia",
			filters={"unidade": self.unidade, "name": ["!=", self.name or ""]},
			fields=["name", "data_inicio_vigencia", "data_fim_vigencia"],
			order_by="name asc",
		):
			if periods_overlap(
				self.data_inicio_vigencia,
				self.data_fim_vigencia,
				period.data_inicio_vigencia,
				period.data_fim_vigencia,
			):
				frappe.throw(
					_("A unidade já possui um protocolo vigente nesse período ({0}).").format(period.name)
				)
