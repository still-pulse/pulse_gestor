import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class TipodeComissao(Document):
	def validate(self):
		self.nome_tipo = (self.nome_tipo or "").strip()
		if not self.nome_tipo:
			frappe.throw(_("Informe o nome do tipo de comissão."))
		self.validar_duplicidade()
		self.registrar_alteracao_regimento()

	def validar_duplicidade(self):
		# O nome é gerado por ID, então a unicidade passa a ser por empresa.
		existente = frappe.db.exists(
			"Tipo de Comissao",
			{"nome_tipo": self.nome_tipo, "empresa": self.empresa, "name": ("!=", self.name)},
		)
		if existente:
			frappe.throw(
				_("Já existe um tipo de comissão com o nome {0} para a empresa {1}.").format(
					frappe.bold(self.nome_tipo), frappe.bold(self.empresa)
				)
			)

	def registrar_alteracao_regimento(self):
		"""Grava no histórico o texto anterior sempre que o regimento muda."""
		motivo = (self.motivo_alteracao_regimento or "").strip()
		self.motivo_alteracao_regimento = None

		antes = self.get_doc_before_save()
		texto_anterior = (antes.regimento if antes else None) or ""
		texto_atual = self.regimento or ""
		if texto_anterior == texto_atual:
			return

		if texto_anterior and not motivo:
			frappe.throw(_("Informe o motivo da alteração do regimento."))

		self.append(
			"historico_regimento",
			{
				"versao": len(self.historico_regimento) + 1,
				"data_alteracao": now_datetime(),
				"responsavel": frappe.session.user,
				"motivo": motivo or _("Versão inicial do regimento"),
				"texto_anterior": texto_anterior,
			},
		)
