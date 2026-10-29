frappe.query_reports["Atividades de Comissao"] = {
	filters: [
		{
			fieldname: "data_inicio",
			label: __("Data Início"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.year_start(),
		},
		{
			fieldname: "data_fim",
			label: __("Data Fim"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "empresa",
			label: __("Empresa"),
			fieldtype: "Link",
			options: "Company",
		},
		{
			fieldname: "tipo_comissao",
			label: __("Comissão"),
			fieldtype: "Link",
			options: "Tipo de Comissao",
			get_query: () => {
				const empresa = frappe.query_report.get_filter_value("empresa");
				return empresa ? { filters: { empresa } } : {};
			},
		},
		{
			fieldname: "incluir_pauta",
			label: __("Incluir pauta"),
			fieldtype: "Check",
			default: 0,
		},
	],
};
