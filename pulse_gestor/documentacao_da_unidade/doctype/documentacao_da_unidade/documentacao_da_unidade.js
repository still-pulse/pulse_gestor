// Copyright (c) 2026, StillPulse Tecnologia LTDA and contributors
// For license information, please see license.txt

frappe.ui.form.on("Documentacao da Unidade", {
	setup(frm) {
		frm.set_query("tipo_documento", () => ({
			filters: { ativo: 1 },
		}));
	},

	refresh(frm) {
		apply_indicator(frm);
	},

	possui_validade(frm) {
		if (!frm.doc.possui_validade) {
			frm.set_value("data_inicio", null);
			frm.set_value("data_fim", null);
		}
	},
});

function apply_indicator(frm) {
	const status_map = {
		Válido: "green",
		Vencido: "red",
		"Sem validade": "blue",
	};
	if (!frm.doc.status) {
		return;
	}
	frm.page.set_indicator(__(frm.doc.status), status_map[frm.doc.status] || "gray");
}
