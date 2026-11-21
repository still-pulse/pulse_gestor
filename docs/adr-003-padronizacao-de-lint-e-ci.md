# ADR-003: Padronização de lint e CI

## Status

Aceita (2026-11-21).

## Contexto

Os 10 apps Frappe do conjunto (`bhcl_site`, `rh_brasil`, `busca_cnpj`, `integracoes_customizadas`,
`assinatura_eletronica`, `clm`, `pdf_ocr`, `pulse_gestor` e os demais) estão sendo preparados para unificação e
para a migração v15 -> v16/v17. Os apps divergiam em lint e CI (versão de Python, regras e versões do ruff, ignores,
excludes do pre-commit, globais do ESLint), o que dificulta revisar e mover código entre eles. Esta ADR registra o
padrão adotado, sem alterar lógica nem comportamento em runtime.

## Decisão

1. **Piso de Python 3.11** (`target-version = "py311"`, `requires-python = ">=3.11"`), mantido por restrição de
   produção. Produção e homologação estão confirmadas em **Python 3.12**; o `ci.yml` passou a rodar 3.12 para
   refletir a produção (o 3.14 anterior é incompatível com o Frappe v15: `freezegun`, usado pelos testes do
   ERPNext, quebra na coleta com `AttributeError: module 'uuid' has no attribute '_load_system_functions'`, o que
   deixava o Run Tests vermelho em `main`). O `linter.yml` também roda em **3.12** (alinhado à produção e ao
   `ci.yml`); 3.11 permanece só como piso de compatibilidade do código (`requires-python`, `target-version`). O alvo de migração ao
   Frappe v16 é `>=3.13` (`target-version = "py313"`, `requires-python = ">=3.13"`, com `linter.yml` e `ci.yml`
   coerentes), a executar na migração, não antes.
2. **ruff fixado em v0.16.10** via `ruff-pre-commit`, regras `F, E, W, I, UP, B, RUF` e lista de `ignore`
   idêntica à do CLM.
3. **pyupgrade coberto pela regra `UP` do ruff**, sem hook separado.
4. **F401 não é ignorado**: imports mortos são removidos; reexportações e imports por efeito colateral são mantidos
   com `# noqa: F401  # <motivo>`. Strings visíveis ao usuário com caractere unicode ambíguo recebem
   `# noqa: RUF001` em vez de alterar o texto.
5. **prettier 2.7.1 e eslint 8.44.0 mantidos**: a atualização foi adiada para não misturar com a padronização;
   revisar na preparação para v16/v17.
6. **Excludes do pre-commit** são sempre caminhos do próprio repositório; entradas mortas foram removidas, sem
   ampliar o escopo ignorado.
7. **Globais do ESLint** declarados no `.eslintrc` com escopo mínimo. Neste repo: `root_element` (variável injetada
   pelo Frappe em Custom HTML Block) como `readonly`, em `overrides` restrito a `**/custom_blocks/**/*.js`.
   Nenhum global de namespace do app foi necessário.
8. **Arquivos JS com Jinja** são excluídos de prettier/eslint por caminho exato. Neste repo: nenhum.
9. **JS formatado pelo prettier em commit exclusivo de estilo.** Neste repo: 5 arquivos.
10. **pip-audit é um job separado e informativo** (`continue-on-error: true`, não bloqueia o gate). Audita o
    `pyproject` do app e, clonando a branch `version-15`, o `pyproject` de `frappe`, `erpnext` e `hrms`, as versões
    usadas pelo CI. Achados são lidos nos logs do job e tratados à parte, sem deixar o gate obrigatório vermelho.
11. **commitlint mantido** e `pre-commit install` documentado no `AGENTS.md`.
12. **Sem tag nem mudança de `__version__`** nesta padronização.
13. **Actions alinhadas em todos os apps:** `actions/checkout@v7`, `actions/setup-python@v7`,
    `actions/setup-node@v7` e `actions/cache@v6`. `pre-commit/action` foi trocado por três passos (instalar
    `pre-commit`, `actions/cache@v6` de `~/.cache/pre-commit`, `pre-commit run --all-files`). Os dois workflows têm
    `workflow_dispatch` para validar a branch sem abrir PR. No disparo manual o semgrep compara com a `main`
    (`--baseline-commit`), mantendo o escopo diff-aware do pull request em vez de varrer achados antigos.
