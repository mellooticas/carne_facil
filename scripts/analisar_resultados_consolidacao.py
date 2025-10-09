#!/usr/bin/env python3
"""
Script para analisar os resultados da consolidação inteligente
"""

import pandas as pd
from pathlib import Path

def analisar_resultados():
    """Analisa os resultados da consolidação"""
    
    print("📊 ANÁLISE DOS RESULTADOS DA CONSOLIDAÇÃO INTELIGENTE")
    print("=" * 80)
    
    arquivo = Path("data/processed/base_consolidada_inteligente.xlsx")
    
    if not arquivo.exists():
        print("❌ Arquivo de resultados não encontrado!")
        return
    
    # Carregar dados
    print("📁 Carregando resultados...")
    
    try:
        # Base consolidada
        df_consolidado = pd.read_excel(arquivo, sheet_name='base_consolidada')
        print(f"✅ Base consolidada: {len(df_consolidado)} registros")
        
        # Relatório de mesclagens
        df_mesclagens = pd.read_excel(arquivo, sheet_name='relatorio_mesclagens')
        print(f"✅ Relatório de mesclagens: {len(df_mesclagens)} grupos")
        
        # Estatísticas
        df_stats = pd.read_excel(arquivo, sheet_name='estatisticas')
        print(f"✅ Estatísticas carregadas")
        
    except Exception as e:
        print(f"❌ Erro ao carregar: {e}")
        return
    
    # Análise da qualidade dos dados
    print(f"\n🔍 QUALIDADE DOS DADOS CONSOLIDADOS")
    print("-" * 50)
    
    # Completude dos campos
    campos_importantes = ['nome', 'cpf', 'telefone', 'email', 'endereco']
    
    for campo in campos_importantes:
        if campo in df_consolidado.columns:
            preenchidos = df_consolidado[campo].notna().sum()
            total = len(df_consolidado)
            percentual = (preenchidos / total) * 100
            print(f"   📋 {campo.capitalize()}: {preenchidos:,}/{total:,} ({percentual:.1f}%)")
    
    # Análise de mesclagens
    print(f"\n🔄 ANÁLISE DE MESCLAGENS")
    print("-" * 50)
    
    if len(df_mesclagens) > 0:
        # Estatísticas de mesclagem
        total_registros_mesclados = df_mesclagens['registros_mesclados'].sum()
        media_mesclagem = df_mesclagens['registros_mesclados'].mean()
        max_mesclagem = df_mesclagens['registros_mesclados'].max()
        
        print(f"   📊 Total de registros mesclados: {total_registros_mesclados:,}")
        print(f"   📊 Média de registros por grupo: {media_mesclagem:.1f}")
        print(f"   📊 Maior grupo mesclado: {max_mesclagem} registros")
        
        # Top 10 mesclagens
        print(f"\n🏆 TOP 10 MAIORES MESCLAGENS:")
        top_10 = df_mesclagens.nlargest(10, 'registros_mesclados')
        
        for i, row in top_10.iterrows():
            nome = str(row['nome_final'])[:30] + "..." if len(str(row['nome_final'])) > 30 else str(row['nome_final'])
            print(f"   {i+1:2d}. {nome:<35} - {row['registros_mesclados']} registros → {row['total_os']} OS")
    
    # Análise de OS
    print(f"\n📝 ANÁLISE DE ORDENS DE SERVIÇO")
    print("-" * 50)
    
    # Clientes com múltiplas OS
    clientes_multiplas_os = df_consolidado[df_consolidado['total_os'] > 1]
    print(f"   👥 Clientes com múltiplas OS: {len(clientes_multiplas_os):,}")
    
    if len(clientes_multiplas_os) > 0:
        media_os = clientes_multiplas_os['total_os'].mean()
        max_os = clientes_multiplas_os['total_os'].max()
        print(f"   📊 Média de OS por cliente (múltiplas): {media_os:.1f}")
        print(f"   📊 Cliente com mais OS: {max_os} ordens")
        
        # Top clientes por número de OS
        print(f"\n🎯 TOP 5 CLIENTES POR NÚMERO DE OS:")
        top_os = clientes_multiplas_os.nlargest(5, 'total_os')
        
        for i, row in top_os.iterrows():
            nome = str(row['nome'])[:40] + "..." if len(str(row['nome'])) > 40 else str(row['nome'])
            cpf = str(row['cpf']) if pd.notna(row['cpf']) else "Sem CPF"
            print(f"   {i+1}. {nome:<45} - {row['total_os']} OS (CPF: {cpf})")
    
    # Estatísticas gerais
    print(f"\n📈 ESTATÍSTICAS GERAIS")
    print("-" * 50)
    
    for _, row in df_stats.iterrows():
        print(f"   📊 {row['Métrica']}: {row['Valor']}")
    
    # Verificar dados de exemplo
    print(f"\n🔍 AMOSTRA DE DADOS CONSOLIDADOS")
    print("-" * 50)
    
    # Mostrar 3 exemplos de registros mesclados
    exemplos = df_consolidado[df_consolidado['total_registros_mesclados'] > 5].head(3)
    
    for i, row in exemplos.iterrows():
        print(f"\n   📋 Exemplo {i+1}:")
        print(f"      Nome: {row['nome']}")
        print(f"      CPF: {row.get('cpf', 'N/A')}")
        print(f"      Telefone: {row.get('telefone', 'N/A')}")
        print(f"      Email: {row.get('email', 'N/A')}")
        print(f"      Registros mesclados: {row['total_registros_mesclados']}")
        print(f"      Total de OS: {row['total_os']}")
        
        if pd.notna(row.get('os_numeros')):
            os_nums = str(row['os_numeros'])
            os_preview = os_nums[:50] + "..." if len(os_nums) > 50 else os_nums
            print(f"      OS: {os_preview}")

def main():
    analisar_resultados()

if __name__ == "__main__":
    main()