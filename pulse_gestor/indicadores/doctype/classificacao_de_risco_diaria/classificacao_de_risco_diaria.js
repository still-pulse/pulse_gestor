frappe.ui.form.on("Classificacao de Risco Diaria", {
	refresh(frm) {
		configurar_grade(frm);
	},
	onload(frm) {
		if (frm.is_new() && frm.doc.unidade && frm.doc.data) {
			carregar_niveis(frm);
		}
	},
	unidade(frm) {
		carregar_niveis(frm);
	},
	data(frm) {
		carregar_niveis(frm);
	},
});

frappe.ui.form.on("Classificacao Diaria Nivel", {
	qtd_pacientes_classificados(frm) {
		atualizar_total(frm);
	},
});

function atualizar_total(frm) {
	const total = (frm.doc.niveis_classificados || []).reduce(
		(soma, linha) => soma + (Number(line.qtd_pacientes_classificados) || 0),
		0,
	);
	frm.set_value("total_classificados", total);
}

async function carregar_niveis(frm) {
	if (!frm.is_new() && frm.doc.docstatus !== 0) {
		return;
	}
	const unidade = frm.doc.unidade;
	const data = frm.doc.data;
	const requisicao = (frm._classificacao_requisicao || 0) + 1;
	frm._classificacao_requisicao = requisicao;
	frm.set_value("protocolo", null);
	frm.clear_table("niveis_classificados");
	frm.refresh_field("niveis_classificados");
	atualizar_total(frm);
	if (!unidade || !data) {
		return;
	}
	try {
		const resposta = await frappe.call({
			method: "pulse_gestor.indicadores.doctype.classificacao_de_risco_diaria.classificacao_de_risco_diaria.buscar_protocolo_e_niveis",
			args: { unidade, data },
		});
		if (requisicao !== frm._classificacao_requisicao) {
			return;
		}
		const resolvido = resposta.message;
		frm.set_value("protocolo", resolvido.protocolo);
		for (const nivel of resolvido.niveis) {
			frm.add_child("niveis_classificados", nivel);
		}
		frm.refresh_field("niveis_classificados");
	} catch (erro) {
		// A chamada apresenta a mensagem do servidor; o documento permanece sem protocolo.
	}
}

function configurar_grade(frm) {
	const grade = frm.fields_dict.niveis_classificados.grid;
	grade.df.in_place_edit = 1;
	grade.df.cannot_add_rows = 1;
	grade.df.cannot_delete_rows = 1;
	$(frm.wrapper)
		.off("grid-row-render.pulse-classificacao")
		.on("grid-row-render.pulse-classificacao", (_evento, linha) => {
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
