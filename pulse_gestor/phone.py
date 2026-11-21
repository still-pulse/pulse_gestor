"""Mask and validation of Brazilian phone numbers (mobile/WhatsApp)."""

import re

import frappe
from frappe import _


def national_digits_only(value) -> str:
	digits = re.sub(r"\D", "", str(value or ""))
	if len(digits) > 11 and digits.startswith("55"):
		digits = digits[2:]
	return digits


def format_phone(value) -> str:
	"""(DD) 99999-9999 or (DD) 9999-9999; returns the original value unless it has 10 or 11 digits."""
	digits = national_digits_only(value)
	if len(digits) == 11:
		return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
	if len(digits) == 10:
		return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
	return value


def normalize_phone(value) -> str | None:
	"""55 + area code + number, validating the area code and the ninth digit; None if invalid."""
	from integracoes_customizadas.whatsapp.conector import normalizar_numero_br

	return normalizar_numero_br(value)


def validate_and_format_rows(rows):
	"""Apply the mask to the `telefone` field of each row and reject invalid numbers."""
	for row in rows or []:
		if not row.get("telefone"):
			continue
		if not _is_valid_number(row.telefone):
			frappe.throw(
				_("Linha {0}: telefone inválido ({1}). Use DDD + número, ex.: (11) 99999-9999.").format(
					row.idx, row.telefone
				)
			)
		row.telefone = format_phone(row.telefone)


def _is_valid_number(value) -> bool:
	try:
		return bool(normalize_phone(value))
	except ImportError:
		return len(national_digits_only(value)) in (10, 11)
