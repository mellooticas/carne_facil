#!/usr/bin/env python3
"""
Análise dos dados REAIS que temos:
- OS_NOVA: dados dos clientes
- todos_os_caixas: dados das vendas
"""

import pandas as pd
import os

print("=" * 80)
print("🔍 ANÁLISE DOS DADOS REAIS DISPONÍVEIS")
print("=" * 80)

# 1. OS_NOVA - Dados dos Clientes
print("\n📋 1. OS_NOVA (Dados dos Clientes)")
print("-" * 80)

try:
    arquivo_os = 'data/backup_raw_20250113_144000/OS_NOVA.xlsx'
    
    if os.path.exists(arquivo_os):
        xls_os = pd.ExcelFile(arquivo_os)
        print(f"✅ Arquivo encontrado: {arquivo_os}")
        print(f"📑 Abas disponíveis: {xls_os.sheet_names}")
        
        # Ler primeira aba
        df_os = pd.read_excel(arquivo_os, sheet_name=0)
        print(f"\n📊 Total de registros: {len(df_os):,}")
        print(f"📝 Colunas ({len(df_os.columns)}):")
        
        for i, col in enumerate(df_os.columns, 1):
            tipo = df_os[col].dtype
            nulos = df_os[col].isna().sum()
            unicos = df_os[col].nunique()
            print(f"   {i:2d}. {col:30s} | Tipo: {str(tipo):10s} | Nulos: {nulos:5d} | Únicos: {unicos:,}")
        
        # Amostra dos dados
        print(f"\n📌 Primeiras 3 linhas:")
        print(df_os.head(3).to_string())
        
    else:
        print(f"❌ Arquivo não encontrado: {arquivo_os}")
        
except Exception as e:
    print(f"❌ Erro ao ler OS_NOVA: {e}")

# 2. todos_os_caixas - Dados de Vendas
print("\n" + "=" * 80)
print("💰 2. TODOS_OS_CAIXAS (Dados de Vendas)")
print("-" * 80)

try:
    arquivo_caixas = 'data/todos_os_caixas_original.xlsx'
    
    if os.path.exists(arquivo_caixas):
        xls_caixas = pd.ExcelFile(arquivo_caixas)
        print(f"✅ Arquivo encontrado: {arquivo_caixas}")
        print(f"📑 Abas disponíveis ({len(xls_caixas.sheet_names)}): {xls_caixas.sheet_names}")
        
        total_registros = 0
        total_valores = 0
        
        for aba in xls_caixas.sheet_names:
            df_aba = pd.read_excel(arquivo_caixas, sheet_name=aba)
            registros = len(df_aba)
            total_registros += registros
            
            # Tentar encontrar coluna de valores
            colunas_valor = [c for c in df_aba.columns if 'valor' in c.lower() or 'total' in c.lower()]
            valor_aba = 0
            
            if colunas_valor:
                try:
                    valor_aba = df_aba[colunas_valor[0]].sum()
                    total_valores += valor_aba
                except:
                    pass
            
            print(f"\n   📄 {aba}:")
            print(f"      - Registros: {registros:,}")
            if valor_aba > 0:
                print(f"      - Valor Total: R$ {valor_aba:,.2f}")
            print(f"      - Colunas ({len(df_aba.columns)}): {list(df_aba.columns)}")
        
        print(f"\n📊 TOTAIS:")
        print(f"   - Total de registros: {total_registros:,}")
        if total_valores > 0:
            print(f"   - Valor total: R$ {total_valores:,.2f}")
        
    else:
        print(f"❌ Arquivo não encontrado: {arquivo_caixas}")
        
except Exception as e:
    print(f"❌ Erro ao ler todos_os_caixas: {e}")

# 3. RECOMENDAÇÃO
print("\n" + "=" * 80)
print("💡 RECOMENDAÇÃO PARA MODELO SIMPLIFICADO")
print("=" * 80)

print("""
Com base nos dados REAIS que temos, o banco deveria ter:

🎯 MODELO ENXUTO:

1. TABELA: clientes (fonte: OS_NOVA)
   - id (UUID)
   - nome
   - cpf
   - telefone
   - endereco
   - cidade
   
2. TABELA: vendas (fonte: todos_os_caixas - aba 'vend')
   - id (UUID)
   - cliente_id (FK -> clientes)
   - data_venda
   - loja
   - valor_total
   - forma_pagamento
   - os_numero (OS do sistema)
   
3. TABELA: recebimentos (fonte: todos_os_caixas - aba 'rec_carn')
   - id (UUID)
   - venda_id (FK -> vendas)
   - data_recebimento
   - valor_recebido
   
4. TABELA: entregas (fonte: todos_os_caixas - aba 'os_entr_dia')
   - id (UUID)
   - os_numero
   - data_entrega
   - loja

⚠️ EVITAR:
- Schemas complexos demais
- Muitas tabelas de auditoria antes de ter o básico funcionando
- Normalização excessiva

✅ FOCO:
- Começar simples e funcional
- 4 tabelas principais
- Importar dados reais
- Testar queries básicas
- Depois expandir conforme necessidade
""")

print("\n" + "=" * 80)
