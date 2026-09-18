frappe.ui.form.on("Atendimento Diario", {
	setup(frm) {
		frm.set_query("setor", () => ({ filters: { company: frm.doc.unidade || "" } }));
	},
	onload(frm) {
		if (frm.is_new() && frm.doc.unidade && frm.doc.setor && frm.doc.data) {
			carregar_especialidades(frm);
		}
	},
	refresh(frm) {
		const grade = frm.fields_dict.especialidades.grid;
		grade.df.in_place_edit = 1;
		grade.df.cannot_add_rows = 1;
		grade.df.cannot_delete_rows = 1;
		grade.refresh();
	},
	unidade(frm) {
		frm.set_value("setor", null);
		carregar_especialidades(frm);
	},
	setor(frm) {
		carregar_especialidades(frm);
	},
	data(frm) {
		carregar_especialidades(frm);
	},
});

frappe.ui.form.on("Atendimento Diario Especialidade", {
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
	const { unidade, setor, data } = frm.doc;
	const requisicao = (frm._atendimento_requisicao || 0) + 1;
	frm._atendimento_requisicao = requisicao;
	frm.set_value("vigencia", null);
	frm.clear_table("especialidades");
	frm.refresh_field("especialidades");
	atualizar_total(frm);
	if (!unidade || !setor || !data) return;
	try {
		const resposta = await frappe.call({
			method: "pulse_gestor.indicadores.doctype.atendimento_diario.atendimento_diario.buscar_vigencia_e_especialidades",
			args: { unidade, setor, data },
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
