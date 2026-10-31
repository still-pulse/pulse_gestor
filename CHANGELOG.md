# Histórico de alterações

Reconstruído a partir de `git tag` e `git log` (somente leitura) e conferido com os arquivos do app. Limites do que o
git permite:

- **Início do histórico:** o primeiro commit é de 2026-08-17 (v0.1.0). O repositório tem **duas raízes**: a do ramo
  antigo (`e1d6111`) e a do commit `2fa98f2` ("Merge pull request #3", 2026-09-28, sem pai), um instantâneo que
  recriou a `main`. A linha do instantâneo (`f17bb23` em diante) só se uniu ao ramo antigo (v0.10.0) pelo merge
  `f515085` (v0.10.2). Por isso `git merge-base` entre as duas linhas não existe.
- **Tags fora do histórico:** nenhuma. Todas as tags estão contidas no HEAD (`git tag --no-merged HEAD` vazio). A v0.10.0
  está no ramo antigo, anterior ao merge.
- **Tags fora de ordem:** a v0.1.5 (2026-09-21) foi criada depois da v0.2.9, em outra linha de trabalho
  (Documentação da Unidade). A v0.9.2 aponta para o mesmo commit da v0.9.1.
- **Versões sem tag:** v0.2.4 e v0.2.5 (a numeração salta da v0.2.3 para a v0.2.6); suas entradas vêm do texto do
  CHANGELOG antigo, entregue no commit da v0.2.6. Commits sem tag ficam na entrada da primeira tag seguinte.
- **Datas:** as das tags (ou do commit, quando a tag é leve). As entradas já existentes no CHANGELOG anterior foram
  mantidas, com o cabeçalho trocado do formato antigo (`## [data] — versão`) para o atual; as da v0.1.5, v0.2.8,
  v0.2.9, v0.9.2, v0.9.4 e v0.9.5, que faltavam, foram acrescentadas só pelo assunto e pelo diff dos commits.
- **Incoerências de numeração:**
  - `__version__` (em `pulse_gestor/__init__.py`) diverge de `app_version` (em `hooks.py`) em quatro tags: v0.1.5
    (0.1.4), v0.9.4 e v0.9.5 (0.9.3) e v0.10.1 (0.9.3, `chore: versão 0.10.1` só mexeu no `hooks.py`). A v0.10.2 e a
    v0.11.0 trazem as duas iguais à tag. Na linha v0.11: v0.11.1 e v0.11.2 (ambas 0.10.0); v0.11.3 (`__version__` 0.11.3, hooks
    0.10.0); v0.11.4 a v0.11.6 (`__version__` igual à tag, hooks 0.11.0). Só a v0.11.7 alinha as duas.
  - Os patches usam o prefixo `vX_Y_Z_` apenas em parte (`v0_2_6_*`, `v0_4_0_*`, `v0_9_0_*`, `v0_9_2_*`; o
    `rename_configuracoes_documentos_da_unidade` não tem versão), **não acompanham a versão do app** e não foram
    renumerados.
  - Não há patches da linha v0.10 e v0.11: os ajustes de Workspace, formatos de impressão e Modelos são feitos no
    `after_migrate` (`setup/install.py`).
- Não há tags `rc/*` neste repositório.

## v0.11.7 — alinhamento de versão · 2026-10-29

Merge `d02b9d8` de `feature/configuracoes-documentos-unidade` em `main`, com o commit `d63d20f`: `app_version` dos hooks
alinhado a `__version__` (0.11.7) após o merge da feature de configurações de documentos da unidade.

## v0.11.6 — ferramentas de checagem do Frappe · 2026-10-28

Commit `e2d1488`: commitlint, linter e CI (`ci: ferramentas de checagem do Frappe`). Sem mudança funcional.

## v0.11.5 — merge dos indicadores e do aviso de vencimento · 2026-10-28

Commit `3d6d5dd` ("merge das features de indicadores e aviso de vencimento em main"), que segue o merge `9f090ea` de
`feature/indicadores-protocolos-triagem` e o commit `c90856d` (teste do aviso de vencimento ajustado ao layout
institucional do e-mail).

