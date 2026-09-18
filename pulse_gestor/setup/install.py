# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

"""Instalação e migrate do Pulse Gestor."""

from __future__ import annotations

import json

import frappe
from frappe.model.rename_doc import rename_doc

ROLES = (
	{"role_name": "Pulse Gestor Manager", "desk_access": 1},
	{"role_name": "Pulse Gestor Viewer", "desk_access": 1},
)

NOTIFICACAO_A_VENCER = "Documento da Unidade a Vencer"
DIAS_ALERTA_PADRAO = 30


def after_install():
	ensure_roles()
	ensure_settings()
	ensure_gestor_workspace()
	ensure_indicadores_workspace()
	frappe.db.commit()


def after_migrate():
	ensure_roles()
	ensure_settings()
	sincronizar_dias_alerta()
	ensure_gestor_workspace()
	ensure_ascii_indicadores_report()
	ensure_indicadores_workspace()
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
		"link_to": "Configuracoes Pulse Gestor",
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
		"link_to": "Configuracoes Pulse Gestor",
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
OUR_LINK_TOS = {
	"Documentacao da Unidade",
	"Tipo de Documento da Unidade",
	"Configuracoes Pulse Gestor",
}


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


def ensure_indicadores_workspace():
	"""Inclui o quadro, o lançamento e o relatório em Workspaces já instalados."""
	if not frappe.db.exists("Workspace", "Indicadores"):
		return

	doc = frappe.get_doc("Workspace", "Indicadores")
	try:
		content = json.loads(doc.content or "[]")
	except json.JSONDecodeError:
		content = []

	changed = False
	old_links = {
		"Unidade Protocolo Vigência": "Unidade Protocolo Vigencia",
		"Classificação de Risco Diária": "Classificacao de Risco Diaria",
		INDICADORES_RELATORIO_ANTIGO: INDICADORES_RELATORIO,
	}
	for link in doc.links:
		if link.link_to in old_links:
			link.link_to = old_links[link.link_to]
			changed = True
	for shortcut in doc.shortcuts:
		if shortcut.link_to in old_links:
			shortcut.link_to = old_links[shortcut.link_to]
			changed = True
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
	if not any(link.type == "Link" and link.link_to == INDICADORES_RELATORIO for link in doc.links):
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
					"label": INDICADORES_RELATORIO,
					"link_type": "Report",
					"link_to": INDICADORES_RELATORIO,
					"is_query_report": 1,
				},
			)
			doc.links.remove(row)
			doc.links.insert(card_index + 1, row)
			_fix_link_counts(doc)
			changed = True
	if changed:
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
	return lk.type == "Link" and (lk.link_to or "") in OUR_LINK_TOS


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
		if last_break and last_break.label == OUR_CARD_LABEL:
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
	if not frappe.db.exists("DocType", "Configuracoes Pulse Gestor"):
		return
	atual = frappe.db.get_single_value("Configuracoes Pulse Gestor", "dias_alerta_vencimento")
	if atual is not None:
		return
	frappe.db.set_single_value(
		"Configuracoes Pulse Gestor",
		"dias_alerta_vencimento",
		DIAS_ALERTA_PADRAO,
	)


def sincronizar_dias_alerta():
	"""Espelha o prazo das configurações na Notification nativa."""
	if not frappe.db.exists("Notification", NOTIFICACAO_A_VENCER):
		return
	if not frappe.db.exists("DocType", "Configuracoes Pulse Gestor"):
		return

	dias = frappe.db.get_single_value("Configuracoes Pulse Gestor", "dias_alerta_vencimento")
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
