""" "Pulse Gestor" card in the ERPNext Settings workspace (idempotent).

The Gestor workspace is restricted to the unit manager role, but the settings are read by System Manager and
the Pulse Gestor roles; ERPNext Settings is open and Frappe shows the link only to those who can read the DocType.
"""

import json

import frappe

WORKSPACE = "ERPNext Settings"
CARD_LABEL = "Pulse Gestor"
LINKS = [("Configuracoes Documentos da Unidade", "Configurações de Documentos da Unidade")]


def ensure_settings_card():
	if not frappe.db.exists("Workspace", WORKSPACE):
		return
	desired = [(d, r) for d, r in LINKS if frappe.db.exists("DocType", d)]
	if not desired:
		return
	ws = frappe.get_doc("Workspace", WORKSPACE)
	changed = False
	if CARD_LABEL not in {l.label for l in ws.links if l.type == "Card Break"}:
		ws.append("links", {"type": "Card Break", "label": CARD_LABEL, "hidden": 0})
		changed = True
	existing = {l.link_to for l in ws.links if l.type == "Link"}
	for doctype, link_label in desired:
		if doctype not in existing:
			ws.append(
				"links", {"type": "Link", "label": link_label, "link_type": "DocType", "link_to": doctype}
			)
			changed = True
	try:
		blocks = json.loads(ws.content or "[]")
	except Exception:
		blocks = []
	if not any((b.get("data") or {}).get("card_name") == CARD_LABEL for b in blocks):
		blocks.append(
			{
				"id": frappe.generate_hash(length=10),
				"type": "card",
				"data": {"card_name": CARD_LABEL, "col": 4},
			}
		)
		ws.content = json.dumps(blocks, ensure_ascii=False)
		changed = True
	if changed:
		ws.flags.ignore_permissions = True
		ws.flags.ignore_links = True
		ws.save()
		frappe.clear_cache()  # the desk caches the workspace page per user
