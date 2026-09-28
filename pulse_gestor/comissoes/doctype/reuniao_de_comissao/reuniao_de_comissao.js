frappe.ui.form.on("Reuniao de Comissao", {
	refresh(frm) {
		if (frm.doc.membros_comissao) {
			frm.add_custom_button(__("Buscar Participantes"), () => carregar_participantes(frm, true));
		}
	},
	membros_comissao(frm) {
		if (frm.doc.participantes && frm.doc.participantes.length) {
			return;
		}
		carregar_participantes(frm);
	},
});

async function carregar_participantes(frm, forcar) {
	if (!frm.doc.membros_comissao) {
		return;
	}
	if (forcar && frm.doc.participantes && frm.doc.participantes.length) {
		const confirmado = await new Promise((resolve) => {
			frappe.confirm(
				__("Isso substitui a lista de participantes atual. Deseja continuar?"),
				() => resolve(true),
				() => resolve(false),
			);
		});
		if (!confirmado) {
			return;
		}
	}
	const resposta = await frappe.call({
		method: "pulse_gestor.comissoes.doctype.reuniao_de_comissao.reuniao_de_comissao.buscar_membros",
		args: { membros_comissao: frm.doc.membros_comissao },
	});
	const membros = resposta.message || [];
	frm.clear_table("participantes");
	for (const membro of membros) {
		frm.add_child("participantes", {
			nome: membro.nome,
			funcao: membro.funcao,
			email: membro.email,
			status_presenca: "Presente",
		});
	}
	frm.refresh_field("participantes");
}