## v0.11.4 — `__version__` e versão do aviso de vencimento · 2026-10-28

Commit `2f0eac8` ("alinha `__version__` com a tag v0.11.3 e versiona o aviso de vencimento por e-mail"), precedido de
`1591510` ("app_version 0.1.5 no hooks da Documentação da Unidade"), e merge `876224c` do ramo
`feature/bump-versao-0-11-4`.

## v0.11.3 — aviso de vencimento por e-mail no layout do clm · 2026-10-28

Commit `3b2a354` ("alinha `__version__` com a tag v0.11.2"). A faixa inclui os commits `5e02f94` e `4d9e2e7`
(2026-10-24, "aviso de vencimento por e-mail no layout institucional do clm"): mudança em `tasks.py` e teste novo
`tests/test_email_vencimento.py`.

## v0.11.2 — limpa o cache do Desk ao injetar o card · 2026-10-20

Commit `93da1d4`: `setup/settings_workspace.py` limpa o cache do Desk ao injetar o card no ERPNext Settings.

## v0.11.1 — atalho das configurações de documentos no ERPNext Settings · 2026-10-20

Commit `ab6823d`: novo `setup/settings_workspace.py` e chamada em `setup/install.py` para o atalho das configurações
de documentos no ERPNext Settings.

## v0.11.0 — Relatórios de Patrimônio e Termo de Responsabilidade · 2026-10-17

### Adicionado
- Relatórios "Relação de Ativos" e "Ativos por Localização" (Script Reports do módulo Patrimonio, card "Relatórios de Patrimônio" no Workspace Gestor). Filtros por empresa e por localização vinculada à empresa (`Location.custom_empresa`), incluindo sublocais, além de categoria, situação, utilização e estado de conservação. O relatório por localização agrupa os bens em árvore, com quantidade, valores e gráfico das localizações com mais bens
- "Termo de Responsabilidade do Ativo" (Asset, assinado pelo custodiante na custódia inicial) e "Termo de Responsabilidade de Movimentacao" (Asset Movement, assinado por cada colaborador em "Para Funcionário", que vê só os seus bens), no padrão BHCL e com o registro das evidências da assinatura
- Perfis `PerfilTermoDoAtivo` e `PerfilTermoDeMovimentacao` no motor `assinatura_eletronica` e Modelos de Assinatura semeados para Asset e Asset Movement (paralelo, após o submit, aceite eletrônico, comprovante no formato do Termo). O recebimento automático (Receipt) é recusado na movimentação: a custódia inicial se assina no próprio Ativo
- Custodiante do Ativo filtrado por colaboradores ativos da empresa do bem, com validação no servidor

### Alterado
- A "Data do termo" do Termo do Ativo e a data de emissão usam a data de criação do Ativo
- `registro_assinaturas` usa o próprio rótulo de data no cartão do processo encerrado (era fixo em "Data da reunião")
- `ensure_modelo_assinatura` virou `ensure_modelos_assinatura`, com os modelos em `MODELOS`

## v0.10.2 — Integração da linha v0.10.0 à main · 2026-10-16

### Alterado
- Integra a linha v0.10.0 (módulo Patrimonio e formatos de impressão) à `main`, que havia sido recriada a partir de um snapshot sem histórico em comum. Ata e Convocação ficam com as macros da v0.10.0 (`commission_name`, `meeting_card`, `agenda_card`, `participants_card`), acrescidas do registro da assinatura eletrônica da ata (`registro_assinaturas`: evidências quando há Processo de Assinatura encerrado; caso contrário, o cartão padrão com a data da reunião)

## v0.10.1 — Print Formats de Comissões no padrão BHCL · 2026-10-16

