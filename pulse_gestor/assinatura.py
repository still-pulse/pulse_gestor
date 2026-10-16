"""Integração opcional com os apps `assinatura_eletronica` e `integracoes_customizadas`.

- Comissao Membro como signatário (nome, telefone e e-mail da linha do cadastro).
- Perfil de assinatura da ata de Reuniao de Comissao: assinam os participantes presentes.
- Semeadura idempotente do Modelo de Assinatura e do Modelo WhatsApp de convocação (after_migrate).
"""

import frappe
from frappe import _
from frappe.utils import cstr, format_datetime, strip_html

REUNIAO = "Reuniao de Comissao"
MODELO_CONVOCACAO = "Convocação de Reunião de Comissão"

try:
	from assinatura_eletronica.destinatarios import Destinatario
	from assinatura_eletronica.perfil import PerfilAssinatura, Signatario
except ImportError:  # app opcional: o módulo continua importável sem ele
	Destinatario = PerfilAssinatura = Signatario = None


def nome_comissao(doc):
	return frappe.db.get_value("Tipo de Comissao", doc.tipo_comissao, "nome_tipo") or doc.tipo_comissao


def destinatario_membro(name):
	linha = frappe.db.get_value("Comissao Membro", name, ["nome", "telefone", "email"], as_dict=True)
	if not linha:
		return None
	# Ser membro e cadastrar o telefone já indica o canal; o aceite formal vem no link (OTP + declaração).
	return Destinatario(linha.nome, linha.telefone, linha.email, True, bool(linha.telefone))


if PerfilAssinatura:

	class PerfilReuniaoDeComissao(PerfilAssinatura):
		prefixo_arquivo = "Ata-Comissao"
		situacoes = {"Concluído": "assinatura", "Recusado": "recusa"}  # noqa: RUF012

		def _presentes(self, doc):
			return [p for p in doc.participantes if p.membro_origem and p.status_presenca == "Presente"]

		def conteudo(self, doc) -> dict:
			return {
				"comissao": cstr(nome_comissao(doc)),
				"mandato": cstr(doc.mandato_comissao),
				"data_reuniao": cstr(doc.data_reuniao),
				"local": cstr(doc.local_reuniao),
				"pauta": [cstr(p.assunto) for p in doc.pauta],
				"deliberacoes": strip_html(doc.deliberacoes or ""),
				"encaminhamentos": strip_html(doc.encaminhamentos_conclusoes or ""),
				"presentes": sorted(p.membro_origem for p in self._presentes(doc)),
			}

		def signatarios(self, doc):
			return [Signatario("Comissao Membro", p.membro_origem, p.funcao or "Membro", 1) for p in self._presentes(doc)]

		def validar_solicitacao(self, doc):
			super().validar_solicitacao(doc)
			if not self._presentes(doc):
				frappe.throw(_("A reunião não tem participantes presentes vindos do cadastro de membros."))

		def resumo_publico(self, doc, signatario) -> dict:
			return {
				"secao": _("Ata de reunião"),
				"fatos": [
					(_("Comissão"), nome_comissao(doc)),
					(_("Reunião"), format_datetime(doc.data_reuniao)),
					(_("Local"), doc.local_reuniao),
					(_("Deliberações"), strip_html(doc.deliberacoes or "")[:400]),
				],
				"tabela": None,
			}

		def dados_verificacao(self, doc) -> list[tuple]:
			return [(_("Comissão"), nome_comissao(doc)), (_("Empresa"), doc.empresa)]


def ensure_modelo_assinatura():
	if not frappe.db.exists("DocType", "Modelo de Assinatura") or frappe.db.exists("Modelo de Assinatura", REUNIAO):
		return
	valores = {
		"doctype": "Modelo de Assinatura",
		"documento": REUNIAO,
		"ativo": 1,
		"modo": "Paralelo",
		"exigir_submissao": 0,
		"titulo": "Ata de reunião de comissão",
		"subtitulo": "Registro da participação e das deliberações",
		"descricao_previa": "Confira e assine a ata da reunião da comissão.",
		"assunto_email": "Ata de reunião de comissão para assinatura",
		"setor": "Comissões",
		"texto_suporte": "Em caso de dúvida, procure a secretaria da comissão.",
		"exigir_aceite_eletronico": 1,
		"exigir_aceite_whatsapp": 0,
		"validade_link_horas": 72,
		"emitir_comprovante": 1,
		"enviar_comprovante": 1,
		"enviar_link_automaticamente": 0,
		"texto_declaracao": (
			"<p>Declaro que participei da reunião descrita acima e que estou de acordo com o registro "
			"das deliberações na ata.</p>"
		),
		"texto_consentimento": "Li e concordo com a declaração acima.",
		"msg_otp": "Seu código para assinar a ata é {{ codigo }}. Ele vale por {{ validade_minutos }} minutos. Não o compartilhe.",
		"msg_link": (
			"Olá, {{ nome }}! A ata da reunião da comissão está disponível para a sua assinatura. "
			"Acesse o link abaixo (válido por {{ validade_horas }} horas):\n{{ link }}"
		),
		"msg_comprovante": (
			"Olá, {{ nome }}! Segue o comprovante da {{ situacao }} da ata.\n"
			"Código de verificação: *{{ codigo }}*\nConfira a autenticidade em:\n{{ link_verificacao }}"
		),
	}
	if frappe.db.exists("Print Format", "Ata de Reuniao de Comissao"):
		valores["print_format"] = "Ata de Reuniao de Comissao"
	modelo = frappe.get_doc(valores)
	modelo.flags.ignore_permissions = True
	modelo.insert()


def ensure_modelo_convocacao():
	if not frappe.db.exists("DocType", "Modelo WhatsApp") or frappe.db.exists("Modelo WhatsApp", MODELO_CONVOCACAO):
		return
	frappe.get_doc(
		{
			"doctype": "Modelo WhatsApp",
			"titulo": MODELO_CONVOCACAO,
			"documento": REUNIAO,
			"ativo": 1,
			"assunto_email": "Convocação para reunião – {{ extra.comissao }}",
			"mensagem": (
				"Olá, {{ seguro(extra.participante.nome) }}!\n\n"
				"Você está convocado(a) para a reunião da *{{ seguro(extra.comissao) }}*.\n\n"
				"📅 *Data:* {{ data(doc.data_reuniao) }} às {{ hora(doc.data_reuniao) }}\n"
				"📍 *Local:* {{ seguro(doc.local_reuniao) or 'a definir' }}\n"
				"{% if doc.pauta %}\n*Pauta:*\n"
				"{% for item in doc.pauta %}• {{ seguro(item.assunto) }}\n{% endfor %}{% endif %}\n"
				"Pedimos que confirme sua presença."
			),
		}
	).insert(ignore_permissions=True)


def after_migrate():
	ensure_modelo_assinatura()
	ensure_modelo_convocacao()
