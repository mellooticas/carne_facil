# 🏪 SISTEMA UNIVERSAL DE VENDAS - GUIA COMPLETO

## 🎯 VISÃO GERAL
Sistema completo para processar dados de vendas de óticas, gerando documentos únicos padronizados com todas as informações necessárias.

## 📋 ESTRUTURA DO SISTEMA

### 🔧 Ferramentas Disponíveis

#### 1. `sistema_vendas_universal.py` - **PROCESSADOR INDIVIDUAL**
**Função**: Processa um arquivo específico de uma loja
**Uso**: `python sistema_vendas_universal.py [LOJA] [ARQUIVO]`

**Exemplos**:
```bash
# Ver lojas disponíveis
python sistema_vendas_universal.py

# Processar MAUA abril/2024
python sistema_vendas_universal.py MAUA abr_24

# Processar SUZANO maio/2024
python sistema_vendas_universal.py SUZANO mai_24.xlsx

# Processar RIO_PEQUENO junho/2024
python sistema_vendas_universal.py RIO_PEQUENO jun_24
```

**Saída**: 
- Arquivo Excel com colunas padronizadas: `loja`, `data`, `numero_venda`, `cliente`, `forma_pgto`, `valor_venda`, `entrada`
- Relatório detalhado no terminal
- Arquivo salvo em: `data/vendas_processadas/`

---

#### 2. `processar_lote.py` - **PROCESSADOR EM LOTE**
**Função**: Processa múltiplas lojas ou múltiplos períodos
**Uso**: `python processar_lote.py`

**Opções do Menu**:
1. **Processar todas as lojas para um período** - Ex: todas as lojas em "abr_24"
2. **Processar todos os períodos de uma loja** - Ex: MAUA completo (jan a dez)
3. **Processar tudo** - Todas as lojas, todos os períodos disponíveis
4. **Sair**

**Saída**:
- Documentos individuais para cada processamento
- Documento consolidado por loja (todos os meses)
- Relatórios detalhados com estatísticas

---

#### 3. `relatorio_executivo.py` - **RELATÓRIO CONSOLIDADO**
**Função**: Consolida TODOS os dados processados em relatório executivo
**Uso**: `python relatorio_executivo.py`

**Saída**:
- **Excel consolidado** com múltiplas abas:
  - `VENDAS_CONSOLIDADAS`: Todas as vendas de todas as lojas
  - `RESUMO_POR_LOJA`: Estatísticas por loja
  - `RESUMO_MENSAL`: Performance mensal
  - `TOP_CLIENTES`: Ranking de clientes
  - `FORMAS_PAGAMENTO`: Análise de formas de pagamento
  - `ARQUIVOS_PROCESSADOS`: Lista de arquivos processados

- **Relatório em texto**: Resumo executivo completo
- **Dashboards visuais**: Gráficos de performance (se matplotlib disponível)

---

## 🏗️ ESTRUTURA DE PASTAS

```
d:/projetos/carne_facil/
├── data/
│   ├── caixa_lojas/                    # Dados originais
│   │   ├── MAUA/2024_MAU/             # 12 arquivos .xlsx
│   │   ├── SUZANO/2024_SUZ/           # 12 arquivos .xlsx  
│   │   └── RIO_PEQUENO/2024_RIO/      # 12 arquivos .xlsx
│   ├── vendas_processadas/             # Documentos gerados individuais
│   ├── relatorios_consolidados/        # Consolidados por loja
│   └── relatorios_executivos/          # Relatórios finais
├── sistema_vendas_universal.py         # Processador individual
├── processar_lote.py                   # Processador em lote  
└── relatorio_executivo.py             # Gerador de relatório final
```

---

## 🚀 FLUXO DE USO RECOMENDADO

### **CENÁRIO 1: Processar uma loja específica**
```bash
# 1. Ver lojas disponíveis
python sistema_vendas_universal.py

# 2. Processar arquivo específico
python sistema_vendas_universal.py MAUA abr_24

# Resultado: Documento único com todas as vendas de MAUA em abril/2024
```

### **CENÁRIO 2: Processar loja completa (ano todo)**
```bash
# 1. Executar processador em lote
python processar_lote.py

# 2. Escolher opção "2" (todos os períodos de uma loja)
# 3. Escolher loja (ex: MAUA)

# Resultado: 
# - 12 documentos individuais (jan a dez)
# - 1 documento consolidado do ano completo
# - Relatório detalhado da performance anual
```

### **CENÁRIO 3: Processar todas as lojas**
```bash
# 1. Executar processador em lote
python processar_lote.py

# 2. Escolher opção "3" (processar tudo)

# Resultado: Processamento completo de todas as lojas e períodos
```

### **CENÁRIO 4: Gerar relatório executivo final**
```bash
# 1. Após processar os dados desejados, gerar relatório
python relatorio_executivo.py

# Resultado: 
# - Relatório Excel consolidado com múltiplas análises
# - Relatório em texto para apresentações
# - Dashboards visuais (gráficos)
```

