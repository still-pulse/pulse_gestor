# Copyright (c) 2026, StillPulse Tecnologia LTDA and contributors
# For license information, please see license.txt

"""Install and migrate hooks of Pulse Gestor."""

from __future__ import annotations

import json
from pathlib import Path

import frappe
from frappe.model.rename_doc import rename_doc
from frappe.permissions import add_permission

from pulse_gestor.print_formats import ensure_default_print_formats, retire_legacy_print_formats
from pulse_gestor.setup.settings_workspace import ensure_settings_card

ROLES = (
	{"role_name": "Pulse Gestor Manager", "desk_access": 1},
	{"role_name": "Pulse Gestor Viewer", "desk_access": 1},
)

EXPIRING_NOTIFICATION = "Documento da Unidade a Vencer"
DEFAULT_ALERT_DAYS = 30


def after_install():
	ensure_roles()
	ensure_classification_import_permissions()
	ensure_settings()
	ensure_pulse_gestor_workspace()
	frappe.db.commit()


def after_migrate():
	ensure_roles()
	ensure_classification_import_permissions()
	ensure_settings()
	sync_alert_days()
	ensure_ascii_indicators_report()
	ensure_pulse_gestor_workspace()
	ensure_settings_card()
	backfill_daily_classification_colors()
	backfill_daily_classification_times()
	from pulse_gestor.signature_profiles import after_migrate as seed_communication

	seed_communication()
	ensure_print_formats()
	frappe.db.commit()


WORKSPACE = "Gestor"
# Card Breaks and Links of the app, appended to the Gestor Workspace
WORKSPACE_LINKS_JSON = Path(__file__).resolve().parent / "gestor_links.json"
BLOCK_PREFIX = "pg_"
# App Workspaces that were merged into Gestor
MERGED_WORKSPACES = ("Pulse Gestor", "Indicadores", "Comissoes", "Documentacao da Unidade")
DOCUMENT_NUMBER_CARDS = (
	("PG Total Documentos", "Total"),
	("PG Documentos Validos", "Válidos"),
	("PG Documentos Vencidos", "Vencidos"),
)

INDICATORS_ENTRY_DOCTYPE = "Classificacao de Risco Diaria"
INDICATORS_REPORT = "Apuracao de Classificacao de Risco"
INDICATORS_REPORT_LEGACY = "Apuração de Classificação de Risco"
COMMITTEES_BLOCKS_DIR = Path(__file__).resolve().parent.parent / "comissoes" / "custom_blocks"
# (Custom HTML Block name, base filename, displayed label)
COMMITTEES_CUSTOM_BLOCKS = (
	("Comissoes Proximas Reunioes", "proximas_reunioes", "Próximas reuniões"),
	("Comissoes em Atencao", "comissoes_em_atencao", "Comissões que exigem atenção"),
)
COMMITTEES_NUMBER_CARDS = (
	("Reunioes nos Proximos 7 Dias", "Reuniões nos próximos 7 dias"),
	("Mandatos a Vencer", "Mandatos a vencer"),
	("Comissoes sem Reuniao Recente", "Comissões sem reunião recente"),
	("Mandatos Vigentes", "Mandatos vigentes"),
	("Reunioes no Mes", "Reuniões no mês"),
	("Presenca Media", "Presença média"),
)
# The 6 top cards of Gestor (label in the Workspace, in order): the Workspace content references the label.
TOP_NUMBER_CARDS = (
	"Total de Colaboradores",
	"Contratações (Este Ano)",
	"Documentos vencidos",
	"Reuniões nos próximos 7 dias",
	"Mandatos a vencer",
	"Comissões sem reunião recente",
)
# App cards that go on top: (Number Card, label).
APP_TOP_NUMBER_CARDS = (
	("PG Documentos Vencidos", "Documentos vencidos"),
	("Reunioes nos Proximos 7 Dias", "Reuniões nos próximos 7 dias"),
	("Mandatos a Vencer", "Mandatos a vencer"),
	("Comissoes sem Reuniao Recente", "Comissões sem reunião recente"),
)
REMOVED_COMMITTEES_CHARTS = ("Reunioes por Mes", "Mandatos por Status", "Reunioes por Unidade")


