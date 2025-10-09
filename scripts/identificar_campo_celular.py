#!/usr/bin/env python3
"""
Identificar Colunas dos Arquivos Excel
Vamos ver onde realmente está o campo de celular! 😄
"""

import pandas as pd
from pathlib import Path

def analisar_colunas_arquivo(arquivo_path):
    """Analisa as colunas de um arquivo específico"""
    
    print(f"📁 Analisando: {arquivo_path.name}")
    print("-" * 60)
    
    try:
        # Carregar arquivo
        engine = 'openpyxl' if arquivo_path.suffix.lower() in ['.xlsx', '.xlsm'] else None
        excel_file = pd.ExcelFile(arquivo_path, engine=engine)
        
        print(f"📋 Sheets disponíveis: {excel_file.sheet_names}")
        
        # Tentar ler a primeira sheet
        sheet_name = excel_file.sheet_names[0]
        df = pd.read_excel(arquivo_path, sheet_name=sheet_name, engine=engine)
        
        print(f"\n📊 Colunas encontradas ({len(df.columns)} total):")
        print("-" * 60)
        
        for i, col in enumerate(df.columns, 1):
            print(f"{i:2d}. {col}")
        
        # Procurar por campos relacionados a telefone/celular
        print(f"\n📱 CAMPOS RELACIONADOS A TELEFONE/CELULAR:")
        print("-" * 60)
        
        campos_telefone = []
        for col in df.columns:
            col_lower = str(col).lower()
            if any(termo in col_lower for termo in ['tel', 'cel', 'fone', 'phone']):
                campos_telefone.append(col)
                print(f"📞 {col}")
        
        if not campos_telefone:
            print("❌ Nenhum campo de telefone/celular encontrado!")
        
        # Mostrar algumas amostras dos campos de telefone
        if campos_telefone:
            print(f"\n📋 AMOSTRAS DOS DADOS (primeiras 5 linhas):")
            print("-" * 60)
            
            for campo in campos_telefone:
                print(f"\n📞 Campo: {campo}")
                amostras = df[campo].dropna().head(5).tolist()
                for i, amostra in enumerate(amostras, 1):
                    print(f"   {i}. {amostra}")
        
        return df.columns.tolist(), campos_telefone
        
    except Exception as e:
        print(f"❌ Erro ao processar: {e}")
        return [], []

def analisar_varios_arquivos():
    """Analisa vários arquivos para encontrar padrões"""
    
    print("🔍 ANÁLISE DE COLUNAS - IDENTIFICANDO CAMPOS DE CELULAR")
    print("=" * 80)
    print("🎯 Objetivo: Encontrar onde estão os dados de celular nos arquivos")
    print("=" * 80)
    
    # Pegar alguns arquivos para análise
    arquivos = list(Path("data/raw").glob("OS*.xlsm"))[:3]  # Analisar apenas 3 para começar
    
    if not arquivos:
        print("❌ Nenhum arquivo encontrado na pasta data/raw")
        return
    
    todos_campos_telefone = set()
    
    for arquivo in arquivos:
        print(f"\n")
        colunas, campos_telefone = analisar_colunas_arquivo(arquivo)
        todos_campos_telefone.update(campos_telefone)
        print("=" * 80)
    
    # Resumo final
    print(f"\n📊 RESUMO - CAMPOS DE TELEFONE/CELULAR ENCONTRADOS:")
    print("-" * 60)
    
    if todos_campos_telefone:
        for campo in sorted(todos_campos_telefone):
            print(f"📱 {campo}")
    else:
        print("❌ Nenhum campo específico de telefone/celular encontrado")
        print("💡 Talvez esteja em um campo genérico como 'contato' ou 'dados'")
    
    print(f"\n🎯 PRÓXIMO PASSO:")
    print("-" * 60)
    print("✅ Atualizar o script de consolidação para usar o campo correto")
    print("✅ Testar a validação de celular no campo identificado")

if __name__ == "__main__":
    analisar_varios_arquivos()