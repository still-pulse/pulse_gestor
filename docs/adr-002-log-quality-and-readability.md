# ADR-002: Quality and readability of external-integration logs

## Context

In `integracoes_customizadas`, the integration with the DataJud public API (CNJ, the Brazilian National Council of
Justice) started failing with HTTP 403 on every court. The existing Error Log only recorded `"Processo X, tribunal Y:
DataJudError. Dados anteriores preservados."`: no endpoint, method, HTTP status, response body or traceback —
diagnosing the cause required re-reading the source code, not the log. At the same time, each failing case became its
own record per run: with 56 cases failing, there were 56 entries per round, flooding the Error Log and hiding the signal
(what the real error is) in the noise (how many times it repeated). The fix (`DataJud Sync Log` DocType with structured
context and grouping by run/error type, masked API key, circuit breaker) is documented in
[`adr-002-qualidade-e-legibilidade-de-logs.md`](../../integracoes_customizadas/docs/adr-002-qualidade-e-legibilidade-de-logs.md)
and [`datajud-qualidade-de-logs.md`](../../integracoes_customizadas/docs/datajud-qualidade-de-logs.md) of
`integracoes_customizadas`.

`pulse_gestor` has external integrations of its own, albeit smaller: `comissoes/doctype/reuniao_de_comissao/
reuniao_de_comissao.py` calls `integracoes_customizadas.whatsapp.modelos.enviar_modelo` (WhatsApp/e-mail) to summon
committee meeting participants, and `pulse_gestor/tasks.py` uses `frappe.sendmail` for document-expiry notices. The
same log-readability principle applies here, even at a much smaller scale than DataJud.

## Decision

Every integration with an external service (third-party API, webhook, queue) of this app must log enough to diagnose
the cause without re-reading the source code, and without flooding the Error Log:

1. **Structured context, not just the exception message**: endpoint/URL, HTTP method, HTTP status, the truncated
   response body (on the order of ~1,000 characters), the exception type and the traceback.
2. **Never write secrets in clear text**: API key, token, password or the full `Authorization` header never go to the
   log; when it is useful to confirm *which* credential was used, only a masked prefix is recorded.
3. **Classify the error**, instead of just repeating the raw exception — at least authentication/authorization, rate
   limit, not found, unavailability and invalid data, enough to decide the action (change credential vs. wait vs.
   nothing to do).
4. **Group repeated failures of the same run by error type**, with a count and the list of affected items, instead of
   one record per processed item.

This is the same guideline adopted by `integracoes_customizadas` (see its ADR-002, referenced in the Context) and
applies to any external integration of this app, future or existing: when touching an external integration for another
reason, take the opportunity to align its log with this standard.

## Open item / finding (not fixed by this document)

This ADR only records the principle; no code was changed. Survey done on this repository's code:

- `send_convocation` (`comissoes/doctype/reuniao_de_comissao/reuniao_de_comissao.py`; formerly `convocar`) calls
  `enviar_modelo` of `integracoes_customizadas` per participant and, on failure, only stores the first 140 characters
  of the error message in `status_convocacao` (a child-row field, visible only on the meeting screen) — there is no
  `frappe.log_error` nor any other record with HTTP status, response body or exception type; the root cause of a
  sending failure (e.g. channel down, invalid number, expired credential in `integracoes_customizadas`) is not
  diagnosable without reproducing the problem. Since the volume per run is low (participants of one meeting, not a
  batch synchronization), it does not necessarily call for a DocType of its own like `DataJud Sync Log` — but at least a
  `frappe.log_error` with the context of item 1 above is missing, grouped per meeting/run of `send_convocation`
  instead of one log per participant.
- `send_expiry_notices` (`pulse_gestor/tasks.py`; formerly `enviar_avisos_vencimento_documentos`) uses
  `frappe.sendmail`, which already delegates delivery failures to Frappe's native e-mail queue (`Email Queue`); it was
  not evaluated here whether that native queue meets the standard above for template/render failures before sending
  (e.g. `template.get_formatted_email` raising an exception) — that call is not inside its own `try/except` today.
- Recommendation: when changing `send_convocation` for another reason, add `frappe.log_error` with structured context
  (and, if the volume justifies it, grouping by run) in a commit of its own, following the Decision above.

## Consequences

- PR review: a new or changed external integration in this app that only records `frappe.log_error(str(exc))`, or
  records nothing, without HTTP status/body/classification, is not complete.
- This does not require a DocType of its own in every integration — low-failure-volume calls can keep using the native
  Error Log, as long as it carries the structured context of item 1. A DocType of its own (like
  `integracoes_customizadas`'s `DataJud Sync Log`) is only justified when the volume of failures per run calls for
  grouping (item 4) or when a queryable state summary is needed.
