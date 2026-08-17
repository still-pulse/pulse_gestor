# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

"""Funções puras do Pulse Gestor (sem dependência de banco)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any


STATUS_VALIDO = "Válido"
STATUS_VENCIDO = "Vencido"
STATUS_SEM_VALIDADE = "Sem validade"

EXTENSOES_PDF = (".pdf",)


def _para_data(valor: Any) -> date | None:
	if valor is None or valor == "":
		return None
	if isinstance(valor, datetime):
		return valor.date()
	if isinstance(valor, date):
		return valor
	texto = str(valor).strip()[:10]
	if not texto:
		return None
	return date.fromisoformat(texto)


def calcular_status(possui_validade: Any, data_fim: Any, hoje: Any = None) -> str:
	"""Calcula o badge de status do documento."""
	if not int(possui_validade or 0):
		return STATUS_SEM_VALIDADE

	fim = _para_data(data_fim)
	if not fim:
		return STATUS_VALIDO

	referencia = _para_data(hoje) or date.today()
	if fim < referencia:
		return STATUS_VENCIDO
	return STATUS_VALIDO


def calcular_dias_para_vencimento(possui_validade: Any, data_fim: Any, hoje: Any = None) -> int | None:
	if not int(possui_validade or 0):
		return None
	fim = _para_data(data_fim)
	if not fim:
		return None
	referencia = _para_data(hoje) or date.today()
	return (fim - referencia).days


def eh_pdf(caminho: str | None) -> bool:
	if not caminho:
		return False
	nome = str(caminho).split("?")[0].rsplit("/", 1)[-1].lower()
	return nome.endswith(EXTENSOES_PDF)
