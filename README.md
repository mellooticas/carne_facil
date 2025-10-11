# 👁️ Sistema de Gestão de Óticas - Carne Fácil# 👁️ Sistema de Gestão de Óticas - Carne Fácil



![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)

![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)![Status](https://img.shields.io/badge/Status-Operacional-brightgreen.svg)

![Status](https://img.shields.io/badge/Status-Enterprise--Ready-brightgreen.svg)![License](https://img.shields.io/badge/License-Private-red.svg)



## 🎯 Visão Geral## 🎯 Visão Geral



Sistema **enterprise** para gestão unificada de 6 óticas com processamento de planilhas Excel, banco de dados PostgreSQL profissional e interface web FastAPI.Sistema web avançado para gestão unificada de óticas com processamento inteligente de planilhas Excel, normalização de dados, sistema de relacionamento Cliente-OS e controle completo de duplicações.



## 🏗️ Arquitetura### ✨ Características Principais



```- 🌐 **Interface Web Moderna** - FastAPI + Jinja2

carne_facil/- 📊 **Dashboard Executivo** - Métricas em tempo real

├── 📂 app/                 # 🌐 Aplicação Web (FastAPI)- 🔗 **Sistema de Relacionamento** - Cliente-OS inteligente

├── 📂 database/            # 🗄️ Scripts SQL Enterprise- 👁️ **Dioptrías Completas** - 25+ campos de prescrição

├── 📂 etl/                 # 📥 Importação de Dados (5 scripts)- 💰 **Gestão de Vendas** - Produtos, pagamentos e análises

├── 📂 scripts/             # 🛠️ Utilitários (58 scripts organizados)- 🏪 **Multi-loja** - MAUA, SAO_MATEUS, RIO_PEQUENO

│   ├── analise/           #    📊 Análises (26)- 🤖 **Deduplicação Inteligente** - FuzzyWuzzy + Levenshtein

│   ├── relatorios/        #    📈 Relatórios (8)

│   ├── processamento/     #    ⚙️ Processadores (17)## 📊 Resultados Alcançados

│   ├── limpeza/           #    🧹 Manutenção (5)

│   └── deprecated/        #    📦 Legado (2)### 🎯 Dados Processados

├── 📂 data/                # 📁 Dados Excel- **👥 3,262** clientes únicos identificados

└── 📂 docs/                # 📚 Documentação- **📋 14,337** ordens de serviço processadas  

```- **🔗 5,624** relacionamentos OS-Cliente estabelecidos

- **👁️ 12,309** registros de dioptrías extraídos

## ✨ Características Enterprise- **💰 R$ 70.2M** em vendas analisadas

- **🏷️ 373** produtos únicos catalogados

### 🗄️ Banco de Dados PostgreSQL

- ✅ **5 schemas** organizados (core, vendas, optica, marketing, auditoria)### 🆕 Sistema Universal de Vendas (NOVO!)

- ✅ **UUIDs** como chaves primárias- **🚀 Sistema Completo Implementado** - Processamento individual e em lote

- ✅ **Soft delete** (nunca perde dados)- **📊 264 vendas** processadas (MAUA: 60, SUZANO: 204)

- ✅ **Auditoria automática** (created_at, updated_at, version)- **💰 R$ 144.510,92** em faturamento consolidado

- ✅ **Busca fuzzy** com pg_trgm- **📅 Suporte 2024/2025** - Estrutura multi-anos

- ✅ **Normalização automática** de textos- **🔧 Formatação Brasileira** - Valores monetários corretos

- ✅ **Validação de CPF** via triggers- **📈 Relatórios Executivos** - Dashboards e análises completas

- ✅ **25+ índices otimizados**

### 📈 Performance do Sistema

### 🌐 Web App (FastAPI)- **✅ 33.6%** taxa de identificação Cliente-OS

- 🚀 Servidor rápido e assíncrono- **✅ 96.7%** OS com dados de vendas

- 📊 Dashboard com métricas- **✅ 83.0%** OS com produtos registrados

- 📤 Upload de planilhas Excel- **✅ 100%** automação do processamento

- 🔍 Busca inteligente de clientes

- 📈 Relatórios executivos## 🚀 Instalação e Execução



### 📥 ETL Robusto### Pré-requisitos

- 📊 **20.175 registros** processados- Python 3.11+

- 💰 **R$ 7.752.688,50** em valores- pip (gerenciador de pacotes Python)

- 🏪 **6 lojas** (5 ativas + 1 fechada)

- 🔄 Importação automática### 1. Clone o Repositório

```bash

## 📊 Dados Atuaisgit clone https://github.com/mellooticas/carne_facil.git

cd carne_facil

| Fonte | Registros | Valor |```

|-------|-----------|-------|

| **Vendas (VEND)** | 7.547 | R$ 6.032.727,49 |### 2. Crie o Ambiente Virtual

| **Recebimentos** | 3.108 | R$ 379.671,97 |```bash

| **Entregas OS** | 5.974 | - |python -m venv .venv

| **Entregas Carnê** | 678 | R$ 411.087,49 |```

| **Restantes** | 2.868 | R$ 929.201,55 |

| **TOTAL** | **20.175** | **R$ 7.752.688,50** |### 3. Ative o Ambiente Virtual

**Windows:**

## 🚀 Quick Start```bash

.venv\Scripts\activate

### 1. Clonar e Instalar```

```bash

git clone https://github.com/mellooticas/carne_facil.git**Linux/Mac:**

cd carne_facil```bash

python -m venv .venvsource .venv/bin/activate

source .venv/Scripts/activate  # Windows```

pip install -r requirements.txt

```### 4. Instale as Dependências

```bash

### 2. Criar Banco de Dadospip install -r requirements.txt

```bash```

# Criar database PostgreSQL

createdb -U postgres oticas_db### 5. Execute o Sistema Principal

```bash

# Executar scripts SQL (em ordem)uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

psql -U postgres -d oticas_db -f database/01_inicial_config.sql```

psql -U postgres -d oticas_db -f database/02_schema_core.sql

```### 6. Execute o Dashboard (opcional)

```bash

### 3. Importar Dadospython dashboard_simples.py

```bash```

# Importar dados das planilhas Excel

python etl/importador_caixas_completo.py## 🌐 Acesso ao Sistema

python etl/padronizar_clientes_vixen.py

```- **Sistema Principal:** http://localhost:8000

- **Dashboard Executivo:** http://localhost:8002

### 4. Executar App Web- **Upload de Arquivos:** http://localhost:8000/upload

```bash

uvicorn app.main:app --reload## 📁 Estrutura do Projeto

# Acesse: http://localhost:8000

``````

carne_facil/

## 📚 Documentação├── app/                    # Aplicação web FastAPI

│   ├── main.py            # Servidor principal

### Database│   ├── models/            # Modelos de dados

- 📖 [README Completo](database/README.md) - Arquitetura completa│   ├── services/          # Serviços de negócio

- 🗺️ [Diagrama ERD](database/ERD_DIAGRAMA.md) - Mermaid visual│   └── templates/         # Templates HTML

- 📄 [Resumo Executivo](database/RESUMO_EXECUTIVO.md) - Visão geral├── scripts/               # Scripts de processamento

│   ├── analisar_estrutura_os.py

### Scripts│   ├── criar_sistema_id_cliente.py

- 📥 [ETL](etl/README.md) - Importação de dados│   ├── extrair_dioptrias.py

- 📊 [Análises](scripts/analise/README.md) - 26 scripts│   ├── extrair_vendas.py

- 📈 [Relatórios](scripts/relatorios/README.md) - 8 geradores│   ├── criar_relacionamento_os_cliente.py

- ⚙️ [Processamento](scripts/processamento/README.md) - 17 scripts│   └── sistema_final_integrado.py

- 🧹 [Limpeza](scripts/limpeza/README.md) - 5 utilitários├── data/                  # Dados do sistema

│   ├── raw/              # Dados brutos

## 🎯 Uso Comum│   └── processed/        # Dados processados

├── dashboard_simples.py   # Dashboard executivo

### Importar novos dados└── requirements.txt       # Dependências

```bash```

python etl/importador_caixas_completo.py

```## 🔧 Scripts Disponíveis



### Gerar relatório executivo### 📊 Análise e Processamento

```bash```bash

python scripts/relatorios/relatorio_executivo_final.py# Analisar estrutura das OS

```python scripts/analisar_estrutura_os.py



### Analisar dados# Criar sistema de ID único para clientes

```bashpython scripts/criar_sistema_id_cliente.py

python scripts/analise/analisar_dados_reais.py

```# Extrair dados de dioptrías

python scripts/extrair_dioptrias.py

### Iniciar servidor web

```bash# Extrair dados de vendas

uvicorn app.main:app --reloadpython scripts/extrair_vendas.py

```

# Criar relacionamentos OS-Cliente

## 🏪 Lojas Gerenciadaspython scripts/criar_relacionamento_os_cliente.py



| Loja | Código | Status | Cidade |# Gerar sistema final integrado

|------|--------|--------|--------|python scripts/sistema_final_integrado.py

| Mauá | MAUA | ✅ Ativa | Mauá |```

| Suzano | SUZANO | ✅ Ativa | Suzano |

| Suzano 2 | SUZANO2 | ✅ Ativa | Suzano |## 🎯 Funcionalidades Implementadas

| Rio Pequeno | RIO_PEQUENO | ✅ Ativa | São Paulo |

| Perus | PERUS | ✅ Ativa | São Paulo |### ✅ Sistema Base

| São Mateus | SAO_MATEUS | ❌ Fechada | São Paulo |- [x] Interface web operacional

- [x] Upload de arquivos Excel

## 🛠️ Stack Tecnológica- [x] Processamento de múltiplos formatos

- [x] Sistema de logs detalhado

- **Backend**: Python 3.11+, FastAPI

- **Database**: PostgreSQL 15+### ✅ Processamento de Dados

- **Data Processing**: Pandas, Openpyxl- [x] Normalização automática

- **Fuzzy Search**: FuzzyWuzzy, Python-Levenshtein- [x] Deduplicação inteligente

- **Frontend**: Jinja2, HTML/CSS- [x] Mapeamento de 82 campos únicos

- **Analysis**: Jupyter Notebooks- [x] Identificação de 3 lojas ativas



## 📈 Métricas do Projeto### ✅ Sistema de Relacionamento

- [x] IDs únicos para clientes (CLI_000001)

- **Scripts Python**: 63 organizados- [x] Fuzzy matching para nomes

- **Schemas SQL**: 5 (core, vendas, optica, marketing, auditoria)- [x] Busca por CPF com prioridade

- **Tabelas**: 13 principais- [x] Taxa de identificação de 33.6%

- **Funções**: 8 utilitárias

- **Índices**: 25+ otimizados### ✅ Dioptrías Completas

- **Triggers**: 5 automáticos- [x] 25 campos de prescrição

- **Dados**: 20.175 registros- [x] Olho direito (OD) e esquerdo (OE)

- **Valor Total**: R$ 7.75M- [x] ESF, CIL, EIXO, DNP, ALTURA

- [x] ADIÇÃO para multifocais

## 🤝 Contribuindo

### ✅ Gestão de Vendas

Este é um projeto privado para uso interno da rede de óticas.- [x] 5 produtos por OS

- [x] Códigos Trello

## 📞 Suporte- [x] Formas de pagamento

- [x] Sinais e valores restantes

Para dúvidas sobre o sistema:

- 📧 Email: suporte@sistema-oticas.com### ✅ Dashboard Executivo

- 📚 Docs: Ver pasta `/docs/`- [x] Métricas em tempo real

- 🗺️ ERD: `/database/ERD_DIAGRAMA.md`- [x] Análise por loja

- [x] Interface responsiva

## 📄 Licença- [x] Auto-refresh



Private - Uso interno apenas## 📋 Dados Suportados



---### 🏪 Lojas Operacionais

- **MAUA** - 5,252 registros

**Versão**: 2.0.0 (Enterprise)  - **SAO_MATEUS** - Múltiplos arquivos

**Última atualização**: 10/10/2025  - **RIO_PEQUENO** - 552 registros

**Status**: ✅ Produção

### ⚙️ Sistemas Integrados
- **LANCASTER** - Sistema principal
- **OTM** - Sistema complementar

### 📊 Campos de Dioptrías
```
PONTE, HORIZONTAL, DIAG_MAIOR, VERTICAL
ESF_OD, CIL_OD, EIXO_OD, DNP_OD, ALTURA_OD
ESF_OE, CIL_OE, EIXO_OE, DNP_OE, ALTURA_OE
ADICAO_OD, ADICAO_OE
AR_LONGE, AR_PERTO, MULTIFOCAL
```

### 💰 Campos de Vendas
```
Cod_trello
Produto_1-5: codigo, descricao, valor
Valor_total, Pagto_1/2, Sinal_1/2, Valor_resta
```

## 🛠️ Tecnologias Utilizadas

- **Backend:** FastAPI, Uvicorn
- **Dados:** Pandas, Openpyxl, SQLAlchemy
- **Deduplicação:** FuzzyWuzzy, Python-Levenshtein
- **Frontend:** Jinja2, Bootstrap 5, Font Awesome
- **Gráficos:** Plotly.js (dashboard avançado)
- **Análise:** Jupyter Notebooks

## 📈 Próximos Passos

1. **Padronização de Dados** - Template Excel unificado
2. **Expansão de Lojas** - Integração das 6 lojas
3. **API REST** - Endpoints para integração
4. **Relatórios Avançados** - PDFs automatizados
5. **Mobile App** - Interface mobile nativa

## 🤝 Contribuição

Este é um projeto privado para gestão de óticas. Para contribuições, entre em contato com a equipe de desenvolvimento.

## 📞 Suporte

Para dúvidas ou suporte técnico:
- 📧 Email: suporte@carnefacil.com.br
- 🏢 Sistema: Óticas Carne Fácil

---

### 🏆 Conquistas do Sistema

✅ **Clientes Consolidados** - Base única e limpa  
✅ **Relacionamento OS-Cliente** - Sistema inteligente  
✅ **Dioptrías Completas** - 25+ campos extraídos  
✅ **Vendas Integradas** - R$ 70.2M processados  
✅ **Dashboard Executivo** - Visão estratégica  
✅ **Multi-loja** - 3 lojas operacionais  

---

**Desenvolvido com ❤️ para Óticas Carne Fácil**