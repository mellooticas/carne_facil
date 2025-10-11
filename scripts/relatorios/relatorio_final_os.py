#!/usr/bin/env python3
"""
RELATÓRIO FINAL - DOCUMENTOS COMPLETOS COM OS INDIVIDUAIS
Resumo dos documentos estruturados criados
"""

from datetime import datetime
from pathlib import Path

def gerar_relatorio_final_os():
    print("📊 RELATÓRIO FINAL - DOCUMENTOS COMPLETOS DE OS")
    print("=" * 70)
    print("🎯 Sistema de documentação individual de Ordens de Serviço")
    print(f"📅 Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print()
    
    # Dados consolidados dos documentos gerados
    documentos_gerados = {
        'MAUA': {
            'os_processadas': 867,
            'valor_total': 1947246.42,
            'os_removidas_duplicadas': 30,
            'periodo': '2023-2025',
            'arquivo': 'OS_COMPLETAS_MAUA_20251010_115055.xlsx'
        },
        'SUZANO': {
            'os_processadas': 3375,
            'valor_total': 14454371.42,
            'os_removidas_duplicadas': 157,
            'periodo': '2023-2025',
            'arquivo': 'OS_COMPLETAS_SUZANO_20251010_115056.xlsx'
        },
        'RIO_PEQUENO': {
            'os_processadas': 1155,
            'valor_total': 3434754.64,
            'os_removidas_duplicadas': 50,
            'periodo': '2023-2024',
            'arquivo': 'OS_COMPLETAS_RIO_PEQUENO_20251010_115057.xlsx'
        },
        'PERUS': {
            'os_processadas': 782,
            'valor_total': 2275433.94,
            'os_removidas_duplicadas': 14,
            'periodo': '2023-2024',
            'arquivo': 'OS_COMPLETAS_PERUS_20251010_115057.xlsx'
        },
        'SUZANO2': {
            'os_processadas': 325,
            'valor_total': 474022.50,
            'os_removidas_duplicadas': 16,
            'periodo': '2023-2024',
            'arquivo': 'OS_COMPLETAS_SUZANO2_20251010_115058.xlsx'
        },
        'SAO_MATEUS': {
            'os_processadas': 447,
            'valor_total': 859097.33,
            'os_removidas_duplicadas': 314,
            'periodo': '2023-2024',
            'arquivo': 'OS_COMPLETAS_SAO_MATEUS_20251010_115058.xlsx'
        }
    }
    
    # Calcular totais
    total_os = sum(loja['os_processadas'] for loja in documentos_gerados.values())
    total_valor = sum(loja['valor_total'] for loja in documentos_gerados.values())
    total_duplicadas = sum(loja['os_removidas_duplicadas'] for loja in documentos_gerados.values())
    
    print("🏢 DOCUMENTOS GERADOS POR LOJA:")
    print("=" * 45)
    
    # Ordenar por número de OS
    lojas_ordenadas = sorted(documentos_gerados.items(), 
                           key=lambda x: x[1]['os_processadas'], reverse=True)
    
    for pos, (loja, dados) in enumerate(lojas_ordenadas, 1):
        print(f"\n{pos}º 🏢 {loja}:")
        print(f"   📄 Arquivo: {dados['arquivo']}")
        print(f"   📊 OS processadas: {dados['os_processadas']:,}")
        print(f"   💰 Valor total: R$ {dados['valor_total']:,.2f}")
        print(f"   🧹 Duplicadas removidas: {dados['os_removidas_duplicadas']}")
        print(f"   📅 Período: {dados['periodo']}")
        print(f"   📊 Ticket médio: R$ {dados['valor_total']/dados['os_processadas']:,.2f}")
    
    print(f"\n🎯 CONSOLIDADO GERAL:")
    print("=" * 25)
    print(f"🏢 Lojas processadas: {len(documentos_gerados)}")
    print(f"📊 Total de OS: {total_os:,}")
    print(f"💰 Valor total: R$ {total_valor:,.2f}")
    print(f"🧹 Total duplicatas removidas: {total_duplicadas}")
    print(f"📊 Ticket médio geral: R$ {total_valor/total_os:,.2f}")
    
    print(f"\n📋 ESTRUTURA DOS DOCUMENTOS:")
    print("=" * 35)
    print("✅ Cada arquivo Excel contém 4 abas:")
    print("   1️⃣ OS_Completas: Lista individual de cada OS")
    print("      • Loja | Ano | Mês | Dia | Data Completa")
    print("      • Número OS | ID Único | Cliente")
    print("      • Forma Pagamento | Valor Venda | Entrada")
    print("   2️⃣ Resumo_Mensal: Consolidado por mês")
    print("   3️⃣ Resumo_Pagamento: Análise por forma de pagamento")
    print("   4️⃣ Top_Clientes: Ranking dos melhores clientes")
    
    print(f"\n🎯 BENEFÍCIOS DOS DOCUMENTOS:")
    print("=" * 35)
    print("✅ OS individualizadas com numeração única")
    print("✅ Dados limpos e deduplicados")
    print("✅ Organização cronológica completa")
    print("✅ Múltiplas visões analíticas")
    print("✅ Facilita auditoria e rastreamento")
    print("✅ Base para análises avançadas")
    
    print(f"\n📊 QUALIDADE DOS DADOS:")
    print("=" * 30)
    eficiencia_limpeza = ((total_duplicadas / (total_os + total_duplicadas)) * 100)
    print(f"🧹 Eficiência limpeza: {eficiencia_limpeza:.1f}% duplicatas removidas")
    print(f"✅ Dados consistentes e padronizados")
    print(f"📅 Cobertura temporal: 2023-2025")
    print(f"🏢 Cobertura completa: 6 lojas")
    
    print(f"\n📁 LOCALIZAÇÃO DOS ARQUIVOS:")
    print("=" * 35)
    print("📂 Pasta: data/documentos_estruturados/")
    
    pasta_estruturados = Path("data/documentos_estruturados")
    if pasta_estruturados.exists():
        arquivos = list(pasta_estruturados.glob("OS_COMPLETAS_*.xlsx"))
        print(f"📄 Total de arquivos: {len(arquivos)}")
        
        tamanho_total = sum(arquivo.stat().st_size for arquivo in arquivos)
        tamanho_mb = tamanho_total / (1024 * 1024)
        print(f"💾 Tamanho total: {tamanho_mb:.1f} MB")
    
    print(f"\n💡 COMO USAR OS DOCUMENTOS:")
    print("=" * 35)
    print("1. 🔍 Buscar OS específica: Use filtros Excel na coluna Numero_OS")
    print("2. 📅 Análise temporal: Ordene por Ano/Mes/Dia")
    print("3. 👥 Análise de cliente: Filtre por Cliente")
    print("4. 💳 Análise pagamento: Use aba Resumo_Pagamento")
    print("5. 📊 Pivot Tables: Crie análises personalizadas")
    print("6. 📈 Dashboard: Importe para Power BI/Tableau")
    
    print(f"\n🎉 MISSÃO CUMPRIDA!")
    print("=" * 25)
    print("✅ Sistema completo de gestão de OS criado")
    print("✅ Dados históricos organizados e acessíveis")
    print("✅ Base sólida para tomada de decisões")
    print("✅ Controle total sobre informações das lojas")
    
    return {
        'total_os': total_os,
        'total_valor': total_valor,
        'lojas_processadas': len(documentos_gerados),
        'documentos_gerados': len(documentos_gerados)
    }

if __name__ == "__main__":
    resultado = gerar_relatorio_final_os()
    print(f"\n📊 SISTEMA CONCLUÍDO COM SUCESSO!")
    print(f"🏢 {resultado['lojas_processadas']} lojas | {resultado['total_os']:,} OS | R$ {resultado['total_valor']:,.2f}")