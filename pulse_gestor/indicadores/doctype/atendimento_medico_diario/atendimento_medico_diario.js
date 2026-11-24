frappe.ui.form.on("Atendimento Medico Diario", {
	onload(frm) {
		if (frm.is_new() && frm.doc.unidade && frm.doc.data) {
			load_specialties(frm);
		}
	},
	refresh(frm) {
		configure_grid(frm);
	},
	unidade(frm) {
		load_specialties(frm);
	},
	data(frm) {
		load_specialties(frm);
	},
});

frappe.ui.form.on("Atendimento Medico Diario Especialidade", {
	quantidade(frm) {
		update_total(frm);
	},
});

function update_total(frm) {
	const total = (frm.doc.especialidades || []).reduce(
		(sum, row) => sum + (Number(row.quantidade) || 0),
		0
	);
	frm.set_value("total_dia", total);
}

async function load_specialties(frm) {
	if (!frm.is_new() && frm.doc.docstatus !== 0) return;
	const { unidade: unit, data: date } = frm.doc;
	const request_id = (frm._entry_request_id || 0) + 1;
	frm._entry_request_id = request_id;
	frm.set_value("vigencia", null);
	frm.clear_table("especialidades");
	frm.refresh_field("especialidades");
	update_total(frm);
	if (!unit || !date) return;
	try {
		const response = await frappe.call({
			method: "pulse_gestor.indicadores.doctype.atendimento_medico_diario.atendimento_medico_diario.fetch_validity_and_specialties",
			args: { unit, date },
		});
		if (request_id !== frm._entry_request_id) return;
		frm.set_value("vigencia", response.message.vigencia);
		for (const specialty of response.message.especialidades) {
			frm.add_child("especialidades", specialty);
		}
		frm.refresh_field("especialidades");
	} catch (error) {
		// The call shows the server message and the form stays without specialties.
	}
}

function configure_grid(frm) {
	const grid = frm.fields_dict.especialidades.grid;
	grid.df.in_place_edit = 1;
	grid.df.cannot_add_rows = 1;
	grid.df.cannot_delete_rows = 1;
	$(frm.wrapper)
		.off("grid-row-render.pulse-atendimento")
		.on("grid-row-render.pulse-atendimento", (_event, row) => {
			if (row.grid !== grid) return;
			keep_action_spacer(row);
			row.open_form_button = null;
			row.row.off("click");
			row.row_index?.off("click");
		});
	grid.refresh();
}

// The header reserves a final cell for the row action; keeping it empty preserves the alignment.
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
