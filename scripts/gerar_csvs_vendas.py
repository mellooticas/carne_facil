"""
Script: gerar_csvs_vendas.py
Objetivo: Gerar arquivos CSV para upload direto no Supabase
Data: 2025-10-23

IMPORTANTE: 
- Os UUIDs de clientes e lojas serão resolvidos no Supabase
- CSVs serão importados via Table Editor ou API
- Muito mais rápido que executar 744 SQLs manualmente
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import numpy as np

# Configurações
OUTPUT_DIR = Path("povoamento/dados/csv")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def limpar_string(valor):
    """Remove caracteres problemáticos de strings"""
    if pd.isna(valor) or valor is None:
        return None
    
    valor_str = str(valor).strip()
    if not valor_str or valor_str.upper() in ['NAN', 'NONE', 'NULL', '']:
        return None
    
    # Limitar tamanho
    if len(valor_str) > 500:
        valor_str = valor_str[:500]
    
    return valor_str

def formatar_data(valor):
    """Formata datas para ISO 8601"""
    if pd.isna(valor) or valor is None:
        return None
    
    try:
        if isinstance(valor, str):
            dt = pd.to_datetime(valor)
        else:
            dt = valor
        
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return None

def formatar_data_simples(valor):
    """Formata apenas a data (sem hora)"""
    if pd.isna(valor) or valor is None:
        return None
    
    try:
        if isinstance(valor, str):
            dt = pd.to_datetime(valor)
        else:
            dt = valor
        
        return dt.strftime('%Y-%m-%d')
    except:
        return None

def criar_csv_vendas_vixen(df_vendas, clientes_lookup):
    """Cria CSV de vendas Vixen com id_legado_cliente para lookup"""
    
    print(f"\n=== PROCESSANDO VENDAS VIXEN PARA CSV ===")
    print(f"Total de vendas: {len(df_vendas):,}")
    
    # Filtrar apenas vendas com id_cliente
    df_com_cliente = df_vendas[df_vendas['id_cliente'].notna()].copy()
    print(f"Vendas com cliente: {len(df_com_cliente):,}")
    
    # Criar lookup de clientes Vixen (id_cliente -> existe?)
    clientes_vixen_ids = set(
        clientes_lookup[clientes_lookup['origem'] == 'VIXEN']['id_cliente'].astype(str)
    )
    
    print(f"Clientes Vixen no lookup: {len(clientes_vixen_ids):,}")
    
    # Filtrar vendas que têm cliente válido
    df_com_cliente['id_cliente_str'] = df_com_cliente['id_cliente'].astype(str)
    df_validas = df_com_cliente[df_com_cliente['id_cliente_str'].isin(clientes_vixen_ids)].copy()
    
    print(f"Vendas com cliente válido: {len(df_validas):,}")
    
    # Preparar DataFrame para CSV
    vendas_csv = pd.DataFrame({
        'id_legado': df_validas['id_dav'].fillna(df_validas['nro_dav']).apply(limpar_string),
        'id_legado_cliente': df_validas['id_cliente'].astype(str),
        'id_loja_codigo': df_validas['id_loja'].astype(str).str.strip(),
        'origem': 'VIXEN',
        'tipo': df_validas['origem'].apply(limpar_string),
        'status': df_validas['status'].apply(limpar_string),
        'descricao': df_validas['descricao'].apply(limpar_string),
        'valor_bruto': df_validas['vl_bruto'],
        'valor_acrescimo': df_validas['vl_acrescimo'],
        'valor_desconto': df_validas['vl_desconto'],
        'valor_liquido': df_validas['vl_liquido'],
        'percentual_adiantamento': df_validas['perc_adiantamento'],
        'valor_adiantamento': df_validas['vl_adiantamento'],
        'data_venda': df_validas['dh_dav'].apply(formatar_data),
        'data_previsao_entrega': df_validas['dt_prev_entrega'].apply(formatar_data_simples),
        'data_entrega': df_validas['dt_entrega'].apply(formatar_data_simples),
        'id_vendedor': df_validas['id_vendedor'].apply(limpar_string),
        'nome_vendedor': df_validas['vendedor'].apply(limpar_string),
        'id_operador': df_validas['id_operador'].apply(limpar_string),
        'nome_operador': df_validas['operador'].apply(limpar_string),
        'id_caixa': df_validas['id_caixa'].apply(limpar_string),
        'eh_garantia': df_validas['eh_garantia'].fillna(False),
        'meios_contato': df_validas['meios_contato'].apply(limpar_string),
        'mes_referencia': df_validas['mes_ref'].apply(limpar_string),
        'arquivo_origem': df_validas['arquivo'].apply(limpar_string),
    })
    
    # Salvar CSV
    arquivo_saida = OUTPUT_DIR / "vendas_vixen.csv"
    vendas_csv.to_csv(arquivo_saida, index=False, encoding='utf-8')
    
    print(f"\n✅ CSV criado: {arquivo_saida}")
    print(f"   Total de registros: {len(vendas_csv):,}")
    print(f"   Tamanho do arquivo: {arquivo_saida.stat().st_size / 1024 / 1024:.2f} MB")
    
    return len(vendas_csv)

def criar_csv_vendas_os(df_os_map, clientes_lookup):
    """Cria CSV de vendas OS com id_legado_cliente para lookup"""
    
    print(f"\n=== PROCESSANDO VENDAS OS PARA CSV ===")
    print(f"Total de vendas: {len(df_os_map):,}")
    
    # Criar lookup de clientes OS (id_cliente -> existe?)
    clientes_os_ids = set(
        clientes_lookup[clientes_lookup['origem'] == 'OS']['id_cliente'].astype(int)
    )
    
    print(f"Clientes OS no lookup: {len(clientes_os_ids):,}")
    
    # Filtrar vendas que têm cliente válido
    df_validas = df_os_map[df_os_map['id_cliente'].isin(clientes_os_ids)].copy()
    
    print(f"Vendas com cliente válido: {len(df_validas):,}")
    
    # Preparar DataFrame para CSV
    vendas_csv = pd.DataFrame({
        'id_legado': df_validas['nro_dav'].astype(str).str.strip(),
        'id_legado_cliente': df_validas['id_cliente'].astype(str),
        'id_loja_codigo': df_validas['id_loja'].astype(str).str.strip(),
        'origem': 'OS',
        'tipo': 'ORDEM DE SERVIÇO',
        'status': 'FINALIZADO',
        'valor_liquido': 0.00,
        'data_venda': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    })
    
    # Salvar CSV
    arquivo_saida = OUTPUT_DIR / "vendas_os.csv"
    vendas_csv.to_csv(arquivo_saida, index=False, encoding='utf-8')
    
    print(f"\n✅ CSV criado: {arquivo_saida}")
    print(f"   Total de registros: {len(vendas_csv):,}")
    print(f"   Tamanho do arquivo: {arquivo_saida.stat().st_size / 1024 / 1024:.2f} MB")
    
    return len(vendas_csv)

def criar_csv_itens_venda(df_itens, df_vendas_vixen):
    """Cria CSV de itens de venda"""
    
    print(f"\n=== PROCESSANDO ITENS DE VENDA PARA CSV ===")
    print(f"Total de itens: {len(df_itens):,}")
    
    # Criar mapeamento de (id_loja, nro_dav) -> id_dav (id_legado da venda)
    vendas_map = {}
    for _, row in df_vendas_vixen.iterrows():
        key = (str(row['id_loja']).strip(), str(row['nro_dav']).strip())
        vendas_map[key] = str(row['id_dav'])
    
    print(f"Vendas no mapa: {len(vendas_map):,}")
    
    # Preparar dados dos itens
    itens_data = []
    
    for idx, row in df_itens.iterrows():
        id_loja = str(row['id_loja']).strip()
        nro_dav = str(row['nro_dav']).strip()
        key = (id_loja, nro_dav)
        
        # Verificar se venda existe
        if key not in vendas_map:
            continue
        
        id_legado_venda = vendas_map[key]
        
        # Calcular valor unitário
        try:
            qtd = float(row.get('qtd', 1))
            vl_total = float(row.get('vl_total', 0))
            valor_unitario = vl_total / qtd if qtd > 0 else 0
        except:
            valor_unitario = 0
        
        itens_data.append({
            'id_legado_venda': id_legado_venda,
            'id_loja_codigo': id_loja,  # Adicionar para lookup
            'item_numero': int(row.get('item', 1)),
            'id_produto': limpar_string(row.get('produto')),
            'descricao_produto': limpar_string(row.get('produto')) or 'PRODUTO',
            'modelo': limpar_string(row.get('modelo')),
            'grupo': limpar_string(row.get('grupo')),
            'detalhe': limpar_string(row.get('detalhe')),
            'quantidade': float(row.get('qtd', 1)),
            'valor_unitario': round(valor_unitario, 2),
            'valor_total': float(row.get('vl_total', 0)),
            'mes_referencia': limpar_string(row.get('mes_ref')),
            'arquivo_origem': limpar_string(row.get('arquivo')),
        })
    
    # Criar DataFrame
    itens_csv = pd.DataFrame(itens_data)
    
    # Salvar CSV
    arquivo_saida = OUTPUT_DIR / "itens_venda.csv"
    itens_csv.to_csv(arquivo_saida, index=False, encoding='utf-8')
    
    print(f"\n✅ CSV criado: {arquivo_saida}")
    print(f"   Total de registros: {len(itens_csv):,}")
    print(f"   Tamanho do arquivo: {arquivo_saida.stat().st_size / 1024 / 1024:.2f} MB")
    
    return len(itens_csv)

def criar_lookup_clientes():
    """Cria lookup de clientes para validação"""
    print("\n=== CRIANDO LOOKUP DE CLIENTES ===")
    
    df = pd.read_parquet('data/clientes/_consolidado/clientes_unificados.parquet')
    
    print(f"Total de clientes no lookup: {len(df):,}")
    print(f"  - Vixen: {(df['origem'] == 'VIXEN').sum():,}")
    print(f"  - OS: {(df['origem'] == 'OS').sum():,}")
    
    return df

def main():
    print("="*60)
    print("GERAÇÃO DE CSVs DE VENDAS E ITENS")
    print("="*60)
    
    # 1. Criar lookup de clientes
    clientes_lookup = criar_lookup_clientes()
    
    # 2. Carregar dados de vendas
    print("\n=== CARREGANDO DADOS DE VENDAS ===")
    df_vendas_vixen = pd.read_parquet('data/vendas/_com_cliente/lista_dav_com_cliente.parquet')
    df_os_map = pd.read_parquet('data/vendas/_com_cliente/os_para_cliente_map.parquet')
    df_itens = pd.read_parquet('data/originais/vendas/conf_dav/_consolidado/conf_dav_itens.parquet')
    
    print(f"✓ Vendas Vixen: {len(df_vendas_vixen):,}")
    print(f"✓ Vendas OS: {len(df_os_map):,}")
    print(f"✓ Itens: {len(df_itens):,}")
    
    # 3. Criar CSVs
    total_vixen = criar_csv_vendas_vixen(df_vendas_vixen, clientes_lookup)
    total_os = criar_csv_vendas_os(df_os_map, clientes_lookup)
    total_itens = criar_csv_itens_venda(df_itens, df_vendas_vixen)
    
    # 4. Resumo final
    print("\n" + "="*60)
    print("RESUMO FINAL")
    print("="*60)
    print(f"✅ Vendas Vixen: {total_vixen:,} registros")
    print(f"✅ Vendas OS: {total_os:,} registros")
    print(f"✅ Itens de Venda: {total_itens:,} registros")
    print(f"\nArquivos salvos em: {OUTPUT_DIR.absolute()}")
    
    # 5. Instruções de importação
    print("\n" + "="*60)
    print("PRÓXIMOS PASSOS")
    print("="*60)
    print("\n1️⃣ No Supabase, acesse o Table Editor")
    print("2️⃣ Crie uma view temporária para lookup de UUIDs:")
    print("   CREATE VIEW tmp_cliente_lookup AS")
    print("   SELECT id, id_legado, created_by FROM core.clientes;")
    print("\n3️⃣ Importe os CSVs na seguinte ordem:")
    print("   a) vendas_vixen.csv → core.vendas")
    print("   b) vendas_os.csv → core.vendas")
    print("   c) itens_venda.csv → core.itens_venda")
    print("\n4️⃣ Execute queries de validação (20_validacao_vendas.sql)")
    print("\n✓ Processo concluído com sucesso!")

if __name__ == "__main__":
    main()
