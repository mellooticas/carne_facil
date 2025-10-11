#!/usr/bin/env python3
"""
Análise de Dados para Modelagem de Banco de Dados
Extrai estruturas de todos os arquivos para criar modelo conceitual completo
"""

import pandas as pd
import os
from collections import defaultdict

def analisar_dados_completos():
    """Analisar todos os dados disponíveis para modelagem do banco"""
    
    print("🔍 ANÁLISE COMPLETA DE DADOS PARA MODELAGEM DE BANCO")
    print("="*70)
    
    # Estrutura de dados
    estruturas = {}
    
    # 1. DADOS DE CAIXA (5 ABAS)
    print("\n📊 1. ANALISANDO DADOS DE CAIXA (todos_os_caixas.xlsx)")
    print("-" * 70)
    
    arquivo_caixas = 'data/todos_os_caixas_original.xlsx'
    wb_caixas = pd.ExcelFile(arquivo_caixas)
    
    for aba in wb_caixas.sheet_names:
        df = pd.read_excel(arquivo_caixas, sheet_name=aba)
        estruturas[f'caixa_{aba}'] = {
            'fonte': 'todos_os_caixas.xlsx',
            'aba': aba,
            'linhas': len(df),
            'colunas': list(df.columns),
            'tipos': df.dtypes.to_dict(),
            'amostra': df.head(2).to_dict('records') if len(df) > 0 else []
        }
        
        print(f"\n   📋 {aba.upper()}")
        print(f"      Registros: {len(df):,}")
        print(f"      Colunas: {', '.join(df.columns)}")
        
        # Identificar campos chave
        campos_id = [col for col in df.columns if any(x in col.lower() for x in ['id', 'os', 'nº', 'número'])]
        if campos_id:
            print(f"      🔑 Campos ID: {', '.join(campos_id)}")
        
        # Identificar campos de valor
        campos_valor = [col for col in df.columns if any(x in col.lower() for x in ['valor', 'entrada', 'parcela', 'total'])]
        if campos_valor:
            print(f"      💰 Campos Valor: {', '.join(campos_valor)}")
    
    # 2. DADOS DE CLIENTES
    print("\n\n📊 2. ANALISANDO DADOS DE CLIENTES (clientes_totais.xlsx)")
    print("-" * 70)
    
    arquivo_clientes = 'data/clientes_totais_original.xlsx'
    if os.path.exists(arquivo_clientes):
        wb_clientes = pd.ExcelFile(arquivo_clientes)
        
        for aba in wb_clientes.sheet_names:
            df = pd.read_excel(arquivo_clientes, sheet_name=aba)
            estruturas[f'clientes_{aba}'] = {
                'fonte': 'clientes_totais.xlsx',
                'aba': aba,
                'linhas': len(df),
                'colunas': list(df.columns),
                'tipos': df.dtypes.to_dict(),
                'amostra': df.head(2).to_dict('records') if len(df) > 0 else []
            }
            
            print(f"\n   📋 {aba.upper()}")
            print(f"      Registros: {len(df):,}")
            print(f"      Principais colunas: {', '.join(list(df.columns)[:10])}")
            if len(df.columns) > 10:
                print(f"      ... e mais {len(df.columns) - 10} colunas")
    
    # 3. IDENTIFICAR ENTIDADES PRINCIPAIS
    print("\n\n🎯 3. ENTIDADES IDENTIFICADAS PARA MODELAGEM")
    print("-" * 70)
    
    entidades = {
        'CLIENTES': {
            'campos_principais': ['ID', 'Nome', 'CPF', 'RG', 'Data de Nascimento', 'Celular', 'Email'],
            'fonte': ['clientes_totais.xlsx', 'todos_os_caixas.xlsx (vend, rec_carn, rest_entr)'],
            'chave': 'UUID (migrado de ID legado)',
            'relacionamentos': ['endereco', 'telefones', 'os', 'vendas']
        },
        'ENDERECO': {
            'campos_principais': ['CEP', 'Logradouro', 'Numero', 'Complemento', 'Bairro', 'Cidade', 'UF'],
            'fonte': ['clientes_totais.xlsx (OSs_Gerais)'],
            'chave': 'UUID',
            'relacionamentos': ['cliente_id (FK)']
        },
        'VENDAS': {
            'campos_principais': ['Nº Venda', 'Data', 'Loja', 'Cliente', 'Valor Venda', 'Entrada', 'Forma Pagamento'],
            'fonte': ['todos_os_caixas.xlsx (vend)'],
            'chave': 'UUID (venda_id)',
            'relacionamentos': ['cliente_id (FK)', 'loja_id (FK)', 'formas_pagamento']
        },
        'OS (ORDENS DE SERVIÇO)': {
            'campos_principais': ['OS Nº', 'Data', 'Loja', 'Cliente', 'Vendedor', 'Status', 'Valor Total'],
            'fonte': ['clientes_totais.xlsx (OS_lancaster, OSs_Gerais)', 'todos_os_caixas.xlsx (os_entr_dia)'],
            'chave': 'UUID (os_id)',
            'relacionamentos': ['cliente_id (FK)', 'vendedor_id (FK)', 'loja_id (FK)', 'dioptrias', 'produtos']
        },
        'DIOPTRIAS': {
            'campos_principais': ['OS_id', 'Olho (OD/OE)', 'ESF', 'CIL', 'EIXO', 'DNP', 'ALTURA', 'ADIÇÃO'],
            'fonte': ['clientes_totais.xlsx (OSs_Gerais)'],
            'chave': 'UUID',
            'relacionamentos': ['os_id (FK)']
        },
        'FORMAS_PAGAMENTO': {
            'campos_principais': ['Venda_id', 'Forma', 'Valor', 'Parcela', 'Status'],
            'fonte': ['todos_os_caixas.xlsx (vend, rec_carn, rest_entr)'],
            'chave': 'UUID',
            'relacionamentos': ['venda_id (FK)', 'os_id (FK)']
        },
        'RECEBIMENTOS_CARNE': {
            'campos_principais': ['OS', 'Cliente', 'Data', 'Valor Parcela', 'Nº Parcela', 'Forma Pagamento'],
            'fonte': ['todos_os_caixas.xlsx (rec_carn)'],
            'chave': 'UUID',
            'relacionamentos': ['os_id (FK)', 'cliente_id (FK)']
        },
        'ENTREGAS_CARNE': {
            'campos_principais': ['OS', 'Data', 'Parcelas', 'Valor Total'],
            'fonte': ['todos_os_caixas.xlsx (entr_carn)'],
            'chave': 'UUID',
            'relacionamentos': ['os_id (FK)']
        },
        'LOJAS': {
            'campos_principais': ['Nome', 'Codigo', 'Endereco', 'Status'],
            'fonte': ['todos_os_caixas.xlsx (campo Loja)'],
            'chave': 'UUID',
            'valores': ['MAUA', 'SUZANO', 'SUZANO2', 'RIO_PEQUENO', 'PERUS', 'SAO_MATEUS']
        },
        'VENDEDORES': {
            'campos_principais': ['Nome', 'Loja', 'Status'],
            'fonte': ['clientes_totais.xlsx (OSs_Gerais)', 'todos_os_caixas.xlsx (os_entr_dia)'],
            'chave': 'UUID',
            'relacionamentos': ['loja_id (FK)']
        },
        'MARKETING': {
            'campos_principais': ['Cliente_id', 'Como_Conheceu', 'Data_Primeira_Compra', 'Faixa_Etaria'],
            'fonte': ['clientes_totais.xlsx (CLIENTES)'],
            'chave': 'UUID',
            'relacionamentos': ['cliente_id (FK)']
        }
    }
    
    for entidade, info in entidades.items():
        print(f"\n   🗂️  {entidade}")
        print(f"      📋 Campos: {', '.join(info['campos_principais'])}")
        print(f"      🔑 Chave: {info['chave']}")
        if 'relacionamentos' in info:
            print(f"      🔗 Relacionamentos: {', '.join(info['relacionamentos'])}")
        if 'valores' in info:
            print(f"      📊 Valores: {', '.join(info['valores'])}")
        print(f"      📁 Fonte: {info['fonte'][0]}")
    
    # 4. SCHEMAS SUGERIDOS
    print("\n\n🏗️  4. ESTRUTURA DE SCHEMAS SUGERIDA")
    print("-" * 70)
    
    schemas = {
        'core': ['clientes', 'endereco', 'telefones', 'lojas', 'vendedores'],
        'vendas': ['vendas', 'formas_pagamento', 'recebimentos_carne', 'entregas_carne'],
        'optica': ['os', 'dioptrias', 'produtos_os', 'entregas_os'],
        'marketing': ['marketing_info', 'campanhas', 'aniversarios'],
        'auditoria': ['log_alteracoes', 'historico_precos', 'snapshots']
    }
    
    for schema, tabelas in schemas.items():
        print(f"\n   📦 SCHEMA: {schema}")
        for tabela in tabelas:
            print(f"      - {tabela}")
    
    # 5. CAMPOS COMUNS (PADRÃO)
    print("\n\n⚙️  5. CAMPOS PADRÃO PARA TODAS AS TABELAS")
    print("-" * 70)
    
    campos_padrao = [
        'id UUID PRIMARY KEY DEFAULT gen_random_uuid()',
        'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        'updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        'created_by VARCHAR(100)',
        'updated_by VARCHAR(100)',
        'deleted_at TIMESTAMP NULL  -- Soft delete',
        'version INT DEFAULT 1  -- Controle de versão'
    ]
    
    for campo in campos_padrao:
        print(f"   {campo}")
    
    # Salvar estruturas em JSON
    import json
    with open('data/estruturas_modelagem.json', 'w', encoding='utf-8') as f:
        json.dump(estruturas, f, indent=2, ensure_ascii=False, default=str)
    
    print("\n\n✅ Análise concluída!")
    print(f"📁 Estruturas salvas em: data/estruturas_modelagem.json")
    
    return estruturas, entidades, schemas

if __name__ == "__main__":
    estruturas, entidades, schemas = analisar_dados_completos()