---

## 📊 FORMATO DOS DOCUMENTOS GERADOS

### **Documento Individual** (por loja/período)
**Nome**: `VENDAS_[LOJA]_[ANO]_[MES]_[TIMESTAMP].xlsx`
**Exemplo**: `VENDAS_MAUA_2024_ABR_20251010_095043.xlsx`

**Colunas**:
- `loja`: Nome da loja (MAUA, SUZANO, RIO_PEQUENO)
- `data`: Data da venda (YYYY-MM-DD)
- `numero_venda`: Número da venda no sistema
- `cliente`: Nome do cliente
- `forma_pgto`: Forma de pagamento (DN, CTC, CTD, PIX, etc.)
- `valor_venda`: Valor total da venda (formato brasileiro R$)
- `entrada`: Valor da entrada/sinal (formato brasileiro R$)

### **Documento Consolidado** (por loja - ano completo)
**Nome**: `CONSOLIDADO_[LOJA]_2024_COMPLETO_[TIMESTAMP].xlsx`
**Abas**:
- `VENDAS_COMPLETAS`: Todas as vendas ordenadas por data
- `RESUMO_MENSAL`: Estatísticas por mês
- `TOP_CLIENTES`: Ranking dos 50 melhores clientes

### **Relatório Executivo** (todas as lojas)
**Nome**: `RELATORIO_EXECUTIVO_[TIMESTAMP].xlsx`
**Abas**:
- `VENDAS_CONSOLIDADAS`: TODAS as vendas de TODAS as lojas
- `RESUMO_POR_LOJA`: Performance comparativa das lojas
- `RESUMO_MENSAL`: Evolução temporal
- `TOP_CLIENTES`: Top 100 clientes de toda a rede
- `FORMAS_PAGAMENTO`: Análise de formas de pagamento
- `ARQUIVOS_PROCESSADOS`: Controle de qualidade

---

## 🎯 CASOS DE USO PRÁTICOS

### **Para o Gestor de Loja Individual**
```bash
# Processar relatório mensal da minha loja
python sistema_vendas_universal.py MAUA abr_24

# Resultado: Excel com todas as vendas de abril para análise local
```

### **Para o Gestor Regional** 
```bash
# Processar uma loja completa para avaliação anual
python processar_lote.py
# Opção 2 → SUZANO

# Resultado: Relatório anual completo da loja SUZANO
```

### **Para a Diretoria/Controladoria**
```bash
# 1. Processar todas as lojas
python processar_lote.py  # Opção 3

# 2. Gerar relatório executivo
python relatorio_executivo.py

# Resultado: Relatório executivo consolidado de toda a rede
```

### **Para Análise Específica** 
```bash
# Comparar todas as lojas em um período específico
python processar_lote.py  # Opção 1 → mai_24

# Resultado: Documentos comparativos do mesmo período
```

---

## 🔍 INFORMAÇÕES TÉCNICAS

### **Formatação Monetária**
- Sistema adaptado para formato brasileiro (vírgula decimal)
- Conversão automática de formatos mistos
- Valores zerados para vendas tipo "SS" e "GARANTIA"

### **Identificação de Tabelas**
- Busca automática por cabeçalhos de vendas nas planilhas
- Mapeamento inteligente de colunas
- Processamento de 30/31 abas por arquivo (dias do mês)

### **Validação de Dados**
- Verificação de números de venda válidos
- Tratamento de células vazias
- Aplicação de regras de negócio específicas

### **Performance**
- Processamento otimizado para grandes volumes
- Relatórios detalhados de progresso
- Sistema de log para depuração

---

## 📝 EXEMPLOS DE COMANDOS RÁPIDOS

```bash
# Ver ajuda
python sistema_vendas_universal.py

# Processar arquivo específico  
python sistema_vendas_universal.py MAUA abr_24

# Menu interativo para lotes
python processar_lote.py

# Relatório executivo completo
python relatorio_executivo.py
```

---

## 📈 RESULTADOS TÍPICOS

### **MAUA - Abril/2024**
- 60 vendas processadas
- R$ 29.315,92 em faturamento
- R$ 13.415,00 em entradas
- Ticket médio: R$ 488,60

### **SUZANO - Maio/2024**  
- 204 vendas processadas
- R$ 115.195,00 em faturamento
- R$ 71.321,97 em entradas
- Ticket médio: R$ 564,68

---

## 🎉 VANTAGENS DO SISTEMA

✅ **Universalidade**: Funciona com qualquer loja  
✅ **Padronização**: Documentos únicos com formato consistente  
✅ **Flexibilidade**: Processamento individual ou em lote  
✅ **Completude**: Relatórios desde operacional até executivo  
✅ **Confiabilidade**: Formatação monetária brasileira correta  
✅ **Rastreabilidade**: Controle completo dos arquivos processados  

---

**🏪 Sistema desenvolvido para gestão unificada de óticas com foco em dados confiáveis e relatórios executivos**