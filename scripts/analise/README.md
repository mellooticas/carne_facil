# 📊 Scripts de Análise

Scripts para análise exploratória e investigação dos dados das planilhas Excel.

## 📂 Total: 26 scripts

### 🔍 Análises Principais

- **analisar_dados_reais.py** ⭐ - Análise dos dados reais disponíveis (OS_NOVA + todos_os_caixas)
- **analisar_modelo_banco_correto.py** ⭐ - Mapeamento para modelagem do banco de dados
- **analisar_dados_modelagem.py** - Análise para criação do modelo

### 📋 Análises de Caixa

- analisar_caixa_lojas.py
- analisar_padrao_caixa.py
- analisar_relatorio_caixa.py

### 👥 Análises de Clientes

- analisar_clientes_vixen.py
- analise_sao_mateus.py

### 📝 Análises de Vendas

- analisar_vendas_completas.py
- analisar_detalhado_VEND.py

### 🔎 Investigações

- investigador_2025.py
- investigar_estrutura.py
- investigar_estrutura_excel.py
- investigar_tabelas_pagina.py
- investigar_valores_brutos.py
- localizar_dados_2025.py

### ✅ Verificações

- verificar_arquivos_base.py
- verificar_documentos_estruturados.py
- verificar_os_8434_corrigida.py
- verificar_os_multiplas.py
- verificar_sao_mateus.py
- verificar_tabelas_vend_dia.py

### 🗺️ Mapeamentos

- mapear_arquivo_caixa.py
- mapear_estrutura_real.py
- mapeador_tabelas_restantes.py

## 🎯 Como Usar

```bash
# Análise geral dos dados
python scripts/analise/analisar_dados_reais.py

# Investigar estrutura Excel
python scripts/analise/investigar_estrutura_excel.py

# Verificar dados de loja específica
python scripts/analise/verificar_sao_mateus.py
```

## 📊 Saídas Típicas

- Relatórios em console
- Arquivos JSON com estruturas
- CSVs com dados processados
- Logs de problemas encontrados

## ⚠️ Nota

Estes scripts são para **análise exploratória**. Para importação de dados, use os scripts em `/etl/`.
