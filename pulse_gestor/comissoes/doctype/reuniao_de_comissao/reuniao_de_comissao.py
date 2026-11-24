import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime

from pulse_gestor.phone import validate_and_format_rows
from pulse_gestor.signature_profiles import get_committee_name

CONVOCATION_TEMPLATE = "Convocação de Reunião de Comissão"


@frappe.whitelist()
def fetch_members(members_doc):
	if not frappe.has_permission("Reuniao de Comissao", "create"):
		frappe.throw(_("Sem permissão para criar reuniões de comissão."), frappe.PermissionError)
	return frappe.get_all(
		"Comissao Membro",
		filters={"parent": members_doc, "parenttype": "Membros de Comissao"},
		fields=["name", "nome", "funcao", "email", "telefone", "canal_preferencial"],
		order_by="idx asc",
	)


@frappe.whitelist()
def send_convocation(name, channel=None):
	"""Summon the participants through the WhatsApp Template; `channel` forces WhatsApp/E-mail/Ambos for everyone."""
	doc = frappe.get_doc("Reuniao de Comissao", name)
	doc.check_permission("write")
	if channel and channel not in ("WhatsApp", "E-mail", "Ambos"):
		frappe.throw(_("Canal inválido."))
	# Weak dependency (not in required_apps): guard before importing; see docs/dependencies.md.
	if "integracoes_customizadas" not in frappe.get_installed_apps() or not frappe.db.exists(
		"DocType", "Modelo WhatsApp"
	):
		frappe.throw(_("O app integracoes_customizadas é necessário para enviar convocações."))
	from integracoes_customizadas.whatsapp.modelos import enviar_modelo

	summary = {"enviados": 0, "falhas": 0}
	for row in doc.participantes:
		result = enviar_modelo(
			CONVOCATION_TEMPLATE,
			doc,
			telefone=row.telefone,
			email=row.email,
			canal=channel or row.canal_preferencial or "WhatsApp",
			extra={"participante": row, "comissao": get_committee_name(doc)},
		)
		if result["canais"]:
			row.db_set("convocado_em", now_datetime())
			row.db_set("status_convocacao", _("Enviado: {0}").format(", ".join(result["canais"])))
			summary["enviados"] += 1
		else:
			row.db_set("status_convocacao", (result["erro"] or "")[:140])
			summary["falhas"] += 1
	doc.add_comment(
		"Info",
		_("Convocação enviada: {0} participante(s) notificado(s), {1} falha(s).").format(
			summary["enviados"], summary["falhas"]
		),
	)
	return summary


class ReuniaodeComissao(Document):
	def validate(self):
		validate_and_format_rows(self.participantes)
