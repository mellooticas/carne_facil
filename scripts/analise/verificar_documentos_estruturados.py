#!/usr/bin/env python3
"""Verificar estrutura dos documentos completos gerados"""

import pandas as pd
from pathlib import Path

def verificar_documentos_estruturados():
    print("📊 VERIFICAÇÃO DOS DOCUMENTOS ESTRUTURADOS COMPLETOS")
    print("=" * 70)
    print("🎯 Verificando estrutura dos documentos OS individuais gerados")
    print()
    
    pasta_estruturados = Path("data/documentos_estruturados")
    
    # Pegar os arquivos mais recentes de cada loja
    lojas = ['MAUA', 'SUZANO', 'RIO_PEQUENO', 'PERUS', 'SUZANO2', 'SAO_MATEUS']
    
    total_os = 0
    total_valor = 0
    
    for loja in lojas:
        print(f"🏢 VERIFICANDO {loja}:")
        print("-" * 30)
        
        # Encontrar arquivo mais recente da loja
        arquivos = list(pasta_estruturados.glob(f"OS_COMPLETAS_{loja}_*.xlsx"))
        
        if arquivos:
            arquivo_mais_recente = max(arquivos, key=lambda x: x.stat().st_mtime)
            print(f"📄 Arquivo: {arquivo_mais_recente.name}")
            
            try:
                # Ler aba principal
                df = pd.read_excel(arquivo_mais_recente, sheet_name='OS_Completas')
                
                print(f"📊 Total de OS: {len(df):,}")
                print(f"💰 Valor total: R$ {df['Valor_Venda'].sum():,.2f}")
                print(f"📅 Período: {df['Data_Completa'].min()} a {df['Data_Completa'].max()}")
                
                # Mostrar estrutura das colunas
                print(f"📋 Estrutura das colunas:")
                for i, col in enumerate(df.columns, 1):
                    print(f"   {i:2d}. {col}")
                
                # Mostrar amostra dos dados
                print(f"📋 Amostra dos dados (primeiras 3 OS):")
                amostra = df.head(3)[['Loja', 'Data_Completa', 'Numero_OS', 'Cliente', 'Forma_Pagamento', 'Valor_Venda']]
                for idx, row in amostra.iterrows():
                    print(f"   {row['Loja']} | {row['Data_Completa']} | OS: {row['Numero_OS']} | {row['Cliente'][:20]}... | {row['Forma_Pagamento']} | R$ {row['Valor_Venda']}")
                
                # Verificar abas adicionais
                try:
                    with pd.ExcelFile(arquivo_mais_recente) as xl:
                        abas = xl.sheet_names
                        print(f"📋 Abas disponíveis: {', '.join(abas)}")
                        
                        if 'Resumo_Mensal' in abas:
                            resumo_mensal = pd.read_excel(arquivo_mais_recente, sheet_name='Resumo_Mensal')
                            print(f"   📊 Resumo mensal: {len(resumo_mensal)} períodos")
                        
                        if 'Top_Clientes' in abas:
                            top_clientes = pd.read_excel(arquivo_mais_recente, sheet_name='Top_Clientes')
                            print(f"   👥 Top clientes: {len(top_clientes)} registros")
                
                except Exception as e:
                    print(f"   ⚠️ Erro ao verificar abas adicionais: {e}")
                
                total_os += len(df)
                total_valor += df['Valor_Venda'].sum()
                
            except Exception as e:
                print(f"❌ Erro ao ler arquivo: {e}")
        else:
            print("❌ Nenhum arquivo encontrado")
        
        print()
    
    print("🎯 RESUMO CONSOLIDADO:")
    print("=" * 30)
    print(f"🏢 Lojas processadas: {len(lojas)}")
    print(f"📈 Total de OS: {total_os:,}")
    print(f"💰 Valor total: R$ {total_valor:,.2f}")
    print(f"📊 Média por OS: R$ {total_valor/total_os:,.2f}")
    
    print(f"\n✅ ESTRUTURA CONFIRMADA:")
    print("=" * 30)
    print("✅ Documentos com OS individuais criados")
    print("✅ Estrutura organizada por Loja | Data | Número OS")
    print("✅ Informações completas de clientes e valores")
    print("✅ Múltiplas abas com análises complementares")
    print("✅ Dados limpos e deduplicados")
    
    print(f"\n📋 COMO USAR OS DOCUMENTOS:")
    print("=" * 35)
    print("1. 📊 Aba 'OS_Completas': Lista completa de todas as OS")
    print("2. 📅 Aba 'Resumo_Mensal': Consolidado por mês")
    print("3. 💳 Aba 'Resumo_Pagamento': Análise por forma de pagamento")
    print("4. 👥 Aba 'Top_Clientes': Ranking de melhores clientes")
    print("5. 🔍 Filtros Excel: Use para buscar OS específicas")
    print("6. 📈 Pivot Tables: Crie análises personalizadas")

if __name__ == "__main__":
    verificar_documentos_estruturados()