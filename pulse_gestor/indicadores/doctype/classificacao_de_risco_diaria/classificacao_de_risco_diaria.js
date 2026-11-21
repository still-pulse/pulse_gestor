frappe.ui.form.on("Classificacao de Risco Diaria", {
	refresh(frm) {
		configure_grid(frm);
	},
	onload(frm) {
		if (frm.is_new() && frm.doc.unidade && frm.doc.data) {
			load_levels(frm);
		}
	},
	unidade(frm) {
		load_levels(frm);
	},
	data(frm) {
		load_levels(frm);
	},
});

frappe.ui.form.on("Classificacao Diaria Nivel", {
	qtd_pacientes_classificados(frm) {
		update_total(frm);
	},
});

function update_total(frm) {
	const total = (frm.doc.niveis_classificados || []).reduce(
		(sum, row) => sum + (Number(row.qtd_pacientes_classificados) || 0),
		0
	);
	frm.set_value("total_classificados", total);
}

async function load_levels(frm) {
	if (!frm.is_new() && frm.doc.docstatus !== 0) {
		return;
	}
	const unit = frm.doc.unidade;
	const date = frm.doc.data;
	const request_id = (frm._classification_request_id || 0) + 1;
	frm._classification_request_id = request_id;
	frm.set_value("protocolo", null);
	frm.clear_table("niveis_classificados");
	frm.refresh_field("niveis_classificados");
	update_total(frm);
	if (!unit || !date) {
		return;
	}
	try {
		const response = await frappe.call({
			method: "pulse_gestor.indicadores.doctype.classificacao_de_risco_diaria.classificacao_de_risco_diaria.buscar_protocolo_e_niveis",
			args: { unit, date },
		});
		if (request_id !== frm._classification_request_id) {
			return;
		}
		const resolved = response.message;
		frm.set_value("protocolo", resolved.protocolo);
		for (const level of resolved.niveis) {
			frm.add_child("niveis_classificados", level);
		}
		frm.refresh_field("niveis_classificados");
	} catch (error) {
		// A chamada apresenta a mensagem do servidor; o documento permanece sem protocolo.
	}
}

function configure_grid(frm) {
	const grid = frm.fields_dict.niveis_classificados.grid;
	grid.df.in_place_edit = 1;
	grid.df.cannot_add_rows = 1;
	grid.df.cannot_delete_rows = 1;
	$(frm.wrapper)
		.off("grid-row-render.pulse-classificacao")
		.on("grid-row-render.pulse-classificacao", (_event, row) => {
			if (row.grid !== grid) return;
			keep_action_spacer(row);
			row.open_form_button = null;
			row.row.off("click");
			row.row_index?.off("click");
			apply_row_color(row);
		});
	grid.refresh();
}

function keep_action_spacer(row) {
	let cell = row.row.children(".pulse-grid-action-spacer");
	if (!cell.length) {
		cell = row.open_form_button?.parent() || $('<div class="col"></div>').appendTo(row.row);
	}
	cell.addClass("pulse-grid-action-spacer")
		.off("click keydown")
		.empty()
		.attr("aria-hidden", "true");
}

function apply_row_color(row) {
	const color = row.doc.cor || "";
	const parts = /^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i.exec(color);
	const style = row.row[0].style;
	style.borderInlineStart = "";
	if (!parts) {
		style.backgroundColor = "";
		style.boxShadow = "";
		return;
	}
	const [red, green, blue] = parts.slice(1).map((part) => parseInt(part, 16));
	style.backgroundColor = `rgba(${red}, ${green}, ${blue}, 0.12)`;
	style.boxShadow = `inset 4px 0 0 ${color}`;
}
