-- ============================================
-- SCRIPT: 20_validacao_vendas.sql
-- OBJETIVO: Validar dados de vendas após povoamento
-- DATA: 2025-10-23
-- ============================================
-- ============================================
-- 1. CONTAGEM GERAL
-- ============================================
-- Total de vendas
SELECT 'VENDAS' as tabela,
    COUNT(*) as total,
    COUNT(DISTINCT cliente_id) as clientes_unicos,
    SUM(valor_liquido) as valor_total
FROM core.vendas;
-- Vendas por origem
SELECT origem,
    COUNT(*) as total_vendas,
    COUNT(DISTINCT cliente_id) as clientes_unicos,
    SUM(valor_liquido) as valor_total,
    ROUND(AVG(valor_liquido), 2) as ticket_medio
FROM core.vendas
GROUP BY origem
ORDER BY origem;
-- Vendas por loja
SELECT l.codigo,
    l.nome,
    COUNT(v.id) as total_vendas,
    SUM(v.valor_liquido) as valor_total,
    ROUND(AVG(v.valor_liquido), 2) as ticket_medio
FROM core.vendas v
    JOIN core.lojas l ON v.loja_id = l.id
GROUP BY l.codigo,
    l.nome
ORDER BY l.codigo;
-- ============================================
-- 2. VENDAS POR STATUS (VIXEN)
-- ============================================
SELECT status,
    COUNT(*) as total,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentual
FROM core.vendas
WHERE origem = 'VIXEN'
GROUP BY status
ORDER BY total DESC;
-- ============================================
-- 3. ITENS DE VENDA
-- ============================================
-- Total de itens
SELECT 'ITENS_VENDA' as tabela,
    COUNT(*) as total_itens,
    COUNT(DISTINCT venda_id) as vendas_com_itens,
    SUM(valor_total) as valor_total,
    ROUND(AVG(quantidade), 2) as qtd_media
FROM core.itens_venda;
-- Itens por venda (distribuição)
SELECT itens_por_venda,
    COUNT(*) as qtd_vendas
FROM (
        SELECT venda_id,
            COUNT(*) as itens_por_venda
        FROM core.itens_venda
        GROUP BY venda_id
    ) sub
GROUP BY itens_por_venda
ORDER BY itens_por_venda
LIMIT 10;
-- ============================================
-- 4. INTEGRIDADE REFERENCIAL
-- ============================================
-- Verificar vendas órfãs (sem cliente válido)
SELECT 'Vendas sem cliente válido' as validacao,
    COUNT(*) as total
FROM core.vendas v
    LEFT JOIN core.clientes c ON v.cliente_id = c.id
WHERE c.id IS NULL;
-- Verificar vendas sem loja válida
SELECT 'Vendas sem loja válida' as validacao,
    COUNT(*) as total
FROM core.vendas v
    LEFT JOIN core.lojas l ON v.loja_id = l.id
WHERE l.id IS NULL;
-- Verificar itens órfãos (sem venda válida)
SELECT 'Itens sem venda válida' as validacao,
    COUNT(*) as total
FROM core.itens_venda iv
    LEFT JOIN core.vendas v ON iv.venda_id = v.id
WHERE v.id IS NULL;
-- ============================================
-- 5. VENDAS POR PERÍODO
-- ============================================
-- Vendas por ano (top 10)
SELECT EXTRACT(
        YEAR
        FROM data_venda
    ) as ano,
    COUNT(*) as total_vendas,
    SUM(valor_liquido) as valor_total,
    ROUND(AVG(valor_liquido), 2) as ticket_medio
FROM core.vendas
GROUP BY EXTRACT(
        YEAR
        FROM data_venda
    )
ORDER BY ano DESC
LIMIT 10;
-- Vendas por mês (últimos 12 meses)
SELECT TO_CHAR(data_venda, 'YYYY-MM') as mes,
    COUNT(*) as total_vendas,
    SUM(valor_liquido) as valor_total
FROM core.vendas
WHERE data_venda >= NOW() - INTERVAL '12 months'
GROUP BY TO_CHAR(data_venda, 'YYYY-MM')
ORDER BY mes DESC;
-- ============================================
-- 6. TOP CLIENTES POR VALOR
-- ============================================
SELECT c.nome,
    c.cpf,
    COUNT(v.id) as total_compras,
    SUM(v.valor_liquido) as valor_total,
    ROUND(AVG(v.valor_liquido), 2) as ticket_medio
FROM core.vendas v
    JOIN core.clientes c ON v.cliente_id = c.id
GROUP BY c.id,
    c.nome,
    c.cpf
ORDER BY valor_total DESC
LIMIT 20;
-- ============================================
-- 7. PRODUTOS MAIS VENDIDOS
-- ============================================
SELECT descricao_produto,
    grupo,
    COUNT(*) as qtd_vendas,
    SUM(quantidade) as qtd_total,
    SUM(valor_total) as valor_total
FROM core.itens_venda
WHERE grupo IS NOT NULL
GROUP BY descricao_produto,
    grupo
ORDER BY qtd_vendas DESC
LIMIT 20;
-- ============================================
-- 8. VERIFICAR VENDAS DUPLICADAS
-- ============================================
SELECT 'Vendas duplicadas (origem + id_legado)' as validacao,
    COUNT(*) as total
FROM (
        SELECT origem,
            id_legado,
            COUNT(*) as cnt
        FROM core.vendas
        GROUP BY origem,
            id_legado
        HAVING COUNT(*) > 1
    ) duplicadas;
-- ============================================
-- 9. RESUMO DE QUALIDADE DOS DADOS
-- ============================================
SELECT 'Vendas com valor_liquido zerado' as metrica,
    COUNT(*) as total
FROM core.vendas
WHERE valor_liquido = 0
    OR valor_liquido IS NULL
UNION ALL
SELECT 'Vendas sem data' as metrica,
    COUNT(*) as total
FROM core.vendas
WHERE data_venda IS NULL
UNION ALL
SELECT 'Itens com valor_total zerado' as metrica,
    COUNT(*) as total
FROM core.itens_venda
WHERE valor_total = 0
    OR valor_total IS NULL
UNION ALL
SELECT 'Itens com quantidade zerada' as metrica,
    COUNT(*) as total
FROM core.itens_venda
WHERE quantidade = 0
    OR quantidade IS NULL;
-- ============================================
-- FIM DA VALIDAÇÃO
-- ============================================