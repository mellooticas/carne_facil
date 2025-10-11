#!/usr/bin/env python3
"""
ANALISADOR DE RELATÓRIO DE CAIXA
Analisa o relatório de padrão gerado e examina uma aba diária para entender transações
"""

import pandas as pd
from pathlib import Path
import openpyxl
from datetime import datetime

class AnalisadorRelatorioCaixa:
    def __init__(self):
        self.pasta_base = Path("data/caixa_lojas")
        self.arquivo_exemplo = self.pasta_base / "MAUA/2024_MAU/abr_24.xlsx"
        
    def analisar_relatorio_padrao(self):
        """Analisa o relatório de padrão gerado"""
        print("=" * 80)
        print("ANÁLISE DO RELATÓRIO DE PADRÃO")
        print("=" * 80)
        
        # Procurar o relatório mais recente
        relatorios = list(self.pasta_base.glob("ANALISE_PADRAO_CAIXA_*.xlsx"))
        if not relatorios:
            print("❌ Nenhum relatório de padrão encontrado")
            return
            
        relatorio = max(relatorios, key=lambda x: x.stat().st_mtime)
        print(f"📄 Analisando: {relatorio.name}")
        
        try:
            # Ler o relatório
            df = pd.read_excel(relatorio, sheet_name="Analise_Padrao")
            print(f"📊 Total de registros no relatório: {len(df)}")
            print("\n📋 Estrutura do relatório:")
            print(df.head(10))
            
        except Exception as e:
            print(f"❌ Erro ao ler relatório: {e}")
    
    def analisar_aba_diaria(self):
        """Analisa uma aba diária para entender transações"""
        print("\n" + "=" * 80)
        print("ANÁLISE DE ABA DIÁRIA - TRANSAÇÕES")
        print("=" * 80)
        
        if not self.arquivo_exemplo.exists():
            print(f"❌ Arquivo exemplo não encontrado: {self.arquivo_exemplo}")
            return
        
        try:
            # Analisar aba "01" (primeiro dia do mês)
            print(f"📄 Analisando aba '01' do arquivo: {self.arquivo_exemplo.name}")
            
            df = pd.read_excel(self.arquivo_exemplo, sheet_name="01")
            print(f"📏 Dimensões: {df.shape[0]} linhas × {df.shape[1]} colunas")
            
            # Identificar estrutura
            print("\n📋 ESTRUTURA DAS COLUNAS:")
            print("-" * 70)
            for i, col in enumerate(df.columns, 1):
                non_null = df[col].notna().sum()
                unique_vals = df[col].nunique()
                dtype = df[col].dtype
                print(f"{i:3d} | {str(col)[:25]:25} | {str(dtype):12} | {non_null:8} | {unique_vals:6}")
            
            # Analisar dados não nulos
            print("\n🔍 COLUNAS COM DADOS:")
            colunas_com_dados = []
            for col in df.columns:
                if df[col].notna().sum() > 0:
                    colunas_com_dados.append(col)
                    print(f"  ✓ {col}: {df[col].notna().sum()} registros não nulos")
            
            # Mostrar amostra dos dados com conteúdo
            if colunas_com_dados:
                print("\n📊 AMOSTRA DOS DADOS (primeiras 10 linhas com dados):")
                print("-" * 80)
                df_sample = df[colunas_com_dados].dropna(how='all').head(10)
                print(df_sample.to_string())
                
                # Procurar padrões de transação
                self.identificar_padroes_transacao(df, colunas_com_dados)
                
        except Exception as e:
            print(f"❌ Erro ao analisar aba diária: {e}")
    
    def identificar_padroes_transacao(self, df, colunas_com_dados):
        """Identifica padrões de transação nos dados"""
        print("\n🎯 IDENTIFICAÇÃO DE PADRÕES DE TRANSAÇÃO:")
        print("-" * 50)
        
        # Procurar colunas que podem ser valores monetários
        colunas_valores = []
        for col in colunas_com_dados:
            if df[col].dtype in ['float64', 'int64']:
                valores_nao_nulos = df[col].dropna()
                if len(valores_nao_nulos) > 0:
                    print(f"💰 {col}: {len(valores_nao_nulos)} valores numéricos")
                    print(f"    Min: {valores_nao_nulos.min():.2f} | Max: {valores_nao_nulos.max():.2f}")
                    print(f"    Soma: {valores_nao_nulos.sum():.2f}")
                    colunas_valores.append(col)
        
        # Procurar colunas de texto que podem ser descritivas
        print("\n📝 COLUNAS DE TEXTO:")
        for col in colunas_com_dados:
            if df[col].dtype == 'object':
                valores_unicos = df[col].dropna().unique()
                if len(valores_unicos) > 0:
                    print(f"  📋 {col}: {len(valores_unicos)} valores únicos")
                    if len(valores_unicos) <= 10:
                        print(f"      Valores: {list(valores_unicos)}")
                    else:
                        print(f"      Exemplo: {list(valores_unicos[:5])}")
    
    def analisar_aba_resumo(self):
        """Analisa a aba resumo_cx"""
        print("\n" + "=" * 80)
        print("ANÁLISE DA ABA RESUMO")
        print("=" * 80)
        
        try:
            df = pd.read_excel(self.arquivo_exemplo, sheet_name="resumo_cx")
            print(f"📏 Dimensões: {df.shape[0]} linhas × {df.shape[1]} colunas")
            
            print("\n📊 DADOS DO RESUMO:")
            print(df.to_string())
            
        except Exception as e:
            print(f"❌ Erro ao analisar aba resumo: {e}")
    
    def executar_analise_completa(self):
        """Executa análise completa dos dados de caixa"""
        print("🚀 INICIANDO ANÁLISE COMPLETA DOS DADOS DE CAIXA")
        
        self.analisar_relatorio_padrao()
        self.analisar_aba_diaria() 
        self.analisar_aba_resumo()
        
        print("\n" + "=" * 80)
        print("✅ ANÁLISE COMPLETA FINALIZADA")
        print("=" * 80)
        print("\n🔄 PRÓXIMOS PASSOS:")
        print("1. Criar estrutura padronizada para dados de caixa")
        print("2. Desenvolver script de extração de transações")
        print("3. Integrar com sistema principal de gestão")

if __name__ == "__main__":
    analisador = AnalisadorRelatorioCaixa()
    analisador.executar_analise_completa()