frappe.listview_settings["Unidade Protocolo Vigência"] = {
	onload(listview) {
		// Frappe 15 rejects accented DocType names inside the ORDER BY clause.
		listview.sort_selector.get_sql_string = function () {
			const fields = new Set([
				"name",
				"creation",
				"modified",
				"idx",
				"unidade",
				"protocolo",
				"data_inicio_vigencia",
				"data_fim_vigencia",
			]);
			const field = fields.has(this.sort_by) ? this.sort_by : "modified";
			const direction = this.sort_order === "asc" ? "asc" : "desc";
			const order_by = `\`${field}\` ${direction}`;
			return ["name", "creation", "modified"].includes(field)
				? order_by
				: `${order_by}, \`name\` ${direction}`;
		};
	},
};
