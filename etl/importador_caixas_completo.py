#!/usr/bin/env python3
"""
Importador de Dados Completos - Todos os Caixas
Processa as 5 abas do arquivo consolidado e gera arquivos separados
"""

import pandas as pd
import os
from datetime import datetime

def processar_todos_os_caixas():
    """Processar todas as 5 abas do arquivo consolidado"""
    
    arquivo_origem = 'data/todos_os_caixas_original.xlsx'
    pasta_destino = 'data/caixas_processados'
    
    # Criar pasta de destino
    os.makedirs(pasta_destino, exist_ok=True)
    
    print("🎯 PROCESSADOR DE DADOS COMPLETOS - TODOS OS CAIXAS")
    print("="*60)
    
    try:
        wb = pd.ExcelFile(arquivo_origem)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Definir descrições das abas
        descricoes = {
            'vend': 'Vendas Completas (com Entrada)',
            'rec_carn': 'Recebimento de Carnês', 
            'os_entr_dia': 'Entrega de OSs por Dia',
            'entr_carn': 'Entrega de Carnês',
            'rest_entr': 'Restantes de Entradas'
        }
        
        resultados = {}
        
        for aba in wb.sheet_names:
            print(f"\n📋 Processando aba: {aba}")
            print(f"   📝 Descrição: {descricoes.get(aba, 'Sem descrição')}")
            
            # Ler dados da aba
            df = pd.read_excel(arquivo_origem, sheet_name=aba)
            print(f"   📊 Dados: {df.shape[0]} linhas x {df.shape[1]} colunas")
            
            # Criar coluna de data completa se tiver dia/mes/ano
            if all(col in df.columns for col in ['dia', 'mes', 'ano']):
                print("   📅 Criando coluna de data completa...")
                
                # Mapear meses para números
                meses_map = {
                    'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
                    'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
                }
                
                df['mes_num'] = df['mes'].map(meses_map)
                df['ano_completo'] = df['ano'].apply(lambda x: 2000 + x if x < 100 else x)
                
                # Criar data completa
                df['data_completa'] = pd.to_datetime(
                    df[['ano_completo', 'mes_num', 'dia']].rename(columns={
                        'ano_completo': 'year', 'mes_num': 'month', 'dia': 'day'
                    })
                )
            
            # Estatísticas por aba
            if 'Loja' in df.columns:
                print("   🏢 Distribuição por loja:")
                loja_counts = df['Loja'].value_counts()
                for loja, count in loja_counts.items():
                    print(f"      {loja}: {count} registros")
            
            # Estatísticas de valores
            valor_cols = [col for col in df.columns if 'valor' in col.lower() or 'entrada' in col.lower()]
            if valor_cols:
                print("   💰 Valores encontrados:")
                for col in valor_cols:
                    if df[col].dtype in ['float64', 'int64']:
                        total = df[col].sum()
                        count = df[col].count()
                        print(f"      {col}: R$ {total:,.2f} ({count} registros)")
            
            # Salvar arquivo individual
            nome_arquivo = f"{aba.upper()}_COMPLETO_{timestamp}.xlsx"
            caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)
            df.to_excel(caminho_arquivo, index=False)
            print(f"   💾 Salvo: {nome_arquivo}")
            
            resultados[aba] = {
                'arquivo': nome_arquivo,
                'linhas': df.shape[0],
                'colunas': df.shape[1],
                'colunas_lista': list(df.columns)
            }
        
        # Relatório final
        print("\n" + "="*60)
        print("📊 RELATÓRIO FINAL - IMPORTAÇÃO COMPLETA")
        print("="*60)
        
        total_registros = sum(r['linhas'] for r in resultados.values())
        print(f"🎯 Total de registros processados: {total_registros:,}")
        
        for aba, info in resultados.items():
            print(f"\n📋 {aba.upper()}: {info['arquivo']}")
            print(f"   📊 {info['linhas']} linhas x {info['colunas']} colunas")
            print(f"   📝 Colunas: {', '.join(info['colunas_lista'][:5])}...")
        
        return resultados
        
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        return None

if __name__ == "__main__":
    resultados = processar_todos_os_caixas()