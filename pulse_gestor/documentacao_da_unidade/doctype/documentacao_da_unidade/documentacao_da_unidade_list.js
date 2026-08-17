// Copyright (c) 2026, Still Pulse and contributors
// For license information, please see license.txt

frappe.listview_settings["Documentacao da Unidade"] = {
	add_fields: ["status", "possui_validade", "data_fim", "company", "tipo_documento"],
	get_indicator(doc) {
		if (doc.status === "Vencido") {
			return [__("Vencido"), "red", "status,=,Vencido"];
		}
		if (doc.status === "Sem validade") {
			return [__("Sem validade"), "blue", "status,=,Sem validade"];
		}
		return [__("Válido"), "green", "status,=,Válido"];
	},
};
