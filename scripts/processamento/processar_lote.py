#!/usr/bin/env python3
"""
PROCESSADOR EM LOTE - Sistema de Vendas Universal
Processa múltiplas lojas e períodos de uma vez
Uso: python processar_lote.py
"""

import pandas as pd
from pathlib import Path
import os
from datetime import datetime
from sistema_vendas_universal import SistemaVendasUniversal

class ProcessadorLote:
    def __init__(self):
        self.sistema = SistemaVendasUniversal()
        self.pasta_relatorios = Path("data/relatorios_consolidados")
        self.pasta_relatorios.mkdir(exist_ok=True)
    
    def processar_todas_lojas_periodo(self, periodo: str):
        """Processa todas as lojas para um período específico"""
        print(f"🚀 PROCESSAMENTO EM LOTE - PERÍODO: {periodo}")
        print("=" * 80)
        
        resultados = {}
        
        for loja in ['MAUA', 'SUZANO', 'RIO_PEQUENO']:
            print(f"\n🏪 Processando {loja}...")
            try:
                arquivo_saida = self.sistema.processar_loja_arquivo(loja, periodo)
                if arquivo_saida:
                    resultados[loja] = {
                        'status': 'sucesso',
                        'arquivo': arquivo_saida
                    }
                    print(f"   ✅ {loja}: Processado com sucesso")
                else:
                    resultados[loja] = {
                        'status': 'erro',
                        'arquivo': None
                    }
                    print(f"   ❌ {loja}: Erro no processamento")
            except Exception as e:
                resultados[loja] = {
                    'status': 'erro',
                    'arquivo': None,
                    'erro': str(e)
                }
                print(f"   ❌ {loja}: Erro - {e}")
        
        return resultados
    
    def processar_loja_todos_periodos(self, loja: str):
        """Processa todos os períodos disponíveis de uma loja"""
        print(f"🚀 PROCESSAMENTO COMPLETO DA LOJA: {loja}")
        print("=" * 80)
        
        # Listar arquivos disponíveis
        pasta_loja = self.sistema.pasta_caixa / self.sistema.lojas_disponiveis[loja]
        arquivos = sorted(pasta_loja.glob("*.xlsx"))
        
        print(f"📂 Encontrados {len(arquivos)} arquivos para {loja}")
        
        resultados = {}
        vendas_totais = []
        
        for arquivo in arquivos:
            periodo = arquivo.stem
            print(f"\n📅 Processando {periodo}...")
            
            try:
                arquivo_saida = self.sistema.processar_loja_arquivo(loja, periodo)
                if arquivo_saida:
                    # Ler vendas geradas
                    df_vendas = pd.read_excel(arquivo_saida)
                    vendas_totais.extend(df_vendas.to_dict('records'))
                    
                    resultados[periodo] = {
                        'status': 'sucesso',
                        'arquivo': arquivo_saida,
                        'vendas': len(df_vendas)
                    }
                    print(f"   ✅ {periodo}: {len(df_vendas)} vendas processadas")
                else:
                    resultados[periodo] = {
                        'status': 'erro',
                        'arquivo': None
                    }
                    print(f"   ❌ {periodo}: Erro no processamento")
            except Exception as e:
                resultados[periodo] = {
                    'status': 'erro',
                    'arquivo': None,
                    'erro': str(e)
                }
                print(f"   ❌ {periodo}: Erro - {e}")
        
        # Gerar documento consolidado
        if vendas_totais:
            arquivo_consolidado = self.gerar_consolidado_loja(loja, vendas_totais)
            self.gerar_relatorio_consolidado_loja(loja, vendas_totais, resultados)
        
        return resultados
    
    def gerar_consolidado_loja(self, loja: str, vendas: list) -> Path:
        """Gera documento consolidado de uma loja"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"CONSOLIDADO_{loja}_2024_COMPLETO_{timestamp}.xlsx"
        arquivo_saida = self.pasta_relatorios / nome_arquivo
        
        # Criar DataFrame
        df_vendas = pd.DataFrame(vendas)
        df_vendas['data'] = pd.to_datetime(df_vendas['data'])
        df_vendas = df_vendas.sort_values(['data', 'numero_venda'])
        
        # Adicionar colunas de análise
        df_vendas['mes'] = df_vendas['data'].dt.strftime('%Y-%m')
        df_vendas['dia_semana'] = df_vendas['data'].dt.day_name()
        
        # Salvar com múltiplas abas
        with pd.ExcelWriter(arquivo_saida, engine='openpyxl') as writer:
            # Aba principal
            df_vendas.to_excel(writer, sheet_name='VENDAS_COMPLETAS', index=False)
            
            # Resumo por mês
            resumo_mensal = df_vendas.groupby('mes').agg({
                'numero_venda': 'count',
                'valor_venda': 'sum',
                'entrada': 'sum'
            }).reset_index()
            resumo_mensal.columns = ['mes', 'qtd_vendas', 'valor_total', 'entrada_total']
            resumo_mensal.to_excel(writer, sheet_name='RESUMO_MENSAL', index=False)
            
            # Top clientes
            top_clientes = df_vendas.groupby('cliente').agg({
                'numero_venda': 'count',
                'valor_venda': 'sum'
            }).reset_index().sort_values('valor_venda', ascending=False).head(50)
            top_clientes.columns = ['cliente', 'qtd_vendas', 'valor_total']
            top_clientes.to_excel(writer, sheet_name='TOP_CLIENTES', index=False)
        
        print(f"\n💾 CONSOLIDADO GERADO: {arquivo_saida}")
        print(f"📊 Total de vendas: {len(vendas)}")
        
        return arquivo_saida
    
    def gerar_relatorio_consolidado_loja(self, loja: str, vendas: list, resultados: dict):
        """Gera relatório detalhado da loja"""
        print(f"\n" + "=" * 80)
        print(f"📈 RELATÓRIO CONSOLIDADO - {loja}")
        print("=" * 80)
        
        # Estatísticas gerais
        total_vendas = len(vendas)
        valor_total = sum(v['valor_venda'] for v in vendas)
        entrada_total = sum(v['entrada'] for v in vendas)
        
        print(f"📊 RESUMO GERAL:")
        print(f"   💰 Total de vendas: {total_vendas:,}")
        print(f"   💵 Valor total: R$ {valor_total:,.2f}")
        print(f"   🏧 Entradas total: R$ {entrada_total:,.2f}")
        print(f"   📈 Média por venda: R$ {valor_total/total_vendas:,.2f}")
        
        # Período
        df_vendas = pd.DataFrame(vendas)
        df_vendas['data'] = pd.to_datetime(df_vendas['data'])
        periodo_inicio = df_vendas['data'].min().strftime('%Y-%m-%d')
        periodo_fim = df_vendas['data'].max().strftime('%Y-%m-%d')
        
        print(f"\n📅 PERÍODO: {periodo_inicio} a {periodo_fim}")
        
        # Resumo por mês
        resumo_mensal = df_vendas.groupby(df_vendas['data'].dt.strftime('%Y-%m')).agg({
            'numero_venda': 'count',
            'valor_venda': 'sum'
        })
        
        print(f"\n📊 VENDAS POR MÊS:")
        for mes, dados in resumo_mensal.iterrows():
            print(f"   {mes}: {dados['numero_venda']:,} vendas (R$ {dados['valor_venda']:,.2f})")
        
        # Status dos arquivos
        sucessos = sum(1 for r in resultados.values() if r['status'] == 'sucesso')
        erros = len(resultados) - sucessos
        
        print(f"\n📂 STATUS DO PROCESSAMENTO:")
        print(f"   ✅ Arquivos processados: {sucessos}")
        print(f"   ❌ Arquivos com erro: {erros}")
        
        if erros > 0:
            print(f"\n🚨 ARQUIVOS COM ERRO:")
            for periodo, resultado in resultados.items():
                if resultado['status'] == 'erro':
                    erro = resultado.get('erro', 'Erro desconhecido')
                    print(f"   ❌ {periodo}: {erro}")
    
    def menu_interativo(self):
        """Menu interativo para escolher o tipo de processamento"""
        print("🏪 SISTEMA DE PROCESSAMENTO EM LOTE")
        print("=" * 50)
        print("1. Processar todas as lojas para um período específico")
        print("2. Processar todos os períodos de uma loja específica") 
        print("3. Processar tudo (todas as lojas, todos os períodos)")
        print("4. Sair")
        
        while True:
            escolha = input("\n👉 Escolha uma opção (1-4): ").strip()
            
            if escolha == "1":
                periodo = input("📅 Digite o período (ex: abr_24, mai_24): ").strip()
                self.processar_todas_lojas_periodo(periodo)
                break
            
            elif escolha == "2":
                print("\n🏪 Lojas disponíveis:")
                for i, loja in enumerate(['MAUA', 'SUZANO', 'RIO_PEQUENO'], 1):
                    print(f"   {i}. {loja}")
                
                loja_escolha = input("👉 Escolha a loja (1-3): ").strip()
                lojas = ['MAUA', 'SUZANO', 'RIO_PEQUENO']
                
                try:
                    loja = lojas[int(loja_escolha) - 1]
                    self.processar_loja_todos_periodos(loja)
                except (ValueError, IndexError):
                    print("❌ Opção inválida")
                    continue
                break
            
            elif escolha == "3":
                print("🚀 Processando TODAS as lojas e TODOS os períodos...")
                for loja in ['MAUA', 'SUZANO', 'RIO_PEQUENO']:
                    print(f"\n🎯 INICIANDO PROCESSAMENTO COMPLETO: {loja}")
                    print("=" * 60)
                    self.processar_loja_todos_periodos(loja)
                break
            
            elif escolha == "4":
                print("👋 Saindo...")
                break
            
            else:
                print("❌ Opção inválida. Tente novamente.")

def main():
    processador = ProcessadorLote()
    processador.menu_interativo()

if __name__ == "__main__":
    main()