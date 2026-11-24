"""Optional integration with the `assinatura_eletronica` and `integracoes_customizadas` apps.

- Comissao Membro as signatory (name, phone and e-mail from the registry row).
- Signature profile of the Reuniao de Comissao minutes: the present participants sign.
- Custodian responsibility term: on the Asset (initial custody, signed by `custodian`) and on the Asset Movement
  (signed by each `to_employee`; the Receipt created by ERPNext when submitting the Asset is left out to avoid duplicates).
- Idempotent seeding of the Signature Templates and the WhatsApp convocation Template (after_migrate).

The profile base class and its Portuguese method/attribute names (`conteudo`, `signatarios`, ...) are the API of
`assinatura_eletronica`; they are kept as is. The import is guarded, so this module loads without that app.
"""

import frappe
from frappe import _
from frappe.utils import cstr, format_datetime, strip_html

MEETING = "Reuniao de Comissao"
ASSET = "Asset"
ASSET_MOVEMENT = "Asset Movement"
CONTROL_NUMBER_FIELD = "custom_número_de_controle_bhcl"
MUNICIPAL_ASSET_NUMBER_FIELD = "custom_número_patrimônio_prefeitura"
CONVOCATION_TEMPLATE = "Convocação de Reunião de Comissão"

try:
	from assinatura_eletronica.destinatarios import Destinatario
	from assinatura_eletronica.perfil import PerfilAssinatura, Signatario
except ImportError:  # optional app: the module stays importable without it
	Destinatario = PerfilAssinatura = Signatario = None


def get_committee_name(doc):
	return frappe.db.get_value("Tipo de Comissao", doc.tipo_comissao, "nome_tipo") or doc.tipo_comissao


def member_recipient(name):
	row = frappe.db.get_value("Comissao Membro", name, ["nome", "telefone", "email"], as_dict=True)
	if not row:
		return None
	# WhatsApp applies to everyone (engine default); without a phone the engine skips the channel. The formal
	# acceptance happens on the link (OTP + declaration).
	return Destinatario(row.nome, row.telefone, row.email, aceita_eletronica=True)


if PerfilAssinatura:

	class CommitteeMeetingProfile(PerfilAssinatura):
		prefixo_arquivo = "Ata-Comissao"
		situacoes = {"Concluído": "assinatura", "Recusado": "recusa"}  # noqa: RUF012

		def _present_participants(self, doc):
			return [p for p in doc.participantes if p.membro_origem and p.status_presenca == "Presente"]

		def conteudo(self, doc) -> dict:
			return {
				"comissao": cstr(get_committee_name(doc)),
				"mandato": cstr(doc.mandato_comissao),
				"data_reuniao": cstr(doc.data_reuniao),
				"local": cstr(doc.local_reuniao),
				"pauta": [cstr(p.assunto) for p in doc.pauta],
				"deliberacoes": strip_html(doc.deliberacoes or ""),
				"encaminhamentos": strip_html(doc.encaminhamentos_conclusoes or ""),
				"presentes": sorted(p.membro_origem for p in self._present_participants(doc)),
			}

		def signatarios(self, doc):
			return [
				Signatario("Comissao Membro", p.membro_origem, p.funcao or "Membro", 1)
				for p in self._present_participants(doc)
			]

		def validar_solicitacao(self, doc):
			super().validar_solicitacao(doc)
			if not self._present_participants(doc):
				frappe.throw(_("A reunião não tem participantes presentes vindos do cadastro de membros."))

		def resumo_publico(self, doc, signatario) -> dict:
			return {
				"secao": _("Ata de reunião"),
				"fatos": [
					(_("Comissão"), get_committee_name(doc)),
					(_("Reunião"), format_datetime(doc.data_reuniao)),
					(_("Local"), doc.local_reuniao),
					(_("Deliberações"), strip_html(doc.deliberacoes or "")[:400]),
				],
				"tabela": None,
			}

		def dados_verificacao(self, doc) -> list[tuple]:
			return [(_("Comissão"), get_committee_name(doc)), (_("Empresa"), doc.empresa)]


def get_employee_name(employee):
	return (frappe.db.get_value("Employee", employee, "employee_name") or employee) if employee else ""


def received_rows(doc, employee=None):
	"""Movement rows with a destination custodian (of one employee, if given)."""
	return [r for r in doc.assets if r.to_employee and (employee is None or r.to_employee == employee)]


