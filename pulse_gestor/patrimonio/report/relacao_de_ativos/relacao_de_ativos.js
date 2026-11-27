frappe.query_reports["Relacao de Ativos"] = {
	filters: [
		{
			fieldname: "empresa",
			label: __("Empresa"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			on_change: () => {
				frappe.query_report.set_filter_value("localizacao", "");
			},
		},
		{
			fieldname: "localizacao",
			label: __("Localização"),
			fieldtype: "Link",
			options: "Location",
			get_query: () => {
				const empresa = frappe.query_report.get_filter_value("empresa");
				return empresa ? { filters: { custom_empresa: empresa } } : {};
			},
		},
		{
			fieldname: "categoria",
			label: __("Categoria"),
			fieldtype: "Link",
			options: "Asset Category",
		},
		{
			fieldname: "status",
			label: __("Situação"),
			fieldtype: "Select",
			options: [
				"",
				"Draft",
				"Submitted",
				"Partially Depreciated",
				"Fully Depreciated",
				"Sold",
				"Scrapped",
				"In Maintenance",
				"Out of Order",
				"Issue",
				"Receipt",
				"Capitalized",
				"Work In Progress",
			],
		},
		{
			fieldname: "utilizacao",
			label: __("Utilização"),
			fieldtype: "Select",
			options: ["", "Em uso", "Ocioso", "Em manutenção", "Inservível"],
		},
		{
			fieldname: "conservacao",
			label: __("Estado de conservação"),
			fieldtype: "Select",
			options: ["", "Excelente", "Bom", "Regular", "Ruim", "Péssimo"],
		},
	],
};
