# Copyright (c) 2026, Still Pulse and contributors
# For license information, please see license.txt

from frappe.tests.utils import FrappeTestCase

from pulse_gestor import hooks
from pulse_gestor.tests.site_setup import CAMPOS


class TestFixturesDePatrimonio(FrappeTestCase):
	def test_filtro_de_fixture_cobre_os_campos_que_o_ci_cria(self):
		esperados = {f"{doctype}-{c['fieldname']}" for doctype, lista in CAMPOS.items() for c in lista}
		filtro = next(f for f in hooks.fixtures if f.get("dt") == "Custom Field")
		self.assertEqual(set(filtro["filters"][0][2]), esperados)
		self.assertEqual(len(esperados), 5)
