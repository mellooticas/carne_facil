"""
Script: gerar_sqls_vendas.py
Objetivo: Gerar arquivos SQL para povoamento de vendas e itens de venda
Data: 2025-10-23
"""

import pandas as pd
from pathlib import Path
import re
from datetime import datetime

# Configurações
BATCH_SIZE = 100  # Menor batch para vendas (mais dados por linha)
OUTPUT_DIR = Path("povoamento/dados/vendas")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def limpar_string(valor):
    """Remove caracteres problemáticos de strings"""
    if pd.isna(valor) or valor is None:
        return None
    
    valor_str = str(valor).strip()
    if not valor_str or valor_str.upper() in ['NAN', 'NONE', 'NULL', '']:
        return None
    
    # Escapar aspas simples
    valor_str = valor_str.replace("'", "''")
    
    # Limitar tamanho
    if len(valor_str) > 500:
        valor_str = valor_str[:500]
    
    return valor_str

def formatar_valor(valor):
    """Formata valores monetários"""
    if pd.isna(valor) or valor is None:
        return 'NULL'
    try:
        return f"{float(valor):.2f}"
    except:
        return 'NULL'

def formatar_data(valor):
    """Formata datas para PostgreSQL"""
    if pd.isna(valor) or valor is None:
        return 'NULL'
    
    try:
        if isinstance(valor, str):
            # Tenta parsear string
            dt = pd.to_datetime(valor)
        else:
            dt = valor
        
        return f"'{dt.strftime('%Y-%m-%d %H:%M:%S')}'"
    except:
        return 'NULL'

def formatar_data_simples(valor):
    """Formata apenas a data (sem hora)"""
    if pd.isna(valor) or valor is None:
        return 'NULL'
    
    try:
        if isinstance(valor, str):
            dt = pd.to_datetime(valor)
        else:
            dt = valor
        
        return f"'{dt.strftime('%Y-%m-%d')}'"
    except:
        return 'NULL'

