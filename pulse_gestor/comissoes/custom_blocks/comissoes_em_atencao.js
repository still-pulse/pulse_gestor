const alvo = root_element.querySelector(".pg-conteudo");
const esc = (v) => frappe.utils.escape_html(v || "");

frappe.xcall("pulse_gestor.comissoes.dashboard.comissoes_em_atencao").then((itens) => {
	if (!itens.length) {
		alvo.innerHTML = '<div class="pg-vazio">Nenhuma pendência. Tudo em dia.</div>';
		return;
	}
	alvo.innerHTML =
		'<ul class="pg-lista">' +
		itens
			.slice(0, 10)
			.map(
				(i) => `<li class="pg-item">
					<div class="pg-corpo">
						<a href="/app/mandato-de-comissao/${encodeURIComponent(i.name)}">${esc(i.comissao)}</a>
						<div class="pg-sub">${esc(i.empresa)}</div>
					</div>
					<span class="pg-tag ${i.gravidade}">${esc(i.motivo)}</span>
				</li>`
			)
			.join("") +
		"</ul>";
});
