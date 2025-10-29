#!/usr/bin/env python3
"""
Script CORRIGIDO para criar CSV com apenas as 10 colunas da tabela staging
"""

import pandas as pd
from pathlib import Path

# Arquivo de entrada (original do vixen)
INPUT_FILE = 'dados/csv/vendas_os_completo.csv'
OUTPUT_FILE = 'dados/csv/marketing_origens_vixen_correto.csv'

def criar_csv_correto():
    print("=" * 70)
    print("CRIANDO CSV CORRIGIDO - 10 COLUNAS EXATAS")
    print("=" * 70)
    print()
    
    # Mapeamento de nomes de lojas para códigos
    MAPA_LOJAS = {
        'SUZANO': '042',
        'RIO PEQUENO': '048',
        'PERUS': '049',
        'MAUA': '050',
        'SAO MATEUS': '051',
        'SUZANO II': '052'
    }
    
    # Ler arquivo original
    print(f"📂 Lendo: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE, encoding='utf-8', low_memory=False, dtype={'cpf': str})  # Forçar CPF como string
    print(f"   Total original: {len(df):,} registros")
    print()
    
    # Criar DataFrame com APENAS as 10 colunas da tabela
    print("🔄 Selecionando apenas as 10 colunas necessárias...")
    
    # Mapear nomes de lojas para códigos
    df['loja_codigo'] = df['loja'].astype(str).str.strip().map(MAPA_LOJAS)
    
    # Se não encontrar no mapa, tentar usar direto (caso já seja código)
    df['loja_codigo'] = df['loja_codigo'].fillna(df['loja'])
    
    # Extrair código do campo como_conheceu (ex: "04 CLIENTES" -> "04")
    df['como_conheceu_codigo'] = df['como_conheceu'].fillna('').astype(str).str.extract(r'^(\d+)', expand=False)
    
    df_final = pd.DataFrame({
        'os_n': df['os_n'].astype(str).str.strip(),
        'loja': df['loja_codigo'].astype(str).str.strip(),  # Usar código da loja
        'nome': df['nome'].astype(str).str.strip(),
        'cpf': df['cpf'].astype(str).str.replace(r'\D', '', regex=True).str.zfill(11).str[:11],  # Apenas números, pad com zeros, max 11
        'como_conheceu_codigo': df['como_conheceu_codigo'].fillna('').astype(str).str.strip(),  # Código extraído
        'como_conheceu_raw': df['como_conheceu'].fillna('').astype(str).str.strip(),  # Valor original
        'data_de_compra': pd.to_datetime(df['data_de_compra'], errors='coerce'),
        'prev_de_entr': pd.to_datetime(df['prev_de_entr'], errors='coerce'),
        'consultor': df['consultor'].fillna('').astype(str).str.strip(),
        'venda': df['venda'].fillna('').astype(str).str.strip(),
        'total': pd.to_numeric(df['total'], errors='coerce')
    })
    
    # Limpar dados
    print("🧹 Limpando dados...")
    
    # Garantir limites de caracteres conforme tabela
    df_final['os_n'] = df_final['os_n'].str[:50]
    df_final['loja'] = df_final['loja'].str[:10]
    df_final['nome'] = df_final['nome'].str[:200]
    df_final['cpf'] = df_final['cpf'].str[:11]
    df_final['como_conheceu_codigo'] = df_final['como_conheceu_codigo'].str[:10]
    df_final['como_conheceu_raw'] = df_final['como_conheceu_raw'].str[:200]
    df_final['consultor'] = df_final['consultor'].str[:100]
    df_final['venda'] = df_final['venda'].str[:50]
    
    # Filtros básicos
    antes = len(df_final)
    df_final = df_final[
        (df_final['os_n'].notna()) & 
        (df_final['os_n'] != 'nan') & 
        (df_final['os_n'] != '') &
        (df_final['nome'].notna()) & 
        (df_final['nome'] != 'nan') & 
        (df_final['nome'] != '')
    ]
    print(f"   Removidos {antes - len(df_final):,} registros inválidos")
    
    # Remover duplicatas
    antes = len(df_final)
    df_final = df_final.drop_duplicates(subset=['os_n', 'nome'], keep='first')
    print(f"   Removidas {antes - len(df_final):,} duplicatas")
    print()
    
    # Estatísticas
    print("📊 ESTATÍSTICAS FINAIS:")
    print(f"   Total de registros: {len(df_final):,}")
    print(f"   CPFs únicos: {df_final[df_final['cpf'].str.len() == 11]['cpf'].nunique():,}")
    print()
    
    print("   Por loja:")
    for loja, count in df_final['loja'].value_counts().items():
        print(f"      Loja {loja}: {count:,}")
    print()
    
    print("   Como_conheceu (top 10):")
    top_conheceu = df_final[df_final['como_conheceu_raw'] != '']['como_conheceu_raw'].value_counts().head(10)
    for valor, count in top_conheceu.items():
        print(f"      {valor}: {count:,}")
    print()
    
    # Salvar
    print(f"💾 Salvando: {OUTPUT_FILE}")
    df_final.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    
    tamanho_mb = Path(OUTPUT_FILE).stat().st_size / (1024 * 1024)
    print(f"   Tamanho: {tamanho_mb:.2f} MB")
    print()
    
    # Mostrar colunas do CSV
    print("📋 COLUNAS DO CSV (na ordem):")
    for i, col in enumerate(df_final.columns, 1):
        print(f"   {i}. {col}")
    print()
    
    # Mostrar exemplo de códigos extraídos
    print("🔍 EXEMPLOS DE CÓDIGOS EXTRAÍDOS:")
    exemplos = df_final[df_final['como_conheceu_codigo'] != ''][['como_conheceu_codigo', 'como_conheceu_raw']].drop_duplicates().head(10)
    for _, row in exemplos.iterrows():
        print(f"   {row['como_conheceu_codigo']:>3} -> {row['como_conheceu_raw']}")
    print()
    
    if tamanho_mb > 10:
        print(f"⚠️  CSV > 10 MB - necessário dividir")
        print(f"   Execute: python scripts/python/dividir_csv_marketing_correto.py")
    else:
        print("✅ CSV < 10 MB - pode importar direto no Supabase")
    print()
    
    print("=" * 70)
    print("✅ CONCLUÍDO!")
    print("=" * 70)

if __name__ == '__main__':
    criar_csv_correto()
