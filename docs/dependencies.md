# Dependencies

Map of the strong and weak dependencies of `pulse_gestor`. Strong dependencies are declared in `required_apps`
(`hooks.py`); weak dependencies are optional and every use is guarded.

## Strong (declared in `required_apps`)

| App | Declared as | Used for |
| --- | --- | --- |
| `frappe` | `frappe/frappe@version-15` | Framework. |
| `erpnext` | `frappe/erpnext@version-15` | `Company` (the "unit"), `Asset`, `Asset Movement`, `Location`, `Employee`-based custodian checks. |
| `clm` | `still-pulse/clm@develop` | Print Formats extend `clm/templates/print/clm_base.html`; the PDF engine only serves the modules in `PDF_ENGINE_MODULES` (`Comissoes` and `Patrimonio` must stay listed); the expiry e-mail uses `clm.clm.services.email_layout` (`tasks.build_expiry_email_body`). Install `clm` before `pulse_gestor`. |

## Weak (not declared, guarded)

| App | Where | Guard | Behavior without the app |
| --- | --- | --- | --- |
| `assinatura_eletronica` | `signature_profiles.py` | `try: import ... except ImportError` | The signature profiles are not defined and no Signature Template is seeded. The profile base class API (Portuguese names such as `conteudo`, `signatarios`) belongs to that app and is not renamed here. |
| `integracoes_customizadas` | `comissoes/doctype/reuniao_de_comissao/reuniao_de_comissao.py` (`send_convocation`) | `"integracoes_customizadas" in frappe.get_installed_apps()` plus DocType existence check, import inside the function | *Convocar membros* answers with an error message. |
| `integracoes_customizadas` | `phone.py` (`normalize_phone`) | `except ImportError` in `_is_valid_number` | Falls back to a digit-count check (10 or 11 digits). |

## Cross-app data coupling

- `Location.custom_empresa` is a Custom Field created on the site (not in this app's fixtures) and used by the asset
  reports. Custom Fields on `Asset` (`custom_número_de_controle_bhcl`, `custom_número_patrimônio_prefeitura`,
  `custom_utilização`, `custom_estado_de_conservação`) are also site-created and do not follow the
  `custom_pulse_gestor_<meaning>` pattern; renaming them is Phase 2 work.
- Link fields to foreign DocTypes and the minimum read access of the app roles: see
  [ADR-001](adr-001-minimum-read-access-on-linked-doctypes.md).

## Rules

- Never import `assinatura_eletronica` or `integracoes_customizadas` at module level without a guard.
- Do not add them to `required_apps` (they are optional for this app).
- When adding a cross-app reference, add it to this document in the same commit.
