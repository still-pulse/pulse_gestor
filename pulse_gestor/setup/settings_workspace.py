"""Card "Pulse Gestor" no workspace ERPNext Settings (idempotente).

O workspace Gestor é restrito ao papel Gerente de Unidade, mas as configurações são lidas por System Manager e
pelos papéis Pulse Gestor; ERPNext Settings é aberto e o Frappe mostra o link só a quem pode ler o DocType.
"""

import json

import frappe

WORKSPACE = "ERPNext Settings"
CARD_LABEL = "Pulse Gestor"
LINKS = [("Configuracoes Documentos da Unidade", "Configurações de Documentos da Unidade")]


def ensure_settings_card():
	if not frappe.db.exists("Workspace", WORKSPACE):
		return
	desejados = [(d, r) for d, r in LINKS if frappe.db.exists("DocType", d)]
	if not desejados:
		return
	ws = frappe.get_doc("Workspace", WORKSPACE)
	alterado = False
	if CARD_LABEL not in {l.label for l in ws.links if l.type == "Card Break"}:
		ws.append("links", {"type": "Card Break", "label": CARD_LABEL, "hidden": 0})
		alterado = True
	existentes = {l.link_to for l in ws.links if l.type == "Link"}
	for doctype, rotulo in desejados:
		if doctype not in existentes:
			ws.append("links", {"type": "Link", "label": rotulo, "link_type": "DocType", "link_to": doctype})
			alterado = True
	try:
		blocos = json.loads(ws.content or "[]")
	except Exception:
		blocos = []
	if not any((b.get("data") or {}).get("card_name") == CARD_LABEL for b in blocos):
		blocos.append(
			{"id": frappe.generate_hash(length=10), "type": "card", "data": {"card_name": CARD_LABEL, "col": 4}}
		)
		ws.content = json.dumps(blocos, ensure_ascii=False)
		alterado = True
	if alterado:
		ws.flags.ignore_permissions = True
		ws.flags.ignore_links = True
		ws.save()
		frappe.clear_cache()  # o desk guarda a página do workspace em cache por usuário
