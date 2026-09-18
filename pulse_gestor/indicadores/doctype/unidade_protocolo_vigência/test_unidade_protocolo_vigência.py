from unittest import TestCase

from pulse_gestor.indicadores.doctype.unidade_protocolo_vigência.unidade_protocolo_vigência import (
	periodos_se_sobrepoem,
)


class TestUnidadeProtocoloVigência(TestCase):
	def test_periodos_adjacentes_nao_se_sobrepoem(self):
		self.assertFalse(periodos_se_sobrepoem("2026-01-01", "2026-06-30", "2026-07-01", None))

	def test_data_final_e_inclusiva(self):
		self.assertTrue(periodos_se_sobrepoem("2026-01-01", "2026-06-30", "2026-06-30", None))

	def test_periodo_sem_fim_impede_nova_vigencia(self):
		self.assertTrue(periodos_se_sobrepoem("2026-01-01", None, "2027-01-01", "2027-12-31"))

	def test_periodos_passados_nao_se_sobrepoem(self):
		self.assertFalse(periodos_se_sobrepoem("2027-01-01", None, "2026-01-01", "2026-12-31"))
