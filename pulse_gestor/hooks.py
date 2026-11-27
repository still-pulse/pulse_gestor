app_name = "pulse_gestor"
app_title = "Pulse Gestor"
app_publisher = "StillPulse Tecnologia LTDA"
app_description = "Unit management: unit documentation with expiry alerts, clinical indicators, committees and asset records"
app_email = "dev@stillpulse.com.br"
app_license = "Proprietary"
app_version = "1.0.2"

required_apps = ["frappe/frappe@version-15", "frappe/erpnext@version-15", "still-pulse/clm@develop"]

after_install = "pulse_gestor.setup.install.after_install"
after_migrate = "pulse_gestor.setup.install.after_migrate"
before_migrate = "pulse_gestor.print_formats.preserve_accented_legacy_print_formats"

jinja = {"methods": ["pulse_gestor.print_formats.qr_data_uri"]}

doctype_js = {"Asset": "public/js/asset.js"}

doc_events = {"Asset": {"validate": "pulse_gestor.patrimonio.asset.validate_custodian"}}

add_to_apps_screen = [
	{
		"name": "pulse_gestor",
		"title": "Pulse Gestor",
		"route": "/app/gestor",
	}
]

# E-signature (app assinatura_eletronica, OPTIONAL; the profile API names are defined by that app)
assinatura_eletronica_perfis = {
	"Reuniao de Comissao": "pulse_gestor.signature_profiles.CommitteeMeetingProfile",
	"Asset": "pulse_gestor.signature_profiles.AssetTermProfile",
	"Asset Movement": "pulse_gestor.signature_profiles.AssetMovementTermProfile",
}
assinatura_eletronica_destinatarios = {"Comissao Membro": "pulse_gestor.signature_profiles.member_recipient"}

scheduler_events = {
	"daily": [
		"pulse_gestor.tasks.update_document_statuses",
		"pulse_gestor.tasks.send_expiry_notices",
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
