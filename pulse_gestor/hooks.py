app_name = "pulse_gestor"
app_title = "Pulse Gestor"
app_publisher = "Still Pulse"
app_description = "Documentação da Unidade — cadastro de documentos por empresa/unidade com validade e alerta de vencimento"
app_email = "dev@stillpulse.com.br"
app_license = "mit"
app_version = "0.2.3"

required_apps = ["frappe", "erpnext"]

after_install = "pulse_gestor.setup.install.after_install"
after_migrate = "pulse_gestor.setup.install.after_migrate"

add_to_apps_screen = [
	{
		"name": "pulse_gestor",
		"title": "Pulse Gestor",
		"route": "/app/gestor",
	}
]

scheduler_events = {
	"daily": [
		"pulse_gestor.tasks.atualizar_status_documentos",
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
