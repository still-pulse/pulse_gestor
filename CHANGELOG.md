# Changelog

## [2026-09-18] — v0.2.1

### Corrigido
- Visibilidade do Workspace **Indicadores** após instalação ou migração
- Permissões completas de `System Manager` e `Administrator` nos cadastros de indicadores
- Acesso explícito desses papéis ao Workspace **Indicadores**

## [2026-09-18] — v0.2.0

### Adicionado
- Workspace **Indicadores** com protocolos de triagem e vigências por unidade
- Níveis configuráveis com cor, tempo máximo de espera e meta de conformidade
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
