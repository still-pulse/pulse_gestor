// Copyright (c) 2026, Still Pulse and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tipo de Documento da Unidade", {
	refresh(frm) {
		if (frm.doc.ativo === 0) {
			frm.page.set_indicator(__("Inativo"), "gray");
		}
	},
});
