# Changelog

## [2026-10-17] — v0.11.0 — Relatórios de Patrimônio e Termo de Responsabilidade

### Adicionado
- Relatórios "Relação de Ativos" e "Ativos por Localização" (Script Reports do módulo Patrimonio, card "Relatórios de Patrimônio" no Workspace Gestor). Filtros por empresa e por localização vinculada à empresa (`Location.custom_empresa`), incluindo sublocais, além de categoria, situação, utilização e estado de conservação. O relatório por localização agrupa os bens em árvore, com quantidade, valores e gráfico das localizações com mais bens
- "Termo de Responsabilidade do Ativo" (Asset, assinado pelo custodiante na custódia inicial) e "Termo de Responsabilidade de Movimentacao" (Asset Movement, assinado por cada colaborador em "Para Funcionário", que vê só os seus bens), no padrão BHCL e com o registro das evidências da assinatura
- Perfis `PerfilTermoDoAtivo` e `PerfilTermoDeMovimentacao` no motor `assinatura_eletronica` e Modelos de Assinatura semeados para Asset e Asset Movement (paralelo, após o submit, aceite eletrônico, comprovante no formato do Termo). O recebimento automático (Receipt) é recusado na movimentação: a custódia inicial se assina no próprio Ativo
- Custodiante do Ativo filtrado por colaboradores ativos da empresa do bem, com validação no servidor

### Alterado
- A "Data do termo" do Termo do Ativo e a data de emissão usam a data de criação do Ativo
- `registro_assinaturas` usa o próprio rótulo de data no cartão do processo encerrado (era fixo em "Data da reunião")
- `ensure_modelo_assinatura` virou `ensure_modelos_assinatura`, com os modelos em `MODELOS`

## [2026-10-16] — v0.10.2

### Alterado
- Integra a linha v0.10.0 (módulo Patrimonio e formatos de impressão) à `main`, que havia sido recriada a partir de um snapshot sem histórico em comum. Ata e Convocação ficam com as macros da v0.10.0 (`commission_name`, `meeting_card`, `agenda_card`, `participants_card`), acrescidas do registro da assinatura eletrônica da ata (`registro_assinaturas`: evidências quando há Processo de Assinatura encerrado; caso contrário, o cartão padrão com a data da reunião)

## [2026-10-16] — v0.10.1 — Print Formats de Comissões no padrão BHCL

### Alterado
- `Ata de Reuniao de Comissao` e `Convocacao para Reuniao de Comissao` passam a estender `clm_base.html` (manifesto `apps/clm/docs/brand-manifesto.md`): cartões, tabelas com cabeçalho `teal_dark`, selos de presença, referência "Comissão · Reunião de dd/mm/aaaa" e rodapé com ID
- Assinatura da ata: com Processo de Assinatura encerrado, imprime o registro das evidências (OTP, IP, localização, integridade e QR); caso contrário, o cartão padrão `signature_block` com a caixa "Data da reunião". A convocação usa o cartão padrão com a "Data da convocação"
- Macros próprias em `templates/print/comissoes_macros.html`; pastas dos formatos renomeadas para `scrub(nome)` (exigência do Frappe)
- `required_apps` inclui `clm`

## [2026-10-16] — Tudo no Workspace Gestor

### Alterado
- Os Workspaces Indicadores, Comissoes, Documentacao da Unidade e Pulse Gestor foram removidos; seus cards (Documentação da Unidade, Triagem, Atendimentos, Relatórios de Indicadores, Comissões, Configurações de Comissões, Relatórios de Comissões) e o painel de gestão agora ficam no Workspace Gestor
- Links do app versionados em `setup/gestor_links.json`; `ensure_pulse_gestor_workspace` (after_migrate) os aplica ao Gestor sem alterar o restante do conteúdo e apaga os Workspaces antigos

## [2026-10-14] — v0.10.0

### Adicionado
- Módulo Patrimonio com Print Formats no padrão institucional BHCL (`clm_base.html`, motor WeasyPrint): "Ficha do Ativo Imobilizado" (Asset) e "Ficha de Movimentacao de Ativos" (Asset Movement), definidos como padrão dos DocTypes via Property Setter no after_migrate; QR Code do registro gerado localmente (método Jinja `qr_data_uri`), sem serviço externo
- Testes de padrão e de render dos Print Formats (`tests/test_print_formats.py`)

