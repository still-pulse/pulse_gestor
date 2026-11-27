frappe.listview_settings["Classificacao de Risco Diaria"] = {
	onload(listview) {
		// O validador SQL deste Frappe rejeita o nome acentuado da tabela em ORDER BY.
		listview.sort_selector.get_sql_string = function () {
			const fields = new Set([
				"name",
				"creation",
				"modified",
				"idx",
				"unidade",
				"data",
				"protocolo",
				"total_classificados",
				"status",
			]);
			const field = fields.has(this.sort_by) ? this.sort_by : "data";
			const direction = this.sort_order === "asc" ? "asc" : "desc";
			const order_by = `\`${field}\` ${direction}`;
			return ["name", "creation", "modified"].includes(field)
				? order_by
				: `${order_by}, \`name\` ${direction}`;
		};
	},
};
