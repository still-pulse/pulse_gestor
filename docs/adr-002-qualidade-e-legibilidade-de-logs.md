# ADR-002: Qualidade e legibilidade de logs de integração externa

## Contexto

Em `integracoes_customizadas`, a integração com a API Pública do DataJud (CNJ) passou a falhar com HTTP 403 em
todos os tribunais. O Error Log existente só gravava `"Processo X, tribunal Y: DataJudError. Dados anteriores
preservados."`: sem endpoint, método, status HTTP, corpo da resposta ou traceback — diagnosticar a causa exigiu
reler o código-fonte, não o log. Ao mesmo tempo, cada processo falhando virava um registro próprio por execução:
com 56 processos falhando, eram 56 entradas por rodada, inundando o Error Log e escondendo o sinal (qual é o erro
real) no ruído (quantas vezes ele se repetiu). A correção (DocType `DataJud Sync Log` com contexto estruturado e
agrupamento por execução/tipo de erro, chave de API mascarada, circuit breaker) está documentada em
[`adr-002-qualidade-e-legibilidade-de-logs.md`](../../integracoes_customizadas/docs/adr-002-qualidade-e-legibilidade-de-logs.md)
e [`datajud-qualidade-de-logs.md`](../../integracoes_customizadas/docs/datajud-qualidade-de-logs.md) do
`integracoes_customizadas`.

O `pulse_gestor` tem integrações externas próprias, ainda que menores: `comissoes/doctype/reuniao_de_comissao/
reuniao_de_comissao.py` chama `integracoes_customizadas.whatsapp.modelos.enviar_modelo` (WhatsApp/e-mail) para
convocar participantes de reunião de comissão, e `pulse_gestor/tasks.py` usa `frappe.sendmail` para avisos de
vencimento de documento. O mesmo princípio de legibilidade de log vale aqui, mesmo em escala bem menor que o
DataJud.

## Decisão

Toda integração com um serviço externo (API de terceiro, webhook, fila) deste app deve logar o suficiente para
diagnosticar a causa sem precisar reler o código-fonte, e sem inundar o Error Log:

1. **Contexto estruturado, não só a mensagem da exceção**: endpoint/URL, método HTTP, status HTTP, o corpo da
   resposta truncado (ordem de ~1.000 caracteres), o tipo da exceção e o traceback.
2. **Nunca gravar segredo em claro**: chave de API, token, senha ou header `Authorization` completo nunca vão
   para o log; quando é útil confirmar *qual* credencial foi usada, grava-se só um prefixo mascarado.
3. **Classificar o erro**, não só repetir a exceção crua — pelo menos autenticação/autorização, limite de
   requisições, não encontrado, indisponibilidade e dados inválidos, o suficiente para decidir a ação (trocar
   credencial vs. esperar vs. nada a fazer).
4. **Agrupar falhas repetidas da mesma execução por tipo de erro**, com contagem e a lista dos itens afetados,
   em vez de um registro por item processado.

Esta é a mesma diretriz adotada pelo `integracoes_customizadas` (ver seu ADR-002, referenciado no Contexto) e
vale para qualquer integração externa, futura ou existente, deste app: ao tocar numa integração externa por
outro motivo, aproveite para alinhar o log dela a este padrão.

## Pendência / achado (não corrigido por este documento)

Este ADR é só registro do princípio; nenhum código foi alterado. Levantamento feito no código deste repositório:

- `convocar` (`comissoes/doctype/reuniao_de_comissao/reuniao_de_comissao.py`) chama `enviar_modelo` do
  `integracoes_customizadas` por participante e, em caso de falha, só grava os primeiros 140 caracteres da
  mensagem de erro em `status_convocacao` (campo da linha filha, visível só na tela da reunião) — não há
  `frappe.log_error` nem nenhum outro registro com status HTTP, corpo da resposta ou tipo de exceção; a causa
  raiz de uma falha de envio (ex.: canal fora do ar, número inválido, credencial expirada no
  `integracoes_customizadas`) não fica diagnosticável sem reproduzir o problema. Como o volume por execução é
  baixo (participantes de uma reunião, não uma sincronização em lote), não necessariamente pede um DocType
  próprio como o `DataJud Sync Log` — mas falta pelo menos um `frappe.log_error` com o contexto do item 1 acima,
  agrupado por reunião/execução de `convocar` em vez de um log por participante.
- `enviar_avisos_vencimento_documentos` (`pulse_gestor/tasks.py`) usa `frappe.sendmail`, que já delega falhas de
  entrega à fila nativa de e-mail do Frappe (`Email Queue`); não foi avaliado aqui se essa fila nativa atende ao
  padrão acima para o caso de falha de template/render antes do envio (ex.: `template.get_formatted_email`
  lançando exceção) — essa chamada não está dentro de um `try/except` próprio hoje.
- Recomendação: ao alterar `convocar` por outro motivo, acrescentar `frappe.log_error` com contexto estruturado
  (e, se o volume justificar, agrupamento por execução) num commit próprio, seguindo a Decisão acima.

## Consequências

- Revisão de PR: uma integração externa nova ou alterada neste app que só grava `frappe.log_error(str(exc))`,
  ou não grava nada, sem status HTTP/corpo/classificação, não está completa.
- Isso não exige um DocType próprio em toda integração — chamadas de baixo volume de falha continuam podendo
  usar o Error Log nativo, desde que com o contexto estruturado do item 1. Um DocType próprio (como o
  `DataJud Sync Log` do `integracoes_customizadas`) só se justifica quando o volume de falhas por execução pede
  agrupamento (item 4) ou quando um resumo de estado consultável é necessário.
