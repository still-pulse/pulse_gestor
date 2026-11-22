# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

"""Hooks de instalação/migração e jobs agendados não fazem commit manual (regra frappe-manual-commit).

O Frappe já confirma a transação: `install-app` e `SiteMigration` (etapas `@atomic`) e `execute_job` dos
jobs agendados.
"""

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from pulse_gestor import tasks
from pulse_gestor.print_formats import preserve_accented_legacy_print_formats
from pulse_gestor.setup import install


class TestSemCommitManual(FrappeTestCase):
	def test_before_migrate_nao_faz_commit(self):
		with patch.object(frappe.db, "commit") as commit:
			preserve_accented_legacy_print_formats()
		commit.assert_not_called()

	def test_after_install_nao_faz_commit_e_formatos_ficam_definidos(self):
		with patch.object(frappe.db, "commit") as commit:
			install.after_install()
		commit.assert_not_called()
		self.assertEqual(frappe.get_meta("Asset").default_print_format, "Ficha do Ativo Imobilizado")

	def test_after_migrate_nao_faz_commit(self):
		with patch.object(frappe.db, "commit") as commit:
			install.after_migrate()
		commit.assert_not_called()

	def test_atualizar_status_grava_sem_commit(self):
		documento = frappe._dict(
			name="DOC-TESTE",
			possui_validade=1,
			data_fim="2000-01-01",
			status="Válido",
			dias_para_vencimento=1,
		)
		with (
			patch("pulse_gestor.tasks.frappe.get_all", return_value=[documento]),
			patch("pulse_gestor.tasks.frappe.db.set_value") as set_value,
			patch("pulse_gestor.tasks.frappe.db.commit") as commit,
		):
			tasks.atualizar_status_documentos()
		commit.assert_not_called()
		valores = set_value.call_args.args[2]
		self.assertEqual(valores["status"], "Vencido")
