frappe.ui.form.on("Atendimento Medico Diario", {
	onload(frm) {
		if (frm.is_new() && frm.doc.unidade && frm.doc.data) {
			carregar_especialidades(frm);
		}
	},
	refresh(frm) {
		configurar_grade(frm);
	},
	unidade(frm) {
		carregar_especialidades(frm);
	},
	data(frm) {
		carregar_especialidades(frm);
	},
});

frappe.ui.form.on("Atendimento Medico Diario Especialidade", {
	quantidade(frm) {
		atualizar_total(frm);
	},
});

function atualizar_total(frm) {
	const total = (frm.doc.especialidades || []).reduce(
		(soma, linha) => soma + (Number(linha.quantidade) || 0),
		0,
	);
	frm.set_value("total_dia", total);
}

async function carregar_especialidades(frm) {
	if (!frm.is_new() && frm.doc.docstatus !== 0) return;
	const { unidade, data } = frm.doc;
	const requisicao = (frm._atendimento_requisicao || 0) + 1;
	frm._atendimento_requisicao = requisicao;
	frm.set_value("vigencia", null);
	frm.clear_table("especialidades");
	frm.refresh_field("especialidades");
	atualizar_total(frm);
	if (!unidade || !data) return;
	try {
		const resposta = await frappe.call({
			method: "pulse_gestor.indicadores.doctype.atendimento_medico_diario.atendimento_medico_diario.buscar_vigencia_e_especialidades",
			args: { unidade, data },
		});
		if (requisicao !== frm._atendimento_requisicao) return;
		frm.set_value("vigencia", resposta.message.vigencia);
		for (const especialidade of resposta.message.especialidades) {
			frm.add_child("especialidades", especialidade);
		}
		frm.refresh_field("especialidades");
	} catch (erro) {
		// A chamada mostra a mensagem do servidor e o formulário permanece sem especialidades.
	}
}

function configurar_grade(frm) {
	const grade = frm.fields_dict.especialidades.grid;
	grade.df.in_place_edit = 1;
	grade.df.cannot_add_rows = 1;
	grade.df.cannot_delete_rows = 1;
	$(frm.wrapper)
		.off("grid-row-render.pulse-atendimento")
		.on("grid-row-render.pulse-atendimento", (_evento, linha) => {
			if (linha.grid !== grade) return;
			manter_espaco_acao(linha);
			linha.open_form_button = null;
			linha.row.off("click");
			linha.row_index?.off("click");
		});
	grade.refresh();
}

// O cabeçalho reserva uma célula final para a ação da linha; mantê-la vazia preserva o alinhamento.
function manter_espaco_acao(linha) {
	let celula = linha.row.children(".pulse-grid-action-spacer");
	if (!celula.length) {
		celula = linha.open_form_button?.parent() || $('<div class="col"></div>').appendTo(linha.row);
	}
	celula.addClass("pulse-grid-action-spacer").off("click keydown").empty().attr("aria-hidden", "true");
}