if PerfilAssinatura:

	class AssetTermProfile(PerfilAssinatura):
		prefixo_arquivo = "Termo-Responsabilidade-Ativo"

		def conteudo(self, doc) -> dict:
			# Only identification and custody: depreciation and status change without changing the term.
			return {
				"ativo": doc.name,
				"nome": cstr(doc.asset_name),
				"item": cstr(doc.item_code),
				"categoria": cstr(doc.asset_category),
				"controle_bhcl": cstr(doc.get(CONTROL_NUMBER_FIELD)),
				"patrimonio_prefeitura": cstr(doc.get(MUNICIPAL_ASSET_NUMBER_FIELD)),
				"empresa": cstr(doc.company),
				"localizacao": cstr(doc.location),
				"custodiante": cstr(doc.custodian),
			}

		def signatarios(self, doc):
			return [Signatario("Employee", doc.custodian, "Custodiante", 1)]

		def validar_solicitacao(self, doc):
			super().validar_solicitacao(doc)
			if not doc.custodian:
				frappe.throw(_("Informe o custodiante do ativo para solicitar o termo de responsabilidade."))

		def resumo_publico(self, doc, signatario) -> dict:
			return {
				"secao": _("Termo de responsabilidade"),
				"fatos": [
					(_("Bem"), doc.asset_name),
					(_("Controle BHCL"), doc.get(CONTROL_NUMBER_FIELD)),
					(_("Patrimônio Prefeitura"), doc.get(MUNICIPAL_ASSET_NUMBER_FIELD)),
					(_("Categoria"), doc.asset_category),
					(_("Localização"), doc.location),
					(_("Empresa"), doc.company),
				],
				"tabela": None,
			}

		def dados_verificacao(self, doc) -> list[tuple]:
			return [(_("Empresa"), doc.company), (_("Controle BHCL"), doc.get(CONTROL_NUMBER_FIELD))]

		def contexto_mensagem(self, doc) -> dict:
			return {"bem": cstr(doc.asset_name)}

	class AssetMovementTermProfile(PerfilAssinatura):
		prefixo_arquivo = "Termo-Responsabilidade-Movimentacao"

		def conteudo(self, doc) -> dict:
			return {
				"finalidade": cstr(doc.purpose),
				"empresa": cstr(doc.company),
				"data": cstr(doc.transaction_date),
				"bens": [
					{
						"ativo": cstr(r.asset),
						"origem": cstr(r.source_location),
						"destino": cstr(r.target_location),
						"de": cstr(r.from_employee),
						"para": cstr(r.to_employee),
					}
					for r in doc.assets
				],
			}

		def signatarios(self, doc):
			custodians = dict.fromkeys(r.to_employee for r in received_rows(doc))
			return [Signatario("Employee", emp, "Custodiante", 1) for emp in custodians]

		def validar_solicitacao(self, doc):
			super().validar_solicitacao(doc)
			if doc.purpose == "Receipt":
				frappe.throw(
					_(
						"O recebimento inicial é assinado no próprio ativo. Solicite o termo no cadastro do ativo."
					)
				)
			if not received_rows(doc):
				frappe.throw(
					_("Nenhum bem desta movimentação foi entregue a um custodiante (Para Funcionário).")
				)

		def resumo_publico(self, doc, signatario) -> dict:
			# Only the signatory's own assets.
			rows = [
				[
					{
						"texto": r.asset_name or r.asset,
						"detalhe": cstr(frappe.db.get_value(ASSET, r.asset, CONTROL_NUMBER_FIELD)),
					},
					{"texto": r.source_location or "—", "detalhe": get_employee_name(r.from_employee)},
					r.target_location or "—",
				]
				for r in received_rows(doc, signatario.parte)
			]
			return {
				"secao": _("Termo de responsabilidade"),
				"fatos": [
					(_("Custodiante"), get_employee_name(signatario.parte)),
					(_("Empresa"), doc.company),
					(_("Data da movimentação"), format_datetime(doc.transaction_date)),
				],
				"tabela": {
					"titulo": _("Bens sob sua responsabilidade"),
					"colunas": [_("Bem"), _("Origem"), _("Destino")],
					"linhas": rows,
				},
			}

		def dados_verificacao(self, doc) -> list[tuple]:
			return [
				(_("Empresa"), doc.company),
				(_("Data da movimentação"), format_datetime(doc.transaction_date)),
				(_("Bens"), len(doc.assets)),
			]


def _link_message(document):
	return (
		f"Olá, {{{{ nome }}}}! {document} está disponível para a sua assinatura. "
		"Acesse o link abaixo (válido por {{ validade_horas }} horas):\n{{ link }}"
	)


def _receipt_message(document):
	return (
		f"Olá, {{{{ nome }}}}! Segue o comprovante da {{{{ situacao }}}} {document}.\n"
		"Código de verificação: *{{ codigo }}*\nConfira a autenticidade em:\n{{ link_verificacao }}"
	)


COMMON = {
	"ativo": 1,
	"modo": "Paralelo",
	"exigir_aceite_eletronico": 1,
	"exigir_aceite_whatsapp": 1,  # respects WhatsApp being disabled; enabled by default
	"validade_link_horas": 72,
	"emitir_comprovante": 1,
	"enviar_comprovante": 1,
	"enviar_link_automaticamente": 0,
	"texto_consentimento": "Li e concordo com a declaração acima.",
}

