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
| Configuracoes Documentos da Unidade | Dias de alerta, modelo de e-mail e destinatários por empresa |
| Protocolo de Triagem | Escala e níveis de triagem |
| Protocolo Nivel | Níveis, cores e tempos de cada escala (tabela filha) |
| Unidade Protocolo Vigencia | Protocolo aplicável a uma unidade em um período |
| Classificacao de Risco Diaria | Quantidades classificadas por nível na unidade e data |
| Classificacao Diaria Nivel | Quantidades por nível (tabela filha) |
| Especialidade | Cadastro reutilizável de especialidades |
| Unidade Especialidade Vigencia | Especialidades atendidas por uma unidade (`Company`) em um período |
| Vigencia Especialidade | Especialidade da vigência (tabela filha) |
| Atendimento Medico Diario | Quantidades atendidas por especialidade na unidade e data |
| Atendimento Medico Diario Especialidade | Especialidade e quantidade do dia (tabela filha) |

## Atendimentos médicos diários

O fluxo segue a classificação de risco: cadastre as especialidades, defina quais a unidade atende e lance os atendimentos do dia.

1. **Especialidade**: cadastre cada especialidade uma vez.
2. **Unidade Especialidade Vigencia**: escolha a unidade, o período e as especialidades atendidas nele. A data final é inclusiva; deixe-a vazia para vigência sem prazo final. Períodos da mesma unidade não podem se sobrepor.
3. **Atendimento Medico Diario**: informe unidade e data. O app carrega as especialidades da vigência da unidade nessa data; preencha apenas **Quantidade** em cada linha. O total é calculado automaticamente. Cada unidade e data admite um lançamento não cancelado. Use **Enviar** para concluir o lançamento.

O **Relatório de Atendimentos por Período** (`Relatorio de Atendimentos por Periodo`, Script Report, no card **Relatórios** do Workspace junto com a apuração de classificação de risco) totaliza, por especialidade, os atendimentos enviados da unidade entre duas datas, com percentual do total, dias com atendimento, média por dia lançado e gráfico. Rascunhos não entram. O filtro opcional de especialidade restringe a apuração.

Não há definição de metas por especialidade por enquanto.

## Importação em massa da classificação de risco

Na lista **Classificacao de Risco Diaria**, use **Importar** e baixe o modelo do Data Import. Informe **Unidade** e **Data** na primeira linha de cada lançamento e preencha a tabela **Níveis classificados** com uma linha por nível, na ordem do protocolo vigente, incluindo **Nível** e **Pacientes classificados**. O protocolo, os tempos e o total são calculados pelo servidor. Marque **Enviar após importar** para incluir os lançamentos no relatório de apuração; rascunhos não entram no relatório.

O acesso à importação é concedido a **Pulse Gestor Manager**, **System Manager** e **Administrator**. **Pulse Gestor Viewer** continua apenas com leitura.

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
