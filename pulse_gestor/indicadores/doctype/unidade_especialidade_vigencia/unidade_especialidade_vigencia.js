frappe.ui.form.on("Unidade Especialidade Vigencia", {
	setup(frm) {
		frm.set_query("setor", () => ({ filters: { company: frm.doc.unidade || "" } }));
	},
	unidade(frm) {
		frm.set_value("setor", null);
	},
});
