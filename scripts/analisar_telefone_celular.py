#!/usr/bin/env python3
"""
Verificar Qual Campo Tem Mais Dados: TELEFONE ou CELULAR
"""

import pandas as pd
from pathlib import Path

def analisar_telefone_vs_celular():
    """Compara os campos TELEFONE e CELULAR"""
    
    print("📱 ANÁLISE: TELEFONE vs CELULAR")
    print("=" * 50)
    
    arquivo_teste = Path("data/raw/OS NOVA - mesa01.xlsm")
    
    try:
        df = pd.read_excel(arquivo_teste, sheet_name='base_clientes_OS')
        
        # Procurar ambos os campos
        campo_telefone = None
        campo_celular = None
        
        for col in df.columns:
            col_str = str(col).lower().strip()
            if 'telefone' in col_str and not campo_telefone:
                campo_telefone = col
            elif 'celular' in col_str and not campo_celular:
                campo_celular = col
        
        print(f"📞 Campo TELEFONE encontrado: '{campo_telefone}'")
        print(f"📱 Campo CELULAR encontrado: '{campo_celular}'")
        
        if campo_telefone:
            telefones_preenchidos = df[campo_telefone].notna().sum()
            print(f"   📊 TELEFONE preenchidos: {telefones_preenchidos}")
            
            # Amostras
            print(f"   📋 Amostras TELEFONE:")
            for i, tel in enumerate(df[campo_telefone].dropna().head(5), 1):
                print(f"      {i}. {tel}")
        
        if campo_celular:
            celulares_preenchidos = df[campo_celular].notna().sum()
            print(f"   📊 CELULAR preenchidos: {celulares_preenchidos}")
            
            # Amostras
            print(f"   📋 Amostras CELULAR:")
            for i, cel in enumerate(df[campo_celular].dropna().head(5), 1):
                print(f"      {i}. {cel}")
        
        # Recomendação
        print(f"\n🎯 RECOMENDAÇÃO:")
        if campo_celular and campo_telefone:
            tel_count = df[campo_telefone].notna().sum() if campo_telefone else 0
            cel_count = df[campo_celular].notna().sum() if campo_celular else 0
            
            if cel_count > tel_count:
                print(f"✅ Usar campo CELULAR (mais dados: {cel_count} vs {tel_count})")
            elif tel_count > cel_count:
                print(f"✅ Usar campo TELEFONE (mais dados: {tel_count} vs {cel_count})")
            else:
                print(f"⚖️ Usar CELULAR por prioridade (mesmo número de dados)")
        elif campo_celular:
            print(f"✅ Usar campo CELULAR (único disponível)")
        elif campo_telefone:
            print(f"✅ Usar campo TELEFONE (único disponível)")
        else:
            print(f"❌ Nenhum campo encontrado")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    analisar_telefone_vs_celular()