"""Máscara e validação de telefone brasileiro (celular/WhatsApp)."""

import re

import frappe
from frappe import _


def apenas_digitos_nacionais(valor) -> str:
	digitos = re.sub(r"\D", "", str(valor or ""))
	if len(digitos) > 11 and digitos.startswith("55"):
		digitos = digitos[2:]
	return digitos


def formatar_telefone(valor) -> str:
	"""(DD) 99999-9999 ou (DD) 9999-9999; devolve o valor original se não tiver 10 ou 11 dígitos."""
	digitos = apenas_digitos_nacionais(valor)
	if len(digitos) == 11:
		return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
	if len(digitos) == 10:
		return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
	return valor


def normalizar_telefone(valor) -> str | None:
	"""55 + DDD + número, validando DDD e nono dígito; None se inválido."""
	from integracoes_customizadas.whatsapp.conector import normalizar_numero_br

	return normalizar_numero_br(valor)


def validar_e_formatar_linhas(linhas):
	"""Aplica a máscara ao campo `telefone` de cada linha e rejeita números inválidos."""
	for linha in linhas or []:
		if not linha.get("telefone"):
			continue
		if not _numero_valido(linha.telefone):
			frappe.throw(
				_("Linha {0}: telefone inválido ({1}). Use DDD + número, ex.: (11) 99999-9999.").format(
					linha.idx, linha.telefone
				)
			)
		linha.telefone = formatar_telefone(linha.telefone)


def _numero_valido(valor) -> bool:
	try:
		return bool(normalizar_telefone(valor))
	except ImportError:
		return len(apenas_digitos_nacionais(valor)) in (10, 11)
