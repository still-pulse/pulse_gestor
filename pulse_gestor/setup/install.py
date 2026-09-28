# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

"""Instalação e migrate do Pulse Gestor."""

from __future__ import annotations

import json
from pathlib import Path

import frappe
from frappe.model.rename_doc import rename_doc
from frappe.permissions import add_permission

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
	ensure_gestor_workspace()
	ensure_indicadores_workspace()
	ensure_comissoes_workspace()
	frappe.db.commit()


def after_migrate():
	ensure_roles()
	ensure_classificacao_import_permissions()
	ensure_settings()
	sincronizar_dias_alerta()
	ensure_gestor_workspace()
	ensure_ascii_indicadores_report()
	ensure_indicadores_workspace()
	ensure_comissoes_workspace()
	backfill_cores_classificacao_diaria()
	backfill_tempos_classificacao_diaria()
	frappe.db.commit()


GESTOR_SHORTCUTS = (
	{
		"label": "Documentos da Unidade",
		"link_to": "Documentacao da Unidade",
		"type": "DocType",
		"doc_view": "List",
		"color": "Blue",
	},
	{
		"label": "Tipos de Documento",
		"link_to": "Tipo de Documento da Unidade",
		"type": "DocType",
		"doc_view": "List",
		"color": "Green",
	},
	{
		"label": "Configurações Documentação",
		"link_to": "Configuracoes Documentos da Unidade",
		"type": "DocType",
		"color": "Grey",
	},
)

GESTOR_LINKS = (
	{
		"type": "Card Break",
		"label": "Documentação da Unidade",
		"link_count": 3,
	},
	{
		"type": "Link",
		"label": "Documentos da Unidade",
		"link_type": "DocType",
		"link_to": "Documentacao da Unidade",
		"is_query_report": 0,
		"onboard": 1,
	},
	{
		"type": "Link",
		"label": "Tipos de Documento",
		"link_type": "DocType",
		"link_to": "Tipo de Documento da Unidade",
		"is_query_report": 0,
		"onboard": 1,
	},
	{
		"type": "Link",
		"label": "Configurações",
		"link_type": "DocType",
		"link_to": "Configuracoes Documentos da Unidade",
		"is_query_report": 0,
		"onboard": 0,
	},
)

GESTOR_MODULE_CARD = {
	"id": "pg_card_doc",
	"type": "card",
	"data": {"card_name": "Documentação da Unidade", "col": 4},
}

OUR_CARD_LABEL = "Documentação da Unidade"
INDICADORES_CARD_LABEL = "Triagem"
INDICADORES_CARD = {
	"id": "card_triagem",
	"type": "card",
	"data": {"card_name": INDICADORES_CARD_LABEL, "col": 4},
}
INDICADORES_LANCAMENTO = "Classificacao de Risco Diaria"
INDICADORES_RELATORIO = "Apuracao de Classificacao de Risco"
INDICADORES_RELATORIO_ANTIGO = "Apuração de Classificação de Risco"
ATENDIMENTOS_CARD_LABEL = "Atendimentos"
ATENDIMENTOS_CARD = {
	"id": "card_atendimentos",
	"type": "card",
	"data": {"card_name": ATENDIMENTOS_CARD_LABEL, "col": 4},
}
ATENDIMENTOS_LINKS = (
	("Especialidades", "Especialidade"),
	("Vigências de Especialidades", "Unidade Especialidade Vigencia"),
	("Atendimentos Médicos Diários", "Atendimento Medico Diario"),
)
INDICADORES_RELATORIOS_CARD_LABEL = "Relatórios"
INDICADORES_RELATORIOS_CARD = {
	"id": "card_relatorios_indicadores",
	"type": "card",
	"data": {"card_name": INDICADORES_RELATORIOS_CARD_LABEL, "col": 4},
}
INDICADORES_RELATORIOS = (
	("Apuração de Classificação de Risco", INDICADORES_RELATORIO),
	("Relatório de Atendimentos por Período", "Relatorio de Atendimentos por Periodo"),
)
INDICADORES_RELATORIOS_ANTIGOS = ("Atendimentos Medicos por Periodo",)
COMISSOES_CARD_LABEL = "Comissões"
COMISSOES_CARD = {
	"id": "card_comissoes",
	"type": "card",
	"data": {"card_name": COMISSOES_CARD_LABEL, "col": 4},
}
COMISSOES_LINKS = (
	("Mandatos de Comissão", "Mandato de Comissao"),
	("Membros de Comissão", "Membros de Comissao"),
	("Reuniões de Comissão", "Reuniao de Comissao"),
)
COMISSOES_CONFIG_CARD_LABEL = "Configurações"
COMISSOES_CONFIG_CARD = {
	"id": "card_configuracoes_comissoes",
	"type": "card",
	"data": {"card_name": COMISSOES_CONFIG_CARD_LABEL, "col": 4},
}
COMISSOES_CONFIG_LINKS = (
	("Categorias de Comissão", "Categoria de Comissao"),
	("Tipos de Comissão", "Tipo de Comissao"),
)
COMISSOES_RELATORIOS_CARD_LABEL = "Relatórios"
COMISSOES_RELATORIOS_CARD = {
	"id": "card_relatorios_comissoes",
	"type": "card",
	"data": {"card_name": COMISSOES_RELATORIOS_CARD_LABEL, "col": 4},
}
COMISSOES_RELATORIOS = (("Atividades de Comissão", "Atividades de Comissao"),)
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
COMISSOES_CHARTS_REMOVIDOS = ("Reunioes por Mes", "Mandatos por Status", "Reunioes por Unidade")
COMISSOES_PAINEL_PREFIXO = "pg_painel_"


