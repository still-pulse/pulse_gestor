"""Integração opcional com os apps `assinatura_eletronica` e `integracoes_customizadas`.

- Comissao Membro como signatário (nome, telefone e e-mail da linha do cadastro).
- Perfil de assinatura da ata de Reuniao de Comissao: assinam os participantes presentes.
- Termo de Responsabilidade do custodiante: no Asset (custódia inicial, assina o `custodian`) e na Asset Movement
  (assina cada `to_employee`; o Receipt criado pelo ERPNext ao submeter o Asset fica de fora para não duplicar).
- Semeadura idempotente dos Modelos de Assinatura e do Modelo WhatsApp de convocação (after_migrate).
"""

import frappe
from frappe import _
from frappe.utils import cstr, format_datetime, strip_html

REUNIAO = "Reuniao de Comissao"
ATIVO = "Asset"
MOVIMENTACAO = "Asset Movement"
CONTROLE_BHCL = "custom_número_de_controle_bhcl"
PATRIMONIO_PREFEITURA = "custom_número_patrimônio_prefeitura"
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
			return [
				Signatario("Comissao Membro", p.membro_origem, p.funcao or "Membro", 1)
				for p in self._presentes(doc)
			]

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


def nome_colaborador(employee):
	return (frappe.db.get_value("Employee", employee, "employee_name") or employee) if employee else ""


def linhas_recebidas(doc, employee=None):
	"""Linhas da movimentação com custodiante de destino (de um colaborador, se informado)."""
	return [r for r in doc.assets if r.to_employee and (employee is None or r.to_employee == employee)]


if PerfilAssinatura:

	class PerfilTermoDoAtivo(PerfilAssinatura):
		prefixo_arquivo = "Termo-Responsabilidade-Ativo"

		def conteudo(self, doc) -> dict:
			# Só a identificação e a custódia: depreciação e status mudam sem mudar o termo.
			return {
				"ativo": doc.name,
				"nome": cstr(doc.asset_name),
				"item": cstr(doc.item_code),
				"categoria": cstr(doc.asset_category),
				"controle_bhcl": cstr(doc.get(CONTROLE_BHCL)),
				"patrimonio_prefeitura": cstr(doc.get(PATRIMONIO_PREFEITURA)),
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
					(_("Controle BHCL"), doc.get(CONTROLE_BHCL)),
					(_("Patrimônio Prefeitura"), doc.get(PATRIMONIO_PREFEITURA)),
					(_("Categoria"), doc.asset_category),
					(_("Localização"), doc.location),
					(_("Empresa"), doc.company),
				],
				"tabela": None,
			}

		def dados_verificacao(self, doc) -> list[tuple]:
			return [(_("Empresa"), doc.company), (_("Controle BHCL"), doc.get(CONTROLE_BHCL))]

		def contexto_mensagem(self, doc) -> dict:
			return {"bem": cstr(doc.asset_name)}

	class PerfilTermoDeMovimentacao(PerfilAssinatura):
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
			custodiantes = dict.fromkeys(r.to_employee for r in linhas_recebidas(doc))
			return [Signatario("Employee", emp, "Custodiante", 1) for emp in custodiantes]

		def validar_solicitacao(self, doc):
			super().validar_solicitacao(doc)
			if doc.purpose == "Receipt":
				frappe.throw(
					_(
						"O recebimento inicial é assinado no próprio ativo. Solicite o termo no cadastro do ativo."
					)
				)
			if not linhas_recebidas(doc):
				frappe.throw(
					_("Nenhum bem desta movimentação foi entregue a um custodiante (Para Funcionário).")
				)

		def resumo_publico(self, doc, signatario) -> dict:
			# Só os bens do próprio signatário.
			linhas = [
				[
					{
						"texto": r.asset_name or r.asset,
						"detalhe": cstr(frappe.db.get_value(ATIVO, r.asset, CONTROLE_BHCL)),
					},
					{"texto": r.source_location or "—", "detalhe": nome_colaborador(r.from_employee)},
					r.target_location or "—",
				]
				for r in linhas_recebidas(doc, signatario.parte)
			]
			return {
				"secao": _("Termo de responsabilidade"),
				"fatos": [
					(_("Custodiante"), nome_colaborador(signatario.parte)),
					(_("Empresa"), doc.company),
					(_("Data da movimentação"), format_datetime(doc.transaction_date)),
				],
				"tabela": {
					"titulo": _("Bens sob sua responsabilidade"),
					"colunas": [_("Bem"), _("Origem"), _("Destino")],
					"linhas": linhas,
				},
			}

		def dados_verificacao(self, doc) -> list[tuple]:
			return [
				(_("Empresa"), doc.company),
				(_("Data da movimentação"), format_datetime(doc.transaction_date)),
				(_("Bens"), len(doc.assets)),
			]


