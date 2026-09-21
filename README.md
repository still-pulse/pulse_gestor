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
| Unidade Especialidade Vigencia | Especialidades e metas de um setor (`Department`) em uma unidade (`Company`) por período |
| Vigencia Especialidade | Especialidade, meta e periodicidade (tabela filha) |
| Atendimento Diario | Quantidades atendidas por especialidade, setor e data |
| Atendimento Diario Especialidade | Meta registrada e quantidade do dia (tabela filha) |

## Atendimentos diários

Cadastre cada especialidade uma vez. Em **Unidade Especialidade Vigencia**, escolha a unidade, um setor pertencente a essa unidade e as especialidades com meta mensal ou anual. A data final é inclusiva; deixe-a vazia para vigência sem prazo final. Não é permitido sobrepor vigências do mesmo par unidade e setor.

Ao criar um **Atendimento Diario**, informe unidade, setor e data. O app carrega as especialidades da vigência correspondente e suas metas; preencha apenas **Quantidade** em cada linha. O total é calculado automaticamente. Cada unidade, setor e data admite um lançamento não cancelado. Use **Enviar** para concluir o lançamento; os dados da meta ficam registrados no lançamento, mesmo se a vigência for editada depois.

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
