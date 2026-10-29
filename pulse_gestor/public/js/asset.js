// Custodiante do bem: só colaboradores ativos da empresa do ativo.
frappe.ui.form.on("Asset", {
	setup(frm) {
		frm.set_query("custodian", () => ({
			filters: { company: frm.doc.company, status: "Active" },
		}));
	},
	company(frm) {
		if (!frm.doc.custodian) return;
		frappe.db.get_value("Employee", frm.doc.custodian, "company").then(({ message }) => {
			if (message && message.company !== frm.doc.company) frm.set_value("custodian", "");
		});
	},
});