### Alterado
- `Ata de Reuniao de Comissao` e `Convocacao para Reuniao de Comissao` passam a estender `clm_base.html` (manifesto `apps/clm/docs/brand-manifesto.md`): cartões, tabelas com cabeçalho `teal_dark`, selos de presença, referência "Comissão · Reunião de dd/mm/aaaa" e rodapé com ID
- Assinatura da ata: com Processo de Assinatura encerrado, imprime o registro das evidências (OTP, IP, localização, integridade e QR); caso contrário, o cartão padrão `signature_block` com a caixa "Data da reunião". A convocação usa o cartão padrão com a "Data da convocação"
- Macros próprias em `templates/print/comissoes_macros.html`; pastas dos formatos renomeadas para `scrub(nome)` (exigência do Frappe)
- `required_apps` inclui `clm`

### Adicionado (mesmo commit, f17bb23)
- Ata assinável: perfil `PerfilReuniaoDeComissao` no motor `assinatura_eletronica` (assinam os participantes presentes) e `Comissao Membro` como destinatário; Modelo de Assinatura semeado no `after_migrate`. Dependência opcional: `assinatura.py` importa o app dentro de `try`
- Convocação dos participantes pelo botão *Convocar membros* da Reuniao de Comissao (WhatsApp, e-mail ou ambos, com Modelo WhatsApp semeado), via `integracoes_customizadas`; `telefone.py` aplica máscara e valida os telefones das linhas de membros e participantes

### Alterado (mesmo commit, f17bb23): tudo no Workspace Gestor
- Os Workspaces Indicadores, Comissoes, Documentacao da Unidade e Pulse Gestor foram removidos; seus cards (Documentação da Unidade, Triagem, Atendimentos, Relatórios de Indicadores, Comissões, Configurações de Comissões, Relatórios de Comissões) e o painel de gestão agora ficam no Workspace Gestor
- Links do app versionados em `setup/gestor_links.json`; `ensure_pulse_gestor_workspace` (after_migrate) os aplica ao Gestor sem alterar o restante do conteúdo e apaga os Workspaces antigos

## v0.10.0 — Patrimônio e formatos de impressão no padrão BHCL · 2026-10-14

> Tag fora da linha da `main` até a v0.10.2: o commit pertence ao ramo antigo, que só foi unido à `main` pelo merge `f515085`.

### Adicionado
- Módulo Patrimonio com Print Formats no padrão institucional BHCL (`clm_base.html`, motor WeasyPrint): "Ficha do Ativo Imobilizado" (Asset) e "Ficha de Movimentacao de Ativos" (Asset Movement), definidos como padrão dos DocTypes via Property Setter no after_migrate; QR Code do registro gerado localmente (método Jinja `qr_data_uri`), sem serviço externo
- Testes de padrão e de render dos Print Formats (`tests/test_print_formats.py`)

### Alterado
- "Ata de Reuniao de Comissao" e "Convocacao para Reuniao de Comissao" reescritos sobre `clm_base.html` e as macros do CLM (cabeçalho, rodapé, cartões, tabelas, selos de presença e cartão de assinatura padrão); a Ata passa a ser o formato padrão de Reuniao de Comissao
- O app passa a exigir o `clm` (`required_apps`), que fornece a base de impressão e o motor de PDF (clm v0.1.95 ou superior)
- As fichas antigas de ativos, que existiam só no banco ("Ficha de Ativo Imobilizado" e "Ficha de Movimentação de Ativos"), são desabilitadas sem ser apagadas; a acentuada é renomeada para "Ficha de Movimentacao de Ativos (antiga)" no before_migrate, porque a collation do banco a confundiria com o novo formato

## v0.9.5 — Reescrita do README · 2026-10-13

### Alterado
- Só documentação: `README.md` reescrito (commit `ec05776`). `__version__` continuou em 0.9.3.

## v0.9.4 — Faixas de versão em `pyproject.toml` · 2026-10-08

### Alterado
- `[tool.bench.frappe-dependencies]` limita `frappe` e `erpnext` a `>=15.0.0,<16.0.0` e o `pyproject.toml` ganha comentários sobre as dependências gerenciadas pelo bench (commit `dd071d3`; tag leve, sem anotação). `__version__` continuou em 0.9.3.

