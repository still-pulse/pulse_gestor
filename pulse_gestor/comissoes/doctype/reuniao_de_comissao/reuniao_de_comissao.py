import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime

from pulse_gestor.assinatura import nome_comissao
from pulse_gestor.telefone import validar_e_formatar_linhas

MODELO_CONVOCACAO = "Convocação de Reunião de Comissão"


@frappe.whitelist()
def buscar_membros(membros_comissao):
	if not frappe.has_permission("Reuniao de Comissao", "create"):
		frappe.throw(_("Sem permissão para criar reuniões de comissão."), frappe.PermissionError)
	return frappe.get_all(
		"Comissao Membro",
		filters={"parent": membros_comissao, "parenttype": "Membros de Comissao"},
		fields=["name", "nome", "funcao", "email", "telefone", "canal_preferencial"],
		order_by="idx asc",
	)


@frappe.whitelist()
def convocar(name, canal=None):
	"""Convoca os participantes pelo Modelo WhatsApp; `canal` força WhatsApp/E-mail/Ambos para todos."""
	doc = frappe.get_doc("Reuniao de Comissao", name)
	doc.check_permission("write")
	if canal and canal not in ("WhatsApp", "E-mail", "Ambos"):
		frappe.throw(_("Canal inválido."))
	if not frappe.db.exists("DocType", "Modelo WhatsApp"):
		frappe.throw(_("O app integracoes_customizadas é necessário para enviar convocações."))
	from integracoes_customizadas.whatsapp.modelos import enviar_modelo

	resumo = {"enviados": 0, "falhas": 0}
	for linha in doc.participantes:
		resultado = enviar_modelo(
			MODELO_CONVOCACAO,
			doc,
			telefone=linha.telefone,
			email=linha.email,
			canal=canal or linha.canal_preferencial or "WhatsApp",
			extra={"participante": linha, "comissao": nome_comissao(doc)},
		)
		if resultado["canais"]:
			linha.db_set("convocado_em", now_datetime())
			linha.db_set("status_convocacao", _("Enviado: {0}").format(", ".join(resultado["canais"])))
			resumo["enviados"] += 1
		else:
			linha.db_set("status_convocacao", (resultado["erro"] or "")[:140])
			resumo["falhas"] += 1
	doc.add_comment(
		"Info",
		_("Convocação enviada: {0} participante(s) notificado(s), {1} falha(s).").format(
			resumo["enviados"], resumo["falhas"]
		),
	)
	return resumo


class ReuniaodeComissao(Document):
	def validate(self):
		validar_e_formatar_linhas(self.participantes)
