# Copyright (c) 2026, StillPulse Tecnologia LTDA and contributors
# For license information, please see license.txt

"""Data for the management panel of the Comissoes workspace (cards and blocks)."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_days, cint, date_diff, flt, get_datetime, getdate, now_datetime, nowdate

MEETING = "Reuniao de Comissao"
COMMITTEE_TERM = "Mandato de Comissao"
ACTIVE_STATUSES = ("Vigente", "Prorrogado")
TERM_EXPIRY_WARNING_DAYS = 60
NO_MEETING_DAYS = 90
ATTENDANCE_WINDOW_DAYS = 90


def _require_read(doctype: str = MEETING) -> None:
	frappe.has_permission(doctype, "read", throw=True)


def _active_terms() -> list[dict]:
	return frappe.get_list(
		COMMITTEE_TERM,
		filters={"status_mandato": ["in", ACTIVE_STATUSES]},
		fields=["name", "tipo_comissao", "empresa", "data_inicio_mandato", "data_encerramento_mandato"],
		limit_page_length=0,
	)


def _type_names() -> dict[str, str]:
	return {t.name: t.nome_tipo for t in frappe.get_all("Tipo de Comissao", fields=["name", "nome_tipo"])}


def _last_meeting_by_type() -> dict[str, object]:
	"""Latest meeting already held (data_reuniao <= now) of each committee type."""
	rows = frappe.get_list(
		MEETING,
		filters={"data_reuniao": ["<=", now_datetime()]},
		fields=["tipo_comissao", "max(data_reuniao) as ultima"],
		group_by="tipo_comissao",
		order_by=None,
		limit_page_length=0,
	)
	return {row.tipo_comissao: row.ultima for row in rows if row.tipo_comissao}


def _committees_without_meeting() -> list[dict]:
	"""Committees with an active term and no meeting held in the last NO_MEETING_DAYS days."""
	latest_by_type = _last_meeting_by_type()
	today = getdate(nowdate())
	result = []
	for term in _active_terms():
		latest = latest_by_type.get(term.tipo_comissao)
		days = date_diff(today, getdate(latest)) if latest else None
		if days is None or days > NO_MEETING_DAYS:
			result.append(frappe._dict(term, dias_sem_reuniao=days))
	return result


def _terms_expiring() -> list[dict]:
	"""Active terms ending within TERM_EXPIRY_WARNING_DAYS days (or already overdue)."""
	limit = add_days(nowdate(), TERM_EXPIRY_WARNING_DAYS)
	return [
		m
		for m in _active_terms()
		if m.data_encerramento_mandato and getdate(m.data_encerramento_mandato) <= getdate(limit)
	]


def _meetings_route(route_filters: dict | None = None) -> dict:
	return {"route": ["List", MEETING], "route_options": route_filters or {}}


@frappe.whitelist()
def card_upcoming_meetings(filters=None):
	_require_read()
	now = now_datetime()
	end = get_datetime(add_days(nowdate(), 8))  # 00:00 of day 8 = end of day 7
	value = frappe.db.count(MEETING, {"data_reuniao": ["between", [now, end]]})
	return {
		"value": value,
		"fieldtype": "Int",
		**_meetings_route({"data_reuniao": ["between", [str(now), str(end)]]}),
	}


@frappe.whitelist()
def card_expiring_terms(filters=None):
	_require_read(COMMITTEE_TERM)
	return {
		"value": len(_terms_expiring()),
		"fieldtype": "Int",
		"route": ["List", COMMITTEE_TERM],
		"route_options": {
			"status_mandato": ["in", list(ACTIVE_STATUSES)],
			"data_encerramento_mandato": ["<=", add_days(nowdate(), TERM_EXPIRY_WARNING_DAYS)],
		},
	}


@frappe.whitelist()
def card_committees_without_meeting(filters=None):
	_require_read()
	return {
		"value": len(_committees_without_meeting()),
		"fieldtype": "Int",
		"route": ["List", COMMITTEE_TERM],
	}


@frappe.whitelist()
def card_average_attendance(filters=None):
	"""Percentage of attendees in meetings of the last 90 days."""
	_require_read()
	start = add_days(nowdate(), -ATTENDANCE_WINDOW_DAYS)
	rows = frappe.get_list(
		MEETING,
		filters={"data_reuniao": ["between", [get_datetime(start), now_datetime()]]},
		fields=["name"],
		limit_page_length=0,
		pluck="name",
	)
	total = presentes = 0
	if rows:
		status = frappe.get_all(
			"Comissao Reuniao Participante",
			filters={"parenttype": MEETING, "parent": ["in", rows]},
			pluck="status_presenca",
		)
		total = len(status)
		presentes = sum(1 for s in status if s == "Presente")
	return {
		"value": flt(presentes * 100 / total, 1) if total else 0,
		"fieldtype": "Percent",
		**_meetings_route(),
	}


@frappe.whitelist()
def upcoming_meetings(limit=8):
	"""Upcoming meetings (from now on), nearest first."""
	_require_read()
	meetings = frappe.get_list(
		MEETING,
		filters={"data_reuniao": [">=", now_datetime()]},
		fields=["name", "tipo_comissao", "empresa", "data_reuniao", "local_reuniao"],
		order_by="data_reuniao asc",
		limit_page_length=cint(limit) or 8,
	)
	names = _type_names()
	today = getdate(nowdate())
	for r in meetings:
		r["comissao"] = names.get(r.tipo_comissao) or r.tipo_comissao
		r["dias"] = date_diff(getdate(r.data_reuniao), today)
		r["data_reuniao"] = str(r.data_reuniao)
	return meetings


@frappe.whitelist()
def committees_needing_attention():
	"""Management pending items: expiring/expired terms and committees without a recent meeting."""
	_require_read()
	names = _type_names()
	today = getdate(nowdate())
	items = []
	for m in _terms_expiring():
		days = date_diff(getdate(m.data_encerramento_mandato), today)
		items.append(
			{
				"doctype": COMMITTEE_TERM,
				"name": m.name,
				"comissao": names.get(m.tipo_comissao) or m.tipo_comissao,
				"empresa": m.empresa,
				"motivo": _("Mandato vencido há {0} dia(s)").format(-days)
				if days < 0
				else _("Mandato encerra em {0} dia(s)").format(days),
				"gravidade": "vermelho" if days < 0 else "amarelo",
				"ordem": days,
			}
		)
	for m in _committees_without_meeting():
		days = m.dias_sem_reuniao
		items.append(
			{
				"doctype": COMMITTEE_TERM,
				"name": m.name,
				"comissao": names.get(m.tipo_comissao) or m.tipo_comissao,
				"empresa": m.empresa,
				"motivo": _("Nenhuma reunião realizada")
				if days is None
				else _("Sem reunião há {0} dias").format(days),
				"gravidade": "vermelho" if days is None else "amarelo",
				"ordem": 10000 if days is None else -days,
			}
		)
	items.sort(key=lambda i: (i["gravidade"] != "vermelho", i["ordem"]))
	return items
