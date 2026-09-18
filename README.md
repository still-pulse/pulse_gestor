# Pulse Gestor

App Frappe/ERPNext para **Documentação da Unidade** e **Indicadores**.

Repositório: [still-pulse/pulse_gestor](https://github.com/still-pulse/pulse_gestor)

## O que faz

Cadastro de documentos por unidade (`Company`), com tipo cadastrável, anexo PDF, vigência opcional e alerta de vencimento.

O Workspace **Indicadores** permite cadastrar protocolos de triagem, seus níveis e metas, e associar cada unidade a um protocolo por período de vigência. A unidade corresponde ao cadastro `Company` já usado pelo app. Datas finais de vigência são inclusivas; uma data final vazia indica vigência por prazo indeterminado. Períodos da mesma unidade não podem se sobrepor.

## DocTypes

| DocType | Função |
|---------|--------|
| Tipo de Documento da Unidade | Cadastro dos tipos de PDF |
| Documentacao da Unidade | Documento da unidade |
| Configuracoes Pulse Gestor | Dias de alerta de vencimento |
| Protocolo de Triagem | Escala e níveis de triagem |
| Protocolo Nivel | Níveis, cores e tempos de cada escala (tabela filha) |
| Unidade Protocolo Vigencia | Protocolo aplicável a uma unidade em um período |
| Classificacao de Risco Diaria | Quantidades classificadas por nível na unidade e data |
| Classificacao Diaria Nivel | Quantidades por nível (tabela filha) |

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
