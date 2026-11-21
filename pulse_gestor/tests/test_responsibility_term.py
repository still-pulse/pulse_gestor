import unittest

import frappe
from frappe.tests.utils import FrappeTestCase

try:
	from pulse_gestor.signature_profiles import AssetMovementTermProfile, AssetTermProfile
except ImportError:  # assinatura_eletronica (optional) not installed: the profiles do not exist
	AssetMovementTermProfile = AssetTermProfile = None


def movement(purpose="Transfer", *destinations):
	doc = frappe.new_doc("Asset Movement")
	doc.update({"name": "TEST-001", "purpose": purpose, "docstatus": 1})
	for i, employee in enumerate(destinations):
		doc.append("assets", {"asset_name": f"Bem {i}", "to_employee": employee})
	return doc


@unittest.skipUnless(AssetTermProfile, "assinatura_eletronica ausente")
class TestResponsibilityTerm(FrappeTestCase):
	def test_one_signatory_per_destination_custodian(self):
		profile = AssetMovementTermProfile()
		doc = movement("Transfer", "EMP-A", "EMP-B", "EMP-A", None)
		self.assertEqual([s.parte for s in profile.signatarios(doc)], ["EMP-A", "EMP-B"])

	def test_summary_shows_only_the_signatorys_assets(self):
		profile = AssetMovementTermProfile()
		doc = movement("Transfer", "EMP-A", "EMP-B", "EMP-A")
		rows = profile.resumo_publico(doc, frappe._dict(parte="EMP-A"))["tabela"]["linhas"]
		self.assertEqual([row[0]["texto"] for row in rows], ["Bem 0", "Bem 2"])

	def test_receipt_and_movement_without_custodian_are_rejected(self):
		profile = AssetMovementTermProfile()
		for doc in (movement("Receipt", "EMP-A"), movement("Transfer", None)):
			with self.assertRaises(frappe.ValidationError):
				profile.validar_solicitacao(doc)

	def test_asset_without_custodian_is_rejected(self):
		doc = frappe.new_doc("Asset")
		doc.update({"name": "TEST-001", "docstatus": 1})
		with self.assertRaises(frappe.ValidationError):
			AssetTermProfile().validar_solicitacao(doc)
