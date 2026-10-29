import frappe
from frappe.tests.utils import FrappeTestCase

from pulse_gestor.assinatura import PerfilTermoDeMovimentacao, PerfilTermoDoAtivo


def movimentacao(purpose="Transfer", *destinos):
	doc = frappe.new_doc("Asset Movement")
	doc.update({"name": "TEST-001", "purpose": purpose, "docstatus": 1})
	for i, employee in enumerate(destinos):
		doc.append("assets", {"asset_name": f"Bem {i}", "to_employee": employee})
	return doc


class TestTermoDeResponsabilidade(FrappeTestCase):
	def test_um_signatario_por_custodiante_de_destino(self):
		perfil = PerfilTermoDeMovimentacao()
		doc = movimentacao("Transfer", "EMP-A", "EMP-B", "EMP-A", None)
		self.assertEqual([s.parte for s in perfil.signatarios(doc)], ["EMP-A", "EMP-B"])

	def test_resumo_mostra_so_os_bens_do_signatario(self):
		perfil = PerfilTermoDeMovimentacao()
		doc = movimentacao("Transfer", "EMP-A", "EMP-B", "EMP-A")
		linhas = perfil.resumo_publico(doc, frappe._dict(parte="EMP-A"))["tabela"]["linhas"]
		self.assertEqual([linha[0]["texto"] for linha in linhas], ["Bem 0", "Bem 2"])

	def test_recebimento_e_movimentacao_sem_custodiante_sao_recusados(self):
		perfil = PerfilTermoDeMovimentacao()
		for doc in (movimentacao("Receipt", "EMP-A"), movimentacao("Transfer", None)):
			with self.assertRaises(frappe.ValidationError):
				perfil.validar_solicitacao(doc)

	def test_ativo_sem_custodiante_e_recusado(self):
		doc = frappe.new_doc("Asset")
		doc.update({"name": "TEST-001", "docstatus": 1})
		with self.assertRaises(frappe.ValidationError):
			PerfilTermoDoAtivo().validar_solicitacao(doc)