def _slug(name: str) -> str:
	return "".join(c if c.isalnum() else "_" for c in name.lower())


def _app_blocks(links: list[dict]) -> tuple[list[dict], list[dict]]:
	"""(app cards, number cards + committee blocks at the top of the Workspace)."""

	def block(kind, key, name, col):
		return {
			"id": f"{BLOCK_PREFIX}painel_{_slug(name)}",
			"type": kind,
			"data": {key: name, "col": col},
		}

	cards = [
		{
			"id": f"{BLOCK_PREFIX}card_{_slug(lk['label'])}",
			"type": "card",
			"data": {"card_name": lk["label"], "col": 4},
		}
		for lk in links
		if lk["type"] == "Card Break"
	]
	top = [
		{
			"id": f"{BLOCK_PREFIX}topo_{_slug(label)}",
			"type": "number_card",
			"data": {"number_card_name": label, "col": 4},
		}
		for label in TOP_NUMBER_CARDS
	] + [
		block("custom_block", "custom_block_name", "Comissoes Proximas Reunioes", 6),
		block("custom_block", "custom_block_name", "Comissoes em Atencao", 6),
	]
	return cards, top


def ensure_committees_custom_blocks():
	"""Create/update the panel Custom HTML Blocks (HTML/JS/CSS versioned in the app)."""
	for name, filename, _label in COMMITTEES_CUSTOM_BLOCKS:
		values = {
			"html": (COMMITTEES_BLOCKS_DIR / f"{filename}.html").read_text(encoding="utf-8"),
			"script": (COMMITTEES_BLOCKS_DIR / f"{filename}.js").read_text(encoding="utf-8"),
			"style": (COMMITTEES_BLOCKS_DIR / "style.css").read_text(encoding="utf-8"),
			"private": 0,
		}
		if frappe.db.exists("Custom HTML Block", name):
			doc = frappe.get_doc("Custom HTML Block", name)
			if all((doc.get(k) or "") == v for k, v in values.items()):
				continue
			doc.update(values)
		else:
			doc = frappe.get_doc({"doctype": "Custom HTML Block", "__newname": name, **values})
			doc.flags.name = name
		doc.flags.ignore_permissions = True
		doc.save(ignore_permissions=True)


def _links_without_app_cards(doc, labels: set[str]) -> list[dict]:
	"""Current Workspace links, without the cards (Card Break + links) that belong to the app."""
	kept, is_app_card = [], False
	for lk in doc.links:
		if lk.type == "Card Break":
			is_app_card = lk.label in labels
		if not is_app_card:
			kept.append(lk.as_dict())
	return kept