## v0.9.3 — Relatório de atendimentos renomeado · 2026-09-28

### Alterado
- Relatório "Atendimentos Medicos por Periodo" renomeado para "Relatorio de Atendimentos por Periodo" (título "Relatório de Atendimentos por Período" via pt-BR.csv); o registro antigo é removido por patch
- Workspace Indicadores ganha o card "Relatórios", com a Apuração de Classificação de Risco e o Relatório de Atendimentos por Período, que saem dos cards Triagem e Atendimentos (ajuste idempotente no after_migrate)

### Corrigido
- Classificacao de Risco Diaria: `atualizar_total` usava a variável inexistente `line`, gerando ReferenceError ao editar uma quantidade

## v0.9.2 · 2026-09-28

A tag aponta para o mesmo commit da v0.9.1 (`ef699ce`, `__version__` 0.9.1); não traz alteração própria. O patch `v0_9_2_renomeia_relatorio_de_atendimentos` saiu junto da v0.9.3.

## v0.9.1 — Grade de especialidades alinhada · 2026-09-28

### Corrigido
- Grade de especialidades do Atendimento Medico Diario desalinhada em relação ao cabeçalho: a célula final de ação da linha agora é mantida vazia, como nas demais grades de Indicadores

## v0.9.0 — Atendimento médico diário por vigência · 2026-09-28

### Adicionado
- Relatório "Atendimentos Medicos por Periodo": atendimentos enviados por especialidade em um período, com percentual, dias com atendimento, média por dia lançado, resumo e gráfico; link no card Atendimentos do workspace Indicadores

### Alterado
- "Atendimento Diario" (e sua tabela filha) renomeado para "Atendimento Medico Diario" por patch pré-sincronização
- A vigência de especialidades passa a mapear as especialidades atendidas pela unidade em um período, como a vigência do protocolo de triagem: o campo Setor saiu da vigência e do atendimento, e a busca e a unicidade do lançamento usam apenas unidade e data

### Removido
- Definição de metas por especialidade (quantidade e periodicidade) na vigência e no atendimento; as colunas antigas, inclusive Setor, são removidas do banco no migrate

## v0.8.1 — Painel de Comissões sem gráficos · 2026-09-28

### Removido
- Gráficos "Reuniões por mês", "Mandatos por status" e "Reuniões por unidade" do painel de Comissões (removidos também do banco no migrate)

## v0.8.0 — Painel de gestão de Comissões · 2026-09-28

### Adicionado
- Painel de gestão no topo do workspace Comissoes: cartões (reuniões nos próximos 7 dias, mandatos a vencer em 60 dias, comissões sem reunião há mais de 90 dias, mandatos vigentes, reuniões no mês e presença média dos últimos 90 dias) e dois blocos: "Próximas reuniões" e "Comissões que exigem atenção"
- Number Cards e Dashboard Charts standard em comissoes/number_card e comissoes/dashboard_chart; dados calculados em comissoes/dashboard.py
- Custom HTML Blocks criados/atualizados de forma idempotente no after_migrate (fonte em comissoes/custom_blocks)

## v0.7.0 — Data, hora e local da reunião · 2026-09-28

### Adicionado
- Campo "Local da reunião" na Reuniao de Comissao

### Alterado
- "Data da reunião" passa a "Data e hora da reunião" (Datetime); reuniões já cadastradas ficam com 00:00
- Convocação e ata imprimem horário e local (o horário é omitido quando 00:00)
- Relatório "Atividades de Comissão" mostra data e hora e o local, e o filtro de período considera o dia inteiro da data final

## v0.6.0 — Convocação e ata de reunião · 2026-09-28

### Adicionado
- Formatos de impressão da Reuniao de Comissao: "Convocacao para Reuniao de Comissao" (data, horário e local para preencher, pauta e convocados) e "Ata de Reuniao de Comissao" (participantes com presença, pauta, deliberações, encaminhamentos e assinaturas dos presentes)

