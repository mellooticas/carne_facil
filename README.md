# 🏢 Carnê Fácil - Projeto de Análise de Dados

Sistema de processamento e análise de dados de múltiplas fontes das lojas de ótica para migração ao Supabase.

## 📁 Estrutura do Projeto

```
carne_facil/
├── data/
│   ├── originais/                  # 📂 Dados fonte (INTOCÁVEIS)
│   │   ├── oss_gerais/            # ✅ OSs gerais [PROCESSADO]
│   │   │   ├── *.xlsm             # 16 arquivos originais
│   │   │   ├── README.md          # Documentação detalhada
│   │   │   └── uniao/             # Dados processados
│   │   │       ├── [loja]/        # 6 lojas consolidadas
│   │   │       ├── validados/     # 6.115 OSs validadas (5 etapas)
│   │   │       ├── clientes/      # 4.450 clientes únicos
│   │   │       └── receitas/      # 6.786 receitas óticas
│   │   │
│   │   ├── cxs/                   # 🔜 Sistema CXS [PENDENTE]
│   │   ├── vendas/                # 🔜 Dados de vendas [PENDENTE]
│   │   └── vixen/                 # 🔜 Sistema Vixen [PENDENTE]
│   │
│   ├── analises/                  # 📊 Análises intermediárias
│   └── resultados/                # 📈 Resultados finais
│
├── scripts/                        # � Scripts Python
│   ├── unificar_arquivos_lojas.py
│   ├── consolidar_duplicatas_osn.py
│   ├── etapa1_validar_cpf.py
│   ├── etapa2_validar_cep.py
│   ├── etapa3_validar_email.py
│   ├── etapa4_validar_telefone.py
│   ├── etapa5_validar_datas.py
│   ├── consolidar_clientes.py
│   ├── extrair_receitas.py
│   └── atualizar_caminhos.py
│
└── README.md                       # Este arquivo
```

## 🎯 Status do Projeto

### ✅ CONCLUÍDO - OSs Gerais

**Pipeline completo de processamento:**

1. **Unificação** (16 → 6 arquivos consolidados)
   - 8.154 OSs originais → 6.115 OSs únicas

2. **Validação em 5 Etapas**
   - ✅ CPF: 4.434 válidos (72.7%)
   - ✅ CEP + ViaCEP: 5.611 válidos (91.8%), 1.302 enriquecidos
   - ✅ Email: 2.783 válidos (77.3%)
   - ✅ Telefone/Celular: 552 tel + 5.872 cel válidos
   - ✅ Datas: 2.410 corrigidas por busca inteligente

3. **Extração e Organização**
   - ✅ **Clientes:** 4.450 clientes únicos (27.2% consolidação)
   - ✅ **Receitas:** 6.786 receitas óticas (média 1.11 por OS)

### � PENDENTE

1. **CXS** - Processar dados de caixa
2. **VENDAS** - Processar dados de vendas
3. **VIXEN** - Processar dados Vixen

## 📊 Resultados - OSs Gerais

| Loja | OSs | Clientes | Receitas | Consolidação |
|------|-----|----------|----------|--------------|
| MAUA | 737 | 538 | 853 | 27.0% |
| PERUS | 923 | 530 | 1,242 | 42.6% |
| RIO_PEQUENO | 1,261 | 1,137 | 1,346 | 9.8% |
| SAO_MATEUS | 571 | 486 | 562 | 14.9% |
| SUZANO | 2,190 | 1,409 | 2,329 | 35.7% |
| SUZANO_2 | 433 | 350 | 454 | 19.2% |
| **TOTAL** | **6,115** | **4,450** | **6,786** | **27.2%** |

## 🔗 Sistema de Correlação

Todos os dados estão interligados via **chave de identificação**:

```
CLIENTE (chave_cliente: CPF > RG > Nome+Celular)
    ↓
    ├─→ Lista de OSs (coluna 'oss')
    │      ↓
    │      └─→ OS específica (os_n)
    │             ↓
    │             └─→ Dados da venda, valores, produtos
    │
    └─→ RECEITAS (chave_cliente + os_n)
           ↓
           └─→ Grau OD/OE, medidas da armação
```

## �️ Como Usar

### Pré-requisitos
```bash
pip install pandas openpyxl requests
```

### Pipeline de Processamento (OSs Gerais - Exemplo)

```bash
# 1. Unificar arquivos por loja
python scripts/unificar_arquivos_lojas.py

# 2. Consolidar duplicatas
python scripts/consolidar_duplicatas_osn.py

# 3. Padronizar encoding
python scripts/padronizar_encoding.py

# 4-8. Validar dados (5 etapas)
python scripts/etapa1_validar_cpf.py
python scripts/etapa2_validar_cep.py
python scripts/etapa3_validar_email.py
python scripts/etapa4_validar_telefone.py
python scripts/etapa5_validar_datas.py

# 9. Extrair clientes únicos
python scripts/consolidar_clientes.py

# 10. Extrair receitas óticas
python scripts/extrair_receitas.py
```

## 📝 Padrão de Organização

Cada fonte de dados segue a estrutura **UNIAO**:

```
data/originais/[fonte]/
├── *.xlsx/xlsm          # Arquivos originais
├── README.md            # Documentação específica
└── uniao/               # Dados processados ✨
    ├── [loja]/          # Consolidados por loja
    ├── validados/       # Dados validados
    ├── clientes/        # Clientes únicos
    └── [especificos]/   # Dados específicos da fonte
```

## � Documentação Adicional

- **OSs Gerais:** Ver `data/originais/oss_gerais/README.md`
- **Scripts:** Comentários inline em cada arquivo Python

## �🔗 Supabase

**URL:** `https://jrhevexrzaoeyhmpwvgs.supabase.co`  
**Credenciais:** Ver arquivo `.env`

---

**Última atualização:** 20/10/2025  
**Versão:** 1.0  
**Status:** OSs Gerais ✅ | CXS 🔜 | VENDAS 🔜 | VIXEN 🔜