def ensure_pulse_gestor_workspace():
	"""Gather everything of the app in the Gestor Workspace and remove the app's own Workspaces."""
	if not frappe.db.exists("Workspace", WORKSPACE):
		return

	ensure_committees_custom_blocks()
	app_links = json.loads(WORKSPACE_LINKS_JSON.read_text(encoding="utf-8"))["links"]
	labels = {lk["label"] for lk in app_links if lk["type"] == "Card Break"}
	doc = frappe.get_doc("Workspace", WORKSPACE)
	changed = False

	keys = ("type", "label", "link_type", "link_to", "link_count", "is_query_report", "onboard")
	normalize = lambda rows: [{k: (r.get(k) or None) for k in keys} for r in rows]  # noqa: E731
	desired = normalize(_links_without_app_cards(doc, labels) + app_links)
	if normalize(doc.links) != desired:
		doc.set("links", _links_without_app_cards(doc, labels) + [dict(lk) for lk in app_links])
		changed = True

	for name, label in APP_TOP_NUMBER_CARDS:
		row = next((r for r in doc.number_cards if r.number_card_name == name), None)
		if row:
			row.label = label
		elif frappe.db.exists("Number Card", name):
			doc.append("number_cards", {"number_card_name": name, "label": label})
			changed = True
	keep = [r for r in doc.number_cards if r.label in TOP_NUMBER_CARDS]
	if len(keep) != len(doc.number_cards):
		doc.set("number_cards", keep)
		changed = True
	for name, label in [(n, l) for n, _a, l in COMMITTEES_CUSTOM_BLOCKS]:
		if frappe.db.exists("Custom HTML Block", name) and not any(
			r.custom_block_name == name for r in doc.custom_blocks
		):
			doc.append("custom_blocks", {"custom_block_name": name, "label": label})
			changed = True

	try:
		content = json.loads(doc.content or "[]")
	except json.JSONDecodeError:
		content = []
	remaining = [
		b
		for b in content
		if not str((b or {}).get("id", "")).startswith(BLOCK_PREFIX)
		and b.get("type") != "number_card"
		and not (b.get("type") == "card" and (b.get("data") or {}).get("card_name") in labels)
	]
	body, top = _app_blocks(app_links)
	new_content = top + remaining + body
	if new_content != content:
		doc.content = json.dumps(new_content, ensure_ascii=False)
		changed = True

	if changed:
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)

	for name in MERGED_WORKSPACES:
		if frappe.db.exists("Workspace", name):
			frappe.delete_doc("Workspace", name, force=1, ignore_permissions=True)
	frappe.clear_cache()


def ensure_classification_import_permissions():
	"""Allow the role that enters classifications to use the Data Import tool."""
	role = "Pulse Gestor Manager"
	import_permission = {
		"parent": "Data Import",
		"role": role,
		"permlevel": 0,
		"if_owner": 0,
	}
	if not frappe.db.exists("Custom DocPerm", import_permission):
		add_permission("Data Import", role)

	changed = False
	name = frappe.db.get_value("Custom DocPerm", import_permission, "name")
	for field in ("read", "create", "write"):
		if not frappe.db.get_value("Custom DocPerm", name, field):
			frappe.db.set_value("Custom DocPerm", name, field, 1, update_modified=False)
			changed = True

	classification_permission = frappe.db.get_value(
		"Custom DocPerm",
		{"parent": INDICATORS_ENTRY_DOCTYPE, "role": role, "permlevel": 0, "if_owner": 0},
		["name", "import"],
	)
	if classification_permission and not classification_permission[1]:
		frappe.db.set_value(
			"Custom DocPerm", classification_permission[0], "import", 1, update_modified=False
		)
		changed = True
	if changed:
		frappe.clear_cache()


def backfill_daily_classification_colors():
	"""Store the protocol's current color on old rows that have no color yet."""
	if not frappe.db.exists("DocType", "Classificacao Diaria Nivel"):
		return
	if not frappe.db.has_column("Classificacao Diaria Nivel", "cor"):
		return

	rows = frappe.db.sql(
		"""
		SELECT linha.name, linha.nivel, diario.protocolo
		FROM `tabClassificacao Diaria Nivel` linha
		JOIN `tabClassificacao de Risco Diaria` diario ON diario.name = linha.parent
		WHERE linha.cor IS NULL OR linha.cor = ''
		""",
		as_dict=True,
	)
	colors = {}
	for row in rows:
		key = (row.protocolo, row.nivel)
		if key not in colors:
			level = frappe.get_all(
				"Protocolo Nivel",
				filters={"parent": row.protocolo, "nome_nivel": row.nivel},
				fields=["cor"],
				order_by="ordem asc",
				limit_page_length=1,
			)
			colors[key] = level[0].cor if level else None
		if colors[key]:
			frappe.db.set_value(
				"Classificacao Diaria Nivel", row.name, "cor", colors[key], update_modified=False
			)


