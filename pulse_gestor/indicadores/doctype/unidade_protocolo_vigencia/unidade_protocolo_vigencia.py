import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


def periodos_se_sobrepoem(inicio_a, fim_a, inicio_b, fim_b):
	"""As datas finais são inclusivas; ausência de fim significa prazo aberto."""
	inicio_a, inicio_b = getdate(inicio_a), getdate(inicio_b)
	fim_a = getdate(fim_a) if fim_a else None
	fim_b = getdate(fim_b) if fim_b else None
	return (fim_a is None or inicio_b <= fim_a) and (fim_b is None or inicio_a <= fim_b)


class UnidadeProtocoloVigencia(Document):
	def validate(self):
		if not self.unidade or not self.protocolo or not self.data_inicio_vigencia:
			frappe.throw(_("Informe unidade, protocolo e início da vigência."))
		if self.data_fim_vigencia and getdate(self.data_fim_vigencia) < getdate(self.data_inicio_vigencia):
			frappe.throw(_("O fim da vigência não pode ser anterior ao início."))

		anterior = self.get_doc_before_save() if not self.is_new() else None
		if not anterior or anterior.protocolo != self.protocolo:
			if not int(frappe.db.get_value("Protocolo de Triagem", self.protocolo, "ativo") or 0):
				frappe.throw(_("Selecione um protocolo de triagem ativo."))

		for periodo in frappe.get_all(
			"Unidade Protocolo Vigencia",
			filters={"unidade": self.unidade, "name": ["!=", self.name or ""]},
			fields=["name", "data_inicio_vigencia", "data_fim_vigencia"],
			order_by="name asc",
		):
			if periodos_se_sobrepoem(
				self.data_inicio_vigencia,
				self.data_fim_vigencia,
				periodo.data_inicio_vigencia,
				periodo.data_fim_vigencia,
			):
				frappe.throw(
					_("A unidade já possui um protocolo vigente nesse período ({0}).").format(periodo.name)
				)
