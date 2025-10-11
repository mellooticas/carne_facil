import pandas as pd
import os

def mapear_arquivo_caixa():
    arquivo = 'data/caixa_lojas/MAUA/2024_MAU/mai_24.xlsx'
    if not os.path.exists(arquivo):
        print("Arquivo nao encontrado")
        return
    
    wb = pd.ExcelFile(arquivo)
    print(f"Arquivo: {arquivo}")
    print(f"Planilhas: {len(wb.sheet_names)}")
    
    # Analisar primeira planilha
    planilha = '1'
    if planilha in wb.sheet_names:
        df = pd.read_excel(arquivo, sheet_name=planilha)
        print(f"\nPlanilha: {planilha}")
        print(f"Dimensoes: {df.shape}")
        
        # Mostrar algumas células
        print("\nCelulas nao vazias nas primeiras 50 linhas:")
        for i in range(min(50, df.shape[0])):
            for j in range(min(15, df.shape[1])):
                if i < df.shape[0] and j < df.shape[1]:
                    celula = df.iloc[i, j]
                    if pd.notna(celula) and str(celula).strip():
                        pos = f"{chr(65+j)}{i+1}"
                        print(f"  {pos}: {str(celula).strip()}")

mapear_arquivo_caixa()