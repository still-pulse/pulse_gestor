const alvo = root_element.querySelector(".pg-conteudo");
const esc = (v) => frappe.utils.escape_html(v || "");

frappe
	.xcall("pulse_gestor.comissoes.dashboard.proximas_reunioes", { limite: 8 })
	.then((reunioes) => {
		if (!reunioes.length) {
			alvo.innerHTML = '<div class="pg-vazio">Nenhuma reunião agendada.</div>';
			return;
		}
		alvo.innerHTML =
			'<ul class="pg-lista">' +
			reunioes
				.map((r) => {
					const data = moment(r.data_reuniao);
					const hora = data.format("HH:mm") === "00:00" ? "" : data.format("HH:mm");
					const quando = r.dias === 0 ? "Hoje" : r.dias === 1 ? "Amanhã" : `em ${r.dias} dias`;
					const cor = r.dias <= 1 ? "vermelho" : r.dias <= 7 ? "amarelo" : "azul";
					const sub = [hora, r.local_reuniao, r.empresa].filter(Boolean).map(esc).join(" · ");
					return `<li class="pg-item">
						<div class="pg-data"><div class="pg-dia">${data.format("DD")}</div><div class="pg-mes">${data.format("MMM")}</div></div>
						<div class="pg-corpo">
							<a href="/app/reuniao-de-comissao/${encodeURIComponent(r.name)}">${esc(r.comissao)}</a>
							<div class="pg-sub">${sub}</div>
						</div>
						<span class="pg-tag ${cor}">${quando}</span>
					</li>`;
				})
				.join("") +
			"</ul>";
	});
