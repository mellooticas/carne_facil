#!/usr/bin/env python3
"""
GERADOR DE DOCUMENTOS COMPLETOS COM OS INDIVIDUAIS
Cria tabelas estruturadas com informações detalhadas de cada OS
Organizado por: Loja | Data | Número OS | Cliente | Forma Pgto | Valor | Entrada
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import re

class GeradorDocumentosCompletos:
    def __init__(self):
        self.pasta_finais = Path("data/documentos_finais")
        self.pasta_estruturados = Path("data/documentos_estruturados")
        self.pasta_estruturados.mkdir(parents=True, exist_ok=True)
        
        # Mapeamento de lojas
        self.lojas = ['MAUA', 'SUZANO', 'RIO_PEQUENO', 'PERUS', 'SUZANO2', 'SAO_MATEUS']
    
    def processar_arquivo_loja(self, loja):
        """Processa arquivo de uma loja específica e cria documento estruturado"""
        print(f"\n📊 PROCESSANDO DOCUMENTOS ESTRUTURADOS - {loja}")
        print("=" * 60)
        
        # Encontrar arquivo mais recente da loja
        arquivos_loja = list(self.pasta_finais.glob(f"VENDAS_COMPLETAS_{loja}_*.xlsx"))
        
        if not arquivos_loja:
            print(f"❌ Nenhum arquivo encontrado para {loja}")
            return None
        
        arquivo_mais_recente = max(arquivos_loja, key=lambda x: x.stat().st_mtime)
        print(f"📄 Arquivo fonte: {arquivo_mais_recente.name}")
        
        try:
            # Carregar dados
            df = pd.read_excel(arquivo_mais_recente)
            print(f"📈 Registros carregados: {len(df):,}")
            
            # Processar e estruturar dados
            df_estruturado = self.estruturar_dados(df, loja)
            
            # Salvar documento estruturado
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"OS_COMPLETAS_{loja}_{timestamp}.xlsx"
            caminho_arquivo = self.pasta_estruturados / nome_arquivo
            
            # Salvar com formatação aprimorada
            with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
                # Aba principal com todos os dados
                df_estruturado.to_excel(writer, sheet_name='OS_Completas', index=False)
                
                # Aba resumo por mês
                resumo_mensal = self.criar_resumo_mensal(df_estruturado)
                resumo_mensal.to_excel(writer, sheet_name='Resumo_Mensal', index=False)
                
                # Aba resumo por forma de pagamento
                resumo_pgto = self.criar_resumo_pagamento(df_estruturado)
                resumo_pgto.to_excel(writer, sheet_name='Resumo_Pagamento', index=False)
                
                # Aba top clientes
                top_clientes = self.criar_top_clientes(df_estruturado)
                top_clientes.to_excel(writer, sheet_name='Top_Clientes', index=False)
            
            print(f"✅ Documento estruturado salvo: {nome_arquivo}")
            print(f"📊 OS processadas: {len(df_estruturado):,}")
            print(f"💰 Valor total: R$ {df_estruturado['Valor_Venda'].sum():,.2f}")
            print(f"📅 Período: {df_estruturado['Data_Completa'].min()} a {df_estruturado['Data_Completa'].max()}")
            
            return {
                'loja': loja,
                'arquivo': nome_arquivo,
                'os_count': len(df_estruturado),
                'valor_total': df_estruturado['Valor_Venda'].sum(),
                'periodo': f"{df_estruturado['Data_Completa'].min()} a {df_estruturado['Data_Completa'].max()}"
            }
            
        except Exception as e:
            print(f"❌ Erro ao processar {loja}: {e}")
            return None
    
    def estruturar_dados(self, df, loja):
        """Estrutura dados com informações individuais de OS"""
        print(f"   🔧 Estruturando dados de {loja}...")
        
        # Garantir que temos as colunas necessárias
        colunas_necessarias = ['loja', 'data', 'numero_venda', 'cliente', 'forma_pgto', 'valor_venda', 'entrada']
        for col in colunas_necessarias:
            if col not in df.columns:
                df[col] = ''
        
        # Limpar e padronizar dados
        df_clean = df.copy()
        
        # Limpar número da OS/venda
        df_clean['numero_os'] = df_clean['numero_venda'].astype(str).str.strip()
        df_clean['numero_os'] = df_clean['numero_os'].replace(['nan', 'None', ''], 'SEM_OS')
        
        # Padronizar datas
        df_clean['data_formatada'] = pd.to_datetime(df_clean['data'], errors='coerce')
        df_clean['ano'] = df_clean['data_formatada'].dt.year
        df_clean['mes'] = df_clean['data_formatada'].dt.month
        df_clean['dia'] = df_clean['data_formatada'].dt.day
        df_clean['mes_nome'] = df_clean['data_formatada'].dt.strftime('%B')
        df_clean['data_completa'] = df_clean['data_formatada'].dt.strftime('%d/%m/%Y')
        
        # Limpar nomes de clientes
        df_clean['cliente_limpo'] = df_clean['cliente'].astype(str).str.strip().str.title()
        df_clean['cliente_limpo'] = df_clean['cliente_limpo'].replace(['Nan', 'None', ''], 'CLIENTE_NAO_INFORMADO')
        
        # Padronizar formas de pagamento
        df_clean['forma_pgto_padrao'] = df_clean['forma_pgto'].astype(str).str.strip().str.upper()
        df_clean['forma_pgto_padrao'] = df_clean['forma_pgto_padrao'].replace(['NAN', 'NONE', ''], 'NAO_INFORMADO')
        
        # Garantir valores numéricos
        df_clean['valor_venda'] = pd.to_numeric(df_clean['valor_venda'], errors='coerce').fillna(0)
        df_clean['entrada'] = pd.to_numeric(df_clean['entrada'], errors='coerce').fillna(0)
        
        # Criar ID único da OS
        df_clean['id_os_unico'] = df_clean['loja'] + '_' + df_clean['numero_os'] + '_' + df_clean['data_completa'].fillna('SEM_DATA')
        
        # Estruturar colunas finais
        df_estruturado = df_clean[[
            'loja',
            'ano', 'mes', 'mes_nome', 'dia', 'data_completa',
            'numero_os', 'id_os_unico',
            'cliente_limpo', 'forma_pgto_padrao',
            'valor_venda', 'entrada'
        ]].copy()
        
        # Renomear colunas para clareza
        df_estruturado.columns = [
            'Loja',
            'Ano', 'Mes_Num', 'Mes_Nome', 'Dia', 'Data_Completa',
            'Numero_OS', 'ID_OS_Unico',
            'Cliente', 'Forma_Pagamento',
            'Valor_Venda', 'Valor_Entrada'
        ]
        
        # Ordenar por data e número da OS
        df_estruturado = df_estruturado.sort_values(['Ano', 'Mes_Num', 'Dia', 'Numero_OS'])
        
        # Remover duplicatas baseado no ID único
        antes = len(df_estruturado)
        df_estruturado = df_estruturado.drop_duplicates(subset=['ID_OS_Unico'])
        depois = len(df_estruturado)
        
        if antes != depois:
            print(f"   ⚠️ Removidas {antes - depois} OS duplicadas")
        
        return df_estruturado
    
    def criar_resumo_mensal(self, df):
        """Cria resumo por mês"""
        resumo = df.groupby(['Loja', 'Ano', 'Mes_Num', 'Mes_Nome']).agg({
            'Numero_OS': 'count',
            'Valor_Venda': 'sum',
            'Valor_Entrada': 'sum',
            'Cliente': 'nunique'
        }).reset_index()
        
        resumo.columns = ['Loja', 'Ano', 'Mes_Num', 'Mes_Nome', 'Qtd_OS', 'Faturamento_Total', 'Entrada_Total', 'Clientes_Unicos']
        resumo['Ticket_Medio'] = resumo['Faturamento_Total'] / resumo['Qtd_OS']
        
        return resumo.sort_values(['Ano', 'Mes_Num'])
    
    def criar_resumo_pagamento(self, df):
        """Cria resumo por forma de pagamento"""
        resumo = df.groupby(['Loja', 'Forma_Pagamento']).agg({
            'Numero_OS': 'count',
            'Valor_Venda': 'sum',
            'Cliente': 'nunique'
        }).reset_index()
        
        resumo.columns = ['Loja', 'Forma_Pagamento', 'Qtd_OS', 'Valor_Total', 'Clientes_Unicos']
        resumo['Percentual'] = (resumo['Qtd_OS'] / resumo.groupby('Loja')['Qtd_OS'].transform('sum')) * 100
        
        return resumo.sort_values(['Loja', 'Qtd_OS'], ascending=[True, False])
    
    def criar_top_clientes(self, df):
        """Cria ranking de top clientes"""
        top_clientes = df.groupby(['Loja', 'Cliente']).agg({
            'Numero_OS': 'count',
            'Valor_Venda': 'sum',
            'Valor_Entrada': 'sum'
        }).reset_index()
        
        top_clientes.columns = ['Loja', 'Cliente', 'Qtd_OS', 'Valor_Total', 'Entrada_Total']
        top_clientes['Ticket_Medio'] = top_clientes['Valor_Total'] / top_clientes['Qtd_OS']
        
        # Top 50 por loja
        top_clientes = top_clientes.sort_values(['Loja', 'Valor_Total'], ascending=[True, False])
        top_clientes = top_clientes.groupby('Loja').head(50).reset_index(drop=True)
        
        return top_clientes
    
    def processar_todas_lojas(self):
        """Processa todas as lojas e cria documentos estruturados"""
        print("📊 GERAÇÃO DE DOCUMENTOS COMPLETOS ESTRUTURADOS")
        print("=" * 70)
        print("🎯 Objetivo: Criar tabelas individuais de OS por loja")
        print("📋 Estrutura: Loja | Data | Número OS | Cliente | Forma Pgto | Valor")
        print()
        
        resultados = []
        
        for loja in self.lojas:
            resultado = self.processar_arquivo_loja(loja)
            if resultado:
                resultados.append(resultado)
        
        # Criar relatório consolidado
        if resultados:
            self.criar_relatorio_consolidado(resultados)
        
        return resultados
    
    def criar_relatorio_consolidado(self, resultados):
        """Cria relatório consolidado de todos os documentos gerados"""
        print(f"\n📋 CRIANDO RELATÓRIO CONSOLIDADO...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_relatorio = f"RELATORIO_OS_CONSOLIDADO_{timestamp}.xlsx"
        caminho_relatorio = self.pasta_estruturados / nome_relatorio
        
        # Criar DataFrame do resumo
        df_resumo = pd.DataFrame(resultados)
        
        # Calcular totais
        total_os = df_resumo['os_count'].sum()
        total_valor = df_resumo['valor_total'].sum()
        
        # Adicionar linha de totais
        df_resumo.loc[len(df_resumo)] = {
            'loja': 'TOTAL GERAL',
            'arquivo': f'{len(resultados)} arquivos gerados',
            'os_count': total_os,
            'valor_total': total_valor,
            'periodo': 'Todos os períodos'
        }
        
        # Salvar relatório
        with pd.ExcelWriter(caminho_relatorio, engine='openpyxl') as writer:
            df_resumo.to_excel(writer, sheet_name='Resumo_Geral', index=False)
        
        print(f"✅ Relatório consolidado salvo: {nome_relatorio}")
        print(f"\n🎉 GERAÇÃO CONCLUÍDA!")
        print("=" * 30)
        print(f"🏢 Lojas processadas: {len(resultados)}")
        print(f"📈 Total de OS: {total_os:,}")
        print(f"💰 Valor total: R$ {total_valor:,.2f}")
        print(f"📄 Arquivos gerados: {len(resultados)} + 1 relatório")

def main():
    gerador = GeradorDocumentosCompletos()
    
    print("📊 GERADOR DE DOCUMENTOS COMPLETOS COM OS INDIVIDUAIS")
    print("=" * 65)
    print("🎯 Cria tabelas estruturadas com informações detalhadas de cada OS")
    print()
    print("1. Processar todas as lojas")
    print("2. Processar loja específica")
    print("3. Sair")
    
    while True:
        escolha = input("\n👉 Escolha uma opção (1-3): ").strip()
        
        if escolha == "1":
            gerador.processar_todas_lojas()
            break
        elif escolha == "2":
            loja = input("Digite o nome da loja (MAUA, SUZANO, etc.): ").strip().upper()
            if loja in gerador.lojas:
                gerador.processar_arquivo_loja(loja)
            else:
                print(f"❌ Loja {loja} não encontrada")
            break
        elif escolha == "3":
            print("👋 Saindo...")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()