import pandas as pd

# Carregar arquivo corrigido da SUZANO
df = pd.read_excel('data/documentos_corrigidos/OS_CORRIGIDAS_SUZANO_20251010_121047.xlsx')

# Buscar OS 8434
os_8434 = df[df['numero_os'] == '8434']

if len(os_8434) > 0:
    print('🎯 OS 8434 ENCONTRADA:')
    for idx, row in os_8434.iterrows():
        print(f'   Cliente: {row["cliente"]}')
        print(f'   Formas Pagamento: {row["formas_pagamento"]}')
        print(f'   Valor: R$ {row["valor_total"]}')
        print(f'   Data: {row["data"]}')
    print(f'\n📊 Total de registros para OS 8434: {len(os_8434)} (deveria ser 1)')
else:
    print('❌ OS 8434 não encontrada')

# Verificar também outras OS do dia 2 de janeiro
print('\n🔍 TODAS AS OS DO DIA 02/JAN/2024:')
os_dia_2 = df[df['data'].str.contains('02/jan/2024', na=False)]
print(f'Total de OS no dia 02/jan/2024: {len(os_dia_2)}')

if len(os_dia_2) > 0:
    for idx, row in os_dia_2.iterrows():
        print(f'   OS {row["numero_os"]} | {row["cliente"]} | {row["formas_pagamento"]} | R$ {row["valor_total"]}')