def _msg_link(documento):
	return (
		f"Olá, {{{{ nome }}}}! {documento} está disponível para a sua assinatura. "
		"Acesse o link abaixo (válido por {{ validade_horas }} horas):\n{{ link }}"
	)


def _msg_comprovante(documento):
	return (
		f"Olá, {{{{ nome }}}}! Segue o comprovante da {{{{ situacao }}}} {documento}.\n"
		"Código de verificação: *{{ codigo }}*\nConfira a autenticidade em:\n{{ link_verificacao }}"
	)


COMUM = {
	"ativo": 1,
	"modo": "Paralelo",
	"exigir_aceite_eletronico": 1,
	"exigir_aceite_whatsapp": 0,
	"validade_link_horas": 72,
	"emitir_comprovante": 1,
	"enviar_comprovante": 1,
	"enviar_link_automaticamente": 0,
	"texto_consentimento": "Li e concordo com a declaração acima.",
}

DECLARACAO_RESPONSABILIDADE = (
	"<p>Declaro que recebi {bens} em condições de uso e assumo a responsabilidade pela sua guarda, conservação e "
	"uso adequado, exclusivamente no interesse da instituição.</p>"
	"<p>Comprometo-me a comunicar imediatamente ao setor de Patrimônio qualquer dano, defeito, extravio, furto ou "
	"necessidade de transferência, e a devolvê-{pronome} quando solicitado ou no meu desligamento.</p>"
)

MODELOS = {
	REUNIAO: {
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
		"msg_link": _msg_link("A ata da reunião da comissão"),
		"msg_comprovante": _msg_comprovante("da ata"),
	},
	ATIVO: {
		"print_format": "Termo de Responsabilidade do Ativo",
		"exigir_submissao": 1,
		"titulo": "Termo de responsabilidade",
		"subtitulo": "Guarda e conservação de bem patrimonial",
		"descricao_previa": "Patrimônio · Confira o bem sob a sua guarda e assine o termo de responsabilidade.",
		"assunto_email": "Termo de responsabilidade de bem patrimonial",
		"setor": "Patrimônio",
		"texto_suporte": "Em caso de dúvida, procure o setor de Patrimônio da sua unidade.",
		"texto_declaracao": DECLARACAO_RESPONSABILIDADE.format(bens="o bem acima identificado", pronome="lo"),
		"msg_otp": "Seu código para assinar o termo de responsabilidade é {{ codigo }}. Ele vale por {{ validade_minutos }} minutos. Não o compartilhe.",
		"msg_link": _msg_link("O termo de responsabilidade do bem {{ bem }}"),
		"msg_comprovante": _msg_comprovante("do termo de responsabilidade"),
	},
	MOVIMENTACAO: {
		"print_format": "Termo de Responsabilidade de Movimentacao",
		"exigir_submissao": 1,
		"titulo": "Termo de responsabilidade",
		"subtitulo": "Recebimento e guarda de bens patrimoniais",
		"descricao_previa": "Patrimônio · Confira os bens entregues a você e assine o termo de responsabilidade.",
		"assunto_email": "Termo de responsabilidade de bens patrimoniais",
		"setor": "Patrimônio",
		"texto_suporte": "Em caso de dúvida, procure o setor de Patrimônio da sua unidade.",
		"texto_declaracao": DECLARACAO_RESPONSABILIDADE.format(
			bens="os bens acima relacionados", pronome="los"
		),
		"msg_otp": "Seu código para assinar o termo de responsabilidade é {{ codigo }}. Ele vale por {{ validade_minutos }} minutos. Não o compartilhe.",
		"msg_link": _msg_link("O termo de responsabilidade dos bens recebidos"),
		"msg_comprovante": _msg_comprovante("do termo de responsabilidade"),
	},
}


def ensure_modelos_assinatura():
	"""Cria os Modelos de Assinatura que faltam (só para DocTypes existentes no site); nunca sobrescreve."""
	if not frappe.db.exists("DocType", "Modelo de Assinatura"):
		return
	for doctype, valores in MODELOS.items():
		if not frappe.db.exists("DocType", doctype) or frappe.db.exists("Modelo de Assinatura", doctype):
			continue
		if not frappe.db.exists("Print Format", valores["print_format"]):
			valores = {k: v for k, v in valores.items() if k != "print_format"}
		modelo = frappe.get_doc({"doctype": "Modelo de Assinatura", "documento": doctype, **COMUM, **valores})
		modelo.flags.ignore_permissions = True
		modelo.insert()


def ensure_modelo_convocacao():
	if not frappe.db.exists("DocType", "Modelo WhatsApp") or frappe.db.exists(
		"Modelo WhatsApp", MODELO_CONVOCACAO
	):
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
	ensure_modelos_assinatura()
	ensure_modelo_convocacao()
