// Copyright (c) 2026, Still Pulse and contributors
// For license information, please see license.txt

frappe.ui.form.on("Documentacao da Unidade", {
	setup(frm) {
		frm.set_query("tipo_documento", () => ({
			filters: { ativo: 1 },
		}));
	},

	refresh(frm) {
		aplicar_indicador(frm);
	},

	possui_validade(frm) {
		if (!frm.doc.possui_validade) {
			frm.set_value("data_inicio", null);
			frm.set_value("data_fim", null);
		}
	},
});

function aplicar_indicador(frm) {
	const mapa = {
		Válido: "green",
		Vencido: "red",
		"Sem validade": "blue",
	};
	if (!frm.doc.status) {
		return;
	}
	frm.page.set_indicator(__(frm.doc.status), mapa[frm.doc.status] || "gray");
}
