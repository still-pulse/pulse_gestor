# Memória do projeto pulse_gestor

- Neste app, a unidade é o DocType ERPNext `Company`. O campo `unidade` de `Unidade Protocolo Vigência` aponta para ele.
- `Protocolo Nível` é uma tabela filha de `Protocolo de Triagem`; não recebe um link de navegação próprio no Workspace.
- Um quadro de links no Workspace exige **duas** partes: linhas `Card Break` e `Link` em `links`, e um bloco `type: "card"` em `content` cujo `card_name` seja igual ao rótulo do `Card Break`. Atalhos em `shortcuts` não criam o quadro.
- Nos novos DocTypes navegáveis, incluir permissões completas de `System Manager` e `Administrator`. Em Workspaces com restrição de papéis, incluir ambos em `roles`. Tabelas filhas herdam as permissões do DocType pai.
- O Frappe 15 deste bench rejeita letras acentuadas em `ORDER BY` no `DatabaseQuery`. A lista de `Unidade Protocolo Vigência` usa `unidade_protocolo_vigência_list.js` para enviar apenas nomes de campos permitidos, sem o nome acentuado da tabela.
- Após alterar metadados ou Workspace, executar `bench --site dev migrate` no bench e verificar o registro no site. Arquivos JSON isolados não aparecem na interface antes da migração.
- Em Workspaces já instalados, a migração pode preservar o `content` antigo mesmo quando o JSON do app mudou. Para novos blocos necessários, usar um ajuste idempotente no `after_migrate` (como `ensure_indicadores_workspace`) e conferir o `content` diretamente no site.
