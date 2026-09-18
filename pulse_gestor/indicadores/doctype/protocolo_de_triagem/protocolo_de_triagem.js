frappe.ui.form.on("Protocolo de Triagem", {
	refresh(frm) {
		configurar_grade(frm);
	},
});

frappe.ui.form.on("Protocolo Nivel", {
	cor(frm, cdt, cdn) {
		const linha = frm.fields_dict.niveis.grid.grid_rows_by_docname[cdn];
		if (linha) aplicar_cor_linha(linha);
	},
});

function configurar_grade(frm) {
	const grade = frm.fields_dict.niveis.grid;
	grade.df.in_place_edit = 1;
	$(frm.wrapper)
		.off("grid-row-render.pulse-protocolo")
		.on("grid-row-render.pulse-protocolo", (_evento, linha) => {
			if (linha.grid !== grade) return;
			manter_espaco_acao(linha);
			linha.open_form_button = null;
			linha.row.off("click");
			linha.row_index?.off("click");
			aplicar_cor_linha(linha);
		});
	grade.refresh();
}

function manter_espaco_acao(linha) {
	let celula = linha.row.children(".pulse-grid-action-spacer");
	if (!celula.length) {
		celula = linha.open_form_button?.parent() || $('<div class="col"></div>').appendTo(linha.row);
	}
	celula.addClass("pulse-grid-action-spacer").off("click keydown").empty().attr("aria-hidden", "true");
}

function aplicar_cor_linha(linha) {
	const cor = linha.doc.cor || "";
	const partes = /^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i.exec(cor);
	const estilo = linha.row[0].style;
	estilo.borderInlineStart = "";
	if (!partes) {
		estilo.backgroundColor = "";
		estilo.boxShadow = "";
		return;
	}
	const [vermelho, verde, azul] = partes.slice(1).map((parte) => parseInt(parte, 16));
	estilo.backgroundColor = `rgba(${vermelho}, ${verde}, ${azul}, 0.12)`;
	estilo.boxShadow = `inset 4px 0 0 ${cor}`;
}
