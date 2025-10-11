import pandas as pd
import numpy as np

# Analisar a aba VEND especificamente
arquivo = 'data/caixas_processados/VEND_COMPLETO_20251010_211625.xlsx'
df = pd.read_excel(arquivo)

print('ANÁLISE DETALHADA - VENDAS COMPLETAS (VEND)')
print('='*60)
print(f'Total de registros: {df.shape[0]:,}')
print(f'Período: {df["data_completa"].min()} a {df["data_completa"].max()}')

# Converter colunas numéricas
df['Valor Venda'] = pd.to_numeric(df['Valor Venda'], errors='coerce')
df['Entrada'] = pd.to_numeric(df['Entrada'], errors='coerce')

print('\nVALORES FINANCEIROS:')
valor_venda_total = df['Valor Venda'].sum()
entrada_total = df['Entrada'].sum()
print(f'Valor Venda Total: R$ {valor_venda_total:,.2f}')
print(f'Entrada Total: R$ {entrada_total:,.2f}')
print(f'Média Valor Venda: R$ {df["Valor Venda"].mean():.2f}')
print(f'Média Entrada: R$ {df["Entrada"].mean():.2f}')

print('\nDISTRIBUIÇÃO POR LOJA:')
for loja in df['Loja'].unique():
    loja_df = df[df['Loja'] == loja]
    count = len(loja_df)
    valor_total = loja_df['Valor Venda'].sum()
    entrada_total = loja_df['Entrada'].sum()
    print(f'  {loja}: {count:,} vendas | Valor: R$ {valor_total:,.2f} | Entrada: R$ {entrada_total:,.2f}')

print('\nTIPOS DE PAGAMENTO:')
pagto_stats = df['Forma de Pgto'].value_counts()
for pagto, count in pagto_stats.head(10).items():
    print(f'  {pagto}: {count:,} vendas')

print('\nEXEMPLO DE REGISTROS (primeiras 5 linhas):')
colunas_exemplo = ['Loja', 'data_completa', 'Nº Venda', 'Cliente', 'Valor Venda', 'Entrada', 'Forma de Pgto']
print(df[colunas_exemplo].head().to_string(index=False))