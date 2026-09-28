import frappe
from frappe.tests.utils import FrappeTestCase

from pulse_gestor.comissoes.report.atividades_de_comissao.atividades_de_comissao import execute


class TestAtividadesDeComissao(FrappeTestCase):
	def test_exige_periodo_valido(self):
		with self.assertRaises(frappe.ValidationError):
			execute({"data_inicio": "2026-02-01", "data_fim": "2026-01-01"})
		with self.assertRaises(frappe.ValidationError):
			execute({})

	def test_coluna_de_pauta_depende_do_filtro(self):
		periodo = {"data_inicio": "2026-01-01", "data_fim": "2026-12-31"}
		sem_pauta = [c["fieldname"] for c in execute(periodo)[0]]
		com_pauta = [c["fieldname"] for c in execute({**periodo, "incluir_pauta": 1})[0]]
		self.assertNotIn("assunto", sem_pauta)
		self.assertIn("assunto", com_pauta)
