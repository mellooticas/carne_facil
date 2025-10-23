-- ============================================
-- SCRIPT: 12_importar_vendas_copy.sql
-- OBJETIVO: Importar vendas via COPY com lookup de UUIDs
-- DATA: 2025-10-23
-- NOTA: Use este script com psql ou no SQL Editor do Supabase
-- ============================================
-- ============================================
-- ETAPA 1: Criar tabela temporária para vendas Vixen
-- ============================================
CREATE TEMP TABLE IF NOT EXISTS tmp_vendas_vixen (
    id_legado VARCHAR(50),
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
    data_venda TIMESTAMP,
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
    arquivo_origem VARCHAR(100),
    _id_legado_cliente VARCHAR(50),
    _id_loja_codigo VARCHAR(10)
);
-- ============================================
-- ETAPA 2: Importar CSV para tabela temporária
-- ============================================
-- USANDO PSQL (linha de comando):
-- \copy tmp_vendas_vixen FROM 'D:/projetos/carne_facil/povoamento/dados/csv/vendas_vixen.csv' DELIMITER ',' CSV HEADER;
-- OU copie e cole no Supabase SQL Editor após fazer upload do arquivo:
-- (O Supabase não suporta COPY direto de arquivo local via SQL Editor)
-- ============================================
-- ETAPA 3: Inserir em core.vendas com lookup de UUIDs
-- ============================================
INSERT INTO core.vendas (
        id_legado,
        origem,
        cliente_id,
        loja_id,
        tipo,
        status,
        descricao,
        valor_bruto,
        valor_acrescimo,
        valor_desconto,
        valor_liquido,
        percentual_adiantamento,
        valor_adiantamento,
        data_venda,
        data_previsao_entrega,
        data_entrega,
        id_vendedor,
        nome_vendedor,
        id_operador,
        nome_operador,
        id_caixa,
        eh_garantia,
        meios_contato,
        mes_referencia,
        arquivo_origem
    )
SELECT tv.id_legado,
    tv.origem,
    -- Lookup do UUID do cliente
    (
        SELECT id
        FROM core.clientes
        WHERE id_legado = tv._id_legado_cliente
            AND created_by = 'MIGRACAO_VIXEN'
        LIMIT 1
    ) AS cliente_id,
    -- Lookup do UUID da loja
    (
        SELECT id
        FROM core.lojas
        WHERE codigo = tv._id_loja_codigo
        LIMIT 1
    ) AS loja_id,
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
WHERE EXISTS (
        SELECT 1
        FROM core.clientes
        WHERE id_legado = tv._id_legado_cliente
            AND created_by = 'MIGRACAO_VIXEN'
    )
    AND EXISTS (
        SELECT 1
        FROM core.lojas
        WHERE codigo = tv._id_loja_codigo
    ) ON CONFLICT (origem, id_legado) DO NOTHING;
-- Verificar quantas vendas Vixen foram inseridas
SELECT 'Vendas Vixen inseridas' AS resultado,
    COUNT(*) AS total,
    SUM(valor_liquido) AS valor_total
FROM core.vendas
WHERE origem = 'VIXEN';
-- ============================================
-- ETAPA 4: Repetir para vendas OS
-- ============================================
CREATE TEMP TABLE IF NOT EXISTS tmp_vendas_os (
    id_legado VARCHAR(50),
    origem VARCHAR(20),
    tipo VARCHAR(30),
    status VARCHAR(20),
    valor_liquido DECIMAL(10, 2),
    data_venda TIMESTAMP,
    _id_legado_cliente VARCHAR(50),
    _id_loja_codigo VARCHAR(10)
);
-- IMPORTAR vendas_os.csv:
-- \copy tmp_vendas_os FROM 'D:/projetos/carne_facil/povoamento/dados/csv/vendas_os.csv' DELIMITER ',' CSV HEADER;
INSERT INTO core.vendas (
        id_legado,
        origem,
        cliente_id,
        loja_id,
        tipo,
        status,
        valor_liquido,
        data_venda
    )