def gerar_sql_vendas_vixen(df_vendas, clientes_lookup):
    """Gera SQLs de INSERT para vendas Vixen"""
    
    print(f"\n=== PROCESSANDO VENDAS VIXEN ===")
    print(f"Total de vendas: {len(df_vendas):,}")
    
    # Filtrar apenas vendas com id_cliente
    df_com_cliente = df_vendas[df_vendas['id_cliente'].notna()].copy()
    print(f"Vendas com cliente: {len(df_com_cliente):,}")
    
    # Criar lookup de clientes (id_legado -> UUID)
    lookup = {}
    for _, row in clientes_lookup.iterrows():
        if row['origem'] == 'VIXEN':
            lookup[str(row['id_cliente'])] = row['uuid']
    
    print(f"Clientes Vixen no lookup: {len(lookup):,}")
    
    # Criar lookup de lojas (codigo -> UUID)
    # IMPORTANTE: Usar os mesmos códigos inseridos em 03_inserir_lojas.sql
    lojas_lookup = {
        '009': "(SELECT id FROM core.lojas WHERE codigo = '009')",
        '010': "(SELECT id FROM core.lojas WHERE codigo = '010')",
        '011': "(SELECT id FROM core.lojas WHERE codigo = '011')",
        '012': "(SELECT id FROM core.lojas WHERE codigo = '012')",
        '042': "(SELECT id FROM core.lojas WHERE codigo = '042')",
        '048': "(SELECT id FROM core.lojas WHERE codigo = '048')",
    }
    
    vendas_inseridas = []
    vendas_sem_cliente = 0
    vendas_sem_loja = 0
    
    for idx, row in df_com_cliente.iterrows():
        id_cliente_legado = str(row['id_cliente'])
        id_loja = str(row['id_loja']).strip()
        
        # Verificar se cliente existe
        if id_cliente_legado not in lookup:
            vendas_sem_cliente += 1
            continue
        
        # Verificar se loja existe
        if id_loja not in lojas_lookup:
            vendas_sem_loja += 1
            continue
        
        cliente_uuid_subquery = f"(SELECT id FROM core.clientes WHERE id_legado = '{id_cliente_legado}' AND created_by = 'MIGRACAO_VIXEN')"
        loja_uuid_subquery = lojas_lookup[id_loja]
        
        # Preparar valores
        id_dav = limpar_string(row['id_dav']) or limpar_string(row['nro_dav'])
        tipo = limpar_string(row.get('origem'))
        status = limpar_string(row.get('status'))
        descricao = limpar_string(row.get('descricao'))
        
        valor_bruto = formatar_valor(row.get('vl_bruto'))
        valor_acrescimo = formatar_valor(row.get('vl_acrescimo'))
        valor_desconto = formatar_valor(row.get('vl_desconto'))
        valor_liquido = formatar_valor(row.get('vl_liquido'))
        
        perc_adiantamento = formatar_valor(row.get('perc_adiantamento'))
        vl_adiantamento = formatar_valor(row.get('vl_adiantamento'))
        
        data_venda = formatar_data(row.get('dh_dav'))
        data_prev_entrega = formatar_data_simples(row.get('dt_prev_entrega'))
        data_entrega = formatar_data_simples(row.get('dt_entrega'))
        
        id_vendedor = limpar_string(row.get('id_vendedor'))
        nome_vendedor = limpar_string(row.get('vendedor'))
        id_operador = limpar_string(row.get('id_operador'))
        nome_operador = limpar_string(row.get('operador'))
        id_caixa = limpar_string(row.get('id_caixa'))
        
        eh_garantia = 'TRUE' if row.get('eh_garantia') else 'FALSE'
        meios_contato = limpar_string(row.get('meios_contato'))
        
        mes_ref = limpar_string(row.get('mes_ref'))
        arquivo = limpar_string(row.get('arquivo'))
        
        # Montar INSERT
        insert = f"""INSERT INTO core.vendas (
    id_legado, origem, cliente_id, loja_id,
    tipo, status, descricao,
    valor_bruto, valor_acrescimo, valor_desconto, valor_liquido,
    percentual_adiantamento, valor_adiantamento,
    data_venda, data_previsao_entrega, data_entrega,
    id_vendedor, nome_vendedor, id_operador, nome_operador, id_caixa,
    eh_garantia, meios_contato,
    mes_referencia, arquivo_origem
) VALUES (
    '{id_dav}', 'VIXEN', {cliente_uuid_subquery}, {loja_uuid_subquery},
    {f"'{tipo}'" if tipo else 'NULL'}, {f"'{status}'" if status else 'NULL'}, {f"'{descricao}'" if descricao else 'NULL'},
    {valor_bruto}, {valor_acrescimo}, {valor_desconto}, {valor_liquido},
    {perc_adiantamento}, {vl_adiantamento},
    {data_venda}, {data_prev_entrega}, {data_entrega},
    {f"'{id_vendedor}'" if id_vendedor else 'NULL'}, {f"'{nome_vendedor}'" if nome_vendedor else 'NULL'}, 
    {f"'{id_operador}'" if id_operador else 'NULL'}, {f"'{nome_operador}'" if nome_operador else 'NULL'}, 
    {f"'{id_caixa}'" if id_caixa else 'NULL'},
    {eh_garantia}, {f"'{meios_contato}'" if meios_contato else 'NULL'},
    {f"'{mes_ref}'" if mes_ref else 'NULL'}, {f"'{arquivo}'" if arquivo else 'NULL'}
);"""
        
        vendas_inseridas.append(insert)
    
    print(f"\n✅ Vendas Vixen processadas: {len(vendas_inseridas):,}")
    print(f"⚠️  Sem cliente: {vendas_sem_cliente:,}")
    print(f"⚠️  Sem loja: {vendas_sem_loja:,}")
    
    # Salvar em blocos
    total_blocos = (len(vendas_inseridas) + BATCH_SIZE - 1) // BATCH_SIZE
    
    for i in range(0, len(vendas_inseridas), BATCH_SIZE):
        bloco = vendas_inseridas[i:i + BATCH_SIZE]
        bloco_num = i // BATCH_SIZE + 1
        
        conteudo = f"""-- ============================================
-- VENDAS VIXEN - BLOCO {bloco_num}/{total_blocos}
-- Registros: {len(bloco)}
-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- ============================================

{chr(10).join(bloco)}
"""
        
        arquivo_saida = OUTPUT_DIR / f"vendas_vixen_bloco_{bloco_num:03d}.sql"
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print(f"  ✓ {arquivo_saida.name}")
    
    return len(vendas_inseridas)

