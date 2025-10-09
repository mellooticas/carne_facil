#!/usr/bin/env python3
"""
Debug da Ordem dos Campos
"""

import pandas as pd
from pathlib import Path

def debug_ordem_campos():
    """Debug da ordem de processamento dos campos"""
    
    arquivo_teste = Path("data/raw/OS NOVA - mesa01.xlsm")
    
    try:
        df = pd.read_excel(arquivo_teste, sheet_name='base_clientes_OS')
        
        print("🔍 ORDEM DE PROCESSAMENTO DOS CAMPOS:")
        print("=" * 60)
        
        campos = {}
        
        for i, col in enumerate(df.columns, 1):
            col_lower = str(col).lower().strip()
            print(f"{i:2d}. '{col}' → '{col_lower}'")
            
            # Verificar cada condição
            if 'celular' in col_lower:
                print(f"    📱 MATCH CELULAR!")
                if 'celular' not in campos:
                    campos['celular'] = col
                    print(f"    ✅ DEFINIDO como celular")
                else:
                    print(f"    ❌ Já existe celular: {campos['celular']}")
            
            if 'telefone' in col_lower:
                print(f"    📞 MATCH TELEFONE!")
                if 'celular' not in campos:
                    campos['celular'] = col
                    print(f"    ✅ DEFINIDO como celular (via telefone)")
                else:
                    print(f"    ❌ Já existe celular: {campos['celular']}")
        
        print(f"\n📋 RESULTADO FINAL:")
        print(f"✅ Campo celular mapeado para: '{campos.get('celular', 'NÃO ENCONTRADO')}'")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    debug_ordem_campos()