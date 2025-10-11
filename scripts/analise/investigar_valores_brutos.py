#!/usr/bin/env python3
"""
INVESTIGADOR DE VALORES BRUTOS
Analisa os valores como estão armazenados na planilha
"""

import pandas as pd
from pathlib import Path

def investigar_valores_brutos():
    arquivo = Path("data/caixa_lojas/MAUA/2024_MAU/abr_24.xlsx")
    
    print("🔍 INVESTIGANDO VALORES BRUTOS DA PLANILHA")
    print("=" * 50)
    
    df = pd.read_excel(arquivo, sheet_name='20', header=None)
    
    print("Linha 5 (primeira venda):")
    linha5 = df.iloc[5]
    for i, cell in enumerate(linha5):
        if pd.notna(cell):
            print(f"  Coluna {i}: '{cell}' (tipo: {type(cell).__name__})")
    
    print("\nLinha 6 (segunda venda):")
    linha6 = df.iloc[6]
    for i, cell in enumerate(linha6):
        if pd.notna(cell):
            print(f"  Coluna {i}: '{cell}' (tipo: {type(cell).__name__})")
    
    print(f"\nValores específicos:")
    print(f"Valor venda linha 5, coluna 7: {linha5.iloc[7] if 7 < len(linha5) else 'N/A'}")
    print(f"Entrada linha 5, coluna 8: {linha5.iloc[8] if 8 < len(linha5) else 'N/A'}")
    print(f"Valor venda linha 6, coluna 7: {linha6.iloc[7] if 7 < len(linha6) else 'N/A'}")
    print(f"Entrada linha 6, coluna 8: {linha6.iloc[8] if 8 < len(linha6) else 'N/A'}")

if __name__ == "__main__":
    investigar_valores_brutos()