## v0.5.1 — Nomes amigáveis no relatório de Comissões · 2026-09-28

### Alterado
- Relatório "Atividades de Comissão" mostra o nome da categoria, o nome da comissão e o mandato (início e status) no lugar dos IDs
- Com a pauta incluída, os dados da reunião aparecem só na primeira linha; os demais itens mostram apenas o assunto

## v0.5.0 — Relatório Atividades de Comissão · 2026-09-28

### Adicionado
- Relatório "Atividades de Comissão" (Comissoes): reuniões por período, com filtros de empresa e comissão, presentes/participantes por reunião e opção de incluir a pauta (uma linha por item)
- Card "Relatórios" no workspace Comissoes

## v0.4.0 — Categoria, empresa e regimento da comissão · 2026-09-28

### Adicionado
- Categoria de Comissao (Conselho, Comitê, Núcleo, Grupo de Trabalho etc.), vinculada ao Tipo de Comissao
- Texto do regimento no Tipo de Comissao, com histórico de alterações (versão, data, responsável, motivo e texto anterior); o motivo é obrigatório ao alterar um regimento já salvo

### Alterado
- A empresa passa a ser cadastrada no Tipo de Comissao; o Mandato de Comissao a recebe do tipo, somente leitura
- Categoria e Tipo de Comissao nomeados por ID (CATCOM-/TPCOM-), exibindo o nome amigável nos campos de vínculo; a unicidade do tipo passa a ser por nome e empresa
- Migração copia a empresa dos mandatos para o tipo quando a origem é única

## v0.3.0 — Módulo Comissões · 2026-09-28

### Adicionado
- Módulo Comissões como subworkspace de Gestor: Tipo de Comissao, Mandato de Comissao, Membros de Comissao e Reuniao de Comissao (pauta, participantes com presença, deliberações e encaminhamentos)
- Cópia dos membros da comissão para a lista de participantes da reunião
- Tradução pt-BR do título do workspace, mantendo a rota em ASCII

### Alterado (commits sem tag desde a v0.2.9)
- Workspace Indicadores organizado como subworkspace de Gestor (commit `0c086f7`)

## v0.1.5 — Configurações Documentos da Unidade · 2026-09-21

> Tag fora da ordem numérica (criada depois da v0.2.9), no commit `e8c70c6`; `app_version` do `hooks.py` é 0.1.5, mas `__version__` continuou em 0.1.4.

### Adicionado
- DocType único `Configuracoes Documentos da Unidade` (renomeado de `Configuracoes Pulse Gestor` pelo patch `rename_configuracoes_documentos_da_unidade`) com dias de alerta, modelo de e-mail e tabela filha `Destinatarios Vencimento Documento` (e-mails por empresa)
- Validação: dias de alerta não negativos, empresa sem repetição, e-mails válidos e modelo obrigatório quando há destinatários

## v0.2.9 — Gráfico por nível na apuração de risco · 2026-09-21

### Adicionado
- O relatório de apuração da classificação de risco passa a devolver um gráfico (rosca) por nível

## v0.2.8 — Especialidades e atendimentos diários · 2026-09-18

### Adicionado
- DocTypes `Especialidade`, `Unidade Especialidade Vigencia` (e a tabela filha de vigência), `Atendimento Diario` e `Atendimento Diario Especialidade` (renomeado para Atendimento Medico Diario na v0.9.0), com testes e seção no README
- Nesta versão a vigência e o lançamento ainda tinham setor e metas por especialidade, removidos na v0.9.0

## v0.2.7 — Apuração da classificação de risco · 2026-09-18

### Adicionado
- Relatório de apuração da classificação de risco por unidade e período, com escalas separadas por protocolo e tempo-alvo
- Card com o total de pacientes classificados no período

### Alterado
- Tempo máximo de espera preservado nas linhas diárias; migração preenche os lançamentos anteriores com o valor disponível no protocolo

### Corrigido
- Identificador e rota do relatório em ASCII, com atualização do link no Workspace e migração do nome legado

