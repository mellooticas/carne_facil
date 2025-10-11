#!/usr/bin/env python3
"""
Análise de Dados CORRETOS para Modelagem de Banco de Dados
Baseado apenas nos arquivos processados e validados nas conversas anteriores
"""

import pandas as pd
import os
from collections import defaultdict
import json

def analisar_dados_processados():
    """Analisar dados CORRETOS processados anteriormente"""
    
    print("🔍 ANÁLISE DE DADOS PROCESSADOS PARA MODELAGEM DE BANCO")
    print("="*70)
    print("Fontes: todos_os_caixas.xlsx + arquivos processados + dados Vixen")
    print("="*70)
    
    estruturas = {}
    
    # 1. DADOS DO ARQUIVO CONSOLIDADO todos_os_caixas.xlsx
    print("\n📊 1. DADOS CONSOLIDADOS (todos_os_caixas.xlsx)")
    print("-" * 70)
    
    arquivo_caixas = 'data/todos_os_caixas_original.xlsx'
    if os.path.exists(arquivo_caixas):
        wb_caixas = pd.ExcelFile(arquivo_caixas)
        
        for aba in wb_caixas.sheet_names:
            df = pd.read_excel(arquivo_caixas, sheet_name=aba)
            
            print(f"\n   📋 {aba.upper()}: {len(df):,} registros")
            print(f"      Colunas: {', '.join(df.columns)}")
            
            # Mostrar amostra
            if len(df) > 0:
                print(f"      Exemplo:")
                exemplo = df.iloc[0].to_dict()
                for col, val in list(exemplo.items())[:5]:
                    print(f"        {col}: {val}")
            
            estruturas[f'caixa_{aba}'] = {
                'fonte': 'todos_os_caixas.xlsx',
                'linhas': len(df),
                'colunas': list(df.columns)
            }
    
    # 2. ARQUIVOS PROCESSADOS (que geramos juntos)
    print("\n\n📊 2. ARQUIVOS PROCESSADOS ANTERIORMENTE")
    print("-" * 70)
    
    pastas_processadas = [
        'data/caixas_processados',
        'data/vendas_vend_dia',
        'data/rest_entr_final'
    ]
    
    for pasta in pastas_processadas:
        if os.path.exists(pasta):
            arquivos = [f for f in os.listdir(pasta) if f.endswith('.xlsx')]
            if arquivos:
                print(f"\n   📁 {pasta}:")
                for arq in arquivos[:5]:  # Primeiros 5
                    print(f"      - {arq}")
                if len(arquivos) > 5:
                    print(f"      ... e mais {len(arquivos) - 5} arquivos")
    
    # 3. ENTIDADES PRINCIPAIS IDENTIFICADAS
    print("\n\n🎯 3. ENTIDADES PARA O BANCO DE DADOS")
    print("-" * 70)
    
    entidades = {
        'CLIENTES': {
            'tabela': 'core.clientes',
            'campos': [
                'id UUID PRIMARY KEY',
                'id_legado VARCHAR(50) UNIQUE  -- ID antigo para migração',
                'nome VARCHAR(200) NOT NULL',
                'nome_normalizado VARCHAR(200)  -- Para busca',
                'cpf VARCHAR(14) UNIQUE',
                'rg VARCHAR(20)',
                'data_nascimento DATE',
                'email VARCHAR(100)',
                'sexo CHAR(1)',
                'status VARCHAR(20) DEFAULT \'ATIVO\''
            ],
            'fonte': 'Dados Vixen + todos_os_caixas.xlsx',
            'indices': ['idx_clientes_nome', 'idx_clientes_cpf', 'idx_clientes_legado']
        },
        'ENDERECO_CLIENTE': {
            'tabela': 'core.endereco_cliente',
            'campos': [
                'id UUID PRIMARY KEY',
                'cliente_id UUID NOT NULL REFERENCES core.clientes(id)',
                'cep VARCHAR(9)',
                'logradouro VARCHAR(200)',
                'numero VARCHAR(20)',
                'complemento VARCHAR(100)',
                'bairro VARCHAR(100)',
                'cidade VARCHAR(100)',
                'uf CHAR(2)',
                'pais VARCHAR(50) DEFAULT \'Brasil\'',
                'tipo VARCHAR(20) DEFAULT \'PRINCIPAL\'',
                'principal BOOLEAN DEFAULT TRUE'
            ],
            'fonte': 'Dados das OSs',
            'indices': ['idx_endereco_cliente', 'idx_endereco_cep']
        },
        'TELEFONES': {
            'tabela': 'core.telefones',
            'campos': [
                'id UUID PRIMARY KEY',
                'cliente_id UUID NOT NULL REFERENCES core.clientes(id)',
                'ddd VARCHAR(3)',
                'numero VARCHAR(15) NOT NULL',
                'tipo VARCHAR(20)',  # CELULAR, FIXO, COMERCIAL
                'principal BOOLEAN DEFAULT FALSE',
                'whatsapp BOOLEAN DEFAULT FALSE'
            ],
            'fonte': 'Dados Vixen',
            'indices': ['idx_telefones_cliente', 'idx_telefones_numero']
        },
        'LOJAS': {
            'tabela': 'core.lojas',
            'campos': [
                'id UUID PRIMARY KEY',
                'codigo VARCHAR(20) UNIQUE NOT NULL',
                'nome VARCHAR(100) NOT NULL',
                'endereco TEXT',
                'telefone VARCHAR(20)',
                'email VARCHAR(100)',
                'status VARCHAR(20) DEFAULT \'ATIVA\'',
                'data_abertura DATE',
                'data_fechamento DATE'
            ],
            'fonte': 'todos_os_caixas.xlsx (campo Loja)',
            'valores_iniciais': ['MAUA', 'SUZANO', 'SUZANO2', 'RIO_PEQUENO', 'PERUS', 'SAO_MATEUS'],
            'indices': ['idx_lojas_codigo', 'idx_lojas_status']
        },
        'VENDEDORES': {
            'tabela': 'core.vendedores',
            'campos': [
                'id UUID PRIMARY KEY',
                'nome VARCHAR(100) NOT NULL',
                'codigo VARCHAR(20) UNIQUE',
                'loja_id UUID REFERENCES core.lojas(id)',
                'email VARCHAR(100)',
                'telefone VARCHAR(20)',
                'status VARCHAR(20) DEFAULT \'ATIVO\'',
                'data_admissao DATE',
                'data_desligamento DATE'
            ],
            'fonte': 'todos_os_caixas.xlsx (os_entr_dia)',
            'indices': ['idx_vendedores_loja', 'idx_vendedores_status']
        },
        'VENDAS': {
            'tabela': 'vendas.vendas',
            'campos': [
                'id UUID PRIMARY KEY',
                'numero_venda VARCHAR(50) NOT NULL',
                'data_venda DATE NOT NULL',
                'loja_id UUID NOT NULL REFERENCES core.lojas(id)',
                'cliente_id UUID REFERENCES core.clientes(id)',
                'cliente_nome VARCHAR(200)',  # Denormalizado para performance
                'valor_venda DECIMAL(10,2) DEFAULT 0',
                'valor_entrada DECIMAL(10,2) DEFAULT 0',
                'valor_total DECIMAL(10,2) GENERATED ALWAYS AS (valor_venda + valor_entrada) STORED',
                'observacoes TEXT'
            ],
            'fonte': 'todos_os_caixas.xlsx (vend)',
            'indices': ['idx_vendas_data', 'idx_vendas_loja', 'idx_vendas_cliente', 'idx_vendas_numero'],
            'total_registros': '7,547 vendas | R$ 6.032.727,49'
        },
        'FORMAS_PAGAMENTO_VENDA': {
            'tabela': 'vendas.formas_pagamento_venda',
            'campos': [
                'id UUID PRIMARY KEY',
                'venda_id UUID NOT NULL REFERENCES vendas.vendas(id)',
                'forma_pagamento VARCHAR(50) NOT NULL',  # DN, CTD, CTC, PIX, etc
                'valor DECIMAL(10,2) NOT NULL',
                'parcelas INT DEFAULT 1',
                'observacoes TEXT'
            ],
            'fonte': 'todos_os_caixas.xlsx (vend - Forma de Pgto)',
            'indices': ['idx_fpgto_venda', 'idx_fpgto_forma']
        },
        'ORDENS_SERVICO': {
            'tabela': 'optica.ordens_servico',
            'campos': [
                'id UUID PRIMARY KEY',
                'numero_os VARCHAR(50) NOT NULL UNIQUE',
                'data_os DATE NOT NULL',
                'data_entrega DATE',
                'loja_id UUID NOT NULL REFERENCES core.lojas(id)',
                'cliente_id UUID NOT NULL REFERENCES core.clientes(id)',
                'vendedor_id UUID REFERENCES core.vendedores(id)',
                'venda_id UUID REFERENCES vendas.vendas(id)',  # Ligação com venda
                'status VARCHAR(30) DEFAULT \'ABERTA\'',
                'tem_carne BOOLEAN DEFAULT FALSE',
                'valor_total DECIMAL(10,2)',
                'observacoes TEXT'
            ],
            'fonte': 'todos_os_caixas.xlsx (os_entr_dia)',
            'indices': ['idx_os_numero', 'idx_os_data', 'idx_os_cliente', 'idx_os_loja', 'idx_os_status'],
            'total_registros': '5,974 entregas de OS'
        },
        'DIOPTRIAS': {
            'tabela': 'optica.dioptrias',
            'campos': [
                'id UUID PRIMARY KEY',
                'os_id UUID NOT NULL REFERENCES optica.ordens_servico(id)',
                'olho VARCHAR(2) NOT NULL',  # OD ou OE
                'esf DECIMAL(5,2)',
                'cil DECIMAL(5,2)',
                'eixo INT',
                'dnp DECIMAL(5,2)',
                'altura DECIMAL(5,2)',
                'adicao DECIMAL(5,2)',
                'tipo_visao VARCHAR(30)',  # LONGE, PERTO, MULTIFOCAL
                'CONSTRAINT chk_olho CHECK (olho IN (\'OD\', \'OE\'))'
            ],
            'fonte': 'OSs_Gerais (quando houver)',
            'indices': ['idx_dioptrias_os']
        },
        'RECEBIMENTOS_CARNE': {
            'tabela': 'vendas.recebimentos_carne',
            'campos': [
                'id UUID PRIMARY KEY',
                'os_id UUID NOT NULL REFERENCES optica.ordens_servico(id)',
                'data_recebimento DATE NOT NULL',
                'valor_parcela DECIMAL(10,2) NOT NULL',
                'numero_parcela VARCHAR(20)',  # Ex: PARC. 5/7
                'forma_pagamento VARCHAR(50) NOT NULL',
                'observacoes TEXT'
            ],
            'fonte': 'todos_os_caixas.xlsx (rec_carn)',
            'indices': ['idx_rec_carne_os', 'idx_rec_carne_data'],
            'total_registros': '3,108 registros | R$ 379.671,97'
        },
        'ENTREGAS_CARNE': {
            'tabela': 'vendas.entregas_carne',
            'campos': [
                'id UUID PRIMARY KEY',
                'os_id UUID NOT NULL REFERENCES optica.ordens_servico(id)',
                'data_entrega DATE NOT NULL',
                'valor_total DECIMAL(10,2) NOT NULL',
                'numero_parcelas INT',
                'observacoes TEXT'
            ],
            'fonte': 'todos_os_caixas.xlsx (entr_carn)',
            'indices': ['idx_entr_carne_os', 'idx_entr_carne_data'],
            'total_registros': '678 registros | R$ 411.087,49'
        },
        'RESTANTES_ENTRADA': {
            'tabela': 'vendas.restantes_entrada',
            'campos': [
                'id UUID PRIMARY KEY',
                'venda_id UUID REFERENCES vendas.vendas(id)',
                'data_registro DATE NOT NULL',
                'cliente_nome VARCHAR(200)',
                'valor_entrada DECIMAL(10,2) NOT NULL',
                'forma_pagamento VARCHAR(50)',
                'observacoes TEXT'
            ],
            'fonte': 'todos_os_caixas.xlsx (rest_entr)',
            'indices': ['idx_rest_entr_venda', 'idx_rest_entr_data'],
            'total_registros': '2,868 registros | R$ 929.201,55'
        },
        'MARKETING_INFO': {
            'tabela': 'marketing.cliente_info',
            'campos': [
                'id UUID PRIMARY KEY',
                'cliente_id UUID NOT NULL UNIQUE REFERENCES core.clientes(id)',
                'como_conheceu VARCHAR(100)',
                'data_primeira_compra DATE',
                'faixa_etaria VARCHAR(30)',
                'ultima_compra DATE',
                'total_compras INT DEFAULT 0',
                'valor_total_gasto DECIMAL(10,2) DEFAULT 0',
                'cliente_ativo BOOLEAN DEFAULT TRUE'
            ],
            'fonte': 'Dados Vixen + histórico vendas',
            'indices': ['idx_marketing_cliente']
        }
    }
    
    for entidade, info in entidades.items():
        print(f"\n   🗂️  {entidade}")
        print(f"      📊 Tabela: {info['tabela']}")
        print(f"      📁 Fonte: {info['fonte']}")
        if 'total_registros' in info:
            print(f"      📈 Dados: {info['total_registros']}")
        print(f"      🔧 Campos principais:")
        for campo in info['campos'][:5]:
            print(f"         - {campo}")
        if len(info['campos']) > 5:
            print(f"         ... e mais {len(info['campos']) - 5} campos")
    
    # 4. SCHEMAS
    print("\n\n🏗️  4. ORGANIZAÇÃO EM SCHEMAS")
    print("-" * 70)
    
    schemas = {
        'core': {
            'descricao': 'Dados centrais do sistema',
            'tabelas': ['clientes', 'endereco_cliente', 'telefones', 'lojas', 'vendedores']
        },
        'vendas': {
            'descricao': 'Vendas e pagamentos',
            'tabelas': ['vendas', 'formas_pagamento_venda', 'recebimentos_carne', 'entregas_carne', 'restantes_entrada']
        },
        'optica': {
            'descricao': 'Ordens de serviço e receitas',
            'tabelas': ['ordens_servico', 'dioptrias', 'produtos_os']
        },
        'marketing': {
            'descricao': 'CRM e campanhas',
            'tabelas': ['cliente_info', 'campanhas', 'aniversarios', 'comunicacoes']
        },
        'auditoria': {
            'descricao': 'Logs e histórico',
            'tabelas': ['log_alteracoes', 'historico_valores', 'snapshots_diarios']
        }
    }
    
    for schema, info in schemas.items():
        print(f"\n   📦 {schema.upper()}")
        print(f"      {info['descricao']}")
        for tabela in info['tabelas']:
            print(f"      - {tabela}")
    
    # Salvar análise
    resultado = {
        'entidades': {k: {**v, 'campos': [str(c) for c in v['campos']]} for k, v in entidades.items()},
        'schemas': schemas,
        'estruturas_fonte': estruturas
    }
    
    with open('data/modelo_banco_definitivo.json', 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    
    print("\n\n✅ Análise concluída!")
    print("📁 Modelo salvo em: data/modelo_banco_definitivo.json")
    
    return entidades, schemas

if __name__ == "__main__":
    entidades, schemas = analisar_dados_processados()