SELECT tos.id_legado,
    tos.origem,
    (
        SELECT id
        FROM core.clientes
        WHERE id_legado = tos._id_legado_cliente
            AND created_by = 'MIGRACAO_OS'
        LIMIT 1
    ) AS cliente_id,
    (
        SELECT id
        FROM core.lojas
        WHERE codigo = tos._id_loja_codigo
        LIMIT 1
    ) AS loja_id,
    tos.tipo,
    tos.status,
    tos.valor_liquido,
    tos.data_venda
FROM tmp_vendas_os tos
WHERE EXISTS (
        SELECT 1
        FROM core.clientes
        WHERE id_legado = tos._id_legado_cliente
            AND created_by = 'MIGRACAO_OS'
    )
    AND EXISTS (
        SELECT 1
        FROM core.lojas
        WHERE codigo = tos._id_loja_codigo
    ) ON CONFLICT (origem, id_legado) DO NOTHING;
-- Verificar vendas OS
SELECT 'Vendas OS inseridas' AS resultado,
    COUNT(*) AS total
FROM core.vendas
WHERE origem = 'OS';
-- ============================================
-- ETAPA 5: Importar itens de venda
-- ============================================
CREATE TEMP TABLE IF NOT EXISTS tmp_itens_venda (
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
    arquivo_origem VARCHAR(100),
    _id_legado_venda VARCHAR(50),
    _id_loja_codigo VARCHAR(10)
);
-- IMPORTAR itens_venda.csv:
-- \copy tmp_itens_venda FROM 'D:/projetos/carne_facil/povoamento/dados/csv/itens_venda.csv' DELIMITER ',' CSV HEADER;
INSERT INTO core.itens_venda (
        venda_id,
        item_numero,
        id_produto,
        descricao_produto,
        modelo,
        grupo,
        detalhe,
        quantidade,
        valor_unitario,
        valor_total,
        mes_referencia,
        arquivo_origem
    )
SELECT (
        SELECT id
        FROM core.vendas
        WHERE id_legado = ti._id_legado_venda
            AND origem = 'VIXEN'
        LIMIT 1
    ) AS venda_id,
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
WHERE EXISTS (
        SELECT 1
        FROM core.vendas
        WHERE id_legado = ti._id_legado_venda
            AND origem = 'VIXEN'
    ) ON CONFLICT (venda_id, item_numero) DO NOTHING;
-- Verificar itens
SELECT 'Itens inseridos' AS resultado,
    COUNT(*) AS total,
    COUNT(DISTINCT venda_id) AS vendas_com_itens
FROM core.itens_venda;
-- ============================================
-- ETAPA 6: Validação final
-- ============================================
-- Resumo geral
SELECT 'RESUMO FINAL' as tipo,
    (
        SELECT COUNT(*)
        FROM core.vendas
        WHERE origem = 'VIXEN'
    ) as vendas_vixen,
    (
        SELECT COUNT(*)
        FROM core.vendas
        WHERE origem = 'OS'
    ) as vendas_os,
    (
        SELECT COUNT(*)
        FROM core.itens_venda
    ) as itens,
    (
        SELECT SUM(valor_liquido)
        FROM core.vendas
        WHERE origem = 'VIXEN'
    ) as valor_total;
-- Verificar órfãos (deve retornar 0)
SELECT 'Verificação de integridade' as tipo,
    (
        SELECT COUNT(*)
        FROM core.vendas v
            LEFT JOIN core.clientes c ON v.cliente_id = c.id
        WHERE c.id IS NULL
    ) as vendas_sem_cliente,
    (
        SELECT COUNT(*)
        FROM core.itens_venda i
            LEFT JOIN core.vendas v ON i.venda_id = v.id
        WHERE v.id IS NULL
    ) as itens_sem_venda;
-- ============================================
-- ETAPA 7: Limpar tabelas temporárias
-- ============================================
DROP TABLE IF EXISTS tmp_vendas_vixen;
DROP TABLE IF EXISTS tmp_vendas_os;
DROP TABLE IF EXISTS tmp_itens_venda;
-- ============================================
-- FIM DO SCRIPT
-- ============================================
/*
 RESULTADO ESPERADO:
 ✅ Vendas Vixen: 19.930
 ✅ Vendas OS: 2.649
 ✅ Itens: 51.660
 ✅ Órfãos: 0
 ✅ Valor total: R$ 15.564.551,92
 */