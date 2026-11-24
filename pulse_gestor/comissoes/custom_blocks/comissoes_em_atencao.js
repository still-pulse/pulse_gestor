const target = root_element.querySelector(".pg-conteudo");
const esc = (v) => frappe.utils.escape_html(v || "");

frappe.xcall("pulse_gestor.comissoes.dashboard.committees_needing_attention").then((items) => {
	if (!items.length) {
		target.innerHTML = '<div class="pg-vazio">Nenhuma pendência. Tudo em dia.</div>';
		return;
	}
	target.innerHTML =
		'<ul class="pg-lista">' +
		items
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
