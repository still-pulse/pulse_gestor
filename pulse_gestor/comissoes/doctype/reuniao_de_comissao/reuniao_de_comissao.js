frappe.ui.form.on("Reuniao de Comissao", {
	refresh(frm) {
		if (frm.doc.membros_comissao) {
			frm.add_custom_button(__("Buscar Participantes"), () => carregar_participantes(frm, true));
		}
		if (!frm.is_new()) {
			frm.add_custom_button(__("Convocar membros"), () => convocar(frm), __("Ações"));
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
			telefone: membro.telefone,
			canal_preferencial: membro.canal_preferencial,
			membro_origem: membro.name,
			status_presenca: "Presente",
		});
	}
	frm.refresh_field("participantes");
}

function convocar(frm) {
	if (frm.is_dirty()) {
		frappe.msgprint(__("Salve a reunião antes de convocar."));
		return;
	}
	frappe.prompt(
		[
			{
				fieldname: "canal",
				fieldtype: "Select",
				label: __("Canal"),
				options: ["", "WhatsApp", "E-mail", "Ambos"].join("\n"),
				description: __("Vazio = canal preferencial de cada participante."),
			},
		],
		(valores) => {
			frappe.call({
				method: "pulse_gestor.comissoes.doctype.reuniao_de_comissao.reuniao_de_comissao.convocar",
				args: { name: frm.doc.name, canal: valores.canal || null },
				freeze: true,
				freeze_message: __("Enviando convocações..."),
				callback: (r) => {
					const res = r.message || {};
					frappe.show_alert({
						message: __("Convocados: {0}. Falhas: {1}.", [res.enviados || 0, res.falhas || 0]),
						indicator: res.falhas ? "orange" : "green",
					});
					frm.reload_doc();
				},
			});
		},
		__("Convocar membros"),
		__("Enviar")
	);
}
