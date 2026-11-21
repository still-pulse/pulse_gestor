frappe.ui.form.on("Reuniao de Comissao", {
	refresh(frm) {
		if (frm.doc.membros_comissao) {
			frm.add_custom_button(__("Buscar Participantes"), () => load_participants(frm, true));
		}
		if (!frm.is_new()) {
			frm.add_custom_button(
				__("Convocar membros"),
				() => send_convocation(frm),
				__("Ações")
			);
		}
	},
	membros_comissao(frm) {
		if (frm.doc.participantes && frm.doc.participantes.length) {
			return;
		}
		load_participants(frm);
	},
});

async function load_participants(frm, force) {
	if (!frm.doc.membros_comissao) {
		return;
	}
	if (force && frm.doc.participantes && frm.doc.participantes.length) {
		const confirmed = await new Promise((resolve) => {
			frappe.confirm(
				__("Isso substitui a lista de participantes atual. Deseja continuar?"),
				() => resolve(true),
				() => resolve(false)
			);
		});
		if (!confirmed) {
			return;
		}
	}
	const response = await frappe.call({
		method: "pulse_gestor.comissoes.doctype.reuniao_de_comissao.reuniao_de_comissao.fetch_members",
		args: { members_doc: frm.doc.membros_comissao },
	});
	const members = response.message || [];
	frm.clear_table("participantes");
	for (const member of members) {
		frm.add_child("participantes", {
			nome: member.nome,
			funcao: member.funcao,
			email: member.email,
			telefone: member.telefone,
			canal_preferencial: member.canal_preferencial,
			membro_origem: member.name,
			status_presenca: "Presente",
		});
	}
	frm.refresh_field("participantes");
}

function send_convocation(frm) {
	if (frm.is_dirty()) {
		frappe.msgprint(__("Salve a reunião antes de convocar."));
		return;
	}
	frappe.prompt(
		[
			{
				fieldname: "channel",
				fieldtype: "Select",
				label: __("Canal"),
				options: ["", "WhatsApp", "E-mail", "Ambos"].join("\n"),
				description: __("Vazio = canal preferencial de cada participante."),
			},
		],
		(values) => {
			frappe.call({
				method: "pulse_gestor.comissoes.doctype.reuniao_de_comissao.reuniao_de_comissao.send_convocation",
				args: { name: frm.doc.name, channel: values.channel || null },
				freeze: true,
				freeze_message: __("Enviando convocações..."),
				callback: (r) => {
					const res = r.message || {};
					frappe.show_alert({
						message: __("Convocados: {0}. Falhas: {1}.", [
							res.enviados || 0,
							res.falhas || 0,
						]),
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
