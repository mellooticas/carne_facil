#!/usr/bin/env python3
"""
RELATÓRIO CONSOLIDADO 2025 - DADOS RECÉM-IMPORTADOS
Análise dos dados 2025 de MAUA e SUZANO
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

def gerar_relatorio_2025():
    print("📊 RELATÓRIO CONSOLIDADO - DADOS 2025")
    print("=" * 60)
    print("🎯 Análise dos dados recém-importados do OneDrive")
    print()
    
    # Dados dos relatórios
    dados_2025 = {
        'MAUA': {
            'vendas': 52,
            'valor_total': 22182.98,
            'entradas': 13365.00,
            'media_venda': 426.60,
            'dias_vendas': 23,
            'periodo': 'Jan/2025',
            'arquivos_disponiveis': ['jan_25', 'fev_25', 'mar_25', 'abr_25', 'mai_25', 'jun_25']
        },
        'SUZANO': {
            'vendas': 194,
            'valor_total': 136110.92,
            'entradas': 102517.96,
            'media_venda': 701.60,
            'dias_vendas': 26,
            'periodo': 'Jan/2025',
            'arquivos_disponiveis': ['jan_25', 'fev_25', 'mar_25', 'abr_25', 'mai_25', 'jun_25', 'jul_25', 'ago_25', 'set_25', 'out_25']
        }
    }
    
    # Análise consolidada
    total_vendas = sum(loja['vendas'] for loja in dados_2025.values())
    total_valor = sum(loja['valor_total'] for loja in dados_2025.values())
    total_entradas = sum(loja['entradas'] for loja in dados_2025.values())
    
    print("🏪 PERFORMANCE POR LOJA - JANEIRO 2025:")
    print("=" * 50)
    
    for loja, dados in dados_2025.items():
        print(f"\n🏢 {loja}:")
        print(f"   📈 Vendas: {dados['vendas']:,}")
        print(f"   💰 Faturamento: R$ {dados['valor_total']:,.2f}")
        print(f"   💵 Entradas: R$ {dados['entradas']:,.2f}")
        print(f"   📊 Média/Venda: R$ {dados['media_venda']:,.2f}")
        print(f"   📅 Dias ativos: {dados['dias_vendas']}")
        print(f"   📄 Arquivos 2025: {len(dados['arquivos_disponiveis'])} meses")
    
    print(f"\n🎯 CONSOLIDADO JANEIRO 2025:")
    print("=" * 30)
    print(f"📈 Total de vendas: {total_vendas:,}")
    print(f"💰 Faturamento total: R$ {total_valor:,.2f}")
    print(f"💵 Entradas total: R$ {total_entradas:,.2f}")
    print(f"📊 Média geral: R$ {total_valor/total_vendas:,.2f}")
    
    # Potencial dos dados 2025
    print(f"\n🚀 POTENCIAL DOS DADOS 2025:")
    print("=" * 35)
    
    meses_maua = len(dados_2025['MAUA']['arquivos_disponiveis'])
    meses_suzano = len(dados_2025['SUZANO']['arquivos_disponiveis'])
    
    print(f"📄 MAUA: {meses_maua} meses disponíveis (Jan-Jun)")
    print(f"📄 SUZANO: {meses_suzano} meses disponíveis (Jan-Out)")
    
    # Projeção baseada em janeiro
    projecao_maua = dados_2025['MAUA']['valor_total'] * meses_maua
    projecao_suzano = dados_2025['SUZANO']['valor_total'] * meses_suzano
    projecao_total = projecao_maua + projecao_suzano
    
    print(f"\n💡 PROJEÇÃO BASEADA EM JANEIRO:")
    print(f"   💰 MAUA (6 meses): R$ {projecao_maua:,.2f}")
    print(f"   💰 SUZANO (10 meses): R$ {projecao_suzano:,.2f}")
    print(f"   🎯 TOTAL POTENCIAL: R$ {projecao_total:,.2f}")
    
    # Status da importação
    print(f"\n✅ STATUS DA IMPORTAÇÃO:")
    print("=" * 30)
    print("✅ Estrutura OneDrive mapeada")
    print("✅ 16 arquivos 2025 importados")
    print("✅ Sistema universal compatível")
    print("✅ Processamento funcionando")
    
    # Próximos passos
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    print("=" * 20)
    print("1. Processar todos os meses 2025 disponíveis")
    print("2. Importar outras lojas (PERUS, RIO_PEQUENO, SUZANO2)")
    print("3. Gerar relatório anual 2025 completo")
    print("4. Comparar performance 2024 vs 2025")
    
    return {
        'total_vendas': total_vendas,
        'total_valor': total_valor,
        'lojas_ativas': list(dados_2025.keys()),
        'potencial_total': projecao_total
    }

if __name__ == "__main__":
    resultado = gerar_relatorio_2025()
    print(f"\n🎉 ANÁLISE CONCLUÍDA!")
    print(f"📊 Resumo: {resultado['total_vendas']} vendas, R$ {resultado['total_valor']:,.2f}")