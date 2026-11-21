import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, getdate, now_datetime


def resolve_protocol_and_levels(unit, date):
	"""Resolve the validity period, including its first and last day."""
	if not unit or not date:
		return None

	validities = frappe.db.sql(
		"""
		SELECT name, protocolo
		FROM `tabUnidade Protocolo Vigencia`
		WHERE unidade = %s
			AND data_inicio_vigencia <= %s
			AND (data_fim_vigencia IS NULL OR data_fim_vigencia >= %s)
		LIMIT 2
		""",
		(unit, date, date),
		as_dict=True,
	)
	if not validities:
		frappe.throw(_("Não há protocolo de triagem vigente para esta unidade na data informada."))
	if len(validities) > 1:
		frappe.throw(_("Há mais de uma vigência para esta unidade na data informada."))

	protocol = validities[0].protocolo
	levels = frappe.get_all(
		"Protocolo Nivel",
		filters={"parent": protocol, "parenttype": "Protocolo de Triagem"},
		fields=["nome_nivel", "cor", "ordem", "tempo_maximo_espera_min"],
		order_by="ordem asc",
	)
	if not levels:
		frappe.throw(_("O protocolo vigente não possui níveis de triagem."))
	return {
		"protocolo": protocol,
		"niveis": [
			{
				"nivel": level.nome_nivel,
				"cor": level.cor,
				"tempo_maximo_espera_min": level.tempo_maximo_espera_min,
			}
			for level in levels
		],
	}


@frappe.whitelist()
def fetch_protocol_and_levels(unit, date):
	if not frappe.has_permission("Classificacao de Risco Diaria", "create"):
		frappe.throw(_("Sem permissão para criar classificações diárias."), frappe.PermissionError)
	return resolve_protocol_and_levels(unit, date)


class ClassificacaodeRiscoDiaria(Document):
	def before_insert(self):
		self.lancado_por = frappe.session.user
		self.criado_em = now_datetime()

	def validate(self):
		if not self.unidade or not self.data:
			frappe.throw(_("Informe a unidade e a data."))
		previous = self.get_doc_before_save() if not self.is_new() else None
		if previous:
			self.lancado_por = previous.lancado_por
			self.criado_em = previous.criado_em

		self._validar_lancamento_unico()
		resolved = resolve_protocol_and_levels(self.unidade, self.data)
		self.protocolo = resolved["protocolo"]
		levels = resolved["niveis"]
		if not self.niveis_classificados and self.is_new():
			for level in levels:
				self.append("niveis_classificados", level)

		rows = self.niveis_classificados or []
		if [row.nivel for row in rows] != [level["nivel"] for level in levels]:
			frappe.throw(
				_(
					"Os níveis devem corresponder, na mesma ordem, ao protocolo vigente. "
					"Atualize a unidade ou a data para recarregá-los."
				)
			)
		same_context = (
			previous
			and previous.unidade == self.unidade
			and getdate(previous.data) == getdate(self.data)
			and previous.protocolo == self.protocolo
			and [row.nivel for row in previous.niveis_classificados] == [level["nivel"] for level in levels]
		)
		for index, row in enumerate(rows):
			row.cor = previous.niveis_classificados[index].cor if same_context else levels[index]["cor"]
			row.tempo_maximo_espera_min = (
				previous.niveis_classificados[index].tempo_maximo_espera_min
				if same_context and previous.niveis_classificados[index].tempo_snapshot_preenchido
				else levels[index]["tempo_maximo_espera_min"]
			)
			row.tempo_snapshot_preenchido = 1

		total = 0
		for row in rows:
			classified = cint(row.qtd_pacientes_classificados)
			if classified < 0:
				frappe.throw(_("A quantidade do nível {0} não pode ser negativa.").format(row.nivel))
			total += classified
		self.total_classificados = total
		self.status = "Rascunho" if self.docstatus == 0 else "Enviado"

	def before_submit(self):
		self.status = "Enviado"

	def _validate_unique_entry(self):
		other = frappe.db.exists(
			"Classificacao de Risco Diaria",
			{
				"unidade": self.unidade,
				"data": getdate(self.data),
				"docstatus": ["<", 2],
				"name": ["!=", self.name or ""],
			},
		)
		if other:
			frappe.throw(
				_("Já existe uma classificação diária para esta unidade e data ({0}).").format(other)
			)
