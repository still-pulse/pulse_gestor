const target = root_element.querySelector(".pg-conteudo");
const esc = (v) => frappe.utils.escape_html(v || "");

frappe
	.xcall("pulse_gestor.comissoes.dashboard.upcoming_meetings", { limit: 8 })
	.then((meetings) => {
		if (!meetings.length) {
			target.innerHTML = '<div class="pg-vazio">Nenhuma reunião agendada.</div>';
			return;
		}
		target.innerHTML =
			'<ul class="pg-lista">' +
			meetings
				.map((r) => {
					const date = moment(r.data_reuniao);
					const time = date.format("HH:mm") === "00:00" ? "" : date.format("HH:mm");
					const when =
						r.dias === 0 ? "Hoje" : r.dias === 1 ? "Amanhã" : `em ${r.dias} dias`;
					const color = r.dias <= 1 ? "vermelho" : r.dias <= 7 ? "amarelo" : "azul";
					const sub = [time, r.local_reuniao, r.empresa]
						.filter(Boolean)
						.map(esc)
						.join(" · ");
					return `<li class="pg-item">
						<div class="pg-data"><div class="pg-dia">${date.format(
							"DD"
						)}</div><div class="pg-mes">${date.format("MMM")}</div></div>
						<div class="pg-corpo">
							<a href="/app/reuniao-de-comissao/${encodeURIComponent(r.name)}">${esc(r.comissao)}</a>
							<div class="pg-sub">${sub}</div>
						</div>
						<span class="pg-tag ${color}">${when}</span>
					</li>`;
				})
				.join("") +
			"</ul>";
	});
