app_name = "pulse_gestor"
app_title = "Pulse Gestor"
app_publisher = "Still Pulse"
app_description = "Documentação da Unidade — cadastro de documentos por empresa/unidade com validade e alerta de vencimento"
app_email = "dev@stillpulse.com.br"
app_license = "mit"
app_version = "0.11.7"

required_apps = ["frappe", "erpnext", "clm"]

after_install = "pulse_gestor.setup.install.after_install"
after_migrate = "pulse_gestor.setup.install.after_migrate"
before_migrate = "pulse_gestor.print_formats.preserve_accented_legacy_print_formats"

jinja = {"methods": ["pulse_gestor.print_formats.qr_data_uri"]}

doctype_js = {"Asset": "public/js/asset.js"}

doc_events = {"Asset": {"validate": "pulse_gestor.patrimonio.asset.validar_custodiante"}}

add_to_apps_screen = [
	{
		"name": "pulse_gestor",
		"title": "Pulse Gestor",
		"route": "/app/gestor",
	}
]

# Assinatura eletrônica (app assinatura_eletronica, OPCIONAL)
assinatura_eletronica_perfis = {
	"Reuniao de Comissao": "pulse_gestor.assinatura.PerfilReuniaoDeComissao",
	"Asset": "pulse_gestor.assinatura.PerfilTermoDoAtivo",
	"Asset Movement": "pulse_gestor.assinatura.PerfilTermoDeMovimentacao",
}
assinatura_eletronica_destinatarios = {"Comissao Membro": "pulse_gestor.assinatura.destinatario_membro"}

scheduler_events = {
	"daily": [
		"pulse_gestor.tasks.atualizar_status_documentos",
		"pulse_gestor.tasks.enviar_avisos_vencimento_documentos",
	]
}

fixtures = [
	{
		"dt": "Role",
		"filters": [["name", "in", ["Pulse Gestor Manager", "Pulse Gestor Viewer"]]],
	},
	{
		"dt": "Notification",
		"filters": [
			[
				"name",
				"in",
				[
					"Documento da Unidade a Vencer",
					"Documento da Unidade Vencido",
				],
			]
		],
	},
	{
		"dt": "Number Card",
		"filters": [["module", "=", "Documentacao da Unidade"]],
	},
]
