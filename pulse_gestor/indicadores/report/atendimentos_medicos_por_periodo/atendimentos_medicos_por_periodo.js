frappe.query_reports["Atendimentos Medicos por Periodo"] = {
	filters: [
		{
			fieldname: "unidade",
			label: __("Unidade"),
			fieldtype: "Link",
			options: "Company",
			reqd: 1,
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "data_inicio",
			label: __("Data Início"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.month_start(),
		},
		{
			fieldname: "data_fim",
			label: __("Data Fim"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.month_end(),
		},
		{
			fieldname: "especialidade",
			label: __("Especialidade"),
			fieldtype: "Link",
			options: "Especialidade",
		},
	],
};
