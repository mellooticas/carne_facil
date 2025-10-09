#!/usr/bin/env python3
"""
Relatório Detalhado dos Resultados da Consolidação Por Loja
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

def gerar_relatorio_completo():
    """Gera relatório completo com análises e visualizações"""
    
    print("📊 RELATÓRIO DETALHADO - CONSOLIDAÇÃO POR LOJA")
    print("=" * 80)
    print(f"📅 Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 80)
    
    # Carregar dados
    dashboard_file = Path("data/processed/dashboard_consolidacao_por_loja.xlsx")
    
    if not dashboard_file.exists():
        print("❌ Dashboard não encontrado. Execute primeiro a consolidação!")
        return
    
    try:
        # Carregar todas as sheets
        excel_file = pd.ExcelFile(dashboard_file)
        df_dashboard = pd.read_excel(dashboard_file, sheet_name='Dashboard_Principal')
        df_resumo_loja = pd.read_excel(dashboard_file, sheet_name='Resumo_Por_Loja')
        df_stats = pd.read_excel(dashboard_file, sheet_name='Estatisticas_Gerais')
        
        # Carregar qualidade se existir
        df_qualidade = None
        try:
            df_qualidade = pd.read_excel(dashboard_file, sheet_name='Qualidade_Dados')
        except:
            pass
        
        print("\n🔍 ANÁLISE GERAL:")
        print("-" * 50)
        
        # Estatísticas principais
        sucessos = df_dashboard[df_dashboard['status'] == 'sucesso']
        erros = df_dashboard[df_dashboard['status'] == 'erro']
        
        print(f"📁 Total de arquivos analisados: {len(df_dashboard)}")
        print(f"✅ Processados com sucesso: {len(sucessos)} ({len(sucessos)/len(df_dashboard)*100:.1f}%)")
        print(f"❌ Erros encontrados: {len(erros)} ({len(erros)/len(df_dashboard)*100:.1f}%)")
        
        if len(sucessos) > 0:
            total_originais = sucessos['registros_originais'].sum()
            total_consolidados = sucessos['registros_consolidados'].sum()
            total_duplicatas = sucessos['duplicatas_encontradas'].sum()
            total_os = sucessos['total_os'].sum()
            
            print(f"\n📊 NÚMEROS CONSOLIDADOS:")
            print(f"   📋 Registros originais: {total_originais:,}")
            print(f"   📋 Registros consolidados: {total_consolidados:,}")
            print(f"   🔄 Duplicatas removidas: {total_duplicatas:,}")
            print(f"   📈 Taxa de duplicação: {(total_duplicatas/total_originais*100):.1f}%")
            print(f"   🎯 Eficiência da consolidação: {((total_originais-total_consolidados)/total_originais*100):.1f}%")
            print(f"   📝 Total de OS identificadas: {total_os:,}")
        
        print(f"\n🏪 ANÁLISE POR LOJA:")
        print("-" * 50)
        
        # Análise por loja
        df_resumo_sorted = df_resumo_loja.sort_values('registros_originais', ascending=False)
        
        for _, loja in df_resumo_sorted.iterrows():
            reducao = ((loja['registros_originais'] - loja['registros_consolidados']) / loja['registros_originais'] * 100) if loja['registros_originais'] > 0 else 0
            
            print(f"\n🏢 {loja['loja']}:")
            print(f"   📁 Arquivos: {loja['total_arquivos']}")
            print(f"   📊 {loja['registros_originais']:,} → {loja['registros_consolidados']:,} registros")
            print(f"   🔄 {loja['duplicatas_encontradas']:,} duplicatas ({reducao:.1f}% redução)")
            print(f"   📝 {loja['total_os']:,} OS identificadas")
        
        print(f"\n📈 TOP 10 ARQUIVOS COM MAIS DUPLICATAS:")
        print("-" * 50)
        
        # Top arquivos com duplicatas
        top_duplicatas = sucessos.nlargest(10, 'duplicatas_encontradas')
        
        for i, (_, arquivo) in enumerate(top_duplicatas.iterrows(), 1):
            reducao = ((arquivo['registros_originais'] - arquivo['registros_consolidados']) / arquivo['registros_originais'] * 100) if arquivo['registros_originais'] > 0 else 0
            nome_arquivo = arquivo['arquivo'][:40] + "..." if len(arquivo['arquivo']) > 40 else arquivo['arquivo']
            
            print(f"{i:2d}. {nome_arquivo}")
            print(f"    🏪 {arquivo['loja']} | 📊 {arquivo['registros_originais']} → {arquivo['registros_consolidados']} | 🔄 {arquivo['duplicatas_encontradas']} duplicatas ({reducao:.1f}%)")
        
        if df_qualidade is not None:
            print(f"\n📋 QUALIDADE DOS DADOS:")
            print("-" * 50)
            
            # Análise de qualidade por campo
            qualidade_por_campo = df_qualidade.groupby('campo').agg({
                'preenchidos': 'sum',
                'total': 'sum'
            }).reset_index()
            
            qualidade_por_campo['percentual'] = (qualidade_por_campo['preenchidos'] / qualidade_por_campo['total'] * 100)
            qualidade_por_campo = qualidade_por_campo.sort_values('percentual', ascending=False)
            
            for _, campo in qualidade_por_campo.iterrows():
                status = "🟢" if campo['percentual'] >= 80 else "🟡" if campo['percentual'] >= 50 else "🔴"
                campo_nome = "CELULAR" if campo['campo'] == 'celular' else campo['campo'].upper()
                print(f"{status} {campo_nome}: {campo['percentual']:.1f}% ({campo['preenchidos']:,}/{campo['total']:,})")
        
        print(f"\n🎯 ESTRATÉGIA APLICADA:")
        print("-" * 50)
        print("✅ Consolidação POR ARQUIVO/LOJA (não entre lojas)")
        print("✅ Critérios seguros: CPF exato OU Nome + Data Nascimento")
        print("✅ Preservação da integridade das lojas")
        print("✅ Mesclagem inteligente de informações")
        
        print(f"\n📁 ARQUIVOS GERADOS:")
        print("-" * 50)
        print(f"📊 Dashboard principal: {dashboard_file}")
        
        # Listar arquivos consolidados por loja
        output_dir = Path("data/processed/por_arquivo")
        if output_dir.exists():
            arquivos_individuais = list(output_dir.glob("*_consolidado.xlsx"))
            print(f"📁 Arquivos individuais: {len(arquivos_individuais)} em {output_dir}")
        
        print(f"\n🚀 PRÓXIMAS ETAPAS SUGERIDAS:")
        print("-" * 50)
        print("1. 📋 Normalizar sequências de OS por loja")
        print("2. 🔍 Análise detalhada de clientes com múltiplas OS")
        print("3. 📊 Implementar dashboard de vendas por loja")
        print("4. 🏪 Configurar sistema de entrada contínua de dados")
        print("5. 📈 Análises de tendências e relatórios gerenciais")
        
        print(f"\n💡 INSIGHTS IDENTIFICADOS:")
        print("-" * 50)
        
        if len(sucessos) > 0:
            # Insights automáticos
            loja_mais_duplicatas = df_resumo_sorted.iloc[0]
            arquivo_mais_problematico = sucessos.loc[sucessos['duplicatas_encontradas'].idxmax()]
            
            print(f"📊 Loja com mais duplicatas: {loja_mais_duplicatas['loja']} ({loja_mais_duplicatas['duplicatas_encontradas']:,} duplicatas)")
            print(f"📁 Arquivo mais problemático: {arquivo_mais_problematico['arquivo'][:50]}...")
            print(f"🎯 Taxa média de duplicação: {(sucessos['duplicatas_encontradas'].sum()/sucessos['registros_originais'].sum()*100):.1f}%")
            
            # Distribuição de arquivos por loja
            dist_lojas = sucessos['loja'].value_counts()
            print(f"🏪 Distribuição: {', '.join([f'{loja}({count})' for loja, count in dist_lojas.head(3).items()])}")
        
        print(f"\n🌐 DASHBOARD WEB:")
        print("-" * 50)
        print("🚀 Acesse: http://localhost:8001")
        print("📊 Dashboard interativo com filtros por loja")
        print("📈 Métricas em tempo real e visualizações")
        
        print("\n" + "=" * 80)
        print("🎉 RELATÓRIO CONCLUÍDO COM SUCESSO!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Erro ao gerar relatório: {e}")

def main():
    """Função principal"""
    gerar_relatorio_completo()

if __name__ == "__main__":
    main()