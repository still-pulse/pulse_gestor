frappe.ui.form.on("Protocolo de Triagem", {
	refresh(frm) {
		configure_grid(frm);
	},
});

frappe.ui.form.on("Protocolo Nivel", {
	cor(frm, cdt, cdn) {
		const row = frm.fields_dict.niveis.grid.grid_rows_by_docname[cdn];
		if (row) apply_row_color(row);
	},
});

function configure_grid(frm) {
	const grid = frm.fields_dict.niveis.grid;
	grid.df.in_place_edit = 1;
	$(frm.wrapper)
		.off("grid-row-render.pulse-protocolo")
		.on("grid-row-render.pulse-protocolo", (_event, row) => {
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
