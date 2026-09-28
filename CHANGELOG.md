# Changelog

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
