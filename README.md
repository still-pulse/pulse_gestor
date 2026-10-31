# Pulse Gestor (`pulse_gestor`)

App Frappe/ERPNext de gestão por unidade, com quatro áreas: **Documentação da Unidade**, **Indicadores** (triagem e
atendimentos), **Comissões** e **Patrimônio** (impressos e relatórios de ativos). Em todas elas, a *unidade* é o
DocType `Company` do ERPNext. Os cadastros e relatórios ficam no Workspace **Gestor**.

Repositório: [still-pulse/pulse_gestor](https://github.com/still-pulse/pulse_gestor)

Versão atual: **0.11.7** (`pulse_gestor/__init__.py`, `hooks.py` e tag `v0.11.7`). Histórico em [CHANGELOG.md](CHANGELOG.md).

## Funcionalidades

### Documentação da Unidade

- **Tipo de Documento da Unidade**: cadastro dos tipos de documento exigidos das unidades.
- **Documentação da Unidade**: documento por unidade, com anexo em PDF e vigência opcional. O status é
  `Válido`, `Vencido` ou `Sem validade`, com contagem de dias para o vencimento.
- **Rotinas diárias**: recalculam o status e os dias para vencimento e enfileiram avisos por e-mail no prazo
  configurado.
- **Configurações Documentos da Unidade**: dias de alerta, modelo de e-mail e destinatários por empresa.
- Notificações `Documento da Unidade a Vencer` e `Documento da Unidade Vencido`, e Number Cards (total, válidos e
  vencidos) no Workspace.

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
- **Convocação** pelo botão *Convocar membros* da reunião, por WhatsApp, e-mail ou ambos, conforme o canal
  preferencial de cada participante. Exige o app `integracoes_customizadas` (veja *Requisitos*).
- **Ata assinável**: com o app `assinatura_eletronica`, os participantes presentes assinam a ata pelo motor de
  assinatura (perfil `PerfilReuniaoDeComissao`, Modelo de Assinatura semeado no `after_migrate`). Quando há Processo
  de Assinatura encerrado, a ata imprime o registro das evidências.
- **Formatos de impressão** no padrão BHCL: *Convocação para Reunião de Comissão* e *Ata de Reunião de Comissão*
  (padrão do DocType).
- **Relatório** *Atividades de Comissão* (reuniões por período, presença e pauta opcional).
- **Painel de gestão** no Workspace: reuniões nos próximos 7 dias, mandatos a vencer em 60 dias, comissões sem
  reunião há mais de 90 dias, mandatos vigentes, reuniões no mês e presença média, além dos blocos *Próximas
  reuniões* e *Comissões que exigem atenção*.

### Patrimônio

O módulo **Patrimonio** não cria DocTypes: estende o `Asset` e o `Asset Movement` do ERPNext.

- **Formatos de impressão** (padrão BHCL, motor WeasyPrint): *Ficha do Ativo Imobilizado* e *Ficha de Movimentacao
  de Ativos*, definidos como padrão dos DocTypes no `after_migrate`; *Termo de Responsabilidade do Ativo* e *Termo de
  Responsabilidade de Movimentacao*, usados como comprovante da assinatura. O QR Code do registro é gerado
  localmente (método Jinja `qr_data_uri`).
- **Relatórios** (Script Reports sobre `Asset`): *Relacao de Ativos* e *Ativos por Localizacao* (bens agrupados em
  árvore, com quantidade, valores e gráfico). Filtram por empresa, localização (incluindo sublocais), categoria,
  situação, utilização e estado de conservação. A empresa da localização vem do campo `custom_empresa` de
  `Location`, um Custom Field criado no site, que **não** está nas fixtures do app.
- **Custodiante**: no `Asset`, só colaboradores ativos da empresa do bem (filtro em `public/js/asset.js`), com
  validação no servidor (`validar_custodiante`, evento `validate`).
- **Termos assinados eletronicamente**: com o app `assinatura_eletronica`, o custodiante assina o Termo na custódia
  inicial, no próprio `Asset` (`PerfilTermoDoAtivo`), e cada colaborador em *Para Funcionário* assina o Termo da
  `Asset Movement` (`PerfilTermoDeMovimentacao`). O recebimento (`Receipt`) criado pelo ERPNext ao submeter o Asset
  é recusado na movimentação, para não duplicar a assinatura.

### Workspace Gestor

Os cards do app ficam num só Workspace, o **Gestor**: Documentação da Unidade, Triagem, Atendimentos, Relatórios de
Indicadores, Comissões, Configurações de Comissões, Relatórios de Comissões e Relatórios de Patrimônio, mais o
painel de gestão no topo. Os links vêm de `pulse_gestor/setup/gestor_links.json` e são aplicados pelo `after_migrate`
(`ensure_pulse_gestor_workspace`), que também apaga os Workspaces antigos `Pulse Gestor`, `Indicadores`, `Comissoes` e
`Documentacao da Unidade`. O Workspace `Gestor` **não é criado por este app**: se não existir no site, nada é
aplicado.

## Papéis e permissões

| Papel | Acesso |
| --- | --- |
| `Pulse Gestor Manager` | Cadastro, edição e importação em massa |
| `Pulse Gestor Viewer` | Somente leitura |
| `System Manager` / `Administrator` | Acesso completo aos DocTypes e Workspaces |

## Requisitos

- Frappe v15 e ERPNext v15.
- App `clm`: `required_apps = ["frappe", "erpnext", "clm"]`. Os formatos de impressão estendem
  `clm/templates/print/clm_base.html` (macros, manifesto de marca em `clm/docs/brand-manifesto.md`) e o PDF sai do
  motor do `clm`, que só atende aos módulos listados em `PDF_ENGINE_MODULES` (`apps/clm/clm/clm/services/pdf_engine.py`). `Comissoes` e
  `Patrimonio` já estão nessa lista. Instale o `clm` antes do `pulse_gestor`.
- Workspace `Gestor` existente no site (veja *Workspace Gestor*).
- Fila de e-mail configurada para os avisos de vencimento.
- **Opcionais, não declarados em `required_apps`**:
  - `assinatura_eletronica`: assinatura da ata e dos Termos de Responsabilidade. `assinatura.py` importa o app dentro
    de `try`; sem ele, os perfis não são definidos e nada é semeado.
  - `integracoes_customizadas`: convocação por WhatsApp/e-mail (`Modelo WhatsApp`) e normalização de telefone. Os
    imports ficam dentro das funções; sem o app, *Convocar membros* responde com erro.

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

Contagem em `git ls-files`: 23 DocTypes (14 independentes, sendo 1 Single, e 9 tabelas filhas), 5 Script Reports, 6 formatos
de impressão, 6 Number Cards de Comissões (`comissoes/number_card`) e 3 de Documentação (`fixtures/number_card.json`),
2 jobs diários, 7 patches e 46 testes em 11 arquivos.

```text
pulse_gestor/
├── hooks.py · modules.txt · patches.txt
├── documentacao_da_unidade/   # 4 DocTypes (1 Single, 1 filho)
├── indicadores/               # 10 DocTypes, 2 relatórios
├── comissoes/                 # 9 DocTypes, relatório, 2 formatos, Number Cards, custom_blocks (painel)
├── patrimonio/                # 2 relatórios (e report/utils.py), 4 formatos, asset.py (custodiante)
├── assinatura.py              # perfis do motor assinatura_eletronica, Modelos semeados (opcional)
├── print_formats.py           # formatos padrão, legados, qr_data_uri
├── telefone.py                # máscara e validação de telefone
├── tasks.py                   # rotinas agendadas (diárias)
├── utils.py                   # cálculo de status e vencimento
├── setup/                     # install.py (after_install/after_migrate), gestor_links.json
├── public/js/asset.js         # filtro do custodiante
├── templates/print/           # comissoes_macros.html, patrimonio_macros.html
├── patches/ · fixtures/ · translations/pt-BR.csv
└── tests/                     # formatos de impressão, status, termos
```

Convenções do
projeto (identificadores técnicos em ASCII, Workspaces e migração) estão em [AGENTS.md](AGENTS.md). Após alterar
metadados ou Workspaces, execute `bench --site <site> migrate`.

### Testes

A partir da raiz do bench:

```bash
bench --site <site> run-tests --app pulse_gestor
```

## Documentação

- [CHANGELOG.md](CHANGELOG.md): histórico de versões e limites do git.
- [AGENTS.md](AGENTS.md): convenções, Workspace, Termos de Responsabilidade e dependências.

## Licença

MIT — Still Pulse / BHCL (veja [license.txt](license.txt)).
