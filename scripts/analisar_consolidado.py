#!/usr/bin/env python3
"""
Análise dos dados consolidados das lojas operacionais
"""

import pandas as pd
import numpy as np
from pathlib import Path

def analisar_dados_consolidados():
    """Analisa o arquivo consolidado das lojas operacionais"""
    
    print("🔍 ANÁLISE DOS DADOS CONSOLIDADOS")
    print("="*60)
    
    # Caminho do arquivo consolidado
    arquivo_consolidado = Path("data/processed/lojas_operacionais_consolidado.xlsx")
    
    if not arquivo_consolidado.exists():
        print("❌ Arquivo consolidado não encontrado!")
        return
    
    # Carregar dados
    print("📂 Carregando dados consolidados...")
    df = pd.read_excel(arquivo_consolidado)
    
    print(f"📊 Total de registros: {len(df):,}")
    print(f"📊 Total de colunas: {len(df.columns)}")
    print()
    
    # Estrutura dos dados
    print("📋 ESTRUTURA DOS DADOS")
    print("-" * 40)
    print("🏷️ Colunas disponíveis:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i:2d}. {col}")
    print()
    
    # Primeiras linhas
    print("👀 PRIMEIRAS 10 LINHAS")
    print("-" * 40)
    print(df.head(10).to_string())
    print()
    
    # Estatísticas por loja
    if 'loja' in df.columns:
        print("📊 ESTATÍSTICAS POR LOJA")
        print("-" * 40)
        
        stats_loja = df.groupby('loja').agg({
            'loja': 'count',  # Total de registros
        }).rename(columns={'loja': 'total_registros'})
        
        # Verificar se há colunas de OS
        for col in ['OS_LANCASTER', 'OS_OTM', 'os_lancaster', 'os_otm']:
            if col in df.columns:
                stats_loja[f'{col}_validas'] = df.groupby('loja')[col].count()
                stats_loja[f'{col}_min'] = df.groupby('loja')[col].min()
                stats_loja[f'{col}_max'] = df.groupby('loja')[col].max()
        
        print(stats_loja)
        print()
    
    # Verificar duplicações
    print("🔍 ANÁLISE DE DUPLICAÇÕES")
    print("-" * 40)
    
    # Duplicações por OS LANCASTER
    for col in ['OS_LANCASTER', 'os_lancaster']:
        if col in df.columns:
            duplicados = df[df[col].duplicated(keep=False)]
            if not duplicados.empty:
                print(f"⚠️ {col}: {len(duplicados)} registros duplicados")
                print("   Exemplos de duplicações:")
                exemplos = duplicados.groupby(col)['loja'].apply(list).head(5)
                for os_num, lojas in exemplos.items():
                    print(f"     OS {os_num}: {', '.join(lojas)}")
            else:
                print(f"✅ {col}: Sem duplicações")
    
    # Duplicações por OS OTM
    for col in ['OS_OTM', 'os_otm']:
        if col in df.columns:
            duplicados = df[df[col].duplicated(keep=False)]
            if not duplicados.empty:
                print(f"⚠️ {col}: {len(duplicados)} registros duplicados")
                print("   Exemplos de duplicações:")
                exemplos = duplicados.groupby(col)['loja'].apply(list).head(5)
                for os_num, lojas in exemplos.items():
                    print(f"     OS {os_num}: {', '.join(lojas)}")
            else:
                print(f"✅ {col}: Sem duplicações")
    
    print()
    
    # Valores únicos em colunas categóricas
    print("📊 VALORES ÚNICOS")
    print("-" * 40)
    
    for col in df.columns:
        if df[col].dtype == 'object' or df[col].nunique() <= 20:
            valores_unicos = df[col].value_counts()
            print(f"🏷️ {col}:")
            print(f"   Total de valores únicos: {df[col].nunique()}")
            if df[col].nunique() <= 10:
                print("   Valores:")
                for valor, count in valores_unicos.items():
                    print(f"     • {valor}: {count}")
            else:
                print("   Top 5 valores:")
                for valor, count in valores_unicos.head().items():
                    print(f"     • {valor}: {count}")
            print()
    
    # Verificar dados nulos
    print("🔍 DADOS NULOS")
    print("-" * 40)
    nulos = df.isnull().sum()
    nulos_perc = (nulos / len(df) * 100).round(2)
    
    for col in df.columns:
        if nulos[col] > 0:
            print(f"⚠️ {col}: {nulos[col]} nulos ({nulos_perc[col]}%)")
        else:
            print(f"✅ {col}: Sem dados nulos")
    
    print("\n🎉 Análise concluída!")

if __name__ == "__main__":
    analisar_dados_consolidados()