import frappe


def execute():
	"""Copia a empresa dos mandatos para o tipo, quando a origem é inequívoca.

	Tipos usados por mais de uma empresa (ou sem mandato) ficam sem empresa
	e precisam ser completados manualmente, junto com a categoria.
	"""
	if not frappe.db.has_column("Tipo de Comissao", "empresa"):
		return

	tipos = frappe.get_all("Tipo de Comissao", filters={"empresa": ["is", "not set"]}, pluck="name")
	for tipo in tipos:
		empresas = frappe.get_all(
			"Mandato de Comissao",
			filters={"tipo_comissao": tipo, "empresa": ["is", "set"]},
			pluck="empresa",
			distinct=True,
		)
		if len(empresas) == 1:
			frappe.db.set_value("Tipo de Comissao", tipo, "empresa", empresas[0], update_modified=False)
