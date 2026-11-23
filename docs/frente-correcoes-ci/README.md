# Frente de correções de produto reveladas pelo CI: pulse_gestor

Registro de 2026-11-23. Branch: `claude/frappe-ci-product-fixes-ag289b`. PR #6 (draft). HEAD antes desta documentação: `ccf5eb1`.
Este retrato pode ficar desatualizado: confira `git log`, o PR e os checks reais antes de agir.

## O que foi feito
- Fixtures reais dos 5 Custom Fields de Patrimônio (idênticas ao export de produção); `tests/site_setup.py` removido.
- Testes de Patrimônio sem skip (`setUpClass`) e 2 Employees em `test_print_formats.py`.
- Semgrep de 18 para 0 sem `# nosemgrep` novo: type hints, SQL parametrizado e remoção de 4 `db.commit()`.

## Estado
- HEAD `ccf5eb1`: Server e Linters verdes no dispatch. Revisor aprovou duas vezes. **CI do PR não foi visto.**
- 4 testes do `TestTermoDeResponsabilidade` são pulados enquanto `assinatura_eletronica` não está no CI (registrado na ADR-003).

## Pendências
- Aprovar nominalmente `# nosemgrep: frappe-monkey-patching-not-allowed` em `patches/v0_2_6_rename_indicadores_doctypes.py:5`
  (pré-existente; recomendação: aprovar). Os 2 de SQL das patches `v0_2_6` e `v0_9_0` já estavam aprovados.
- Os 4 campos de layout de Asset não foram versionados (decisão na ADR-003).

## Arquivos desta pasta
- `prompt-nova-sessao.md`: contexto completo da frente, com as regras permanentes, os padrões institucionais, as decisões
  do usuário e o estado de **todos** os apps. Cópia idêntica em cada repositório.
- `setup-ambiente-frappe.sh`: script único de ambiente (bench, MariaDB, Redis, `payments`, `erpnext`, `hrms` e os apps
  clonados). **Nunca foi executado de ponta a ponta**; só a sintaxe e a lógica do `frappe-env` foram validadas.

## Regras que valem aqui
CI verde sempre; nenhum `# nosemgrep`, skip ou job desativado sem aprovação explícita; todo bug corrigido ganha teste;
Semgrep em varredura completa; arredondamento monetário proibido (truncar na 2ª casa); PR só depois de revisor isolado.
