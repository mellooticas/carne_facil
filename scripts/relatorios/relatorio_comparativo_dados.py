#!/usr/bin/env python3
"""
Relatório Comparativo - Dados Corretos vs Anteriores
Compara os novos dados completos com as análises anteriores
"""

import pandas as pd
import os
from datetime import datetime

def gerar_relatorio_comparativo():
    """Gerar relatório comparativo dos dados"""
    
    print("📊 RELATÓRIO COMPARATIVO - DADOS CORRETOS vs ANTERIORES")
    print("="*70)
    
    # Carregar dados corretos das 5 abas
    pasta_caixas = 'data/caixas_processados'
    timestamp = '20251010_211625'
    
    arquivos_corretos = {
        'vendas': f'VEND_COMPLETO_{timestamp}.xlsx',
        'rec_carne': f'REC_CARN_COMPLETO_{timestamp}.xlsx', 
        'os_entrega': f'OS_ENTR_DIA_COMPLETO_{timestamp}.xlsx',
        'entr_carne': f'ENTR_CARN_COMPLETO_{timestamp}.xlsx',
        'rest_entr': f'REST_ENTR_COMPLETO_{timestamp}.xlsx'
    }
    
    dados_corretos = {}
    for tipo, arquivo in arquivos_corretos.items():
        caminho = os.path.join(pasta_caixas, arquivo)
        if os.path.exists(caminho):
            dados_corretos[tipo] = pd.read_excel(caminho)
    
    print(f"\n🎯 DADOS CORRETOS CARREGADOS:")
    total_registros = 0
    for tipo, df in dados_corretos.items():
        print(f"   {tipo.upper()}: {len(df):,} registros")
        total_registros += len(df)
    print(f"   TOTAL: {total_registros:,} registros")
    
    # Análise detalhada das VENDAS (principal descoberta)
    if 'vendas' in dados_corretos:
        df_vendas = dados_corretos['vendas']
        
        # Converter valores numéricos
        df_vendas['Valor Venda'] = pd.to_numeric(df_vendas['Valor Venda'], errors='coerce')
        df_vendas['Entrada'] = pd.to_numeric(df_vendas['Entrada'], errors='coerce')
        
        print(f"\n💰 ANÁLISE FINANCEIRA - VENDAS CORRETAS:")
        valor_venda_total = df_vendas['Valor Venda'].sum()
        entrada_total = df_vendas['Entrada'].sum()
        print(f"   Valor Venda Total: R$ {valor_venda_total:,.2f}")
        print(f"   Entrada Total: R$ {entrada_total:,.2f}")
        print(f"   TOTAL MOVIMENTADO: R$ {valor_venda_total + entrada_total:,.2f}")
        
        # Comparação com dados anteriores
        print(f"\n📈 COMPARAÇÃO COM DADOS ANTERIORES:")
        valor_anterior = 4153525.89  # Valor das vendas processadas anteriormente
        entrada_anterior = 134.00    # Valor rest_entr processado anteriormente
        
        print(f"   Vendas Anteriores: R$ {valor_anterior:,.2f}")
        print(f"   Vendas Corretas: R$ {valor_venda_total:,.2f}")
        diferenca_vendas = valor_venda_total - valor_anterior
        print(f"   Diferença Vendas: R$ {diferenca_vendas:,.2f} ({diferenca_vendas/valor_anterior*100:+.1f}%)")
        
        print(f"\n   Entradas Anteriores: R$ {entrada_anterior:,.2f}")
        print(f"   Entradas Corretas: R$ {entrada_total:,.2f}")
        diferenca_entradas = entrada_total - entrada_anterior
        print(f"   Diferença Entradas: R$ {diferenca_entradas:,.2f} ({diferenca_entradas/entrada_anterior*100:+.1f}%)")
        
        total_anterior = valor_anterior + entrada_anterior
        total_correto = valor_venda_total + entrada_total
        diferenca_total = total_correto - total_anterior
        print(f"\n   TOTAL Anterior: R$ {total_anterior:,.2f}")
        print(f"   TOTAL Correto: R$ {total_correto:,.2f}")
        print(f"   DIFERENÇA TOTAL: R$ {diferenca_total:,.2f} ({diferenca_total/total_anterior*100:+.1f}%)")
        
        # Distribuição por loja
        print(f"\n🏢 DISTRIBUIÇÃO POR LOJA - DADOS CORRETOS:")
        for loja in df_vendas['Loja'].unique():
            loja_df = df_vendas[df_vendas['Loja'] == loja]
            count = len(loja_df)
            valor_total = loja_df['Valor Venda'].sum()
            entrada_total_loja = loja_df['Entrada'].sum()
            total_loja = valor_total + entrada_total_loja
            print(f"   {loja}: {count:,} vendas | Total: R$ {total_loja:,.2f}")
    
    # Análise dos outros tipos de dados
    print(f"\n📋 OUTROS DADOS IMPORTANTES:")
    
    if 'rec_carne' in dados_corretos:
        df_rec = dados_corretos['rec_carne']
        df_rec['Valor Parcela'] = pd.to_numeric(df_rec['Valor Parcela'], errors='coerce')
        rec_total = df_rec['Valor Parcela'].sum()
        print(f"   Recebimento Carnês: R$ {rec_total:,.2f} ({len(df_rec):,} registros)")
    
    if 'entr_carne' in dados_corretos:
        df_entr = dados_corretos['entr_carne']
        df_entr['Valor Total'] = pd.to_numeric(df_entr['Valor Total'], errors='coerce')
        entr_total = df_entr['Valor Total'].sum()
        print(f"   Entrega Carnês: R$ {entr_total:,.2f} ({len(df_entr):,} registros)")
    
    if 'os_entrega' in dados_corretos:
        df_os = dados_corretos['os_entrega']
        print(f"   Entrega OSs: {len(df_os):,} entregas")
    
    if 'rest_entr' in dados_corretos:
        df_rest = dados_corretos['rest_entr']
        df_rest['Entrada'] = pd.to_numeric(df_rest['Entrada'], errors='coerce')
        rest_total = df_rest['Entrada'].sum()
        print(f"   Restantes Entradas: R$ {rest_total:,.2f} ({len(df_rest):,} registros)")
    
    # Resumo final
    print(f"\n" + "="*70)
    print(f"🎯 RESUMO EXECUTIVO:")
    print(f"   ✅ DESCOBERTA: Coluna 'Entrada' estava sendo perdida")
    print(f"   ✅ CORREÇÃO: Dados completos agora disponíveis")
    print(f"   ✅ IMPACTO: Aumento significativo nos valores totais")
    print(f"   ✅ PRÓXIMO: Processar demais tabelas para documento final")
    
    return dados_corretos

if __name__ == "__main__":
    dados = gerar_relatorio_comparativo()