## v0.2.6 — DocTypes de indicadores sem acentos · 2026-09-18

### Alterado
- Nomes dos DocTypes de indicadores sem acentos
- Classificação diária registra apenas a quantidade classificada por nível
- Níveis do protocolo mantêm cor e tempo máximo de espera

## v0.2.5 — Edição direta nos grids de indicadores · 2026-09-18

> Sem tag e sem commit próprio: o texto entrou junto do commit da v0.2.6 (`67ecb49`).

### Alterado
- Edição direta dos níveis no protocolo e das quantidades na classificação diária, sem abrir a linha sobreposta
- Destaque das linhas pela cor do protocolo, com fundo suave e faixa lateral
- Cor dos níveis preservada nos lançamentos diários e preenchida nos registros anteriores durante a migração
- Alinhamento das linhas com o cabeçalho do grid ao ocultar a ação de expansão

## v0.2.4 — Lançamento diário da classificação de risco · 2026-09-18

> Sem tag e sem commit próprio: o texto entrou junto do commit da v0.2.6 (`67ecb49`).

### Adicionado
- Lançamento diário da classificação de risco, com protocolo e níveis preenchidos pela vigência da unidade
- Total calculado, validação das quantidades e envio que bloqueia a edição
- Link para o lançamento no quadro **Triagem** do Workspace **Indicadores**

### Corrigido
- Compatibilidade de leitura e gravação dos DocTypes de indicadores no Query Builder deste bench
- Ordenação da consulta de sobreposição de vigências

## v0.2.3 — Quadro de links de Triagem · 2026-09-18

### Adicionado
- Quadro de links para os cadastros de triagem no Workspace **Indicadores**
- Sincronização idempotente do quadro em Workspaces já instalados
- Memória das convenções do app em `AGENTS.md`

## v0.2.2 — Ordenação da lista de vigências · 2026-09-18

### Corrigido
- Listagem de vigências por unidade com ordenação compatível com o validador SQL do Frappe 15

## v0.2.1 — Visibilidade do Workspace Indicadores · 2026-09-18

### Corrigido
- Visibilidade do Workspace **Indicadores** após instalação ou migração
- Permissões completas de `System Manager` e `Administrator` nos cadastros de indicadores
- Acesso explícito desses papéis ao Workspace **Indicadores**

## v0.2.0 — Indicadores e protocolos de triagem · 2026-09-18

### Adicionado
- Workspace **Indicadores** com protocolos de triagem e vigências por unidade
- Níveis configuráveis com cor e tempo máximo de espera
- Validação de períodos sobrepostos para cada unidade (`Company`)

## v0.1.4 — Card da Documentação da Unidade separado · 2026-08-17

### Corrigido
- Links da documentação saem do card Patrimônio e vão para o card **Documentação da Unidade**

## v0.1.3 — Card na seção Módulos · 2026-08-17

### Alterado
- Card **Documentação da Unidade** na seção Módulos do Workspace Gestor

## v0.1.2 — Atalhos no Workspace Gestor · 2026-08-17

### Alterado
- Atalhos da Documentação da Unidade passam a ficar no Workspace **Gestor**
- Workspace Pulse Gestor oculto no menu lateral

## v0.1.1 — Correção do nome do Workspace · 2026-08-17

### Corrigido
- Workspace deixou de usar o mesmo nome do DocType (o botão Novo abria um Espaço de Trabalho)

## v0.1.0 — Documentação da Unidade · 2026-08-17

### Adicionado

- App `pulse_gestor` com o módulo Documentação da Unidade
- DocType `Tipo de Documento da Unidade` para cadastro dos tipos de PDF
- DocType `Documentacao da Unidade` vinculado à unidade (`Company`)
- Vigência opcional, anexo PDF e badge de status (Válido / Vencido / Sem validade)
- Notificação de vencimento próximo e no dia do vencimento
- Job diário para atualizar o status
- Workspace e papéis Pulse Gestor Manager / Viewer
