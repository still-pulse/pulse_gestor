// Máscara (DD) 99999-9999 no telefone dos membros; o servidor revalida no validate.
function mask_phone(value) {
	let d = String(value || "").replace(/\D/g, "");
	if (d.length > 11 && d.startsWith("55")) {
		d = d.slice(2);
	}
	d = d.slice(0, 11);
	if (d.length <= 2) {
		return d ? `(${d}` : "";
	}
	if (d.length <= 6) {
		return `(${d.slice(0, 2)}) ${d.slice(2)}`;
	}
	if (d.length <= 10) {
		return `(${d.slice(0, 2)}) ${d.slice(2, 6)}-${d.slice(6)}`;
	}
	return `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`;
}

frappe.ui.form.on("Comissao Membro", {
	form_render(frm, cdt, cdn) {
		const field = frm.fields_dict.membros.grid.get_row(cdn)?.grid_form?.fields_dict?.telefone;
		if (!field || !field.$input) {
			return;
		}
		field.$input.attr({ placeholder: "(11) 99999-9999", maxlength: 15, inputmode: "tel" });
		field.$input.off("input.pg_mask").on("input.pg_mask", function () {
			const masked = mask_phone(this.value);
			if (masked !== this.value) {
				this.value = masked;
			}
		});
	},
	telefone(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		const masked = mask_phone(row.telefone);
		if (row.telefone && masked !== row.telefone) {
			frappe.model.set_value(cdt, cdn, "telefone", masked);
		}
	},
});