RESPONSIBILITY_DECLARATION = (
	"<p>Declaro que recebi {bens} em condições de uso e assumo a responsabilidade pela sua guarda, conservação e "
	"uso adequado, exclusivamente no interesse da instituição.</p>"
	"<p>Comprometo-me a comunicar imediatamente ao setor de Patrimônio qualquer dano, defeito, extravio, furto ou "
	"necessidade de transferência, e a devolvê-{pronome} quando solicitado ou no meu desligamento.</p>"
)

TEMPLATES = {
	MEETING: {
		"print_format": "Ata de Reuniao de Comissao",
		"exigir_submissao": 0,
		"titulo": "Ata de reunião de comissão",
		"subtitulo": "Registro da participação e das deliberações",
		"descricao_previa": "Confira e assine a ata da reunião da comissão.",
		"assunto_email": "Ata de reunião de comissão para assinatura",
		"setor": "Comissões",
		"texto_suporte": "Em caso de dúvida, procure a secretaria da comissão.",
		"texto_declaracao": (
			"<p>Declaro que participei da reunião descrita acima e que estou de acordo com o registro "
			"das deliberações na ata.</p>"
		),
		"msg_otp": "Seu código para assinar a ata é {{ codigo }}. Ele vale por {{ validade_minutos }} minutos. Não o compartilhe.",
		"msg_link": _link_message("A ata da reunião da comissão"),
		"msg_comprovante": _receipt_message("da ata"),
	},
	ASSET: {
		"print_format": "Termo de Responsabilidade do Ativo",
		"exigir_submissao": 1,
		"titulo": "Termo de responsabilidade",
		"subtitulo": "Guarda e conservação de bem patrimonial",
		"descricao_previa": "Patrimônio · Confira o bem sob a sua guarda e assine o termo de responsabilidade.",
		"assunto_email": "Termo de responsabilidade de bem patrimonial",
		"setor": "Patrimônio",
		"texto_suporte": "Em caso de dúvida, procure o setor de Patrimônio da sua unidade.",
		"texto_declaracao": RESPONSIBILITY_DECLARATION.format(bens="o bem acima identificado", pronome="lo"),
		"msg_otp": "Seu código para assinar o termo de responsabilidade é {{ codigo }}. Ele vale por {{ validade_minutos }} minutos. Não o compartilhe.",
		"msg_link": _link_message("O termo de responsabilidade do bem {{ bem }}"),
		"msg_comprovante": _receipt_message("do termo de responsabilidade"),
	},
	ASSET_MOVEMENT: {
		"print_format": "Termo de Responsabilidade de Movimentacao",
		"exigir_submissao": 1,
		"titulo": "Termo de responsabilidade",
		"subtitulo": "Recebimento e guarda de bens patrimoniais",
		"descricao_previa": "Patrimônio · Confira os bens entregues a você e assine o termo de responsabilidade.",
		"assunto_email": "Termo de responsabilidade de bens patrimoniais",
		"setor": "Patrimônio",
		"texto_suporte": "Em caso de dúvida, procure o setor de Patrimônio da sua unidade.",
		"texto_declaracao": RESPONSIBILITY_DECLARATION.format(
			bens="os bens acima relacionados", pronome="los"
		),
		"msg_otp": "Seu código para assinar o termo de responsabilidade é {{ codigo }}. Ele vale por {{ validade_minutos }} minutos. Não o compartilhe.",
		"msg_link": _link_message("O termo de responsabilidade dos bens recebidos"),
		"msg_comprovante": _receipt_message("do termo de responsabilidade"),
	},
}


def ensure_signature_templates():
	"""Create the missing Signature Templates (only for DocTypes present on the site); never overwrites."""
	if not frappe.db.exists("DocType", "Modelo de Assinatura"):
		return
	for doctype, values in TEMPLATES.items():
		if not frappe.db.exists("DocType", doctype) or frappe.db.exists("Modelo de Assinatura", doctype):
			continue
		if not frappe.db.exists("Print Format", values["print_format"]):
			values = {k: v for k, v in values.items() if k != "print_format"}
		template = frappe.get_doc(
			{"doctype": "Modelo de Assinatura", "documento": doctype, **COMMON, **values}
		)
		template.flags.ignore_permissions = True
		template.insert()


def ensure_convocation_template():
	if not frappe.db.exists("DocType", "Modelo WhatsApp") or frappe.db.exists(
		"Modelo WhatsApp", CONVOCATION_TEMPLATE
	):
		return
	frappe.get_doc(
		{
			"doctype": "Modelo WhatsApp",
			"titulo": CONVOCATION_TEMPLATE,
			"documento": MEETING,
			"ativo": 1,
			"assunto_email": "Convocação para reunião – {{ extra.comissao }}",  # noqa: RUF001
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
	ensure_signature_templates()
	ensure_convocation_template()