def _comissoes_painel_content() -> list[dict]:
	def bloco(tipo, chave, nome, col):
		slug = "".join(c if c.isalnum() else "_" for c in nome.lower())
		return {"id": f"{COMISSOES_PAINEL_PREFIXO}{slug}", "type": tipo, "data": {chave: nome, "col": col}}

	return [
		{
			"id": f"{COMISSOES_PAINEL_PREFIXO}header",
			"type": "header",
			"data": {"text": '<span class="h4">Painel de gestão</span>', "col": 12},
		},
		*[bloco("number_card", "number_card_name", nome, 4) for nome, _label in COMISSOES_NUMBER_CARDS],
		bloco("custom_block", "custom_block_name", "Comissoes Proximas Reunioes", 6),
		bloco("custom_block", "custom_block_name", "Comissoes em Atencao", 6),
	]


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


def _garantir_painel_comissoes(doc) -> bool:
	"""Garante o painel de cartões e blocos no topo do workspace Comissoes."""
	changed = False
	for row in [r for r in doc.charts if r.chart_name in COMISSOES_CHARTS_REMOVIDOS]:
		doc.charts.remove(row)
		changed = True
	for nome in COMISSOES_CHARTS_REMOVIDOS:
		if frappe.db.exists("Dashboard Chart", nome):
			frappe.delete_doc("Dashboard Chart", nome, force=1, ignore_permissions=True)
	for tabela, campo, doctype, itens in (
		("number_cards", "number_card_name", "Number Card", COMISSOES_NUMBER_CARDS),
		(
			"custom_blocks",
			"custom_block_name",
			"Custom HTML Block",
			[(nome, label) for nome, _arquivo, label in COMISSOES_CUSTOM_BLOCKS],
		),
	):
		for nome, label in itens:
			if frappe.db.exists(doctype, nome) and not any(row.get(campo) == nome for row in doc.get(tabela)):
				doc.append(tabela, {campo: nome, "label": label})
				changed = True

	try:
		content = json.loads(doc.content or "[]")
	except json.JSONDecodeError:
		content = []
	restante = [
		b for b in content if not str((b or {}).get("id", "")).startswith(COMISSOES_PAINEL_PREFIXO)
	]
	novo = _comissoes_painel_content() + restante
	if novo != content:
		doc.content = json.dumps(novo, ensure_ascii=False)
		changed = True
	return changed


OUR_LINK_TOS = {
	"Documentacao da Unidade",
	"Tipo de Documento da Unidade",
	"Configuracoes Documentos da Unidade",
}
OLD_SETTINGS_DOCTYPE = "Configuracoes Pulse Gestor"


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