def gerar_sql_vendas_os(df_os_map, clientes_lookup):
    """Gera SQLs de INSERT para vendas OS"""
    
    print(f"\n=== PROCESSANDO VENDAS OS ===")
    print(f"Total de vendas: {len(df_os_map):,}")
    
    # Criar lookup de clientes OS (id_cliente -> UUID)
    lookup = {}
    for _, row in clientes_lookup.iterrows():
        if row['origem'] == 'OS':
            lookup[int(row['id_cliente'])] = row['uuid']
    
    print(f"Clientes OS no lookup: {len(lookup):,}")
    
    # Lojas
    lojas_lookup = {
        '009': "(SELECT id FROM core.lojas WHERE codigo = '009')",
        '010': "(SELECT id FROM core.lojas WHERE codigo = '010')",
        '011': "(SELECT id FROM core.lojas WHERE codigo = '011')",
        '012': "(SELECT id FROM core.lojas WHERE codigo = '012')",
        '042': "(SELECT id FROM core.lojas WHERE codigo = '042')",
        '048': "(SELECT id FROM core.lojas WHERE codigo = '048')",
    }
    
    vendas_inseridas = []
    vendas_sem_cliente = 0
    vendas_sem_loja = 0
    
    for idx, row in df_os_map.iterrows():
        id_cliente_int = row['id_cliente']
        id_loja = str(row['id_loja']).strip()
        nro_dav = str(row['nro_dav']).strip()
        
        # Verificar se cliente existe
        if pd.isna(id_cliente_int) or id_cliente_int not in lookup:
            vendas_sem_cliente += 1
            continue
        
        # Verificar se loja existe
        if id_loja not in lojas_lookup:
            vendas_sem_loja += 1
            continue
        
        cliente_uuid_subquery = f"(SELECT id FROM core.clientes WHERE id_legado = '{int(id_cliente_int)}' AND created_by = 'MIGRACAO_OS')"
        loja_uuid_subquery = lojas_lookup[id_loja]
        
        # OS não tem muitos detalhes, inserir apenas o básico
        insert = f"""INSERT INTO core.vendas (
    id_legado, origem, cliente_id, loja_id,
    tipo, status, valor_liquido, data_venda
) VALUES (
    '{nro_dav}', 'OS', {cliente_uuid_subquery}, {loja_uuid_subquery},
    'ORDEM DE SERVIÇO', 'FINALIZADO', 0.00, NOW()
);"""
        
        vendas_inseridas.append(insert)
    
    print(f"\n✅ Vendas OS processadas: {len(vendas_inseridas):,}")
    print(f"⚠️  Sem cliente: {vendas_sem_cliente:,}")
    print(f"⚠️  Sem loja: {vendas_sem_loja:,}")
    
    # Salvar em blocos
    total_blocos = (len(vendas_inseridas) + BATCH_SIZE - 1) // BATCH_SIZE
    
    for i in range(0, len(vendas_inseridas), BATCH_SIZE):
        bloco = vendas_inseridas[i:i + BATCH_SIZE]
        bloco_num = i // BATCH_SIZE + 1
        
        conteudo = f"""-- ============================================
-- VENDAS OS - BLOCO {bloco_num}/{total_blocos}
-- Registros: {len(bloco)}
-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- ============================================

{chr(10).join(bloco)}
"""
        
        arquivo_saida = OUTPUT_DIR / f"vendas_os_bloco_{bloco_num:03d}.sql"
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print(f"  ✓ {arquivo_saida.name}")
    
    return len(vendas_inseridas)

