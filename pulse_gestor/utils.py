# Copyright (c) 2026, StillPulse Tecnologia LTDA and contributors
# For license information, please see license.txt

"""Pure functions of Pulse Gestor (no database dependency)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

STATUS_VALID = "Válido"
STATUS_EXPIRED = "Vencido"
STATUS_NO_EXPIRY = "Sem validade"

PDF_EXTENSIONS = (".pdf",)


def _to_date(value: Any) -> date | None:
	if value is None or value == "":
		return None
	if isinstance(value, datetime):
		return value.date()
	if isinstance(value, date):
		return value
	text = str(value).strip()[:10]
	if not text:
		return None
	return date.fromisoformat(text)


def calculate_status(has_expiry: Any, end_date: Any, today: Any = None) -> str:
	"""Compute the status badge of the document."""
	if not int(has_expiry or 0):
		return STATUS_NO_EXPIRY

	end = _to_date(end_date)
	if not end:
		return STATUS_VALID

	reference = _to_date(today) or date.today()
	if end < reference:
		return STATUS_EXPIRED
	return STATUS_VALID


def calculate_days_to_expiry(has_expiry: Any, end_date: Any, today: Any = None) -> int | None:
	if not int(has_expiry or 0):
		return None
	end = _to_date(end_date)
	if not end:
		return None
	reference = _to_date(today) or date.today()
	return (end - reference).days


def is_pdf(path: str | None) -> bool:
	if not path:
		return False
	filename = str(path).split("?")[0].rsplit("/", 1)[-1].lower()
	return filename.endswith(PDF_EXTENSIONS)
