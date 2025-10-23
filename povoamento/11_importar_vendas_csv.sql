-- ============================================
-- SCRIPT: 11_importar_vendas_csv.sql
-- OBJETIVO: Preparar e importar vendas via CSV
-- DATA: 2025-10-23
-- ============================================

-- ============================================
-- PASSO 1: Criar tabelas temporárias para CSV
-- ============================================

-- Tabela temporária para vendas Vixen
CREATE TEMP TABLE IF NOT EXISTS tmp_vendas_vixen (
    id_legado VARCHAR(50),
    id_legado_cliente VARCHAR(50),
    id_loja_codigo VARCHAR(10),
    origem VARCHAR(20),
    tipo VARCHAR(30),
    status VARCHAR(20),
    descricao VARCHAR(100),
    valor_bruto DECIMAL(10, 2),
    valor_acrescimo DECIMAL(10, 2),
    valor_desconto DECIMAL(10, 2),
    valor_liquido DECIMAL(10, 2),
    percentual_adiantamento DECIMAL(5, 2),
    valor_adiantamento DECIMAL(10, 2),
    data_venda TIMESTAMPTZ,
    data_previsao_entrega DATE,
    data_entrega DATE,
    id_vendedor VARCHAR(50),
    nome_vendedor VARCHAR(200),
    id_operador VARCHAR(50),
    nome_operador VARCHAR(200),
    id_caixa VARCHAR(50),
    eh_garantia BOOLEAN,
    meios_contato VARCHAR(100),
    mes_referencia VARCHAR(7),
    arquivo_origem VARCHAR(100)
);

-- Tabela temporária para vendas OS
CREATE TEMP TABLE IF NOT EXISTS tmp_vendas_os (
    id_legado VARCHAR(50),
    id_legado_cliente VARCHAR(50),
    id_loja_codigo VARCHAR(10),
    origem VARCHAR(20),
    tipo VARCHAR(30),
    status VARCHAR(20),
    valor_liquido DECIMAL(10, 2),
    data_venda TIMESTAMPTZ
);

-- Tabela temporária para itens
CREATE TEMP TABLE IF NOT EXISTS tmp_itens_venda (
    id_legado_venda VARCHAR(50),
    id_loja_codigo VARCHAR(10),
    item_numero INTEGER,
    id_produto VARCHAR(50),
    descricao_produto TEXT,
    modelo VARCHAR(200),
    grupo VARCHAR(100),
    detalhe VARCHAR(200),
    quantidade DECIMAL(10, 3),
    valor_unitario DECIMAL(10, 2),
    valor_total DECIMAL(10, 2),
    mes_referencia VARCHAR(7),
    arquivo_origem VARCHAR(100)
);

-- ============================================
-- PASSO 2: Importar CSVs para tabelas temporárias
-- ============================================

-- INSTRUÇÕES:
-- 1. Vá para o Supabase SQL Editor
-- 2. Use o comando COPY ou importe via Table Editor:

/*
COPY tmp_vendas_vixen 
FROM '/caminho/para/vendas_vixen.csv' 
DELIMITER ',' 
CSV HEADER;

COPY tmp_vendas_os 
FROM '/caminho/para/vendas_os.csv' 
DELIMITER ',' 
CSV HEADER;

COPY tmp_itens_venda 
FROM '/caminho/para/itens_venda.csv' 
DELIMITER ',' 
CSV HEADER;
*/

-- OU use o Table Editor do Supabase para upload direto

-- ============================================
-- PASSO 3: Inserir vendas Vixen com lookup de UUIDs
-- ============================================

INSERT INTO core.vendas (
    id_legado, origem, cliente_id, loja_id,
    tipo, status, descricao,
    valor_bruto, valor_acrescimo, valor_desconto, valor_liquido,
    percentual_adiantamento, valor_adiantamento,
    data_venda, data_previsao_entrega, data_entrega,
    id_vendedor, nome_vendedor, id_operador, nome_operador, id_caixa,
    eh_garantia, meios_contato,
    mes_referencia, arquivo_origem
)
SELECT 
    tv.id_legado,
    tv.origem,
    c.id AS cliente_id,
    l.id AS loja_id,
    tv.tipo,
    tv.status,
    tv.descricao,
    tv.valor_bruto,
    tv.valor_acrescimo,
    tv.valor_desconto,
    tv.valor_liquido,
    tv.percentual_adiantamento,
    tv.valor_adiantamento,
    tv.data_venda,
    tv.data_previsao_entrega,
    tv.data_entrega,
    tv.id_vendedor,
    tv.nome_vendedor,
    tv.id_operador,
    tv.nome_operador,
    tv.id_caixa,
    tv.eh_garantia,
    tv.meios_contato,
    tv.mes_referencia,
    tv.arquivo_origem
