# ADR-001: Leitura mínima garantida em DocTypes vinculados por Link

## Contexto

DocTypes do `pulse_gestor` referenciam, por campos Link, DocTypes que não pertencem a este app — alguns do
core/ERPNext, outros de apps que o `pulse_gestor` usa como dependência (declarada ou não). Exemplos reais,
levantados nos metadados do app:

- `Documentacao da Unidade` e `Destinatarios Vencimento Documento` → `Company` (`company`).
- `Configuracoes Documentos da Unidade` → `Email Template` (`modelo_email_vencimento`).
- `Reuniao de Comissao`, `Tipo de Comissao`, `Membros de Comissao`, `Mandato de Comissao` → `Company`
  (`empresa`).
- `Comissao Regimento Alteracao` → `User` (`responsavel`).
- `Classificacao de Risco Diaria`, `Unidade Especialidade Vigencia`, `Atendimento Medico Diario`,
  `Unidade Protocolo Vigencia` → `Company` (`unidade`), além de `User` (`lancado_por`).
- O módulo **Patrimônio** não cria DocTypes, mas estende `Asset`, `Asset Movement` e `Location` do ERPNext
  diretamente (ver `README.md`); o custodiante do `Asset` é filtrado por `Employee` da mesma empresa.

Os dois papéis próprios do app (`pulse_gestor/fixtures/role.json`) são `Pulse Gestor Manager` — o papel de
operação do dia a dia, com `create`/`write`/`submit` nos DocTypes do app — e `Pulse Gestor Viewer`, só leitura.
Nenhum dos dois tem permissão própria registrada em fixture sobre `Company`, `User` ou `Email Template`: o
app não declara `Custom DocPerm` nenhum (`pulse_gestor/fixtures/` só tem `role.json`, `notification.json`,
`number_card.json` e `custom_field.json` (os cinco Custom Fields de Patrimônio, sem permissões); `hooks.py` não lista `Custom DocPerm` em `fixtures`). O acesso de hoje depende inteiramente
de permissão concedida por outro módulo (Contabilidade/RH para `Company`, o papel padrão do Frappe para
`User`) — exatamente o padrão que o CLM identificou e corrigiu no
[ADR-006 do `clm`](../../clm/docs/adr-006-leitura-minima-em-doctypes-vinculados.md): se esse outro módulo não
conceder leitura ao usuário, o fluxo do `pulse_gestor` trava no meio — Link vazio ou erro de permissão ao abrir
o registro referenciado — sem indício de que a causa é de outro módulo, não do `pulse_gestor`.

## Decisão

Adotamos aqui o mesmo princípio do CLM: toda vez que um DocType do `pulse_gestor` ganha um campo Link para um
DocType de outro módulo/app (ERPNext, `integracoes_customizadas`, `assinatura_eletronica` ou qualquer outro),
os papéis próprios do app — `Pulse Gestor Manager` e `Pulse Gestor Viewer` — devem ter, no mínimo, permissão de
leitura (`read` ou `select`, o suficiente para o dropdown e para abrir o registro vinculado) sobre o DocType
referenciado, independentemente de qualquer papel de outro módulo já conceder isso. Isso se implementa como
fixture `Custom DocPerm`, registrada em `fixtures` no `hooks.py`, nunca editando o DocType do outro app.

Ao adicionar um campo Link para um DocType fora do `pulse_gestor`, a mudança só está completa quando a fixture
de leitura existir para os dois papéis (ou já existir de uma mudança anterior) — este documento deve ser
atualizado com o novo DocType na lista de exemplos do Contexto.

## Pendência / achado (não corrigido por este documento)

Este ADR é só registro do princípio; nenhuma fixture, permissão ou código foi alterado. Levantamento feito nos
metadados deste repositório (sem acesso ao site/bench para consultar os papéis padrão do Frappe/ERPNext em
tempo de execução):

- Não há hoje nenhuma fixture `Custom DocPerm` no `pulse_gestor` para `Company`, `User` ou `Email Template` em
  favor de `Pulse Gestor Manager`/`Pulse Gestor Viewer`. Falta confirmar, num site rodando, se esses dois
  papéis já conseguem abrir/selecionar `Company`, `User` e `Email Template` por herança de outro papel (ex.:
  `User` costuma ter leitura ampla por padrão do Frappe; `Company` e `Email Template` não necessariamente).
- O módulo Patrimônio depende de `custom_empresa` em `Location`, um Custom Field que agora está versionado em
  `fixtures/custom_field.json` (ver `README.md`); qualquer decisão de leitura mínima sobre `Location` ainda
  não foi avaliada aqui.
- Recomendação: antes ou junto da próxima mudança que toque um desses fluxos, validar no site `dev`
  (`bench --site dev console` ou pela UI, logado como um usuário só com `Pulse Gestor Manager`/`Pulse Gestor
  Viewer`) se os Links acima abrem normalmente; se não abrirem, criar as fixtures `Custom DocPerm`
  correspondentes num commit próprio, seguindo a Decisão acima.

## Consequências

- Nenhum fluxo do `pulse_gestor` deve travar um usuário dos papéis próprios do app por falta de leitura num
  cadastro vinculado de outro módulo: a dependência cruzada deixa de ser implícita e passa a ser explícita e
  garantida pelo próprio app, quando a fixture existir.
- O alcance é só leitura: `write`, `create` e `delete` desses DocTypes externos continuam fora do escopo do
  `pulse_gestor` e seguem governados pelos papéis que já os administram.
- Revisão de PR: toda PR que introduz um campo Link para um DocType externo ao `pulse_gestor` deve checar se a
  fixture de leitura para `Pulse Gestor Manager`/`Pulse Gestor Viewer` já cobre esse DocType; se não, adicionar
  no mesmo commit e atualizar a lista de exemplos deste documento.