### Alterado
- "Ata de Reuniao de Comissao" e "Convocacao para Reuniao de Comissao" reescritos sobre `clm_base.html` e as macros do CLM (cabeçalho, rodapé, cartões, tabelas, selos de presença e cartão de assinatura padrão); a Ata passa a ser o formato padrão de Reuniao de Comissao
- O app passa a exigir o `clm` (`required_apps`), que fornece a base de impressão e o motor de PDF (clm v0.1.95 ou superior)
- As fichas antigas de ativos, que existiam só no banco ("Ficha de Ativo Imobilizado" e "Ficha de Movimentação de Ativos"), são desabilitadas sem ser apagadas; a acentuada é renomeada para "Ficha de Movimentacao de Ativos (antiga)" no before_migrate, porque a collation do banco a confundiria com o novo formato

## [2026-09-28] — v0.9.3

### Alterado
- Relatório "Atendimentos Medicos por Periodo" renomeado para "Relatorio de Atendimentos por Periodo" (título "Relatório de Atendimentos por Período" via pt-BR.csv); o registro antigo é removido por patch
- Workspace Indicadores ganha o card "Relatórios", com a Apuração de Classificação de Risco e o Relatório de Atendimentos por Período, que saem dos cards Triagem e Atendimentos (ajuste idempotente no after_migrate)

### Corrigido
- Classificacao de Risco Diaria: `atualizar_total` usava a variável inexistente `line`, gerando ReferenceError ao editar uma quantidade

## [2026-09-28] — v0.9.1

### Corrigido
- Grade de especialidades do Atendimento Medico Diario desalinhada em relação ao cabeçalho: a célula final de ação da linha agora é mantida vazia, como nas demais grades de Indicadores

## [2026-09-28] — v0.9.0

### Adicionado
- Relatório "Atendimentos Medicos por Periodo": atendimentos enviados por especialidade em um período, com percentual, dias com atendimento, média por dia lançado, resumo e gráfico; link no card Atendimentos do workspace Indicadores

### Alterado
- "Atendimento Diario" (e sua tabela filha) renomeado para "Atendimento Medico Diario" por patch pré-sincronização
- A vigência de especialidades passa a mapear as especialidades atendidas pela unidade em um período, como a vigência do protocolo de triagem: o campo Setor saiu da vigência e do atendimento, e a busca e a unicidade do lançamento usam apenas unidade e data

### Removido
- Definição de metas por especialidade (quantidade e periodicidade) na vigência e no atendimento; as colunas antigas, inclusive Setor, são removidas do banco no migrate

## [2026-09-28] — v0.8.1

### Removido
- Gráficos "Reuniões por mês", "Mandatos por status" e "Reuniões por unidade" do painel de Comissões (removidos também do banco no migrate)

## [2026-09-28] — v0.8.0

### Adicionado
- Painel de gestão no topo do workspace Comissoes: cartões (reuniões nos próximos 7 dias, mandatos a vencer em 60 dias, comissões sem reunião há mais de 90 dias, mandatos vigentes, reuniões no mês e presença média dos últimos 90 dias) e dois blocos: "Próximas reuniões" e "Comissões que exigem atenção"
- Number Cards e Dashboard Charts standard em comissoes/number_card e comissoes/dashboard_chart; dados calculados em comissoes/dashboard.py
- Custom HTML Blocks criados/atualizados de forma idempotente no after_migrate (fonte em comissoes/custom_blocks)

## [2026-09-28] — v0.7.0

### Adicionado
- Campo "Local da reunião" na Reuniao de Comissao

### Alterado
- "Data da reunião" passa a "Data e hora da reunião" (Datetime); reuniões já cadastradas ficam com 00:00
- Convocação e ata imprimem horário e local (o horário é omitido quando 00:00)
- Relatório "Atividades de Comissão" mostra data e hora e o local, e o filtro de período considera o dia inteiro da data final

## [2026-09-28] — v0.6.0

### Adicionado
- Formatos de impressão da Reuniao de Comissao: "Convocacao para Reuniao de Comissao" (data, horário e local para preencher, pauta e convocados) e "Ata de Reuniao de Comissao" (participantes com presença, pauta, deliberações, encaminhamentos e assinaturas dos presentes)

## [2026-09-28] — v0.5.1

### Alterado
- Relatório "Atividades de Comissão" mostra o nome da categoria, o nome da comissão e o mandato (início e status) no lugar dos IDs
- Com a pauta incluída, os dados da reunião aparecem só na primeira linha; os demais itens mostram apenas o assunto

## [2026-09-28] — v0.5.0

### Adicionado
- Relatório "Atividades de Comissão" (Comissoes): reuniões por período, com filtros de empresa e comissão, presentes/participantes por reunião e opção de incluir a pauta (uma linha por item)
- Card "Relatórios" no workspace Comissoes

## [2026-09-28] — v0.4.0

### Adicionado
- Categoria de Comissao (Conselho, Comitê, Núcleo, Grupo de Trabalho etc.), vinculada ao Tipo de Comissao
- Texto do regimento no Tipo de Comissao, com histórico de alterações (versão, data, responsável, motivo e texto anterior); o motivo é obrigatório ao alterar um regimento já salvo

