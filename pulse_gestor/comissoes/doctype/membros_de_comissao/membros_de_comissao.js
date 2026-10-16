// Máscara (DD) 99999-9999 no telefone dos membros; o servidor revalida no validate.
function mascara_telefone(valor) {
	let d = String(valor || "").replace(/\D/g, "");
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
		const campo = frm.fields_dict.membros.grid.get_row(cdn)?.grid_form?.fields_dict?.telefone;
		if (!campo || !campo.$input) {
			return;
		}
		campo.$input.attr({ placeholder: "(11) 99999-9999", maxlength: 15, inputmode: "tel" });
		campo.$input.off("input.pg_mask").on("input.pg_mask", function () {
			const mascarado = mascara_telefone(this.value);
			if (mascarado !== this.value) {
				this.value = mascarado;
			}
		});
	},
	telefone(frm, cdt, cdn) {
		const linha = locals[cdt][cdn];
		const mascarado = mascara_telefone(linha.telefone);
		if (linha.telefone && mascarado !== linha.telefone) {
			frappe.model.set_value(cdt, cdn, "telefone", mascarado);
		}
	},
});
