# 👁️ Sistema de Gestão de Óticas - Carne Fácil

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Status](https://img.shields.io/badge/Status-Operacional-brightgreen.svg)
![License](https://img.shields.io/badge/License-Private-red.svg)

## 🎯 Visão Geral

Sistema web avançado para gestão unificada de óticas com processamento inteligente de planilhas Excel, normalização de dados, sistema de relacionamento Cliente-OS e controle completo de duplicações.

### ✨ Características Principais

- 🌐 **Interface Web Moderna** - FastAPI + Jinja2
- 📊 **Dashboard Executivo** - Métricas em tempo real
- 🔗 **Sistema de Relacionamento** - Cliente-OS inteligente
- 👁️ **Dioptrías Completas** - 25+ campos de prescrição
- 💰 **Gestão de Vendas** - Produtos, pagamentos e análises
- 🏪 **Multi-loja** - MAUA, SAO_MATEUS, RIO_PEQUENO
- 🤖 **Deduplicação Inteligente** - FuzzyWuzzy + Levenshtein

## 📊 Resultados Alcançados

### 🎯 Dados Processados
- **👥 3,262** clientes únicos identificados
- **📋 14,337** ordens de serviço processadas  
- **🔗 5,624** relacionamentos OS-Cliente estabelecidos
- **👁️ 12,309** registros de dioptrías extraídos
- **💰 R$ 70.2M** em vendas analisadas
- **🏷️ 373** produtos únicos catalogados

### 📈 Performance do Sistema
- **✅ 33.6%** taxa de identificação Cliente-OS
- **✅ 96.7%** OS com dados de vendas
- **✅ 83.0%** OS com produtos registrados
- **✅ 100%** automação do processamento

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.11+
- pip (gerenciador de pacotes Python)

### 1. Clone o Repositório
```bash
git clone https://github.com/mellooticas/carne_facil.git
cd carne_facil
```

### 2. Crie o Ambiente Virtual
```bash
python -m venv .venv
```

### 3. Ative o Ambiente Virtual
**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 4. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 5. Execute o Sistema Principal
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Execute o Dashboard (opcional)
```bash
python dashboard_simples.py
```

## 🌐 Acesso ao Sistema

- **Sistema Principal:** http://localhost:8000
- **Dashboard Executivo:** http://localhost:8002
- **Upload de Arquivos:** http://localhost:8000/upload

## 📁 Estrutura do Projeto

```
carne_facil/
├── app/                    # Aplicação web FastAPI
│   ├── main.py            # Servidor principal
│   ├── models/            # Modelos de dados
│   ├── services/          # Serviços de negócio
│   └── templates/         # Templates HTML
├── scripts/               # Scripts de processamento
│   ├── analisar_estrutura_os.py
│   ├── criar_sistema_id_cliente.py
│   ├── extrair_dioptrias.py
│   ├── extrair_vendas.py
│   ├── criar_relacionamento_os_cliente.py
│   └── sistema_final_integrado.py
├── data/                  # Dados do sistema
│   ├── raw/              # Dados brutos
│   └── processed/        # Dados processados
├── dashboard_simples.py   # Dashboard executivo
└── requirements.txt       # Dependências
```

## 🔧 Scripts Disponíveis

### 📊 Análise e Processamento
```bash
# Analisar estrutura das OS
python scripts/analisar_estrutura_os.py

# Criar sistema de ID único para clientes
python scripts/criar_sistema_id_cliente.py

# Extrair dados de dioptrías
python scripts/extrair_dioptrias.py

# Extrair dados de vendas
python scripts/extrair_vendas.py

# Criar relacionamentos OS-Cliente
python scripts/criar_relacionamento_os_cliente.py

# Gerar sistema final integrado
python scripts/sistema_final_integrado.py
```

## 🎯 Funcionalidades Implementadas

### ✅ Sistema Base
- [x] Interface web operacional
- [x] Upload de arquivos Excel
- [x] Processamento de múltiplos formatos
- [x] Sistema de logs detalhado

### ✅ Processamento de Dados
- [x] Normalização automática
- [x] Deduplicação inteligente
- [x] Mapeamento de 82 campos únicos
- [x] Identificação de 3 lojas ativas

### ✅ Sistema de Relacionamento
- [x] IDs únicos para clientes (CLI_000001)
- [x] Fuzzy matching para nomes
- [x] Busca por CPF com prioridade
- [x] Taxa de identificação de 33.6%

### ✅ Dioptrías Completas
- [x] 25 campos de prescrição
- [x] Olho direito (OD) e esquerdo (OE)
- [x] ESF, CIL, EIXO, DNP, ALTURA
- [x] ADIÇÃO para multifocais

### ✅ Gestão de Vendas
- [x] 5 produtos por OS
- [x] Códigos Trello
- [x] Formas de pagamento
- [x] Sinais e valores restantes

### ✅ Dashboard Executivo
- [x] Métricas em tempo real
- [x] Análise por loja
- [x] Interface responsiva
- [x] Auto-refresh

## 📋 Dados Suportados

### 🏪 Lojas Operacionais
- **MAUA** - 5,252 registros
- **SAO_MATEUS** - Múltiplos arquivos
- **RIO_PEQUENO** - 552 registros

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