def gerar_sql_itens_venda(df_itens, df_vendas_vixen):
    """Gera SQLs de INSERT para itens de venda"""
    
    print(f"\n=== PROCESSANDO ITENS DE VENDA ===")
    print(f"Total de itens: {len(df_itens):,}")
    
    # Criar mapeamento de (id_loja, nro_dav) para localizar a venda
    vendas_map = {}
    for _, row in df_vendas_vixen.iterrows():
        key = (str(row['id_loja']).strip(), str(row['nro_dav']).strip())
        vendas_map[key] = str(row['id_dav'])  # id_legado na tabela vendas
    
    print(f"Vendas no mapa: {len(vendas_map):,}")
    
    itens_inseridos = []
    itens_sem_venda = 0
    
    for idx, row in df_itens.iterrows():
        id_loja = str(row['id_loja']).strip()
        nro_dav = str(row['nro_dav']).strip()
        key = (id_loja, nro_dav)
        
        # Verificar se venda existe
        if key not in vendas_map:
            itens_sem_venda += 1
            continue
        
        id_legado_venda = vendas_map[key]
        
        # Preparar valores
        item_num = int(row.get('item', 1))
        id_produto = limpar_string(row.get('produto'))
        descricao = limpar_string(row.get('produto')) or 'PRODUTO'
        modelo = limpar_string(row.get('modelo'))
        grupo = limpar_string(row.get('grupo'))
        detalhe = limpar_string(row.get('detalhe'))
        
        quantidade = formatar_valor(row.get('qtd', 1))
        valor_total = formatar_valor(row.get('vl_total'))
        
        # Calcular valor unitário
        try:
            qtd = float(row.get('qtd', 1))
            vl_total = float(row.get('vl_total', 0))
            valor_unitario = formatar_valor(vl_total / qtd if qtd > 0 else 0)
        except:
            valor_unitario = formatar_valor(row.get('vl_total'))
        
        mes_ref = limpar_string(row.get('mes_ref'))
        arquivo = limpar_string(row.get('arquivo'))
        
        # Subquery para buscar venda_id
        venda_uuid_subquery = f"(SELECT id FROM core.vendas WHERE id_legado = '{id_legado_venda}' AND origem = 'VIXEN')"
        
        # Montar INSERT
        insert = f"""INSERT INTO core.itens_venda (
    venda_id, item_numero, id_produto, descricao_produto,
    modelo, grupo, detalhe,
    quantidade, valor_unitario, valor_total,
    mes_referencia, arquivo_origem
) VALUES (
    {venda_uuid_subquery}, {item_num}, {f"'{id_produto}'" if id_produto else 'NULL'}, '{descricao}',
    {f"'{modelo}'" if modelo else 'NULL'}, {f"'{grupo}'" if grupo else 'NULL'}, {f"'{detalhe}'" if detalhe else 'NULL'},
    {quantidade}, {valor_unitario}, {valor_total},
    {f"'{mes_ref}'" if mes_ref else 'NULL'}, {f"'{arquivo}'" if arquivo else 'NULL'}
);"""
        
        itens_inseridos.append(insert)
    
    print(f"\n✅ Itens processados: {len(itens_inseridos):,}")
    print(f"⚠️  Sem venda: {itens_sem_venda:,}")
    
    # Salvar em blocos
    total_blocos = (len(itens_inseridos) + BATCH_SIZE - 1) // BATCH_SIZE
    
    for i in range(0, len(itens_inseridos), BATCH_SIZE):
        bloco = itens_inseridos[i:i + BATCH_SIZE]
        bloco_num = i // BATCH_SIZE + 1
        
        conteudo = f"""-- ============================================
-- ITENS DE VENDA - BLOCO {bloco_num}/{total_blocos}
-- Registros: {len(bloco)}
-- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- ============================================

{chr(10).join(bloco)}
"""
        
        arquivo_saida = OUTPUT_DIR / f"itens_venda_bloco_{bloco_num:03d}.sql"
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print(f"  ✓ {arquivo_saida.name}")
    
    return len(itens_inseridos)

def criar_lookup_clientes():
    """Cria lookup de clientes com UUID do Supabase"""
    print("\n=== CRIANDO LOOKUP DE CLIENTES ===")
    
    # Ler arquivo de validação para extrair UUIDs
    # Como os UUIDs são gerados pelo Supabase, vamos usar subqueries
    # ao invés de lookup direto
    
    df = pd.read_parquet('data/clientes/_consolidado/clientes_unificados.parquet')
    
    # Criar DataFrame de lookup (será usado apenas para validar)
    lookup_data = []
    for _, row in df.iterrows():
        lookup_data.append({
            'origem': row['origem'],
            'id_cliente': row['id_cliente'],
            'uuid': 'USAR_SUBQUERY'  # Placeholder
        })
    
    df_lookup = pd.DataFrame(lookup_data)
    print(f"Total de clientes no lookup: {len(df_lookup):,}")
    
    return df_lookup

def main():
    print("="*60)
    print("GERAÇÃO DE SQLs DE VENDAS E ITENS")
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
    
    # 3. Gerar SQLs de vendas Vixen
    total_vixen = gerar_sql_vendas_vixen(df_vendas_vixen, clientes_lookup)
    
    # 4. Gerar SQLs de vendas OS
    total_os = gerar_sql_vendas_os(df_os_map, clientes_lookup)
    
    # 5. Gerar SQLs de itens
    total_itens = gerar_sql_itens_venda(df_itens, df_vendas_vixen)
    
    # 6. Resumo final
    print("\n" + "="*60)
    print("RESUMO FINAL")
    print("="*60)
    print(f"✅ Vendas Vixen: {total_vixen:,} registros")
    print(f"✅ Vendas OS: {total_os:,} registros")
    print(f"✅ Itens de Venda: {total_itens:,} registros")
    print(f"\nArquivos salvos em: {OUTPUT_DIR.absolute()}")
    print("\n✓ Processo concluído com sucesso!")

if __name__ == "__main__":
    main()