### Alterado
- A empresa passa a ser cadastrada no Tipo de Comissao; o Mandato de Comissao a recebe do tipo, somente leitura
- Categoria e Tipo de Comissao nomeados por ID (CATCOM-/TPCOM-), exibindo o nome amigável nos campos de vínculo; a unicidade do tipo passa a ser por nome e empresa
- Migração copia a empresa dos mandatos para o tipo quando a origem é única

## [2026-09-28] — v0.3.0

### Adicionado
- Módulo Comissões como subworkspace de Gestor: Tipo de Comissao, Mandato de Comissao, Membros de Comissao e Reuniao de Comissao (pauta, participantes com presença, deliberações e encaminhamentos)
- Cópia dos membros da comissão para a lista de participantes da reunião
- Tradução pt-BR do título do workspace, mantendo a rota em ASCII

## [2026-09-18] — v0.2.7

### Adicionado
- Relatório de apuração da classificação de risco por unidade e período, com escalas separadas por protocolo e tempo-alvo
- Card com o total de pacientes classificados no período

### Alterado
- Tempo máximo de espera preservado nas linhas diárias; migração preenche os lançamentos anteriores com o valor disponível no protocolo

### Corrigido
- Identificador e rota do relatório em ASCII, com atualização do link no Workspace e migração do nome legado

## [2026-09-18] — v0.2.6

### Alterado
- Nomes dos DocTypes de indicadores sem acentos
- Classificação diária registra apenas a quantidade classificada por nível
- Níveis do protocolo mantêm cor e tempo máximo de espera

## [2026-09-18] — v0.2.5

### Alterado
- Edição direta dos níveis no protocolo e das quantidades na classificação diária, sem abrir a linha sobreposta
- Destaque das linhas pela cor do protocolo, com fundo suave e faixa lateral
- Cor dos níveis preservada nos lançamentos diários e preenchida nos registros anteriores durante a migração
- Alinhamento das linhas com o cabeçalho do grid ao ocultar a ação de expansão

## [2026-09-18] — v0.2.4

### Adicionado
- Lançamento diário da classificação de risco, com protocolo e níveis preenchidos pela vigência da unidade
- Total calculado, validação das quantidades e envio que bloqueia a edição
- Link para o lançamento no quadro **Triagem** do Workspace **Indicadores**

### Corrigido
- Compatibilidade de leitura e gravação dos DocTypes de indicadores no Query Builder deste bench
- Ordenação da consulta de sobreposição de vigências

## [2026-09-18] — v0.2.3

### Adicionado
- Quadro de links para os cadastros de triagem no Workspace **Indicadores**
- Sincronização idempotente do quadro em Workspaces já instalados
- Memória das convenções do app em `AGENTS.md`

## [2026-09-18] — v0.2.2

### Corrigido
- Listagem de vigências por unidade com ordenação compatível com o validador SQL do Frappe 15

## [2026-09-18] — v0.2.1

### Corrigido
- Visibilidade do Workspace **Indicadores** após instalação ou migração
- Permissões completas de `System Manager` e `Administrator` nos cadastros de indicadores
- Acesso explícito desses papéis ao Workspace **Indicadores**

## [2026-09-18] — v0.2.0

### Adicionado
- Workspace **Indicadores** com protocolos de triagem e vigências por unidade
- Níveis configuráveis com cor e tempo máximo de espera
- Validação de períodos sobrepostos para cada unidade (`Company`)

## [2026-08-17] — v0.1.4

### Corrigido
- Links da documentação saem do card Patrimônio e vão para o card **Documentação da Unidade**

## [2026-08-17] — v0.1.3

### Alterado
- Card **Documentação da Unidade** na seção Módulos do Workspace Gestor

## [2026-08-17] — v0.1.2

### Alterado
- Atalhos da Documentação da Unidade passam a ficar no Workspace **Gestor**
- Workspace Pulse Gestor oculto no menu lateral

## [2026-08-17] — v0.1.1

### Corrigido
- Workspace deixou de usar o mesmo nome do DocType (o botão Novo abria um Espaço de Trabalho)

## [2026-08-17] — v0.1.0

### Adicionado

- App `pulse_gestor` com o módulo Documentação da Unidade
- DocType `Tipo de Documento da Unidade` para cadastro dos tipos de PDF
- DocType `Documentacao da Unidade` vinculado à unidade (`Company`)
- Vigência opcional, anexo PDF e badge de status (Válido / Vencido / Sem validade)
- Notificação de vencimento próximo e no dia do vencimento
- Job diário para atualizar o status
- Workspace e papéis Pulse Gestor Manager / Viewer