14. **Dependências declaradas explicitamente.** Externas no `pyproject` (`PyQRCode`, `pypng`, usadas em
    `print_formats.py`); apps obrigatórios em `required_apps` (`frappe`, `erpnext`, `clm`). Opcionais, sempre com
    guarda e **de propósito fora** de `required_apps`: `assinatura_eletronica` e `integracoes_customizadas`
    (listados em comentário no `pyproject`). `hrms` não é importado: `Employee` e `Asset` vêm do ERPNext v15.

## Consequências

- Lint, formatação e CI passam a ter o mesmo comportamento entre os apps, facilitando a unificação.
- Imports mortos não são mais tolerados; reexportações precisam de justificativa explícita no `noqa`.
- Atualizações de prettier/eslint exigem uma rodada própria, com possível reformatação de JS.
- O pip-audit cobre também Frappe/ERPNext/HRMS, mas é informativo e não barra o merge.

## Exceção de semgrep

`pulse_gestor/patches/v0_2_6_rename_indicadores_doctypes.py` recebe `# nosemgrep: frappe-monkey-patching-not-allowed`
na linha do `import` (o semgrep reporta o match desde o import até a atribuição). É um patch único e histórico que
troca temporariamente `builder.TABLE_NAME_PATTERN` para renomear DocTypes com acento e restaura o valor em `finally`;
o Frappe 15 não oferece hook para isso. Aprovado pelo responsável do repositório. O achado só apareceu porque o
`semgrep ci` é diff-aware e o `ruff --fix`/`format` reescreveu o arquivo.

### Achados `frappe-sql-format-injection` em patches

`patches/v0_2_6_remove_triagem_fields.py` e `patches/v0_9_0_remove_metas_e_setor_especialidades.py` montam
`ALTER TABLE ... DROP COLUMN` com f-string e `frappe.db.sql`. Os nomes de tabela e coluna são constantes do próprio
patch (sem entrada externa) e identificadores SQL não aceitam parâmetros, então o achado é falso positivo. Decisão:
manter `frappe.db.sql` como em `main` e suprimir com `# nosemgrep: frappe-sql-format-injection` na linha imediatamente
anterior à chamada, acompanhado de comentário com a justificativa. A troca por `frappe.db.sql_ddl` foi descartada:
apenas contornaria a regra, sem reduzir risco, e acrescentaria commit explícito ao patch. A guarda `has_column`
mantém a idempotência. Semgrep com `frappe/semgrep-rules`: 2 achados sem a supressão, 0 com ela.

### Testes de Patrimônio no CI

`install-app` não executa `after_migrate`; o `after_install` agora também chama `ensure_print_formats`, o que define
o formato padrão de `Asset` e `Asset Movement` em sites novos. Os Custom Fields de Patrimônio (`custom_empresa` em
`Location` e quatro campos em `Asset`) foram criados à mão em produção e agora estão versionados em
`pulse_gestor/fixtures/custom_field.json` (definições copiadas de produção, sem `owner`, `creation`, `modified`,
`modified_by`, `idx` e `docstatus`). O CI depende dessas fixtures reais (o setup de teste que criava os campos como
`Data` foi removido). Efeito no `migrate` em produção: a sincronização de fixtures sobrescreve esses cinco campos
com a definição versionada; ajustes feitos depois pela interface devem ser exportados de novo para o arquivo.

## Pendências

- Migrar para Python `>=3.13` junto com o v16 e revisar as versões de prettier/eslint na preparação para v16/v17.
- Avaliar tornar o pip-audit bloqueante quando os achados do job informativo estiverem tratados.

## Estado deste repositório

| Item | Estado |
| --- | --- |
| F401 | 0 ocorrências removidas ou mantidas (`fix: corrigir erros do ruff check` tratou só ordenação de imports, `zip(strict=True)`, variável não usada e um `noqa: RUF001`) |
| Excludes alterados | prettier e eslint: removidos `pulse_gestor/public/dist`, `cypress`, `pulse_gestor/templates/includes` e `pulse_gestor/public/js/lib` (caminhos inexistentes); mantidos `node_modules` e `boilerplate` |
| ESLint | override `root_element` em `**/custom_blocks/**/*.js` |
| JS com Jinja | nenhum |
| JS formatados pelo prettier | 5 arquivos |
| Resultado final do pre-commit | todos os hooks passam (`SKIP=commitlint pre-commit run --all-files`) |