def _garantir_card_relatorios_indicadores(doc, content) -> bool:
	"""Agrupa os relatórios de Indicadores em um card próprio, no fim do Workspace."""
	desejado = [("Card Break", INDICADORES_RELATORIOS_CARD_LABEL, None)] + [
		("Link", label, report) for label, report in INDICADORES_RELATORIOS
	]
	atual = [(link.type, link.label, link.link_to) for link in doc.links]
	tem_bloco = any(
		isinstance(block, dict)
		and block.get("type") == "card"
		and (block.get("data") or {}).get("card_name") == INDICADORES_RELATORIOS_CARD_LABEL
		for block in content
	)
	relatorios_soltos = [
		link
		for link in doc.links
		if link.type == "Link" and link.link_type == "Report" and link.link_to != "" and (
			link.link_to in {report for _label, report in INDICADORES_RELATORIOS}
			or link.link_to in INDICADORES_RELATORIOS_ANTIGOS
		)
	]
	if atual[-len(desejado):] == desejado and len(relatorios_soltos) == len(INDICADORES_RELATORIOS) and tem_bloco:
		return False

	for link in relatorios_soltos:
		doc.remove(link)
	doc.set(
		"links",
		[link for link in doc.links if not (link.type == "Card Break" and link.label == INDICADORES_RELATORIOS_CARD_LABEL)],
	)
	doc.append("links", {"type": "Card Break", "label": INDICADORES_RELATORIOS_CARD_LABEL})
	for label, report in INDICADORES_RELATORIOS:
		doc.append(
			"links",
			{"type": "Link", "label": label, "link_type": "Report", "link_to": report, "is_query_report": 1},
		)
	if not tem_bloco:
		content.append(INDICADORES_RELATORIOS_CARD)
		doc.content = json.dumps(content, ensure_ascii=False)
	return True


def ensure_indicadores_workspace():
	"""Atualiza a navegação de Indicadores em Workspaces já instalados."""
	if not frappe.db.exists("Workspace", "Indicadores"):
		return

	doc = frappe.get_doc("Workspace", "Indicadores")
	changed = False
	if frappe.db.exists("Workspace", "Gestor") and doc.parent_page != "Gestor":
		doc.parent_page = "Gestor"
		changed = True
	try:
		content = json.loads(doc.content or "[]")
	except json.JSONDecodeError:
		content = []

	old_links = {
		"Unidade Protocolo Vigência": "Unidade Protocolo Vigencia",
		"Classificação de Risco Diária": "Classificacao de Risco Diaria",
		INDICADORES_RELATORIO_ANTIGO: INDICADORES_RELATORIO,
		"Atendimento Diario": "Atendimento Medico Diario",
	}
	for link in doc.links:
		if link.link_to in old_links:
			link.link_to = old_links[link.link_to]
			changed = True
			if link.link_to == "Atendimento Medico Diario":
				link.label = "Atendimentos Médicos Diários"
	for shortcut in doc.shortcuts:
		if shortcut.link_to in old_links:
			shortcut.link_to = old_links[shortcut.link_to]
			changed = True
			if shortcut.link_to == "Atendimento Medico Diario":
				shortcut.label = "Atendimentos Médicos Diários"
	if not any(
		isinstance(block, dict)
		and block.get("type") == "card"
		and (block.get("data") or {}).get("card_name") == INDICADORES_CARD_LABEL
		for block in content
	):
		insert_at = next(
			(i + 1 for i, block in enumerate(content) if isinstance(block, dict) and block.get("type") == "header"),
			len(content),
		)
		content.insert(insert_at, INDICADORES_CARD)
		doc.content = json.dumps(content, ensure_ascii=False)
		changed = True
	if not any(
		isinstance(block, dict)
		and block.get("type") == "card"
		and (block.get("data") or {}).get("card_name") == ATENDIMENTOS_CARD_LABEL
		for block in content
	):
		content.append(ATENDIMENTOS_CARD)
		doc.content = json.dumps(content, ensure_ascii=False)
		changed = True

	if not any(link.type == "Link" and link.link_to == INDICADORES_LANCAMENTO for link in doc.links):
		card_index = next(
			(
				i
				for i, link in enumerate(doc.links)
				if link.type == "Card Break" and link.label == INDICADORES_CARD_LABEL
			),
			None,
		)
		if card_index is not None:
			row = doc.append(
				"links",
				{
					"type": "Link",
					"label": "Classificações de Risco Diárias",
					"link_type": "DocType",
					"link_to": INDICADORES_LANCAMENTO,
					"onboard": 1,
				},
			)
			doc.links.remove(row)
			doc.links.insert(card_index + 1, row)
			_fix_link_counts(doc)
			changed = True
	card_index = next(
		(i for i, link in enumerate(doc.links) if link.type == "Card Break" and link.label == ATENDIMENTOS_CARD_LABEL),
		None,
	)
	if card_index is None:
		doc.append("links", {"type": "Card Break", "label": ATENDIMENTOS_CARD_LABEL})
		changed = True
	for label, link_to in ATENDIMENTOS_LINKS:
		if not any(link.type == "Link" and link.link_to == link_to for link in doc.links):
			doc.append(
				"links",
				{"type": "Link", "label": label, "link_type": "DocType", "link_to": link_to, "onboard": 1},
			)
			changed = True
	changed = _garantir_card_relatorios_indicadores(doc, content) or changed
	if changed:
		_fix_link_counts(doc)
		doc.flags.ignore_permissions = True
		doc.save(ignore_permissions=True)
		frappe.clear_cache()