FROM tmp_vendas_vixen tv
INNER JOIN core.clientes c 
    ON c.id_legado = tv.id_legado_cliente 
    AND c.created_by = 'MIGRACAO_VIXEN'
INNER JOIN core.lojas l 
    ON l.codigo = tv.id_loja_codigo
ON CONFLICT (origem, id_legado) DO NOTHING;

-- Verificar quantas vendas Vixen foram inseridas
SELECT 'Vendas Vixen inseridas' AS resultado, COUNT(*) AS total
FROM core.vendas
WHERE origem = 'VIXEN';

-- ============================================
-- PASSO 4: Inserir vendas OS com lookup de UUIDs
-- ============================================

INSERT INTO core.vendas (
    id_legado, origem, cliente_id, loja_id,
    tipo, status, valor_liquido, data_venda
)
SELECT 
    tos.id_legado,
    tos.origem,
    c.id AS cliente_id,
    l.id AS loja_id,
    tos.tipo,
    tos.status,
    tos.valor_liquido,
    tos.data_venda
FROM tmp_vendas_os tos
INNER JOIN core.clientes c 
    ON c.id_legado = tos.id_legado_cliente 
    AND c.created_by = 'MIGRACAO_OS'
INNER JOIN core.lojas l 
    ON l.codigo = tos.id_loja_codigo
ON CONFLICT (origem, id_legado) DO NOTHING;

-- Verificar quantas vendas OS foram inseridas
SELECT 'Vendas OS inseridas' AS resultado, COUNT(*) AS total
FROM core.vendas
WHERE origem = 'OS';

-- ============================================
-- PASSO 5: Inserir itens de venda com lookup de UUID da venda
-- ============================================

INSERT INTO core.itens_venda (
    venda_id, item_numero, id_produto, descricao_produto,
    modelo, grupo, detalhe,
    quantidade, valor_unitario, valor_total,
    mes_referencia, arquivo_origem
)
SELECT 
    v.id AS venda_id,
    ti.item_numero,
    ti.id_produto,
    ti.descricao_produto,
    ti.modelo,
    ti.grupo,
    ti.detalhe,
    ti.quantidade,
    ti.valor_unitario,
    ti.valor_total,
    ti.mes_referencia,
    ti.arquivo_origem
FROM tmp_itens_venda ti
INNER JOIN core.vendas v 
    ON v.id_legado = ti.id_legado_venda 
    AND v.origem = 'VIXEN'
INNER JOIN core.lojas l 
    ON l.codigo = ti.id_loja_codigo
ON CONFLICT (venda_id, item_numero) DO NOTHING;

-- Verificar quantos itens foram inseridos
SELECT 'Itens de venda inseridos' AS resultado, COUNT(*) AS total
FROM core.itens_venda;

-- ============================================
-- PASSO 6: Limpar tabelas temporárias
-- ============================================

DROP TABLE IF EXISTS tmp_vendas_vixen;
DROP TABLE IF EXISTS tmp_vendas_os;
DROP TABLE IF EXISTS tmp_itens_venda;

-- ============================================
-- PASSO 7: Validação rápida
-- ============================================

-- Total de vendas por origem
SELECT 
    origem,
    COUNT(*) as total_vendas,
    SUM(valor_liquido) as valor_total
FROM core.vendas
GROUP BY origem;

-- Total de itens
SELECT 
    COUNT(*) as total_itens,
    COUNT(DISTINCT venda_id) as vendas_com_itens
FROM core.itens_venda;

-- Verificar integridade
SELECT 
    'Vendas sem cliente' as verificacao,
    COUNT(*) as total
FROM core.vendas v
LEFT JOIN core.clientes c ON v.cliente_id = c.id
WHERE c.id IS NULL

UNION ALL

SELECT 
    'Itens sem venda' as verificacao,
    COUNT(*) as total
FROM core.itens_venda i
LEFT JOIN core.vendas v ON i.venda_id = v.id
WHERE v.id IS NULL;

-- ============================================
-- FIM DO SCRIPT
-- ============================================

-- RESUMO ESPERADO:
-- ✅ Vendas Vixen: 19.930
-- ✅ Vendas OS: 2.649
-- ✅ Itens: 51.660
-- ✅ Integridade: 0 órfãos
