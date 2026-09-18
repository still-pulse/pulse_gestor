# Changelog

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
