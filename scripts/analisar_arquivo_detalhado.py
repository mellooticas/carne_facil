#!/usr/bin/env python3
"""
Análise Detalhada dos Arquivos Excel
Vamos encontrar os cabeçalhos reais! 😄
"""

import pandas as pd
from pathlib import Path

def analisar_arquivo_detalhado(arquivo_path):
    """Análise mais detalhada de um arquivo"""
    
    print(f"📁 ANÁLISE DETALHADA: {arquivo_path.name}")
    print("=" * 70)
    
    try:
        # Carregar arquivo
        engine = 'openpyxl' if arquivo_path.suffix.lower() in ['.xlsx', '.xlsm'] else None
        excel_file = pd.ExcelFile(arquivo_path, engine=engine)
        
        print(f"📋 Sheets disponíveis: {excel_file.sheet_names}")
        
        # Tentar a sheet base_clientes_OS primeiro
        sheet_name = 'base_clientes_OS' if 'base_clientes_OS' in excel_file.sheet_names else excel_file.sheet_names[0]
        
        print(f"\n🎯 Analisando sheet: {sheet_name}")
        print("-" * 70)
        
        # Tentar diferentes configurações de header
        for header_row in [0, 1, 2]:
            try:
                print(f"\n📋 Tentativa com header na linha {header_row}:")
                df = pd.read_excel(arquivo_path, sheet_name=sheet_name, header=header_row, engine=engine)
                
                print(f"   📊 Colunas ({len(df.columns)} total):")
                for i, col in enumerate(df.columns, 1):
                    print(f"   {i:2d}. {col}")
                
                # Procurar campos interessantes
                campos_importantes = []
                for col in df.columns:
                    col_str = str(col).lower()
                    if any(termo in col_str for termo in ['nome', 'tel', 'cel', 'cpf', 'email', 'endereco', 'fone', 'contato']):
                        campos_importantes.append(col)
                
                if campos_importantes:
                    print(f"\n   📱 CAMPOS IMPORTANTES ENCONTRADOS:")
                    for campo in campos_importantes:
                        print(f"   ✅ {campo}")
                    
                    # Mostrar algumas amostras
                    print(f"\n   📋 AMOSTRAS DOS DADOS:")
                    for campo in campos_importantes[:3]:  # Apenas os 3 primeiros
                        if campo in df.columns:
                            amostras = df[campo].dropna().head(3).tolist()
                            print(f"   📞 {campo}: {amostras}")
                    
                    return df.columns.tolist(), campos_importantes
                
            except Exception as e:
                print(f"   ❌ Erro com header {header_row}: {e}")
        
        return [], []
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return [], []

def main():
    """Função principal"""
    
    print("🔍 ANÁLISE DETALHADA - ENCONTRANDO CAMPOS REAIS")
    print("=" * 80)
    
    # Analisar um arquivo específico primeiro
    arquivo_teste = Path("data/raw/OS NOVA - mesa01.xlsm")
    
    if arquivo_teste.exists():
        colunas, campos_importantes = analisar_arquivo_detalhado(arquivo_teste)
        
        if campos_importantes:
            print(f"\n🎉 SUCESSO! Campos importantes encontrados:")
            for campo in campos_importantes:
                print(f"✅ {campo}")
        else:
            print(f"\n🤔 Vamos tentar outra abordagem...")
            
            # Tentar ver dados brutos
            try:
                df_raw = pd.read_excel(arquivo_teste, sheet_name='base_clientes_OS', header=None, nrows=10)
                print(f"\n📋 PRIMEIRAS 10 LINHAS (dados brutos):")
                print(df_raw.to_string())
            except Exception as e:
                print(f"❌ Erro ao ler dados brutos: {e}")
    else:
        print(f"❌ Arquivo não encontrado: {arquivo_teste}")

if __name__ == "__main__":
    main()