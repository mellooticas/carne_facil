#!/usr/bin/env python3
"""
Analisador Especial de Arquivo de Clientes Vixen
Análise detalhada da estrutura do arquivo clientes_completos_vixen.XLSX
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import re

class AnalisadorClientesVixen:
    def __init__(self):
        self.arquivo_path = Path("data/analise_especial/clientes_completos_vixen.XLSX")
        self.resultados = {}
        
    def analisar_estrutura_completa(self):
        """Análise completa do arquivo de clientes"""
        print("=" * 80)
        print("ANALISADOR ESPECIAL - CLIENTES VIXEN")
        print("=" * 80)
        
        if not self.arquivo_path.exists():
            print(f"❌ Arquivo não encontrado: {self.arquivo_path}")
            return None
            
        try:
            # 1. Informações básicas do arquivo
            print(f"📄 Arquivo: {self.arquivo_path.name}")
            print(f"📏 Tamanho: {self.arquivo_path.stat().st_size / 1024 / 1024:.2f} MB")
            print()
            
            # 2. Verificar abas disponíveis
            xl_file = pd.ExcelFile(self.arquivo_path)
            print(f"📊 Abas encontradas: {len(xl_file.sheet_names)}")
            for i, aba in enumerate(xl_file.sheet_names, 1):
                try:
                    df_temp = pd.read_excel(self.arquivo_path, sheet_name=aba, nrows=1)
                    total_rows = len(pd.read_excel(self.arquivo_path, sheet_name=aba))
                    print(f"   {i:2}. {aba:30} | {total_rows:,} linhas | {len(df_temp.columns)} colunas")
                except Exception as e:
                    print(f"   {i:2}. {aba:30} | Erro ao ler: {str(e)[:50]}")
            
            # 3. Analisar aba principal (primeira ou maior)
            aba_principal = xl_file.sheet_names[0]
            max_linhas = 0
            
            for aba in xl_file.sheet_names:
                try:
                    df_temp = pd.read_excel(self.arquivo_path, sheet_name=aba)
                    if len(df_temp) > max_linhas:
                        max_linhas = len(df_temp)
                        aba_principal = aba
                except:
                    continue
                    
            print()
            print(f"🎯 ANÁLISE DETALHADA DA ABA PRINCIPAL: '{aba_principal}'")
            print("=" * 60)
            
            # Carregar dados da aba principal
            df = pd.read_excel(self.arquivo_path, sheet_name=aba_principal)
            
            print(f"📏 Dimensões: {len(df):,} linhas × {len(df.columns)} colunas")
            print()
            
            # 4. Análise das colunas
            print("📋 ESTRUTURA DAS COLUNAS:")
            print("-" * 80)
            print(f"{'#':>3} | {'COLUNA':30} | {'TIPO':15} | {'NÃO NULOS':>10} | {'ÚNICOS':>8}")
            print("-" * 80)
            
            for i, col in enumerate(df.columns, 1):
                tipo = str(df[col].dtype)
                nao_nulos = df[col].notna().sum()
                unicos = df[col].nunique()
                print(f"{i:3} | {str(col)[:30]:30} | {tipo:15} | {nao_nulos:>10} | {unicos:>8}")
            
            print()
            
            # 5. Identificar campos importantes
            print("🔍 CAMPOS IDENTIFICADOS:")
            print("-" * 40)
            
            campos_cliente = self.identificar_campos_cliente(df)
            for categoria, campos in campos_cliente.items():
                if campos:
                    print(f"{categoria}:")
                    for campo in campos:
                        print(f"  • {campo}")
                    print()
            
            # 6. Amostra dos dados
            print("📋 AMOSTRA DOS DADOS (primeiras 5 linhas):")
            print("-" * 80)
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', None)
            print(df.head().to_string())
            print()
            
            # 7. Análise de qualidade dos dados
            self.analisar_qualidade_dados(df)
            
            # 8. Salvar relatório
            self.gerar_relatorio(df, aba_principal)
            
            return df
            
        except Exception as e:
            print(f"❌ Erro na análise: {e}")
            return None
    
    def identificar_campos_cliente(self, df):
        """Identifica e categoriza campos relacionados a clientes"""
        campos = {
            "IDENTIFICAÇÃO": [],
            "DADOS PESSOAIS": [],
            "CONTATO": [],
            "ENDEREÇO": [],
            "ÓTICA/LOJA": [],
            "FINANCEIRO": [],
            "DATAS": [],
            "OUTROS": []
        }
        
        for col in df.columns:
            col_lower = str(col).lower()
            
            # Identificação
            if any(x in col_lower for x in ['id', 'codigo', 'numero', 'cpf', 'rg', 'cnpj']):
                campos["IDENTIFICAÇÃO"].append(col)
            # Dados pessoais
            elif any(x in col_lower for x in ['nome', 'sexo', 'idade', 'nascimento', 'genero']):
                campos["DADOS PESSOAIS"].append(col)
            # Contato
            elif any(x in col_lower for x in ['telefone', 'celular', 'email', 'fone', 'whats']):
                campos["CONTATO"].append(col)
            # Endereço
            elif any(x in col_lower for x in ['endereco', 'rua', 'avenida', 'cidade', 'estado', 'cep', 'bairro']):
                campos["ENDEREÇO"].append(col)
            # Ótica/Loja
            elif any(x in col_lower for x in ['loja', 'filial', 'unidade', 'vendedor', 'consultor']):
                campos["ÓTICA/LOJA"].append(col)
            # Financeiro
            elif any(x in col_lower for x in ['valor', 'preco', 'desconto', 'total', 'pagamento']):
                campos["FINANCEIRO"].append(col)
            # Datas
            elif any(x in col_lower for x in ['data', 'date', 'cadastro', 'atualizacao']):
                campos["DATAS"].append(col)
            else:
                campos["OUTROS"].append(col)
                
        return campos
    
    def analisar_qualidade_dados(self, df):
        """Análise da qualidade dos dados"""
        print("📊 QUALIDADE DOS DADOS:")
        print("-" * 40)
        
        total_registros = len(df)
        print(f"Total de registros: {total_registros:,}")
        
        # Registros completamente vazios
        vazios = df.isnull().all(axis=1).sum()
        print(f"Registros completamente vazios: {vazios:,}")
        
        # Registros duplicados
        duplicados = df.duplicated().sum()
        print(f"Registros duplicados: {duplicados:,}")
        
        # Campos com mais dados
        campos_preenchidos = []
        for col in df.columns:
            pct_preenchido = (df[col].notna().sum() / total_registros) * 100
            if pct_preenchido > 50:  # Mais de 50% preenchido
                campos_preenchidos.append((col, pct_preenchido))
        
        print(f"\nCampos bem preenchidos (>50%):")
        for campo, pct in sorted(campos_preenchidos, key=lambda x: x[1], reverse=True)[:10]:
            print(f"  • {campo}: {pct:.1f}%")
        
        print()
    
    def gerar_relatorio(self, df, aba_principal):
        """Gera relatório detalhado da análise"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_saida = f"data/analise_especial/ANALISE_CLIENTES_VIXEN_{timestamp}.xlsx"
        
        with pd.ExcelWriter(arquivo_saida, engine='openpyxl') as writer:
            # 1. Resumo geral
            resumo_data = {
                'MÉTRICA': [
                    'Total de Registros',
                    'Total de Colunas', 
                    'Aba Analisada',
                    'Registros Vazios',
                    'Registros Duplicados',
                    'Data da Análise'
                ],
                'VALOR': [
                    len(df),
                    len(df.columns),
                    aba_principal,
                    df.isnull().all(axis=1).sum(),
                    df.duplicated().sum(),
                    timestamp
                ]
            }
            
            pd.DataFrame(resumo_data).to_excel(writer, sheet_name='Resumo_Geral', index=False)
            
            # 2. Informações das colunas
            colunas_info = []
            for col in df.columns:
                colunas_info.append({
                    'Coluna': col,
                    'Tipo': str(df[col].dtype),
                    'Total_Registros': len(df),
                    'Nao_Nulos': df[col].notna().sum(),
                    'Percentual_Preenchido': f"{(df[col].notna().sum() / len(df)) * 100:.1f}%",
                    'Valores_Unicos': df[col].nunique(),
                    'Exemplo_Valor': str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else 'N/A'
                })
            
            pd.DataFrame(colunas_info).to_excel(writer, sheet_name='Detalhes_Colunas', index=False)
            
            # 3. Amostra dos dados (primeiras 1000 linhas)
            df_sample = df.head(1000)
            df_sample.to_excel(writer, sheet_name='Amostra_Dados', index=False)
        
        print(f"💾 Relatório salvo: {arquivo_saida}")
        return arquivo_saida

def main():
    analisador = AnalisadorClientesVixen()
    resultado = analisador.analisar_estrutura_completa()
    
    if resultado is not None:
        print()
        print("✅ ANÁLISE CONCLUÍDA!")
        print("📁 Arquivos salvos em: data/analise_especial/")
        print()
        print("🔄 PRÓXIMOS PASSOS SUGERIDOS:")
        print("1. Revisar o relatório gerado")
        print("2. Identificar campos para integração")
        print("3. Criar script de integração específico")
        print("4. Testar compatibilidade com sistema atual")

if __name__ == "__main__":
    main()