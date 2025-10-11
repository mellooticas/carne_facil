#!/usr/bin/env python3
"""
ANALISADOR DETALHADO DA TABELA VEND
Analisa a estrutura exata da seção de vendas para ajustar o extrator
"""

import pandas as pd
from pathlib import Path
import openpyxl
from typing import List

class AnalisadorDetalhadoVEND:
    def __init__(self):
        self.pasta_caixa = Path("data/caixa_lojas")
        self.arquivo_exemplo = self.pasta_caixa / "MAUA/2024_MAU/abr_24.xlsx"
    
    def analisar_secao_vend_detalhada(self, aba: str = "04"):
        """Analisa em detalhes a seção de vendas"""
        print("=" * 80)
        print(f"🔬 ANÁLISE DETALHADA DA SEÇÃO VEND - DIA {aba}")
        print("=" * 80)
        
        try:
            df = pd.read_excel(self.arquivo_exemplo, sheet_name=aba, header=None)
            
            # Encontrar seção de vendas
            inicio_vend = None
            for i, row in df.iterrows():
                linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
                if 'VENDAS' in linha_texto.upper() and 'Nº VENDA' in linha_texto.upper():
                    inicio_vend = i
                    break
            
            if inicio_vend is None:
                print("❌ Seção VEND não encontrada")
                return
            
            print(f"✅ Seção VEND encontrada na linha {inicio_vend}")
            
            # Analisar as próximas 15 linhas após o cabeçalho
            print(f"\n📊 ANÁLISE DAS PRÓXIMAS 15 LINHAS:")
            print("-" * 80)
            
            for i in range(inicio_vend, min(inicio_vend + 15, len(df))):
                row = df.iloc[i]
                linha_numero = i + 1  # +1 porque Excel começa em 1
                
                # Mostrar apenas colunas com dados
                valores_nao_nulos = [(j, val) for j, val in enumerate(row) if pd.notna(val)]
                
                if valores_nao_nulos:
                    print(f"Linha {linha_numero:2d}:")
                    for col_idx, valor in valores_nao_nulos:
                        col_letter = chr(65 + col_idx)  # A, B, C, etc.
                        print(f"   {col_letter}: {valor}")
                    
                    # Analisar se pode ser uma venda
                    self.analisar_possivel_venda(valores_nao_nulos, linha_numero)
                    print()
                else:
                    print(f"Linha {linha_numero:2d}: (vazia)")
            
            # Análise específica das vendas
            self.identificar_padroes_venda(df, inicio_vend)
            
        except Exception as e:
            print(f"❌ Erro na análise: {e}")
    
    def analisar_possivel_venda(self, valores: List, linha_num: int):
        """Analisa se uma linha pode ser uma venda"""
        # Extrair apenas os valores
        vals = [val for col_idx, val in valores]
        
        # Procurar número de venda (4 dígitos começando com 4)
        numeros_venda = []
        for val in vals:
            if isinstance(val, (int, float)) and not pd.isna(val):
                val_str = str(int(val))
                if len(val_str) == 4 and val_str.startswith('4'):
                    numeros_venda.append(val_str)
        
        # Procurar valores monetários
        valores_monetarios = []
        for val in vals:
            if isinstance(val, (int, float)) and not pd.isna(val) and val > 50:
                valores_monetarios.append(val)
        
        # Procurar nomes (strings longas)
        nomes_possiveis = []
        for val in vals:
            if isinstance(val, str) and len(val) > 5:
                nomes_possiveis.append(val)
        
        # Procurar formas de pagamento
        formas_pagto = []
        for val in vals:
            if isinstance(val, str):
                val_upper = val.upper().strip()
                if val_upper in ['DN', 'CTD', 'CTC', 'PIX', 'SS', 'GARANTIA']:
                    formas_pagto.append(val_upper)
        
        # Diagnóstico
        if numeros_venda or valores_monetarios or formas_pagto:
            print(f"   🎯 POSSÍVEL VENDA:")
            if numeros_venda:
                print(f"      📄 Números de venda: {numeros_venda}")
            if nomes_possiveis:
                print(f"      👤 Nomes possíveis: {nomes_possiveis}")
            if formas_pagto:
                print(f"      💳 Forma pagamento: {formas_pagto}")
            if valores_monetarios:
                print(f"      💰 Valores: {valores_monetarios}")
    
    def identificar_padroes_venda(self, df: pd.DataFrame, inicio_vend: int):
        """Identifica padrões específicos das vendas"""
        print("=" * 80)
        print("🎯 IDENTIFICAÇÃO DE PADRÕES DE VENDA")
        print("=" * 80)
        
        vendas_encontradas = []
        
        # Analisar cada linha após o cabeçalho
        for i in range(inicio_vend + 1, min(inicio_vend + 10, len(df))):
            row = df.iloc[i]
            valores = [val for val in row if pd.notna(val)]
            
            if not valores:
                continue
            
            # Verificar se contém número de venda
            numero_venda = None
            for val in valores:
                if isinstance(val, (int, float)):
                    val_str = str(int(val))
                    if len(val_str) == 4 and val_str.startswith('4'):
                        numero_venda = val_str
                        break
            
            if numero_venda:
                linha_info = {
                    'linha': i + 1,
                    'numero_venda': numero_venda,
                    'valores': valores,
                    'dados_brutos': str(row.tolist())
                }
                vendas_encontradas.append(linha_info)
                
                print(f"📄 Venda encontrada na linha {i + 1}:")
                print(f"   Número: {numero_venda}")
                print(f"   Dados: {valores}")
                print()
        
        if not vendas_encontradas:
            print("⚠️  Nenhuma venda encontrada com o padrão atual")
            print("\n🔍 VAMOS ANALISAR TODAS AS LINHAS COM NÚMEROS DE 4 DÍGITOS:")
            
            for i in range(len(df)):
                row = df.iloc[i]
                valores = [val for val in row if pd.notna(val)]
                
                for val in valores:
                    if isinstance(val, (int, float)):
                        val_str = str(int(val))
                        if len(val_str) == 4 and val_str.startswith('4'):
                            print(f"   Linha {i + 1}: {val_str} | Dados: {valores}")
        
        return vendas_encontradas

if __name__ == "__main__":
    analisador = AnalisadorDetalhadoVEND()
    
    print("🔬 INICIANDO ANÁLISE DETALHADA DA TABELA VEND")
    
    # Analisar dias específicos
    for dia in ["04", "20", "30"]:
        analisador.analisar_secao_vend_detalhada(dia)
        print("\n" + "="*40 + "\n")