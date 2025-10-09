#!/usr/bin/env python3
"""
Análise detalhada de duplicações entre lojas operacionais
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict

def analisar_duplicacoes_detalhadas():
    """Analisa duplicações entre lojas com detalhes"""
    
    print("🔍 ANÁLISE DETALHADA DE DUPLICAÇÕES")
    print("="*70)
    
    # Carregar dados consolidados
    arquivo_consolidado = Path("data/processed/lojas_operacionais_consolidado.xlsx")
    df = pd.read_excel(arquivo_consolidado)
    
    print(f"📊 Total de registros analisados: {len(df):,}")
    print()
    
    # Análise de duplicações por número de OS
    print("🔍 DUPLICAÇÕES POR NÚMERO DE OS")
    print("-" * 50)
    
    # Contar quantas vezes cada OS aparece
    os_counts = df['numero_os'].value_counts()
    duplicados = os_counts[os_counts > 1]
    
    print(f"📊 Total de OS únicos: {len(os_counts):,}")
    print(f"⚠️ OS duplicados: {len(duplicados):,}")
    print(f"📈 Registros duplicados: {duplicados.sum():,}")
    print()
    
    if len(duplicados) > 0:
        print("🏆 TOP 10 OS MAIS DUPLICADOS")
        print("-" * 30)
        for os_num, count in duplicados.head(10).items():
            lojas_com_os = df[df['numero_os'] == os_num]['loja'].tolist()
            colunas_origem = df[df['numero_os'] == os_num]['coluna_origem'].tolist()
            print(f"   OS {os_num}: {count}x - Lojas: {', '.join(set(lojas_com_os))}")
            print(f"     Colunas: {', '.join(set(colunas_origem))}")
        print()
    
    # Análise de sobreposições entre lojas
    print("🏪 SOBREPOSIÇÕES ENTRE LOJAS")
    print("-" * 40)
    
    lojas = df['loja'].unique()
    matriz_sobreposicoes = defaultdict(lambda: defaultdict(int))
    
    # Para cada OS, verificar em quais lojas aparece
    for os_num in df['numero_os'].unique():
        lojas_desta_os = df[df['numero_os'] == os_num]['loja'].unique()
        
        # Se aparece em mais de uma loja, contar sobreposições
        if len(lojas_desta_os) > 1:
            for loja1 in lojas_desta_os:
                for loja2 in lojas_desta_os:
                    if loja1 != loja2:
                        matriz_sobreposicoes[loja1][loja2] += 1
    
    # Mostrar matriz de sobreposições
    print("📊 Matriz de OS compartilhadas:")
    print(f"{'':15}", end="")
    for loja in sorted(lojas):
        print(f"{loja:>12}", end="")
    print()
    
    for loja1 in sorted(lojas):
        print(f"{loja1:15}", end="")
        for loja2 in sorted(lojas):
            if loja1 == loja2:
                print(f"{'---':>12}", end="")
            else:
                count = matriz_sobreposicoes[loja1][loja2]
                print(f"{count:>12}", end="")
        print()
    print()
    
    # Análise por fonte de dados (coluna_origem)
    print("📊 ANÁLISE POR FONTE DE DADOS")
    print("-" * 40)
    
    fonte_stats = df.groupby(['loja', 'coluna_origem']).size().unstack(fill_value=0)
    print("📈 Distribuição por fonte:")
    print(fonte_stats)
    print()
    
    # Verificar se há padrões nos números de OS
    print("📈 PADRÕES NOS NÚMEROS DE OS")
    print("-" * 40)
    
    for loja in sorted(df['loja'].unique()):
        loja_data = df[df['loja'] == loja]
        
        print(f"🏪 {loja}:")
        print(f"   📊 Total de OS: {len(loja_data):,}")
        
        for origem in loja_data['coluna_origem'].unique():
            origem_data = loja_data[loja_data['coluna_origem'] == origem]
            os_numbers = origem_data['numero_os'].values
            
            print(f"   📋 {origem}:")
            print(f"      • Quantidade: {len(os_numbers):,}")
            print(f"      • Faixa: {min(os_numbers):,} - {max(os_numbers):,}")
            print(f"      • Amplitude: {max(os_numbers) - min(os_numbers) + 1:,}")
            
            # Verificar se é sequencial
            if len(os_numbers) > 1:
                sorted_numbers = sorted(os_numbers)
                gaps = []
                for i in range(1, len(sorted_numbers)):
                    gap = sorted_numbers[i] - sorted_numbers[i-1]
                    if gap > 1:
                        gaps.append(gap)
                
                if not gaps:
                    print(f"      • Padrão: ✅ Sequencial completo")
                else:
                    print(f"      • Padrão: ⚠️ {len(gaps)} lacunas (maior: {max(gaps)})")
        print()
    
    # Identificar possíveis problemas
    print("🚨 POSSÍVEIS PROBLEMAS IDENTIFICADOS")
    print("-" * 50)
    
    problemas = []
    
    # Problema 1: OS duplicados entre lojas
    if len(duplicados) > 0:
        problemas.append(f"📍 {len(duplicados):,} OS aparecem em múltiplas lojas")
        
        # Verificar se são da mesma fonte
        for os_num in duplicados.head(5).index:
            os_data = df[df['numero_os'] == os_num]
            if len(os_data['coluna_origem'].unique()) > 1:
                problemas.append(f"   ⚠️ OS {os_num} aparece em fontes diferentes: {', '.join(os_data['coluna_origem'].unique())}")
    
    # Problema 2: Sobreposições excessivas
    for loja1 in lojas:
        for loja2 in lojas:
            if loja1 < loja2:  # Evitar duplicação na comparação
                overlap = matriz_sobreposicoes[loja1][loja2]
                if overlap > 100:  # Limite arbitrário
                    problemas.append(f"📍 Alta sobreposição: {loja1} ↔ {loja2} ({overlap} OS)")
    
    if problemas:
        for problema in problemas:
            print(problema)
    else:
        print("✅ Nenhum problema crítico identificado")
    
    print()
    print("🎯 RECOMENDAÇÕES")
    print("-" * 20)
    print("1. 🔍 Investigar se OS duplicados são:")
    print("   • Ordens transferidas entre lojas")
    print("   • Erros de importação")
    print("   • Diferentes sistemas de numeração")
    print()
    print("2. 📋 Verificar se existem outros arquivos com:")
    print("   • Dados de clientes")
    print("   • Detalhes das ordens")
    print("   • Histórico de transferências")
    print()
    print("3. 🎯 Focar na implementação de:")
    print("   • Deduplicação inteligente")
    print("   • Rastreamento de origem")
    print("   • Consolidação por cliente")

if __name__ == "__main__":
    analisar_duplicacoes_detalhadas()