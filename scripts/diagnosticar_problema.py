#!/usr/bin/env python3
"""
Script para diagnosticar problema de processamento
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

def diagnosticar_problema():
    """Diagnostica o problema de processamento de dados"""
    
    print("🔍 DIAGNÓSTICO DO PROBLEMA DE PROCESSAMENTO")
    print("=" * 60)
    
    # Verificar arquivos disponíveis
    arquivos_raw = list(Path("data/raw").glob("*.xlsx"))
    print(f"📁 Arquivos disponíveis: {len(arquivos_raw)}")
    
    for arquivo in arquivos_raw:
        print(f"  • {arquivo.name}")
    
    if not arquivos_raw:
        print("❌ Nenhum arquivo encontrado!")
        return
    
    # Testar com o primeiro arquivo
    arquivo_teste = arquivos_raw[0]
    print(f"\n🔬 ANALISANDO: {arquivo_teste.name}")
    print("-" * 40)
    
    # 1. Leitura básica com pandas
    print("1️⃣ LEITURA BÁSICA")
    try:
        df_basic = pd.read_excel(arquivo_teste, engine='openpyxl')
        print(f"   ✅ Leitura básica: {len(df_basic)} linhas, {len(df_basic.columns)} colunas")
        print(f"   📋 Colunas: {list(df_basic.columns)}")
        
        # Verificar dados não vazios
        linhas_com_dados = df_basic.dropna(how='all')
        print(f"   📊 Linhas com dados: {len(linhas_com_dados)}")
        
    except Exception as e:
        print(f"   ❌ Erro na leitura básica: {e}")
        return
    
    # 2. Verificar sheets disponíveis
    print("\n2️⃣ SHEETS DISPONÍVEIS")
    try:
        excel_file = pd.ExcelFile(arquivo_teste, engine='openpyxl')
        sheets = excel_file.sheet_names
        print(f"   📄 Sheets encontrados: {sheets}")
        
        for sheet in sheets:
            try:
                df_sheet = pd.read_excel(arquivo_teste, sheet_name=sheet, engine='openpyxl')
                print(f"   📊 {sheet}: {len(df_sheet)} linhas, {len(df_sheet.columns)} colunas")
            except Exception as e:
                print(f"   ⚠️ {sheet}: Erro ao ler - {e}")
                
    except Exception as e:
        print(f"   ❌ Erro ao verificar sheets: {e}")
    
    # 3. Testar com AnalisadorOS
    print("\n3️⃣ TESTE COM ANALISADOR OS")
    try:
        sys.path.append('.')
        from scripts.analisar_os import AnalisadorOS
        
        analisador = AnalisadorOS()
        
        # Carregar com o analisador
        df_analisador = analisador.carregar_planilha(arquivo_teste)
        print(f"   ✅ Analisador carregou: {len(df_analisador)} linhas")
        
        # Processar
        resultado = analisador.processar_arquivo(arquivo_teste)
        print(f"   📊 Status: {resultado['status']}")
        print(f"   📊 Linhas originais: {resultado['linhas_original']}")
        print(f"   📊 Linhas processadas: {resultado['linhas_processadas']}")
        print(f"   📊 Colunas encontradas: {resultado['colunas_encontradas']}")
        print(f"   📊 Colunas mapeadas: {resultado['colunas_mapeadas']}")
        
        if resultado['erros']:
            print(f"   ⚠️ Erros: {resultado['erros']}")
            
    except Exception as e:
        print(f"   ❌ Erro no AnalisadorOS: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Análise detalhada dos dados
    print("\n4️⃣ ANÁLISE DETALHADA DOS DADOS")
    print("-" * 40)
    
    # Usar o DataFrame carregado
    df = df_basic
    
    print(f"📊 Informações básicas:")
    print(f"   • Shape: {df.shape}")
    print(f"   • Colunas: {len(df.columns)}")
    print(f"   • Linhas totais: {len(df)}")
    
    # Verificar linhas vazias
    linhas_vazias = df.isna().all(axis=1).sum()
    print(f"   • Linhas completamente vazias: {linhas_vazias}")
    
    # Verificar dados por coluna
    print(f"\n📋 Dados por coluna:")
    for col in df.columns:
        valores_nao_nulos = df[col].count()
        valores_unicos = df[col].nunique()
        print(f"   • {col}: {valores_nao_nulos} valores, {valores_unicos} únicos")
    
    # Verificar colunas de OS
    print(f"\n🔍 Análise de colunas de OS:")
    colunas_os = [col for col in df.columns if 'OS' in str(col).upper()]
    
    if colunas_os:
        for col in colunas_os:
            valores_validos = df[col].dropna()
            valores_numericos = pd.to_numeric(valores_validos, errors='coerce').dropna()
            
            print(f"   📈 {col}:")
            print(f"      • Total valores: {len(valores_validos)}")
            print(f"      • Valores numéricos: {len(valores_numericos)}")
            
            if len(valores_numericos) > 0:
                print(f"      • Range: {valores_numericos.min():.0f} - {valores_numericos.max():.0f}")
                print(f"      • Únicos: {valores_numericos.nunique()}")
    else:
        print("   ⚠️ Nenhuma coluna de OS encontrada!")
    
    # 5. Verificar filtros que podem estar removendo dados
    print("\n5️⃣ VERIFICAÇÃO DE FILTROS")
    print("-" * 40)
    
    # Simular processamento step by step
    df_original = df.copy()
    print(f"   📊 Dados originais: {len(df_original)} linhas")
    
    # Remover linhas vazias (como faz o AnalisadorOS)
    df_filtrado = df_original.dropna(how='all')
    print(f"   📊 Após remover linhas vazias: {len(df_filtrado)} linhas")
    
    # Verificar se há algum outro filtro sendo aplicado
    # Procurar por filtros no código do AnalisadorOS
    print(f"   💡 Diferença: {len(df_original) - len(df_filtrado)} linhas removidas por estar vazias")
    
    if len(df_filtrado) > 100:
        print(f"   ✅ Ainda há {len(df_filtrado)} linhas com dados - problema pode estar em outra etapa")
    else:
        print(f"   ⚠️ Apenas {len(df_filtrado)} linhas restaram - investigar filtros adicionais")
    
    # 6. Mostrar amostra dos dados
    print("\n6️⃣ AMOSTRA DOS DADOS")
    print("-" * 40)
    
    print("🔍 Primeiras 5 linhas:")
    print(df_filtrado.head().to_string())
    
    print(f"\n🔍 Últimas 5 linhas:")
    print(df_filtrado.tail().to_string())

if __name__ == "__main__":
    diagnosticar_problema()