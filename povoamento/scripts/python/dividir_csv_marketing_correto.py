#!/usr/bin/env python3
"""
Script para dividir CSV CORRETO em partes menores
"""

import pandas as pd
import os
from pathlib import Path

# Configurações
TAMANHO_MAX_MB = 10
INPUT_FILE = 'dados/csv/marketing_origens_vixen_correto.csv'
OUTPUT_DIR = 'dados/csv/marketing_partes'

def dividir_csv_correto():
    print("📂 Lendo arquivo:", INPUT_FILE)
    
    # Criar diretório
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    # Ler CSV
    df = pd.read_csv(INPUT_FILE, encoding='utf-8')
    
    total_linhas = len(df)
    tamanho_bytes = os.path.getsize(INPUT_FILE)
    tamanho_mb = tamanho_bytes / (1024 * 1024)
    
    print(f"📊 Total: {total_linhas:,} registros | {tamanho_mb:.2f} MB")
    print(f"🎯 Dividindo em partes de até {TAMANHO_MAX_MB} MB...")
    print()
    
    # Calcular linhas por parte
    linhas_por_mb = total_linhas / tamanho_mb
    linhas_por_parte = int(linhas_por_mb * TAMANHO_MAX_MB)
    numero_partes = (total_linhas // linhas_por_parte) + 1
    
    for i in range(numero_partes):
        inicio = i * linhas_por_parte
        fim = min((i + 1) * linhas_por_parte, total_linhas)
        
        df_parte = df.iloc[inicio:fim]
        
        output_file = f"{OUTPUT_DIR}/parte_{i+1:02d}_de_{numero_partes:02d}.csv"
        df_parte.to_csv(output_file, index=False, encoding='utf-8')
        
        tamanho_parte_mb = os.path.getsize(output_file) / (1024 * 1024)
        
        print(f"✅ Parte {i+1}/{numero_partes}: {len(df_parte):,} registros | {tamanho_parte_mb:.2f} MB")
    
    print()
    print("=" * 70)
    print("🎉 DIVISÃO CONCLUÍDA!")
    print("=" * 70)
    print()
    print(f"📁 Arquivos em: {OUTPUT_DIR}/")
    print()
    print("📋 INSTRUÇÕES PARA IMPORTAR:")
    print()
    print("1. Criar tabela: \\i 63_CRIAR_STAGING_MARKETING_VIXEN.sql")
    print()
    print("2. Importar cada parte no DBeaver (⚠️ APPEND, não truncar):")
    for i in range(numero_partes):
        print(f"   {i+1}. parte_{i+1:02d}_de_{numero_partes:02d}.csv")
    print()
    print("3. Validar:")
    print(f"   SELECT COUNT(*) FROM staging.marketing_origens_vixen;")
    print(f"   Esperado: {total_linhas:,}")
    print()

if __name__ == '__main__':
    dividir_csv_correto()
