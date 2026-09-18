# Memória do projeto pulse_gestor

- Neste app, a unidade é o DocType ERPNext `Company`. O campo `unidade` de `Unidade Protocolo Vigencia` aponta para ele.
- `Protocolo Nivel` é uma tabela filha de `Protocolo de Triagem`; não recebe um link de navegação próprio no Workspace.
- Um quadro de links no Workspace exige **duas** partes: linhas `Card Break` e `Link` em `links`, e um bloco `type: "card"` em `content` cujo `card_name` seja igual ao rótulo do `Card Break`. Atalhos em `shortcuts` não criam o quadro.
- Nos novos DocTypes navegáveis, incluir permissões completas de `System Manager` e `Administrator`. Em Workspaces com restrição de papéis, incluir ambos em `roles`. Tabelas filhas herdam as permissões do DocType pai.
- Após alterar metadados ou Workspace, executar `bench --site dev migrate` no bench e verificar o registro no site. Arquivos JSON isolados não aparecem na interface antes da migração.
- Em Workspaces já instalados, a migração pode preservar o `content` antigo mesmo quando o JSON do app mudou. Para novos blocos necessários, usar um ajuste idempotente no `after_migrate` (como `ensure_indicadores_workspace`) e conferir o `content` diretamente no site.
- O Query Builder deste Frappe 15 valida nomes de DocType só em ASCII; os nomes dos DocTypes de indicadores devem permanecer sem acentos.
- `Classificacao de Risco Diaria` resolve o protocolo pela vigência da unidade na data e exige uma linha por nível, na ordem do protocolo. O servidor recalcula o total e valida as quantidades; a tela apenas antecipa esse preenchimento.
- `Protocolo Nivel` e `Classificacao Diaria Nivel` usam `editable_grid=1`. A cor fica guardada na linha diária ao gerar o lançamento, e a migração preenche linhas antigas sem cor usando o protocolo disponível naquele momento.
- O grid do Frappe reserva uma célula final para a ação de cada linha, alinhada ao ícone de configuração no cabeçalho. Ao ocultar a ação de expansão, manter essa célula vazia; removê-la desalinha as colunas. Para a faixa colorida, usar sombra interna em vez de borda para não alterar a largura da linha.
