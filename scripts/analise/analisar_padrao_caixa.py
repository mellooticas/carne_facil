#!/usr/bin/env python3
"""
Analisador de Padrão de Arquivos de Caixa
Analisa estrutura e padrões de um arquivo de caixa para entender o modelo
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import re

class AnalisadorPadraoCaixa:
    def __init__(self):
        self.pasta_caixa = Path("data/caixa_lojas")
        
    def selecionar_arquivo_exemplo(self):
        """Seleciona um arquivo de exemplo para análise"""
        print("=" * 80)
        print("ANALISADOR DE PADRÃO - ARQUIVOS DE CAIXA")
        print("=" * 80)
        
        # Procurar um arquivo recente (2024)
        for loja in self.pasta_caixa.iterdir():
            if loja.is_dir() and loja.name.startswith("RELATORIO") == False:
                # Mapear prefixos das lojas
                prefixos = {
                    'MAUA': 'MAU',
                    'PERUS': 'PER', 
                    'RIO_PEQUENO': 'RIO',
                    'SAO_MATEUS': 'SAM',
                    'SUZANO': 'SUZ',
                    'SUZANO2': 'SUZ'
                }
                
                prefixo = prefixos.get(loja.name, loja.name[:3])
                pasta_2024 = loja / f"2024_{prefixo}"
                
                if pasta_2024.exists():
                    arquivos = list(pasta_2024.glob("*.xlsx"))
                    if arquivos:
                        arquivo_exemplo = arquivos[0]  # Pegar o primeiro
                        print(f"📄 Arquivo selecionado: {arquivo_exemplo}")
                        print(f"🏪 Loja: {loja.name}")
                        print(f"📅 Período: {arquivo_exemplo.stem}")
                        return arquivo_exemplo
        
        print("❌ Nenhum arquivo encontrado!")
        return None
    
    def analisar_estrutura_completa(self, arquivo_path):
        """Analisa completamente a estrutura do arquivo de caixa"""
        print("\n" + "=" * 60)
        print("ANÁLISE DETALHADA DA ESTRUTURA")
        print("=" * 60)
        
        try:
            # 1. Verificar todas as abas
            xl_file = pd.ExcelFile(arquivo_path)
            print(f"📊 ABAS ENCONTRADAS: {len(xl_file.sheet_names)}")
            print("-" * 40)
            
            for i, aba in enumerate(xl_file.sheet_names, 1):
                try:
                    df_temp = pd.read_excel(arquivo_path, sheet_name=aba, nrows=5)
                    total_rows = len(pd.read_excel(arquivo_path, sheet_name=aba))
                    print(f"{i:2}. {aba:25} | {total_rows:4} linhas | {len(df_temp.columns):2} colunas")
                except Exception as e:
                    print(f"{i:2}. {aba:25} | ERRO: {str(e)[:30]}")
            
            # 2. Analisar aba principal (primeira ou com mais dados)
            aba_principal = self.identificar_aba_principal(xl_file, arquivo_path)
            
            print(f"\n🎯 ANALISANDO ABA PRINCIPAL: '{aba_principal}'")
            print("=" * 50)
            
            df = pd.read_excel(arquivo_path, sheet_name=aba_principal)
            
            # 3. Informações básicas
            print(f"📏 Dimensões: {len(df):,} linhas × {len(df.columns)} colunas")
            print(f"📋 Células não vazias: {df.notna().sum().sum():,}")
            print()
            
            # 4. Análise das colunas
            self.analisar_colunas(df)
            
            # 5. Identificar seções/blocos
            self.identificar_secoes(df)
            
            # 6. Analisar tipos de dados
            self.analisar_tipos_dados(df)
            
            # 7. Procurar padrões de controle de caixa
            self.identificar_padroes_caixa(df)
            
            # 8. Gerar relatório
            self.gerar_relatorio_padrao(arquivo_path, xl_file.sheet_names, df, aba_principal)
            
            return df
            
        except Exception as e:
            print(f"❌ Erro na análise: {e}")
            return None
    
    def identificar_aba_principal(self, xl_file, arquivo_path):
        """Identifica a aba principal (com mais dados)"""
        max_linhas = 0
        aba_principal = xl_file.sheet_names[0]
        
        for aba in xl_file.sheet_names:
            try:
                df_temp = pd.read_excel(arquivo_path, sheet_name=aba)
                if len(df_temp) > max_linhas:
                    max_linhas = len(df_temp)
                    aba_principal = aba
            except:
                continue
                
        return aba_principal
    
    def analisar_colunas(self, df):
        """Análise detalhada das colunas"""
        print("📋 ESTRUTURA DAS COLUNAS:")
        print("-" * 70)
        print(f"{'#':>3} | {'COLUNA':25} | {'TIPO':12} | {'NÃO NULOS':>8} | {'ÚNICOS':>6}")
        print("-" * 70)
        
        for i, col in enumerate(df.columns, 1):
            tipo = str(df[col].dtype)
            nao_nulos = df[col].notna().sum()
            unicos = df[col].nunique()
            nome_col = str(col)[:25]
            
            print(f"{i:3} | {nome_col:25} | {tipo:12} | {nao_nulos:>8} | {unicos:>6}")
        
        print()
    
    def identificar_secoes(self, df):
        """Identifica seções/blocos no arquivo"""
        print("🔍 IDENTIFICAÇÃO DE SEÇÕES:")
        print("-" * 40)
        
        # Procurar linhas que podem ser cabeçalhos/seções
        secoes_encontradas = []
        
        for i, row in df.head(50).iterrows():  # Analisar primeiras 50 linhas
            linha_str = ' '.join([str(val) for val in row.values if pd.notna(val)]).upper()
            
            # Padrões típicos de caixa
            if any(palavra in linha_str for palavra in ['CAIXA', 'RECEITA', 'DESPESA', 'SALDO', 'TOTAL', 'ABERTURA', 'FECHAMENTO']):
                secoes_encontradas.append({
                    'linha': i + 1,
                    'conteudo': linha_str[:60] + '...' if len(linha_str) > 60 else linha_str
                })
        
        if secoes_encontradas:
            for secao in secoes_encontradas:
                print(f"  Linha {secao['linha']:2}: {secao['conteudo']}")
        else:
            print("  Nenhuma seção específica identificada")
        
        print()
    
    def analisar_tipos_dados(self, df):
        """Analisa tipos de dados e identifica padrões"""
        print("📊 ANÁLISE DE TIPOS DE DADOS:")
        print("-" * 40)
        
        # Contar tipos
        tipos_count = df.dtypes.value_counts()
        for tipo, count in tipos_count.items():
            print(f"  {tipo}: {count} colunas")
        
        # Identificar colunas numéricas (possíveis valores)
        colunas_numericas = df.select_dtypes(include=[np.number]).columns
        if len(colunas_numericas) > 0:
            print(f"\n💰 COLUNAS NUMÉRICAS ({len(colunas_numericas)}):")
            for col in colunas_numericas:
                if df[col].notna().sum() > 0:
                    min_val = df[col].min()
                    max_val = df[col].max()
                    soma = df[col].sum()
                    print(f"  {col[:25]:25} | Min: {min_val:>10.2f} | Max: {max_val:>12.2f} | Soma: {soma:>15.2f}")
        
        # Identificar colunas de texto importantes
        colunas_texto = df.select_dtypes(include=['object']).columns
        if len(colunas_texto) > 0:
            print(f"\n📝 COLUNAS DE TEXTO ({len(colunas_texto)}):")
            for col in colunas_texto:
                valores_unicos = df[col].nunique()
                print(f"  {col[:30]:30} | {valores_unicos:4} valores únicos")
        
        print()
    
    def identificar_padroes_caixa(self, df):
        """Identifica padrões específicos de controle de caixa"""
        print("🎯 PADRÕES DE CONTROLE DE CAIXA:")
        print("-" * 40)
        
        # Procurar colunas típicas de caixa
        padroes_caixa = {
            'DATA': ['data', 'dt', 'date'],
            'DESCRIÇÃO': ['descricao', 'historico', 'obs', 'observacao'],
            'ENTRADA': ['entrada', 'receita', 'credito', 'debito'],
            'SAÍDA': ['saida', 'despesa', 'gasto'],
            'VALOR': ['valor', 'total', 'quantia'],
            'SALDO': ['saldo', 'acumulado'],
            'CATEGORIA': ['categoria', 'tipo', 'classificacao']
        }
        
        campos_identificados = {}
        
        for padrao, palavras in padroes_caixa.items():
            for col in df.columns:
                col_lower = str(col).lower()
                if any(palavra in col_lower for palavra in palavras):
                    if padrao not in campos_identificados:
                        campos_identificados[padrao] = []
                    campos_identificados[padrao].append(col)
        
        if campos_identificados:
            for padrao, colunas in campos_identificados.items():
                print(f"  {padrao:12}: {', '.join(colunas)}")
        else:
            print("  Nenhum padrão específico identificado automaticamente")
        
        # Mostrar amostra dos dados
        print(f"\n📋 AMOSTRA DOS DADOS (primeiras 5 linhas):")
        print("-" * 80)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        try:
            print(df.head().to_string())
        except:
            print("Erro ao exibir amostra dos dados")
        
        print()
    
    def gerar_relatorio_padrao(self, arquivo_path, sheet_names, df, aba_principal):
        """Gera relatório do padrão identificado"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        relatorio_path = f"data/caixa_lojas/ANALISE_PADRAO_CAIXA_{timestamp}.xlsx"
        
        with pd.ExcelWriter(relatorio_path, engine='openpyxl') as writer:
            # 1. Resumo da análise
            resumo = {
                'ITEM': [
                    'Arquivo Analisado',
                    'Aba Principal', 
                    'Total de Abas',
                    'Linhas de Dados',
                    'Colunas de Dados',
                    'Data da Análise'
                ],
                'VALOR': [
                    arquivo_path.name,
                    aba_principal,
                    len(sheet_names),
                    len(df),
                    len(df.columns),
                    timestamp
                ]
            }
            pd.DataFrame(resumo).to_excel(writer, sheet_name='Resumo_Analise', index=False)
            
            # 2. Lista de abas
            abas_info = pd.DataFrame({'Abas_Encontradas': sheet_names})
            abas_info.to_excel(writer, sheet_name='Lista_Abas', index=False)
            
            # 3. Informações das colunas
            colunas_info = []
            for col in df.columns:
                colunas_info.append({
                    'Coluna': col,
                    'Tipo': str(df[col].dtype),
                    'Nao_Nulos': df[col].notna().sum(),
                    'Valores_Unicos': df[col].nunique(),
                    'Exemplo': str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else 'N/A'
                })
            
            pd.DataFrame(colunas_info).to_excel(writer, sheet_name='Info_Colunas', index=False)
            
            # 4. Amostra dos dados
            df.head(100).to_excel(writer, sheet_name='Amostra_Dados', index=False)
        
        print(f"💾 Relatório de padrão salvo: {relatorio_path}")
        return relatorio_path

def main():
    analisador = AnalisadorPadraoCaixa()
    
    # Selecionar arquivo exemplo
    arquivo = analisador.selecionar_arquivo_exemplo()
    
    if arquivo:
        # Analisar estrutura
        resultado = analisador.analisar_estrutura_completa(arquivo)
        
        if resultado is not None:
            print("\n✅ ANÁLISE DE PADRÃO CONCLUÍDA!")
            print("📁 Relatório salvo em: data/caixa_lojas/")
            print("\n🔄 PRÓXIMOS PASSOS:")
            print("1. Revisar padrões identificados")
            print("2. Criar script de padronização")
            print("3. Processar todos os arquivos de caixa")
    else:
        print("❌ Não foi possível selecionar arquivo para análise")

if __name__ == "__main__":
    main()