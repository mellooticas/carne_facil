#!/usr/bin/env python3
"""
Mapeador de Tabelas Restantes - Carne Fácil
Analisa os arquivos Excel para encontrar outras tabelas além de vend(dia) e rest_entr(dia)
"""

import os
import pandas as pd
from pathlib import Path
import re

def mapear_tabelas_restantes():
    """Mapear todas as tabelas restantes nos arquivos Excel"""
    
    lojas = {
        'MAUA': 'data/caixa_lojas/MAUA',
        'SUZANO': 'data/caixa_lojas/SUZANO', 
        'RIO_PEQUENO': 'data/caixa_lojas/RIO_PEQUENO',
        'PERUS': 'data/caixa_lojas/PERUS',
        'SUZANO2': 'data/caixa_lojas/SUZANO2',
        'SAO_MATEUS': 'data/caixa_lojas/SAO_MATEUS'
    }
    
    tabelas_encontradas = {}
    
    for loja, pasta in lojas.items():
        print(f"\nAnalisando loja: {loja}")
        print("=" * 50)
        
        if not os.path.exists(pasta):
            print(f"   Pasta nao encontrada: {pasta}")
            continue
            
        # Pegar um arquivo de exemplo
        excel_files = [f for f in os.listdir(pasta) if f.endswith('.xlsx')]
        if not excel_files:
            print(f"   Nenhum arquivo Excel encontrado")
            continue
            
        arquivo_exemplo = os.path.join(pasta, excel_files[0])
        print(f"   Analisando arquivo: {excel_files[0]}")
        
        try:
            wb = pd.ExcelFile(arquivo_exemplo)
            
            # Pegar a primeira planilha (dia 1)
            primeira_sheet = wb.sheet_names[0]
            df = pd.read_excel(arquivo_exemplo, sheet_name=primeira_sheet)
            
            print(f"   Planilha: {primeira_sheet}")
            print(f"   Dimensoes: {df.shape}")
            
            # Procurar por cabeçalhos em toda a planilha
            cabeçalhos_encontrados = []
            
            for i in range(min(50, df.shape[0])):  # Verificar até linha 50
                for j in range(min(20, df.shape[1])):  # Verificar até coluna T
                    celula = df.iloc[i, j] if i < df.shape[0] and j < df.shape[1] else None
                    
                    if pd.notna(celula):
                        celula_str = str(celula).strip()
                        
                        # Procurar padrões de cabeçalhos
                        patterns = [
                            r'.*vendas?.*',
                            r'.*entrada.*',
                            r'.*saida.*',
                            r'.*sangria.*',
                            r'.*reforco.*',
                            r'.*gasto.*',
                            r'.*despesa.*',
                            r'.*receita.*',
                            r'.*caixa.*',
                            r'.*pagamento.*',
                            r'.*recebimento.*',
                            r'.*dinheiro.*',
                            r'.*cartao.*',
                            r'.*pix.*',
                            r'.*cheque.*',
                            r'.*total.*'
                        ]
                        
                        for pattern in patterns:
                            if re.match(pattern, celula_str.lower()):
                                posicao = f"{chr(65+j)}{i+1}"
                                if celula_str not in [item[0] for item in cabeçalhos_encontrados]:
                                    cabeçalhos_encontrados.append((celula_str, posicao, i, j))
            
            print(f"   Cabecalhos encontrados:")
            for cabecalho, pos, linha, coluna in cabeçalhos_encontrados:
                print(f"      {pos}: {cabecalho}")
            
            tabelas_encontradas[loja] = cabeçalhos_encontrados
                
        except Exception as e:
            print(f"   Erro ao processar: {e}")
    
    # Resumo consolidado
    print("\n" + "="*70)
    print("RESUMO CONSOLIDADO DAS TABELAS")
    print("="*70)
    
    todos_cabeçalhos = {}
    for loja, cabecalhos in tabelas_encontradas.items():
        for cabecalho, pos, linha, coluna in cabecalhos:
            if cabecalho.lower() not in todos_cabeçalhos:
                todos_cabeçalhos[cabecalho.lower()] = []
            todos_cabeçalhos[cabecalho.lower()].append((loja, pos))
    
    for cabecalho, lojas_pos in todos_cabeçalhos.items():
        print(f"\n{cabecalho.upper()}")
        for loja, pos in lojas_pos:
            print(f"   {loja}: {pos}")
    
    return tabelas_encontradas

if __name__ == "__main__":
    tabelas = mapear_tabelas_restantes()