def ensure_comissoes_workspace():
	"""Garante os cards e links de Comissões em Workspaces já instalados."""
	if not frappe.db.exists("Workspace", "Comissoes"):
		return

	ensure_comissoes_custom_blocks()
	doc = frappe.get_doc("Workspace", "Comissoes")
	changed = _garantir_painel_comissoes(doc)
	if frappe.db.exists("Workspace", "Gestor") and doc.parent_page != "Gestor":
		doc.parent_page = "Gestor"
		changed = True
	try:
		content = json.loads(doc.content or "[]")
	except json.JSONDecodeError:
		content = []

	for card_label, card_block in (
		(COMISSOES_CARD_LABEL, COMISSOES_CARD),
		(COMISSOES_CONFIG_CARD_LABEL, COMISSOES_CONFIG_CARD),
		(COMISSOES_RELATORIOS_CARD_LABEL, COMISSOES_RELATORIOS_CARD),
	):
		if not any(
			isinstance(block, dict)
			and block.get("type") == "card"
			and (block.get("data") or {}).get("card_name") == card_label
			for block in content
		):
			content.append(card_block)
			doc.content = json.dumps(content, ensure_ascii=False)
			changed = True

	for card_label, links in (
		(COMISSOES_CARD_LABEL, COMISSOES_LINKS),
		(COMISSOES_CONFIG_CARD_LABEL, COMISSOES_CONFIG_LINKS),
		(COMISSOES_RELATORIOS_CARD_LABEL, COMISSOES_RELATORIOS),
	):
		link_type = "Report" if card_label == COMISSOES_RELATORIOS_CARD_LABEL else "DocType"
		card_index = next(
			(i for i, link in enumerate(doc.links) if link.type == "Card Break" and link.label == card_label),
			None,
		)
		if card_index is None:
			doc.append("links", {"type": "Card Break", "label": card_label})
			changed = True
			card_index = len(doc.links) - 1
		insert_at = card_index + 1
		for label, link_to in links:
			if not any(link.type == "Link" and link.link_to == link_to for link in doc.links):
				row = doc.append(
					"links",
					{
						"type": "Link",
						"label": label,
						"link_type": link_type,
						"link_to": link_to,
						"is_query_report": 1 if link_type == "Report" else 0,
						"onboard": 1,
					},
				)
				doc.links.remove(row)
				doc.links.insert(insert_at, row)
				insert_at += 1
				changed = True

	if changed:
		_fix_link_counts(doc)
		doc.flags.ignore_permissions = True
		doc.save(ignore_permissions=True)
		frappe.clear_cache()


