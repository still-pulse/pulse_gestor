# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

"""Instalação e migrate do Pulse Gestor."""

from __future__ import annotations

import json
from pathlib import Path

import frappe
from frappe.model.rename_doc import rename_doc
from frappe.permissions import add_permission

from pulse_gestor.print_formats import ensure_default_print_formats, retire_legacy_print_formats

ROLES = (
	{"role_name": "Pulse Gestor Manager", "desk_access": 1},
	{"role_name": "Pulse Gestor Viewer", "desk_access": 1},
)

NOTIFICACAO_A_VENCER = "Documento da Unidade a Vencer"
DIAS_ALERTA_PADRAO = 30


def after_install():
	ensure_roles()
	ensure_classificacao_import_permissions()
	ensure_settings()
	ensure_pulse_gestor_workspace()
	frappe.db.commit()


def after_migrate():
	ensure_roles()
	ensure_classificacao_import_permissions()
	ensure_settings()
	sincronizar_dias_alerta()
	ensure_ascii_indicadores_report()
	ensure_pulse_gestor_workspace()
	backfill_cores_classificacao_diaria()
	backfill_tempos_classificacao_diaria()
	from pulse_gestor.assinatura import after_migrate as semear_comunicacao

	semear_comunicacao()
	ensure_print_formats()
	frappe.db.commit()


WORKSPACE = "Gestor"
# Card Breaks e Links do app, anexados ao Workspace Gestor
WORKSPACE_LINKS_JSON = Path(__file__).resolve().parent / "gestor_links.json"
PREFIXO_BLOCOS = "pg_"
# Workspaces do app que foram unificados no Gestor
WORKSPACES_UNIFICADOS = ("Pulse Gestor", "Indicadores", "Comissoes", "Documentacao da Unidade")
DOCUMENTOS_NUMBER_CARDS = (
	("PG Total Documentos", "Total"),
	("PG Documentos Validos", "Válidos"),
	("PG Documentos Vencidos", "Vencidos"),
)

INDICADORES_LANCAMENTO = "Classificacao de Risco Diaria"
INDICADORES_RELATORIO = "Apuracao de Classificacao de Risco"
INDICADORES_RELATORIO_ANTIGO = "Apuração de Classificação de Risco"
COMISSOES_BLOCOS_DIR = Path(__file__).resolve().parent.parent / "comissoes" / "custom_blocks"
# (nome do Custom HTML Block, arquivo-base, rótulo exibido)
COMISSOES_CUSTOM_BLOCKS = (
	("Comissoes Proximas Reunioes", "proximas_reunioes", "Próximas reuniões"),
	("Comissoes em Atencao", "comissoes_em_atencao", "Comissões que exigem atenção"),
)
COMISSOES_NUMBER_CARDS = (
	("Reunioes nos Proximos 7 Dias", "Reuniões nos próximos 7 dias"),
	("Mandatos a Vencer", "Mandatos a vencer"),
	("Comissoes sem Reuniao Recente", "Comissões sem reunião recente"),
	("Mandatos Vigentes", "Mandatos vigentes"),
	("Reunioes no Mes", "Reuniões no mês"),
	("Presenca Media", "Presença média"),
)
# Os 6 cards do topo do Gestor (rótulo no Workspace, na ordem): o conteúdo do Workspace referencia o rótulo.
TOPO_NUMBER_CARDS = (
	"Total de Colaboradores",
	"Contratações (Este Ano)",
	"Documentos vencidos",
	"Reuniões nos próximos 7 dias",
	"Mandatos a vencer",
	"Comissões sem reunião recente",
)
# Cards do app que entram no topo: (Number Card, rótulo).
TOPO_NUMBER_CARDS_DO_APP = (
	("PG Documentos Vencidos", "Documentos vencidos"),
	("Reunioes nos Proximos 7 Dias", "Reuniões nos próximos 7 dias"),
	("Mandatos a Vencer", "Mandatos a vencer"),
	("Comissoes sem Reuniao Recente", "Comissões sem reunião recente"),
)
COMISSOES_CHARTS_REMOVIDOS = ("Reunioes por Mes", "Mandatos por Status", "Reunioes por Unidade")


