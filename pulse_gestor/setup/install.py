# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

"""Instalação e migrate do Pulse Gestor."""

from __future__ import annotations

import json

import frappe

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
	frappe.db.commit()


def after_migrate():
	ensure_roles()
	ensure_settings()
	sincronizar_dias_alerta()
	ensure_gestor_workspace()
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


def ensure_gestor_workspace():
	"""Atalhos no Workspace Gestor; oculta Pulse Gestor do menu lateral."""
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

	existing_link_labels = {lk.label for lk in (doc.links or [])}
	if "Documentação da Unidade" not in existing_link_labels:
		for lk in GESTOR_LINKS:
			doc.append("links", dict(lk))
			changed = True

	try:
		content = json.loads(doc.content or "[]")
	except json.JSONDecodeError:
		content = []

	existing_ids = {b.get("id") for b in content if isinstance(b, dict)}
	already_card = "pg_card_doc" in existing_ids or any(
		b.get("type") == "card"
		and (b.get("data") or {}).get("card_name") == "Documentação da Unidade"
		for b in content
		if isinstance(b, dict)
	)
	if not already_card:
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
		changed = True

	if changed:
		doc.flags.ignore_links = True
		doc.flags.ignore_permissions = True
		doc.save(ignore_permissions=True)


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
