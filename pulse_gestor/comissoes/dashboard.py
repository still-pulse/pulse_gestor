# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

"""Dados do painel de gestão do workspace Comissoes (cartões e blocos)."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import add_days, cint, date_diff, flt, get_datetime, getdate, now_datetime, nowdate

REUNIAO = "Reuniao de Comissao"
MANDATO = "Mandato de Comissao"
STATUS_ATIVOS = ("Vigente", "Prorrogado")
DIAS_MANDATO_A_VENCER = 60
DIAS_SEM_REUNIAO = 90
DIAS_PRESENCA = 90


def _exigir_leitura(doctype: str = REUNIAO) -> None:
	frappe.has_permission(doctype, "read", throw=True)


def _mandatos_ativos() -> list[dict]:
	return frappe.get_list(
		MANDATO,
		filters={"status_mandato": ["in", STATUS_ATIVOS]},
		fields=["name", "tipo_comissao", "empresa", "data_inicio_mandato", "data_encerramento_mandato"],
		limit_page_length=0,
	)


def _nomes_tipos() -> dict[str, str]:
	return {t.name: t.nome_tipo for t in frappe.get_all("Tipo de Comissao", fields=["name", "nome_tipo"])}


def _ultima_reuniao_por_tipo() -> dict[str, object]:
	"""Última reunião já realizada (data_reuniao <= agora) de cada tipo de comissão."""
	linhas = frappe.get_list(
		REUNIAO,
		filters={"data_reuniao": ["<=", now_datetime()]},
		fields=["tipo_comissao", "max(data_reuniao) as ultima"],
		group_by="tipo_comissao",
		order_by=None,
		limit_page_length=0,
	)
	return {linha.tipo_comissao: linha.ultima for linha in linhas if linha.tipo_comissao}


def _comissoes_sem_reuniao() -> list[dict]:
	"""Comissões com mandato ativo sem reunião realizada nos últimos DIAS_SEM_REUNIAO dias."""
	ultimas = _ultima_reuniao_por_tipo()
	hoje = getdate(nowdate())
	resultado = []
	for mandato in _mandatos_ativos():
		ultima = ultimas.get(mandato.tipo_comissao)
		dias = date_diff(hoje, getdate(ultima)) if ultima else None
		if dias is None or dias > DIAS_SEM_REUNIAO:
			resultado.append(frappe._dict(mandato, dias_sem_reuniao=dias))
	return resultado


def _mandatos_a_vencer() -> list[dict]:
	"""Mandatos ativos que encerram em até DIAS_MANDATO_A_VENCER dias (ou já passaram do prazo)."""
	limite = add_days(nowdate(), DIAS_MANDATO_A_VENCER)
	return [
		m
		for m in _mandatos_ativos()
		if m.data_encerramento_mandato and getdate(m.data_encerramento_mandato) <= getdate(limite)
	]


def _rota_reunioes(filtros: dict | None = None) -> dict:
	return {"route": ["List", REUNIAO], "route_options": filtros or {}}


@frappe.whitelist()
def cartao_reunioes_proximas(filters=None):
	_exigir_leitura()
	agora = now_datetime()
	fim = get_datetime(add_days(nowdate(), 8))  # 00:00 do 8º dia = fim do 7º dia
	valor = frappe.db.count(REUNIAO, {"data_reuniao": ["between", [agora, fim]]})
	return {
		"value": valor,
		"fieldtype": "Int",
		**_rota_reunioes({"data_reuniao": ["between", [str(agora), str(fim)]]}),
	}


@frappe.whitelist()
def cartao_mandatos_a_vencer(filters=None):
	_exigir_leitura(MANDATO)
	return {
		"value": len(_mandatos_a_vencer()),
		"fieldtype": "Int",
		"route": ["List", MANDATO],
		"route_options": {
			"status_mandato": ["in", list(STATUS_ATIVOS)],
			"data_encerramento_mandato": ["<=", add_days(nowdate(), DIAS_MANDATO_A_VENCER)],
		},
	}


@frappe.whitelist()
def cartao_comissoes_sem_reuniao(filters=None):
	_exigir_leitura()
	return {"value": len(_comissoes_sem_reuniao()), "fieldtype": "Int", "route": ["List", MANDATO]}


@frappe.whitelist()
def cartao_presenca_media(filters=None):
	"""Percentual de presentes nas reuniões dos últimos 90 dias."""
	_exigir_leitura()
	inicio = add_days(nowdate(), -DIAS_PRESENCA)
	linhas = frappe.get_list(
		REUNIAO,
		filters={"data_reuniao": ["between", [get_datetime(inicio), now_datetime()]]},
		fields=["name"],
		limit_page_length=0,
		pluck="name",
	)
	total = presentes = 0
	if linhas:
		status = frappe.get_all(
			"Comissao Reuniao Participante",
			filters={"parenttype": REUNIAO, "parent": ["in", linhas]},
			pluck="status_presenca",
		)
		total = len(status)
		presentes = sum(1 for s in status if s == "Presente")
	return {
		"value": flt(presentes * 100 / total, 1) if total else 0,
		"fieldtype": "Percent",
		**_rota_reunioes(),
	}


@frappe.whitelist()
def proximas_reunioes(limite=8):
	"""Próximas reuniões (a partir de agora), da mais próxima para a mais distante."""
	_exigir_leitura()
	reunioes = frappe.get_list(
		REUNIAO,
		filters={"data_reuniao": [">=", now_datetime()]},
		fields=["name", "tipo_comissao", "empresa", "data_reuniao", "local_reuniao"],
		order_by="data_reuniao asc",
		limit_page_length=cint(limite) or 8,
	)
	nomes = _nomes_tipos()
	hoje = getdate(nowdate())
	for r in reunioes:
		r["comissao"] = nomes.get(r.tipo_comissao) or r.tipo_comissao
		r["dias"] = date_diff(getdate(r.data_reuniao), hoje)
		r["data_reuniao"] = str(r.data_reuniao)
	return reunioes


@frappe.whitelist()
def comissoes_em_atencao():
	"""Pendências de gestão: mandatos a vencer/vencidos e comissões sem reunião recente."""
	_exigir_leitura()
	nomes = _nomes_tipos()
	hoje = getdate(nowdate())
	itens = []
	for m in _mandatos_a_vencer():
		dias = date_diff(getdate(m.data_encerramento_mandato), hoje)
		itens.append(
			{
				"doctype": MANDATO,
				"name": m.name,
				"comissao": nomes.get(m.tipo_comissao) or m.tipo_comissao,
				"empresa": m.empresa,
				"motivo": _("Mandato vencido há {0} dia(s)").format(-dias)
				if dias < 0
				else _("Mandato encerra em {0} dia(s)").format(dias),
				"gravidade": "vermelho" if dias < 0 else "amarelo",
				"ordem": dias,
			}
		)
	for m in _comissoes_sem_reuniao():
		dias = m.dias_sem_reuniao
		itens.append(
			{
				"doctype": MANDATO,
				"name": m.name,
				"comissao": nomes.get(m.tipo_comissao) or m.tipo_comissao,
				"empresa": m.empresa,
				"motivo": _("Nenhuma reunião realizada")
				if dias is None
				else _("Sem reunião há {0} dias").format(dias),
				"gravidade": "vermelho" if dias is None else "amarelo",
				"ordem": 10000 if dias is None else -dias,
			}
		)
	itens.sort(key=lambda i: (i["gravidade"] != "vermelho", i["ordem"]))
	return itens