def backfill_daily_classification_times():
	"""Fill the target of old rows with the value available in the protocol."""
	if not frappe.db.exists("DocType", "Classificacao Diaria Nivel"):
		return
	if not frappe.db.has_column("Classificacao Diaria Nivel", "tempo_snapshot_preenchido"):
		return

	rows = frappe.db.sql(
		"""
		SELECT linha.name, linha.idx, linha.nivel, diario.protocolo
		FROM `tabClassificacao Diaria Nivel` linha
		JOIN `tabClassificacao de Risco Diaria` diario ON diario.name = linha.parent
		WHERE linha.tempo_snapshot_preenchido = 0
		""",
		as_dict=True,
	)
	levels_by_protocol = {}
	for row in rows:
		if row.protocolo not in levels_by_protocol:
			levels_by_protocol[row.protocolo] = frappe.get_all(
				"Protocolo Nivel",
				filters={"parent": row.protocolo, "parenttype": "Protocolo de Triagem"},
				fields=["nome_nivel", "tempo_maximo_espera_min"],
				order_by="ordem asc",
			)
		levels = levels_by_protocol[row.protocolo]
		index = row.idx - 1
		level = levels[index] if 0 <= index < len(levels) else None
		if not level or level.nome_nivel != row.nivel:
			matching = [item for item in levels if item.nome_nivel == row.nivel]
			level = matching[0] if len(matching) == 1 else None
		if level:
			frappe.db.set_value(
				"Classificacao Diaria Nivel",
				row.name,
				{
					"tempo_maximo_espera_min": level.tempo_maximo_espera_min,
					"tempo_snapshot_preenchido": 1,
				},
				update_modified=False,
			)


def ensure_ascii_indicators_report():
	"""Rename the legacy record; the database collation ignores accents in ordinary comparisons."""
	old_name = frappe.db.sql(
		"SELECT name FROM `tabReport` WHERE BINARY name = %s",
		INDICATORS_REPORT_LEGACY,
	)
	if not old_name:
		return
	if frappe.db.get_value(
		"Report",
		INDICATORS_REPORT_LEGACY,
		["module", "ref_doctype", "is_standard"],
	) != ("Indicadores", "Classificacao de Risco Diaria", "Yes"):
		return

	# A direct swap looks like an existing name in this collation; use an intermediate name.
	temp_name = "Pulse Gestor Report Rename Temporario"
	rename_doc(
		"Report",
		INDICATORS_REPORT_LEGACY,
		temp_name,
		force=True,
		ignore_permissions=True,
		show_alert=False,
		rebuild_search=False,
	)
	rename_doc(
		"Report",
		temp_name,
		INDICATORS_REPORT,
		force=True,
		ignore_permissions=True,
		show_alert=False,
		rebuild_search=False,
	)
	frappe.db.set_value("Report", INDICATORS_REPORT, "report_name", INDICATORS_REPORT)


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
	current = frappe.db.get_single_value("Configuracoes Documentos da Unidade", "dias_alerta_vencimento")
	if current is not None:
		return
	frappe.db.set_single_value(
		"Configuracoes Documentos da Unidade",
		"dias_alerta_vencimento",
		DEFAULT_ALERT_DAYS,
	)


def sync_alert_days():
	"""Mirror the deadline from the settings into the native Notification."""
	if not frappe.db.exists("Notification", EXPIRING_NOTIFICATION):
		return
	if not frappe.db.exists("DocType", "Configuracoes Documentos da Unidade"):
		return

	days = frappe.db.get_single_value("Configuracoes Documentos da Unidade", "dias_alerta_vencimento")
	if days is None:
		days = DEFAULT_ALERT_DAYS
	days = int(days)

	current = frappe.db.get_value("Notification", EXPIRING_NOTIFICATION, "days_in_advance")
	if int(current or 0) == days:
		return

	frappe.db.set_value(
		"Notification",
		EXPIRING_NOTIFICATION,
		"days_in_advance",
		days,
		update_modified=False,
	)


def ensure_print_formats():
	retire_legacy_print_formats()
	ensure_default_print_formats()
