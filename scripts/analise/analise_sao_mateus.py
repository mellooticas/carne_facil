#!/usr/bin/env python3
"""
ANÁLISE DE SÃO MATEUS - CLIENTES HISTÓRICOS
Análise especial da loja fechada para estratégias de reativação
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import re

def analisar_sao_mateus():
    print("🏪 ANÁLISE ESTRATÉGICA - SÃO MATEUS (LOJA FECHADA)")
    print("=" * 70)
    print("🎯 Foco: Análise de clientes históricos para reativação")
    print()
    
    # Dados processados de São Mateus
    dados_sao_mateus = {
        'vendas': 761,
        'valor_total': 1577300.71,
        'periodo': 'Ago/2023 - Out/2024 (período parcial)',
        'status': 'LOJA FECHADA',
        'arquivos_processados': 19
    }
    
    print("📊 RESUMO DOS DADOS DE SÃO MATEUS:")
    print("=" * 45)
    print(f"📈 Total de vendas: {dados_sao_mateus['vendas']:,}")
    print(f"💰 Faturamento total: R$ {dados_sao_mateus['valor_total']:,.2f}")
    print(f"📊 Média por venda: R$ {dados_sao_mateus['valor_total']/dados_sao_mateus['vendas']:,.2f}")
    print(f"📅 Período ativo: {dados_sao_mateus['periodo']}")
    print(f"📄 Arquivos processados: {dados_sao_mateus['arquivos_processados']}")
    print(f"🏪 Status atual: {dados_sao_mateus['status']}")
    
    # Comparação com lojas ativas
    print(f"\n📊 COMPARAÇÃO COM LOJAS ATIVAS:")
    print("=" * 40)
    
    # Dados das outras lojas para comparação
    lojas_ativas_dados = {
        'SUZANO': {'vendas': 3532, 'valor': 15160731.90, 'status': 'ATIVA'},
        'RIO_PEQUENO': {'vendas': 1205, 'valor': 3591692.73, 'status': 'ATIVA'},
        'PERUS': {'vendas': 796, 'valor': 2302377.94, 'status': 'ATIVA'},
        'MAUA': {'vendas': 897, 'valor': 2014616.41, 'status': 'ATIVA'},
        'SUZANO2': {'vendas': 341, 'valor': 504310.50, 'status': 'ATIVA'}
    }
    
    # Calcular posição de São Mateus
    todas_lojas = dict(lojas_ativas_dados)
    todas_lojas['SAO_MATEUS'] = {'vendas': dados_sao_mateus['vendas'], 
                                'valor': dados_sao_mateus['valor_total'], 
                                'status': 'FECHADA'}
    
    # Ordenar por faturamento
    lojas_ordenadas = sorted(todas_lojas.items(), key=lambda x: x[1]['valor'], reverse=True)
    
    posicao_sao_mateus = None
    for i, (loja, dados) in enumerate(lojas_ordenadas, 1):
        status_emoji = "❌" if dados['status'] == 'FECHADA' else "✅"
        print(f"{i}º {status_emoji} {loja}: R$ {dados['valor']:,.2f} | {dados['vendas']} vendas")
        if loja == 'SAO_MATEUS':
            posicao_sao_mateus = i
    
    print(f"\n🎯 POSIÇÃO DE SÃO MATEUS: {posicao_sao_mateus}º lugar entre 6 lojas")
    
    # Análise de potencial
    print(f"\n💡 ANÁLISE DE POTENCIAL DE REATIVAÇÃO:")
    print("=" * 50)
    
    media_venda_sao_mateus = dados_sao_mateus['valor_total'] / dados_sao_mateus['vendas']
    
    # Comparar com lojas similares (SUZANO2 e PERUS)
    lojas_similares = ['SUZANO2', 'PERUS']
    media_similares = sum(lojas_ativas_dados[loja]['valor']/lojas_ativas_dados[loja]['vendas'] 
                         for loja in lojas_similares) / len(lojas_similares)
    
    print(f"📊 Média por venda São Mateus: R$ {media_venda_sao_mateus:,.2f}")
    print(f"📊 Média lojas similares: R$ {media_similares:,.2f}")
    
    diferenca = ((media_venda_sao_mateus - media_similares) / media_similares) * 100
    if diferenca > 0:
        print(f"✅ São Mateus tinha {diferenca:.1f}% MAIOR ticket médio")
    else:
        print(f"⚠️ São Mateus tinha {abs(diferenca):.1f}% menor ticket médio")
    
    # Estimativa de potencial mensal
    print(f"\n🚀 ESTIMATIVA DE POTENCIAL:")
    print("=" * 35)
    
    # Com base nos dados históricos (considerando período parcial)
    vendas_mes_historico = dados_sao_mateus['vendas'] / 8  # Aproximadamente 8 meses de dados
    faturamento_mes_historico = dados_sao_mateus['valor_total'] / 8
    
    print(f"📈 Vendas mensais históricas: {vendas_mes_historico:.0f}")
    print(f"💰 Faturamento mensal histórico: R$ {faturamento_mes_historico:,.2f}")
    
    # Projeção anual se reaberta
    projecao_anual = faturamento_mes_historico * 12
    print(f"🎯 Projeção anual se reaberta: R$ {projecao_anual:,.2f}")
    
    # Estratégias de reativação
    print(f"\n📋 ESTRATÉGIAS DE REATIVAÇÃO RECOMENDADAS:")
    print("=" * 55)
    
    print("1. 📞 CONTATO COM CLIENTES HISTÓRICOS:")
    print("   • Extrair lista de clientes únicos do período ativo")
    print("   • Campanhas de reativação personalizadas")
    print("   • Ofertas especiais para antigos clientes")
    
    print("\n2. 📊 ANÁLISE DE MERCADO LOCAL:")
    print("   • Avaliar concorrência na região")
    print("   • Pesquisar demanda atual por óticas")
    print("   • Analisar crescimento populacional da área")
    
    print("\n3. 💡 MODELO DE NEGÓCIO OTIMIZADO:")
    print(f"   • Foco em produtos de maior ticket (atual: R$ {media_venda_sao_mateus:,.2f})")
    print("   • Parcerias com planos de saúde")
    print("   • Serviços diferenciados (exames, consultas)")
    
    print("\n4. 🎯 METAS DE REABERTURA:")
    print(f"   • Meta conservadora: 80% do histórico = R$ {projecao_anual*0.8:,.2f}/ano")
    print(f"   • Meta otimista: 120% do histórico = R$ {projecao_anual*1.2:,.2f}/ano")
    print(f"   • Break-even estimado: {vendas_mes_historico*0.6:.0f} vendas/mês")
    
    # Análise temporal
    print(f"\n📅 ANÁLISE TEMPORAL:")
    print("=" * 25)
    print("📊 Dados disponíveis mostram atividade até Out/2024")
    print("⏰ Fechamento recente - clientes ainda 'quentes'")
    print("🎯 Janela de oportunidade para recontato ainda aberta")
    print("💡 Quanto mais tempo passa, menor a taxa de reativação")
    
    # Próximos passos específicos
    print(f"\n✅ PRÓXIMOS PASSOS IMEDIATOS:")
    print("=" * 35)
    print("1. 📋 Extrair lista completa de clientes únicos")
    print("2. 📞 Pesquisa de satisfação e interesse em reabertura") 
    print("3. 📍 Avaliação do ponto comercial atual")
    print("4. 💰 Análise de viabilidade financeira")
    print("5. 🎯 Plano de marketing de reabertura")
    
    return {
        'vendas': dados_sao_mateus['vendas'],
        'valor_total': dados_sao_mateus['valor_total'],
        'posicao_ranking': posicao_sao_mateus,
        'projecao_anual': projecao_anual,
        'vendas_mensais': vendas_mes_historico
    }

def extrair_clientes_sao_mateus():
    """Função para extrair lista de clientes únicos (placeholder)"""
    print(f"\n📋 EXTRAÇÃO DE CLIENTES DE SÃO MATEUS:")
    print("=" * 45)
    print("📄 Arquivo: VENDAS_COMPLETAS_SAO_MATEUS_*.xlsx")
    print("🎯 Objetivo: Lista de clientes únicos para reativação")
    print("💡 Para implementar: análise do arquivo Excel gerado")
    
    # Verificar se arquivo existe
    pasta_finais = Path("data/documentos_finais")
    arquivos_sao_mateus = list(pasta_finais.glob("VENDAS_COMPLETAS_SAO_MATEUS_*.xlsx"))
    
    if arquivos_sao_mateus:
        arquivo_mais_recente = max(arquivos_sao_mateus, key=lambda x: x.stat().st_mtime)
        print(f"✅ Arquivo encontrado: {arquivo_mais_recente.name}")
        print("💡 Use este arquivo para extrair lista de clientes únicos")
    else:
        print("❌ Arquivo de vendas não encontrado")

if __name__ == "__main__":
    resultado = analisar_sao_mateus()
    extrair_clientes_sao_mateus()
    
    print(f"\n🎉 ANÁLISE DE SÃO MATEUS CONCLUÍDA!")
    print(f"📊 {resultado['vendas']} vendas analisadas")
    print(f"💰 R$ {resultado['valor_total']:,.2f} em faturamento histórico")
    print(f"🎯 Potencial anual: R$ {resultado['projecao_anual']:,.2f}")
    print(f"🏆 Posição no ranking: {resultado['posicao_ranking']}º lugar")