def _slug(nome: str) -> str:
	return "".join(c if c.isalnum() else "_" for c in nome.lower())


def _blocos_do_app(links: list[dict]) -> tuple[list[dict], list[dict]]:
	"""(cards do app, number cards + blocos de comissões do topo do Workspace)."""

	def bloco(tipo, chave, nome, col):
		return {"id": f"{PREFIXO_BLOCOS}painel_{_slug(nome)}", "type": tipo, "data": {chave: nome, "col": col}}

	cards = [
		{
			"id": f"{PREFIXO_BLOCOS}card_{_slug(lk['label'])}",
			"type": "card",
			"data": {"card_name": lk["label"], "col": 4},
		}
		for lk in links
		if lk["type"] == "Card Break"
	]
	topo = [
		{
			"id": f"{PREFIXO_BLOCOS}topo_{_slug(label)}",
			"type": "number_card",
			"data": {"number_card_name": label, "col": 4},
		}
		for label in TOPO_NUMBER_CARDS
	] + [
		bloco("custom_block", "custom_block_name", "Comissoes Proximas Reunioes", 6),
		bloco("custom_block", "custom_block_name", "Comissoes em Atencao", 6),
	]
	return cards, topo


def ensure_comissoes_custom_blocks():
	"""Cria/atualiza os Custom HTML Blocks do painel (HTML/JS/CSS versionados no app)."""
	for nome, arquivo, _label in COMISSOES_CUSTOM_BLOCKS:
		valores = {
			"html": (COMISSOES_BLOCOS_DIR / f"{arquivo}.html").read_text(encoding="utf-8"),
			"script": (COMISSOES_BLOCOS_DIR / f"{arquivo}.js").read_text(encoding="utf-8"),
			"style": (COMISSOES_BLOCOS_DIR / "style.css").read_text(encoding="utf-8"),
			"private": 0,
		}
		if frappe.db.exists("Custom HTML Block", nome):
			doc = frappe.get_doc("Custom HTML Block", nome)
			if all((doc.get(k) or "") == v for k, v in valores.items()):
				continue
			doc.update(valores)
		else:
			doc = frappe.get_doc({"doctype": "Custom HTML Block", "__newname": nome, **valores})
			doc.flags.name = nome
		doc.flags.ignore_permissions = True
		doc.save(ignore_permissions=True)


def _links_sem_os_do_app(doc, labels: set[str]) -> list[dict]:
	"""Links atuais do Workspace, sem os cards (Card Break + links) que pertencem ao app."""
	mantidos, nosso = [], False
	for lk in doc.links:
		if lk.type == "Card Break":
			nosso = lk.label in labels
		if not nosso:
			mantidos.append(lk.as_dict())
	return mantidos


def ensure_pulse_gestor_workspace():
	"""Reúne tudo do app no Workspace Gestor e remove os Workspaces próprios do app."""
	if not frappe.db.exists("Workspace", WORKSPACE):
		return

	ensure_comissoes_custom_blocks()
	links_app = json.loads(WORKSPACE_LINKS_JSON.read_text(encoding="utf-8"))["links"]
	labels = {lk["label"] for lk in links_app if lk["type"] == "Card Break"}
	doc = frappe.get_doc("Workspace", WORKSPACE)
	changed = False

	chaves = ("type", "label", "link_type", "link_to", "link_count", "is_query_report", "onboard")
	normaliza = lambda rows: [{k: (r.get(k) or None) for k in chaves} for r in rows]  # noqa: E731
	desejado = normaliza(_links_sem_os_do_app(doc, labels) + links_app)
	if normaliza(doc.links) != desejado:
		doc.set("links", _links_sem_os_do_app(doc, labels) + [dict(lk) for lk in links_app])
		changed = True

	for nome, label in TOPO_NUMBER_CARDS_DO_APP:
		linha = next((r for r in doc.number_cards if r.number_card_name == nome), None)
		if linha:
			linha.label = label
		elif frappe.db.exists("Number Card", nome):
			doc.append("number_cards", {"number_card_name": nome, "label": label})
			changed = True
	manter = [r for r in doc.number_cards if r.label in TOPO_NUMBER_CARDS]
	if len(manter) != len(doc.number_cards):
		doc.set("number_cards", manter)
		changed = True
	for nome, label in [(n, l) for n, _a, l in COMISSOES_CUSTOM_BLOCKS]:
		if frappe.db.exists("Custom HTML Block", nome) and not any(r.custom_block_name == nome for r in doc.custom_blocks):
			doc.append("custom_blocks", {"custom_block_name": nome, "label": label})
			changed = True

	try:
		content = json.loads(doc.content or "[]")
	except json.JSONDecodeError:
		content = []
	restante = [
		b
		for b in content
		if not str((b or {}).get("id", "")).startswith(PREFIXO_BLOCOS)
		and b.get("type") != "number_card"
		and not (b.get("type") == "card" and (b.get("data") or {}).get("card_name") in labels)
	]
	corpo, topo = _blocos_do_app(links_app)
	novo = topo + restante + corpo
	if novo != content:
		doc.content = json.dumps(novo, ensure_ascii=False)
		changed = True

	if changed:
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)

	for nome in WORKSPACES_UNIFICADOS:
		if frappe.db.exists("Workspace", nome):
			frappe.delete_doc("Workspace", nome, force=1, ignore_permissions=True)
	frappe.clear_cache()


