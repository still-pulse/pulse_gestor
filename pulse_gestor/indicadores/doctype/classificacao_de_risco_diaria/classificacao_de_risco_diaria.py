import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, getdate, now_datetime


def obter_protocolo_e_niveis(unidade, data):
	"""Resolve a vigência inclusive no primeiro e no último dia."""
	if not unidade or not data:
		return None

	vigencias = frappe.db.sql(
		"""
		SELECT name, protocolo
		FROM `tabUnidade Protocolo Vigencia`
		WHERE unidade = %s
			AND data_inicio_vigencia <= %s
			AND (data_fim_vigencia IS NULL OR data_fim_vigencia >= %s)
		LIMIT 2
		""",
		(unidade, data, data),
		as_dict=True,
	)
	if not vigencias:
		frappe.throw(_("Não há protocolo de triagem vigente para esta unidade na data informada."))
	if len(vigencias) > 1:
		frappe.throw(_("Há mais de uma vigência para esta unidade na data informada."))

	protocolo = vigencias[0].protocolo
	niveis = frappe.get_all(
		"Protocolo Nivel",
		filters={"parent": protocolo, "parenttype": "Protocolo de Triagem"},
		fields=["nome_nivel", "cor", "ordem"],
		order_by="ordem asc",
	)
	if not niveis:
		frappe.throw(_("O protocolo vigente não possui níveis de triagem."))
	return {
		"protocolo": protocolo,
		"niveis": [{"nivel": nivel.nome_nivel, "cor": nivel.cor} for nivel in niveis],
	}


@frappe.whitelist()
def buscar_protocolo_e_niveis(unidade, data):
	if not frappe.has_permission("Classificacao de Risco Diaria", "create"):
		frappe.throw(_("Sem permissão para criar classificações diárias."), frappe.PermissionError)
	return obter_protocolo_e_niveis(unidade, data)


class ClassificacaodeRiscoDiaria(Document):
	def before_insert(self):
		self.lancado_por = frappe.session.user
		self.criado_em = now_datetime()

	def validate(self):
		if not self.unidade or not self.data:
			frappe.throw(_("Informe a unidade e a data."))
		anterior = self.get_doc_before_save() if not self.is_new() else None
		if anterior:
			self.lancado_por = anterior.lancado_por
			self.criado_em = anterior.criado_em

		self._validar_lancamento_unico()
		resolvido = obter_protocolo_e_niveis(self.unidade, self.data)
		self.protocolo = resolvido["protocolo"]
		niveis = resolvido["niveis"]
		if not self.niveis_classificados and self.is_new():
			for nivel in niveis:
				self.append("niveis_classificados", nivel)

		linhas = self.niveis_classificados or []
		if [linha.nivel for linha in linhas] != [nivel["nivel"] for nivel in niveis]:
			frappe.throw(
				_(
					"Os níveis devem corresponder, na mesma ordem, ao protocolo vigente. "
					"Atualize a unidade ou a data para recarregá-los."
				)
			)
		mesmo_contexto = (
			anterior
			and anterior.unidade == self.unidade
			and getdate(anterior.data) == getdate(self.data)
			and anterior.protocolo == self.protocolo
			and [linha.nivel for linha in anterior.niveis_classificados] == [nivel["nivel"] for nivel in niveis]
		)
		for indice, linha in enumerate(linhas):
			linha.cor = anterior.niveis_classificados[indice].cor if mesmo_contexto else niveis[indice]["cor"]

		total = 0
		for linha in linhas:
			classificados = cint(linha.qtd_pacientes_classificados)
			if classificados < 0:
				frappe.throw(_("A quantidade do nível {0} não pode ser negativa.").format(linha.nivel))
			total += classificados
		self.total_classificados = total
		self.status = "Rascunho" if self.docstatus == 0 else "Enviado"

	def before_submit(self):
		self.status = "Enviado"

	def _validar_lancamento_unico(self):
		outro = frappe.db.exists(
			"Classificacao de Risco Diaria",
			{
				"unidade": self.unidade,
				"data": getdate(self.data),
				"docstatus": ["<", 2],
				"name": ["!=", self.name or ""],
			},
		)
		if outro:
			frappe.throw(_("Já existe uma classificação diária para esta unidade e data ({0}).").format(outro))
