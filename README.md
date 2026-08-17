# Pulse Gestor

App Frappe/ERPNext para **Documentação da Unidade**.

Repositório: [still-pulse/pulse_gestor](https://github.com/still-pulse/pulse_gestor)

## O que faz

Cadastro de documentos por unidade (`Company`), com tipo cadastrável, anexo PDF, vigência opcional e alerta de vencimento.

## DocTypes

| DocType | Função |
|---------|--------|
| Tipo de Documento da Unidade | Cadastro dos tipos de PDF |
| Documentacao da Unidade | Documento da unidade |
| Configuracoes Pulse Gestor | Dias de alerta de vencimento |

## Instalação

```bash
cd frappe-bench
bench get-app https://github.com/still-pulse/pulse_gestor
bench --site SEU_SITE install-app pulse_gestor
bench --site SEU_SITE migrate
```

Atribua o papel **Pulse Gestor Manager** ou **Pulse Gestor Viewer**.

## Licença

MIT — Still Pulse / BHCL