def ensure_classificacao_import_permissions():
	"""Permite ao papel que lança classificações usar a ferramenta Data Import."""
	role = "Pulse Gestor Manager"
	permissao_importacao = {
		"parent": "Data Import",
		"role": role,
		"permlevel": 0,
		"if_owner": 0,
	}
	if not frappe.db.exists("Custom DocPerm", permissao_importacao):
		add_permission("Data Import", role)

	changed = False
	name = frappe.db.get_value("Custom DocPerm", permissao_importacao, "name")
	for campo in ("read", "create", "write"):
		if not frappe.db.get_value("Custom DocPerm", name, campo):
			frappe.db.set_value("Custom DocPerm", name, campo, 1, update_modified=False)
			changed = True

	permissao_classificacao = frappe.db.get_value(
		"Custom DocPerm",
		{"parent": INDICADORES_LANCAMENTO, "role": role, "permlevel": 0, "if_owner": 0},
		["name", "import"],
	)
	if permissao_classificacao and not permissao_classificacao[1]:
		frappe.db.set_value(
			"Custom DocPerm", permissao_classificacao[0], "import", 1, update_modified=False
		)
		changed = True
	if changed:
		frappe.clear_cache()


def backfill_cores_classificacao_diaria():
	"""Registra a cor atual do protocolo em linhas antigas que ainda não têm cor."""
	if not frappe.db.exists("DocType", "Classificacao Diaria Nivel"):
		return
	if not frappe.db.has_column("Classificacao Diaria Nivel", "cor"):
		return

	linhas = frappe.db.sql(
		"""
		SELECT linha.name, linha.nivel, diario.protocolo
		FROM `tabClassificacao Diaria Nivel` linha
		JOIN `tabClassificacao de Risco Diaria` diario ON diario.name = linha.parent
		WHERE linha.cor IS NULL OR linha.cor = ''
		""",
		as_dict=True,
	)
	cores = {}
	for linha in linhas:
		chave = (linha.protocolo, linha.nivel)
		if chave not in cores:
			nivel = frappe.get_all(
				"Protocolo Nivel",
				filters={"parent": linha.protocolo, "nome_nivel": linha.nivel},
				fields=["cor"],
				order_by="ordem asc",
				limit_page_length=1,
			)
			cores[chave] = nivel[0].cor if nivel else None
		if cores[chave]:
			frappe.db.set_value(
				"Classificacao Diaria Nivel", linha.name, "cor", cores[chave], update_modified=False
			)


