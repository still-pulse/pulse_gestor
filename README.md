# Pulse Gestor (`pulse_gestor`)

App Frappe/ERPNext de gestão por unidade, com três áreas: **Documentação da Unidade**, **Indicadores** (triagem e
atendimentos) e **Comissões**. Em todas elas, a *unidade* é o DocType `Company` do ERPNext.

Repositório: [still-pulse/pulse_gestor](https://github.com/still-pulse/pulse_gestor)

## Funcionalidades

### Documentação da Unidade

- **Tipo de Documento da Unidade**: cadastro dos tipos de documento exigidos das unidades.
- **Documentação da Unidade**: documento por unidade, com anexo em PDF e vigência opcional. O status é
  `Válido`, `Vencido` ou `Sem validade`, com contagem de dias para o vencimento.
- **Rotinas diárias**: recalculam o status e os dias para vencimento e enfileiram avisos por e-mail no prazo
  configurado.
- **Configurações Documentos da Unidade**: dias de alerta, modelo de e-mail e destinatários por empresa.
- Notificações `Documento da Unidade a Vencer` e `Documento da Unidade Vencido`, e Number Cards no Workspace.

### Indicadores

- **Triagem**: **Protocolo de Triagem** com níveis (cor e tempo de cada escala, tabela filha *Protocolo Nivel*) e
  **Unidade Protocolo Vigencia**, que associa cada unidade a um protocolo por período. Datas finais são
  inclusivas, data final vazia indica prazo indeterminado e períodos da mesma unidade não podem se sobrepor.
- **Classificação de Risco Diária**: lançamento de pacientes classificados por nível, por unidade e data. O
  servidor resolve o protocolo vigente, exige uma linha por nível na ordem do protocolo e recalcula o total.
  Permite **importação em massa** pelo Data Import.
- **Atendimentos médicos**: **Especialidade**, **Unidade Especialidade Vigencia** (especialidades atendidas pela
  unidade em um período) e **Atendimento Medico Diario** (quantidade por especialidade, submetível, um
  lançamento não cancelado por unidade e data).
- **Relatórios**: *Apuração de Classificação de Risco* e *Relatório de Atendimentos por Período* (totais por
  especialidade, percentual, dias com atendimento, média por dia lançado e gráfico). Somente lançamentos enviados
  entram nas apurações.

### Comissões

- **Categoria de Comissão**, **Tipo de Comissão** (empresa, regimento com histórico de alterações e motivo
  obrigatório ao alterar) e **Mandato de Comissão** (período e status).
- **Membros de Comissão** por mandato e **Reunião de Comissão** com pauta, participantes e presença,
  deliberações e encaminhamentos; a lista de participantes pode ser copiada dos membros.
- **Formatos de impressão**: *Convocação para Reunião de Comissão* e *Ata de Reunião de Comissão*.
- **Relatório** *Atividades de Comissão* (reuniões por período, presença e pauta opcional).
- **Painel de gestão** no Workspace: reuniões nos próximos 7 dias, mandatos a vencer em 60 dias, comissões sem
  reunião há mais de 90 dias, mandatos vigentes, reuniões no mês e presença média, além dos blocos *Próximas
  reuniões* e *Comissões que exigem atenção*.

## Papéis e permissões

| Papel | Acesso |
| --- | --- |
| `Pulse Gestor Manager` | Cadastro, edição e importação em massa |
| `Pulse Gestor Viewer` | Somente leitura |
| `System Manager` / `Administrator` | Acesso completo aos DocTypes e Workspaces |

## Requisitos

- Frappe v15 e ERPNext (`required_apps = ["frappe", "erpnext"]`)
- Fila de e-mail configurada para os avisos de vencimento

## Instalação

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/still-pulse/pulse_gestor
bench --site <site> install-app pulse_gestor
bench --site <site> migrate
```

Atribua o papel **Pulse Gestor Manager** ou **Pulse Gestor Viewer** aos usuários. Em seguida, em *Configurações
Documentos da Unidade*, defina os dias de alerta, o modelo de e-mail e os destinatários.

## Uso: atendimentos médicos diários

1. **Especialidade**: cadastre cada especialidade uma vez.
2. **Unidade Especialidade Vigencia**: escolha a unidade, o período e as especialidades atendidas nele.
3. **Atendimento Medico Diario**: informe unidade e data; o app carrega as especialidades vigentes e basta
   preencher a **Quantidade**. Use **Enviar** para concluir o lançamento.

## Uso: importação em massa da classificação de risco

Na lista **Classificacao de Risco Diaria**, use **Importar** e baixe o modelo do Data Import. Informe **Unidade**
e **Data** na primeira linha de cada lançamento e preencha a tabela **Níveis classificados** com uma linha por
nível, na ordem do protocolo vigente. Marque **Enviar após importar** para incluir os lançamentos na apuração.

## Desenvolvimento

```text
pulse_gestor/
├── documentacao_da_unidade/   # DocTypes, Workspace
├── indicadores/               # DocTypes, relatórios, Workspace
├── comissoes/                 # DocTypes, relatório, formatos de impressão, painel
├── patches/ · fixtures/ · setup/install.py
├── tasks.py                   # rotinas agendadas (diárias)
└── utils.py                   # cálculo de status e vencimento
```

Convenções do projeto (identificadores técnicos em ASCII, Workspaces e migração) estão em
[AGENTS.md](AGENTS.md). Após alterar metadados ou Workspaces, execute `bench --site <site> migrate`.

Testes (a partir da raiz do bench):

```bash
bench --site <site> run-tests --app pulse_gestor
```

Histórico de versões em [CHANGELOG.md](CHANGELOG.md).

## Licença

MIT — Still Pulse / BHCL