def ensure_gestor_workspace():
	"""Card próprio em Módulos do Gestor; tira o workspace Pulse Gestor do menu."""
	for nome in ("Pulse Gestor", "Documentacao da Unidade"):
		if frappe.db.exists("Workspace", nome):
			frappe.db.set_value(
				"Workspace",
				nome,
				{"is_hidden": 1, "public": 0},
				update_modified=False,
			)

	if not frappe.db.exists("Workspace", "Gestor"):
		return

	doc = frappe.get_doc("Workspace", "Gestor")
	changed = False

	existing_labels = {s.label for s in (doc.shortcuts or [])}
	for sc in GESTOR_SHORTCUTS:
		if sc["label"] in existing_labels:
			continue
		row = {
			"label": sc["label"],
			"link_to": sc["link_to"],
			"type": sc["type"],
			"color": sc.get("color") or "Grey",
		}
		if sc.get("doc_view"):
			row["doc_view"] = sc["doc_view"]
		doc.append("shortcuts", row)
		changed = True

	if _reorganizar_links_modulos(doc):
		changed = True

	if _garantir_card_modulos(doc):
		changed = True

	if changed:
		doc.flags.ignore_links = True
		doc.flags.ignore_permissions = True
		doc.save(ignore_permissions=True)
		frappe.clear_cache()


def _is_our_link(lk) -> bool:
	if lk.type == "Card Break" and lk.label == OUR_CARD_LABEL:
		return True
	return lk.type == "Link" and (lk.link_to or "") in OUR_LINK_TOS | {OLD_SETTINGS_DOCTYPE}


def _link_as_dict(lk) -> dict:
	return {
		"type": lk.type,
		"label": lk.label,
		"link_type": lk.link_type,
		"link_to": lk.link_to,
		"hidden": lk.hidden,
		"onboard": lk.onboard,
		"is_query_report": lk.is_query_report,
		"link_count": lk.link_count,
	}


def _fix_link_counts(doc):
	links = doc.links or []
	i = 0
	while i < len(links):
		if links[i].type == "Card Break":
			count = 0
			j = i + 1
			while j < len(links) and links[j].type != "Card Break":
				if links[j].type == "Link":
					count += 1
				j += 1
			links[i].link_count = count
		i += 1


def _reorganizar_links_modulos(doc) -> bool:
	"""Tira nossos links de dentro do Patrimônio e cria o Card Break certo."""
	kept = [_link_as_dict(lk) for lk in (doc.links or []) if not _is_our_link(lk)]
	ja_certo = False
	links = list(doc.links or [])
	if links and links[-1].type != "Card Break":
		# último Card Break deve ser o nosso, seguido só dos 3 links
		last_break = None
		for lk in reversed(links):
			if lk.type == "Card Break":
				last_break = lk
				break
		if last_break and last_break.label == OUR_CARD_LABEL and not any(
			lk.link_to == OLD_SETTINGS_DOCTYPE for lk in links if lk.type == "Link"
		):
			ours = [lk for lk in links if _is_our_link(lk)]
			if len(ours) == 1 + len(OUR_LINK_TOS):
				ja_certo = True

	if ja_certo:
		return False

	doc.set("links", [])
	for row in kept:
		doc.append("links", row)
	for row in GESTOR_LINKS:
		doc.append("links", dict(row))
	_fix_link_counts(doc)
	return True


def _garantir_card_modulos(doc) -> bool:
	try:
		content = json.loads(doc.content or "[]")
	except json.JSONDecodeError:
		content = []

	already = any(
		isinstance(b, dict)
		and b.get("type") == "card"
		and (b.get("data") or {}).get("card_name") == OUR_CARD_LABEL
		for b in content
	)
	if already:
		return False

	insert_at = None
	last_card = None
	modulos_header = None
	for i, block in enumerate(content):
		if not isinstance(block, dict):
			continue
		if block.get("type") == "card":
			last_card = i
		text = (block.get("data") or {}).get("text", "")
		if block.get("type") == "header" and "Módulo" in text:
			modulos_header = i
	if last_card is not None:
		insert_at = last_card + 1
	elif modulos_header is not None:
		insert_at = modulos_header + 1
	if insert_at is None:
		content.append(GESTOR_MODULE_CARD)
	else:
		content.insert(insert_at, GESTOR_MODULE_CARD)
	doc.content = json.dumps(content, ensure_ascii=False)
	return True


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