def backfill_tempos_classificacao_diaria():
	"""Preenche o alvo das linhas antigas com o valor disponível no protocolo."""
	if not frappe.db.exists("DocType", "Classificacao Diaria Nivel"):
		return
	if not frappe.db.has_column("Classificacao Diaria Nivel", "tempo_snapshot_preenchido"):
		return

	linhas = frappe.db.sql(
		"""
		SELECT linha.name, linha.idx, linha.nivel, diario.protocolo
		FROM `tabClassificacao Diaria Nivel` linha
		JOIN `tabClassificacao de Risco Diaria` diario ON diario.name = linha.parent
		WHERE linha.tempo_snapshot_preenchido = 0
		""",
		as_dict=True,
	)
	niveis_por_protocolo = {}
	for linha in linhas:
		if linha.protocolo not in niveis_por_protocolo:
			niveis_por_protocolo[linha.protocolo] = frappe.get_all(
				"Protocolo Nivel",
				filters={"parent": linha.protocolo, "parenttype": "Protocolo de Triagem"},
				fields=["nome_nivel", "tempo_maximo_espera_min"],
				order_by="ordem asc",
			)
		niveis = niveis_por_protocolo[linha.protocolo]
		indice = linha.idx - 1
		nivel = niveis[indice] if 0 <= indice < len(niveis) else None
		if not nivel or nivel.nome_nivel != linha.nivel:
			correspondentes = [item for item in niveis if item.nome_nivel == linha.nivel]
			nivel = correspondentes[0] if len(correspondentes) == 1 else None
		if nivel:
			frappe.db.set_value(
				"Classificacao Diaria Nivel",
				linha.name,
				{
					"tempo_maximo_espera_min": nivel.tempo_maximo_espera_min,
					"tempo_snapshot_preenchido": 1,
				},
				update_modified=False,
			)


def ensure_ascii_indicadores_report():
	"""Renomeia o registro legado; a collation do banco ignora acentos em comparações comuns."""
	old_name = frappe.db.sql(
		"SELECT name FROM `tabReport` WHERE BINARY name = %s",
		INDICADORES_RELATORIO_ANTIGO,
	)
	if not old_name:
		return
	if frappe.db.get_value(
		"Report",
		INDICADORES_RELATORIO_ANTIGO,
		["module", "ref_doctype", "is_standard"],
	) != ("Indicadores", "Classificacao de Risco Diaria", "Yes"):
		return

	# A troca direta parece um nome já existente nessa collation; usar um nome intermediário.
	temporario = "Pulse Gestor Report Rename Temporario"
	rename_doc(
		"Report", INDICADORES_RELATORIO_ANTIGO, temporario,
		force=True, ignore_permissions=True, show_alert=False, rebuild_search=False,
	)
	rename_doc(
		"Report", temporario, INDICADORES_RELATORIO,
		force=True, ignore_permissions=True, show_alert=False, rebuild_search=False,
	)
	frappe.db.set_value("Report", INDICADORES_RELATORIO, "report_name", INDICADORES_RELATORIO)




def ensure_roles():
	for role in ROLES:
		if frappe.db.exists("Role", role["role_name"]):
			continue
		frappe.get_doc(
			{
				"doctype": "Role",
				"role_name": role["role_name"],
				"desk_access": role["desk_access"],
			}
		).insert(ignore_permissions=True)


def ensure_settings():
	if not frappe.db.exists("DocType", "Configuracoes Documentos da Unidade"):
		return
	atual = frappe.db.get_single_value("Configuracoes Documentos da Unidade", "dias_alerta_vencimento")
	if atual is not None:
		return
	frappe.db.set_single_value(
		"Configuracoes Documentos da Unidade",
		"dias_alerta_vencimento",
		DIAS_ALERTA_PADRAO,
	)


def sincronizar_dias_alerta():
	"""Espelha o prazo das configurações na Notification nativa."""
	if not frappe.db.exists("Notification", NOTIFICACAO_A_VENCER):
		return
	if not frappe.db.exists("DocType", "Configuracoes Documentos da Unidade"):
		return

	dias = frappe.db.get_single_value("Configuracoes Documentos da Unidade", "dias_alerta_vencimento")
	if dias is None:
		dias = DIAS_ALERTA_PADRAO
	dias = int(dias)

	atual = frappe.db.get_value("Notification", NOTIFICACAO_A_VENCER, "days_in_advance")
	if int(atual or 0) == dias:
		return

	frappe.db.set_value(
		"Notification",
		NOTIFICACAO_A_VENCER,
		"days_in_advance",
		dias,
		update_modified=False,
	)


def ensure_print_formats():
	retire_legacy_print_formats()
	ensure_default_print_formats()
