# ADR-001: Guaranteed minimum read access on DocTypes linked by Link fields

## Context

DocTypes of `pulse_gestor` reference, through Link fields, DocTypes that do not belong to this app: some from
core/ERPNext, others from apps that `pulse_gestor` uses as a dependency (declared or not). Real examples, taken from
the app metadata:

- `Documentacao da Unidade` and `Destinatarios Vencimento Documento` → `Company` (`company`).
- `Configuracoes Documentos da Unidade` → `Email Template` (`modelo_email_vencimento`).
- `Reuniao de Comissao`, `Tipo de Comissao`, `Membros de Comissao`, `Mandato de Comissao` → `Company`
  (`empresa`).
- `Comissao Regimento Alteracao` → `User` (`responsavel`).
- `Classificacao de Risco Diaria`, `Unidade Especialidade Vigencia`, `Atendimento Medico Diario`,
  `Unidade Protocolo Vigencia` → `Company` (`unidade`), plus `User` (`lancado_por`).
- The **Patrimonio** (assets) module creates no DocTypes, but extends ERPNext's `Asset`, `Asset Movement` and
  `Location` directly (see `README.md`); the custodian of the `Asset` is filtered by `Employee` of the same company.

The app's two own roles (`pulse_gestor/fixtures/role.json`) are `Pulse Gestor Manager` — the day-to-day operation
role, with `create`/`write`/`submit` on the app's DocTypes — and `Pulse Gestor Viewer`, read-only. Neither has its own
permission registered in a fixture on `Company`, `User` or `Email Template`: the app declares no `Custom DocPerm` at
all (`pulse_gestor/fixtures/` only has `role.json`, `notification.json` and `number_card.json`; `hooks.py` does not
list `Custom DocPerm` in `fixtures`). Today's access depends entirely on permission granted by another module
(Accounting/HR for `Company`, the default Frappe role for `User`) — exactly the pattern CLM identified and fixed in
[ADR-006 of `clm`](../../clm/docs/adr-006-minimum-read-access-on-linked-doctypes.md): if that other module does not
grant the user read access, the `pulse_gestor` flow stalls halfway — empty Link or permission error when opening the
referenced record — with no hint that the cause lies in another module, not in `pulse_gestor`.

## Decision

We adopt the same principle as CLM: whenever a `pulse_gestor` DocType gets a Link field to a DocType of another
module/app (ERPNext, `integracoes_customizadas`, `assinatura_eletronica` or any other), the app's own roles —
`Pulse Gestor Manager` and `Pulse Gestor Viewer` — must have at least read permission (`read` or `select`, enough for
the dropdown and for opening the linked record) on the referenced DocType, regardless of whether any role from
another module already grants it. This is implemented as a `Custom DocPerm` fixture, registered in `fixtures` in
`hooks.py`, never by editing the other app's DocType.

When adding a Link field to a DocType outside `pulse_gestor`, the change is only complete once the read fixture exists
for both roles (or already exists from a previous change) — this document must be updated with the new DocType in the
list of examples in the Context.

## Open item / finding (not fixed by this document)

This ADR only records the principle; no fixture, permission or code was changed. Survey done on this repository's
metadata (without access to the site/bench to query the default Frappe/ERPNext roles at runtime):

- There is currently no `Custom DocPerm` fixture in `pulse_gestor` for `Company`, `User` or `Email Template` in favor
  of `Pulse Gestor Manager`/`Pulse Gestor Viewer`. It remains to be confirmed, on a running site, whether these two
  roles can already open/select `Company`, `User` and `Email Template` by inheritance from another role (e.g. `User`
  usually has broad read by Frappe default; `Company` and `Email Template` do not necessarily).
- The Patrimonio module depends on `custom_empresa` on `Location`, a Custom Field created directly on the site and
  outside the app's fixtures (see `README.md`); any minimum-read decision about `Location` also goes through that
  peculiarity and was not evaluated here.
- Recommendation: before or together with the next change that touches one of these flows, validate on the `dev` site
  (`bench --site dev console` or the UI, logged in as a user with only `Pulse Gestor Manager`/`Pulse Gestor Viewer`)
  whether the Links above open normally; if they do not, create the corresponding `Custom DocPerm` fixtures in a
  commit of their own, following the Decision above.

## Consequences

- No `pulse_gestor` flow should block a user of the app's own roles for lack of read access to a linked record of
  another module: the cross-dependency stops being implicit and becomes explicit and guaranteed by the app itself, once
  the fixture exists.
- The scope is read-only: `write`, `create` and `delete` on these external DocTypes remain outside the scope of
  `pulse_gestor` and stay governed by the roles that already administer them.
- PR review: every PR that introduces a Link field to a DocType external to `pulse_gestor` must check whether the read
  fixture for `Pulse Gestor Manager`/`Pulse Gestor Viewer` already covers that DocType; if not, add it in the same
  commit and update the list of examples in this document.
