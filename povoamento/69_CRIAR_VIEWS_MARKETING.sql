-- ============================================================================
-- 69_CRIAR_VIEWS_MARKETING.sql
-- Views analíticas para facilitar consultas ao schema marketing
-- ============================================================================
-- ============================================================================
-- VIEW 1: Visão Completa de Origens com Todos os Relacionamentos
-- ============================================================================
CREATE OR REPLACE VIEW marketing.v_clientes_origem_completa AS
SELECT co.id,
    -- Dados do Cliente
    c.id as cliente_id,
    c.nome as cliente_nome,
    c.cpf as cliente_cpf,
    c.telefone as cliente_telefone,
    c.email as cliente_email,
    -- Dados da Loja
    l.id as loja_id,
    l.codigo as loja_codigo,
    l.nome as loja_nome,
    -- Dados do Canal
    ca.id as canal_id,
    ca.codigo as canal_codigo,
    ca.nome as canal_nome,
    ca.categoria as canal_categoria,
    -- Dados da OS (se existir)
    os.id as os_id,
    os.numero_os,
    os.data_abertura as os_data_abertura,
    os.valor_total as os_valor_total,
    -- Dados da Origem
    co.data_aquisicao,
    co.valor_primeira_compra,
    co.como_conheceu_original,
    co.observacoes,
    co.fonte_dados,
    co.criado_em,
    -- Campos Calculados
    EXTRACT(
        YEAR
        FROM co.data_aquisicao
    ) as ano_aquisicao,
    EXTRACT(
        MONTH
        FROM co.data_aquisicao
    ) as mes_aquisicao,
    TO_CHAR(co.data_aquisicao, 'YYYY-MM') as periodo_aquisicao,
    -- Status
    CASE
        WHEN co.os_id IS NOT NULL THEN 'COM_OS'
        ELSE 'SEM_OS'
    END as status_os
FROM marketing.clientes_origem co
    INNER JOIN core.clientes c ON c.id = co.cliente_id
    INNER JOIN core.lojas l ON l.id = co.loja_id
    INNER JOIN marketing.canais_aquisicao ca ON ca.id = co.canal_id
    LEFT JOIN core.ordens_servico os ON os.id = co.os_id;
COMMENT ON VIEW marketing.v_clientes_origem_completa IS 'View consolidada com todos os dados de origem dos clientes e seus relacionamentos';
-- ============================================================================
-- VIEW 2: Ranking de Canais por Performance
-- ============================================================================
CREATE OR REPLACE VIEW marketing.v_ranking_canais AS
SELECT ROW_NUMBER() OVER (
        ORDER BY COUNT(*) DESC
    ) as posicao,
    ca.codigo,
    ca.nome as canal,
    ca.categoria,
    COUNT(*) as total_clientes,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentual,
    ROUND(AVG(co.valor_primeira_compra), 2) as ticket_medio,
    ROUND(SUM(co.valor_primeira_compra), 2) as receita_total,
    COUNT(*) FILTER (
        WHERE co.os_id IS NOT NULL
    ) as com_os_vinculada,
    ROUND(
        COUNT(*) FILTER (
            WHERE co.os_id IS NOT NULL
        ) * 100.0 / NULLIF(COUNT(*), 0),
        2
    ) as perc_com_os,
    MIN(co.data_aquisicao) as primeira_ocorrencia,
    MAX(co.data_aquisicao) as ultima_ocorrencia
FROM marketing.clientes_origem co
    INNER JOIN marketing.canais_aquisicao ca ON ca.id = co.canal_id
WHERE ca.ativo = true
GROUP BY ca.id,
    ca.codigo,
    ca.nome,
    ca.categoria
ORDER BY total_clientes DESC;
COMMENT ON VIEW marketing.v_ranking_canais IS 'Ranking de canais ordenado por número de clientes adquiridos com métricas de performance';
-- ============================================================================
-- VIEW 3: Performance por Loja
-- ============================================================================
CREATE OR REPLACE VIEW marketing.v_performance_por_loja AS
SELECT l.codigo as loja_codigo,
    l.nome as loja_nome,
    ca.nome as canal,
    ca.categoria,
    COUNT(*) as total_clientes,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY l.id),
        2
    ) as percentual_loja,
    ROUND(AVG(co.valor_primeira_compra), 2) as ticket_medio,
    ROUND(SUM(co.valor_primeira_compra), 2) as receita_total
FROM marketing.clientes_origem co
    INNER JOIN core.lojas l ON l.id = co.loja_id
    INNER JOIN marketing.canais_aquisicao ca ON ca.id = co.canal_id
GROUP BY l.id,
    l.codigo,
    l.nome,
    ca.id,
    ca.nome,
    ca.categoria
ORDER BY l.codigo,
    total_clientes DESC;
COMMENT ON VIEW marketing.v_performance_por_loja IS 'Performance de cada canal segmentado por loja';
-- ============================================================================
-- VIEW 4: Evolução Temporal (Últimos 12 Meses)
-- ============================================================================
CREATE OR REPLACE VIEW marketing.v_evolucao_temporal AS
SELECT TO_CHAR(co.data_aquisicao, 'YYYY-MM') as periodo,
    EXTRACT(
        YEAR
        FROM co.data_aquisicao
    ) as ano,
    EXTRACT(
        MONTH
        FROM co.data_aquisicao
    ) as mes,
    COUNT(*) as novos_clientes,
    COUNT(DISTINCT co.canal_id) as canais_ativos,
    COUNT(DISTINCT co.loja_id) as lojas_ativas,
    ROUND(AVG(co.valor_primeira_compra), 2) as ticket_medio,
    ROUND(SUM(co.valor_primeira_compra), 2) as receita_total,
    COUNT(*) FILTER (
        WHERE co.os_id IS NOT NULL
    ) as com_os_vinculada
FROM marketing.clientes_origem co
WHERE co.data_aquisicao IS NOT NULL
    AND co.data_aquisicao >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY TO_CHAR(co.data_aquisicao, 'YYYY-MM'),
    EXTRACT(
        YEAR
        FROM co.data_aquisicao
    ),
    EXTRACT(
        MONTH
        FROM co.data_aquisicao
    )
ORDER BY periodo DESC;
COMMENT ON VIEW marketing.v_evolucao_temporal IS 'Evolução mensal de aquisição de clientes nos últimos 12 meses';
-- ============================================================================
-- VIEW 5: Análise por Categoria de Canal
-- ============================================================================
CREATE OR REPLACE VIEW marketing.v_analise_por_categoria AS
SELECT ca.categoria,
    COUNT(*) as total_clientes,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentual,
    COUNT(DISTINCT ca.id) as canais_na_categoria,
    ROUND(AVG(co.valor_primeira_compra), 2) as ticket_medio,
    ROUND(SUM(co.valor_primeira_compra), 2) as receita_total,
    COUNT(DISTINCT co.loja_id) as lojas_atingidas,
    MIN(co.data_aquisicao) as primeira_ocorrencia,
    MAX(co.data_aquisicao) as ultima_ocorrencia,
    COUNT(*) FILTER (
        WHERE co.data_aquisicao >= CURRENT_DATE - INTERVAL '6 months'
    ) as ultimos_6_meses
FROM marketing.clientes_origem co
    INNER JOIN marketing.canais_aquisicao ca ON ca.id = co.canal_id
GROUP BY ca.categoria
ORDER BY total_clientes DESC;
COMMENT ON VIEW marketing.v_analise_por_categoria IS 'Análise agregada por categoria de canal (INTERNO, INDICACAO, MARKETING, ORGANICO)';
-- ============================================================================
-- VIEW 6: Clientes Sem Origem (Para Análise de Cobertura)
-- ============================================================================
CREATE OR REPLACE VIEW marketing.v_clientes_sem_origem AS
SELECT c.id as cliente_id,
    c.nome as cliente_nome,
    c.cpf as cliente_cpf,
    l.codigo as loja_codigo,
    l.nome as loja_nome,
    c.criado_em as data_cadastro,
    c.ativo as cliente_ativo,
    (
        SELECT COUNT(*)
        FROM core.ordens_servico os
        WHERE os.cliente_id = c.id
    ) as total_oss,
    (
        SELECT MAX(os.data_abertura)
        FROM core.ordens_servico os
        WHERE os.cliente_id = c.id
    ) as ultima_os_data,
    (
        SELECT SUM(os.valor_total)
        FROM core.ordens_servico os
        WHERE os.cliente_id = c.id
    ) as valor_total_oss
FROM core.clientes c
    INNER JOIN core.lojas l ON l.id = c.loja_id
WHERE NOT EXISTS (
        SELECT 1
        FROM marketing.clientes_origem co
        WHERE co.cliente_id = c.id
    )
ORDER BY c.criado_em DESC;
COMMENT ON VIEW marketing.v_clientes_sem_origem IS 'Lista de clientes que ainda não têm origem mapeada para análise de cobertura';
-- ============================================================================
-- VIEW 7: Top Canais por Loja (Simplificado)
-- ============================================================================
CREATE OR REPLACE VIEW marketing.v_top_canais_por_loja AS WITH ranked AS (
        SELECT l.codigo as loja_codigo,
            l.nome as loja_nome,
            ca.nome as canal,
            COUNT(*) as total_clientes,
            ROUND(AVG(co.valor_primeira_compra), 2) as ticket_medio,
            ROW_NUMBER() OVER (
                PARTITION BY l.id
                ORDER BY COUNT(*) DESC
            ) as ranking
        FROM marketing.clientes_origem co
            INNER JOIN core.lojas l ON l.id = co.loja_id
            INNER JOIN marketing.canais_aquisicao ca ON ca.id = co.canal_id
        GROUP BY l.id,
            l.codigo,
            l.nome,
            ca.nome
    )
SELECT *
FROM ranked
WHERE ranking <= 5;
COMMENT ON VIEW marketing.v_top_canais_por_loja IS 'Top 5 canais mais efetivos por loja';
-- ============================================================================
-- VIEW 8: Dashboard Executivo
-- ============================================================================
CREATE OR REPLACE VIEW marketing.v_dashboard_executivo AS
SELECT (
        SELECT COUNT(*)
        FROM core.clientes
    ) as total_clientes_sistema,
    (
        SELECT COUNT(DISTINCT cliente_id)
        FROM marketing.clientes_origem
    ) as clientes_com_origem,
    (
        SELECT COUNT(*)
        FROM core.clientes
    ) - (
        SELECT COUNT(DISTINCT cliente_id)
        FROM marketing.clientes_origem
    ) as clientes_sem_origem,
    ROUND(
        (
            SELECT COUNT(DISTINCT cliente_id)
            FROM marketing.clientes_origem
        ) * 100.0 / NULLIF(
            (
                SELECT COUNT(*)
                FROM core.clientes
            ),
            0
        ),
        2
    ) as percentual_cobertura,
    (
        SELECT COUNT(*)
        FROM marketing.canais_aquisicao
        WHERE ativo = true
    ) as canais_ativos,
    (
        SELECT COUNT(DISTINCT categoria)
        FROM marketing.canais_aquisicao
    ) as categorias_ativas,
    (
        SELECT nome
        FROM marketing.canais_aquisicao ca
            INNER JOIN marketing.clientes_origem co ON co.canal_id = ca.id
        GROUP BY ca.nome
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ) as canal_mais_efetivo,
    (
        SELECT COUNT(*)
        FROM marketing.clientes_origem co
            INNER JOIN marketing.canais_aquisicao ca ON ca.id = co.canal_id
        WHERE ca.nome = (
                SELECT nome
                FROM marketing.canais_aquisicao ca2
                    INNER JOIN marketing.clientes_origem co2 ON co2.canal_id = ca2.id
                GROUP BY ca2.nome
                ORDER BY COUNT(*) DESC
                LIMIT 1
            )
    ) as clientes_canal_top,
    ROUND(
        (
            SELECT AVG(valor_primeira_compra)
            FROM marketing.clientes_origem
        ),
        2
    ) as ticket_medio_geral,
    (
        SELECT MIN(data_aquisicao)
        FROM marketing.clientes_origem
    ) as primeira_aquisicao,
    (
        SELECT MAX(data_aquisicao)
        FROM marketing.clientes_origem
    ) as ultima_aquisicao;
COMMENT ON VIEW marketing.v_dashboard_executivo IS 'Visão executiva única com métricas principais do schema marketing';
-- ============================================================================
-- RESUMO DAS VIEWS CRIADAS
-- ============================================================================
DO $$ BEGIN RAISE NOTICE '';
RAISE NOTICE '✓ 8 views analíticas criadas no schema marketing:';
RAISE NOTICE '';
RAISE NOTICE '  1. marketing.v_clientes_origem_completa';
RAISE NOTICE '     → Visão completa com todos os relacionamentos';
RAISE NOTICE '';
RAISE NOTICE '  2. marketing.v_ranking_canais';
RAISE NOTICE '     → Ranking de canais por performance';
RAISE NOTICE '';
RAISE NOTICE '  3. marketing.v_performance_por_loja';
RAISE NOTICE '     → Performance de canais por loja';
RAISE NOTICE '';
RAISE NOTICE '  4. marketing.v_evolucao_temporal';
RAISE NOTICE '     → Evolução mensal (últimos 12 meses)';
RAISE NOTICE '';
RAISE NOTICE '  5. marketing.v_analise_por_categoria';
RAISE NOTICE '     → Análise por categoria de canal';
RAISE NOTICE '';
RAISE NOTICE '  6. marketing.v_clientes_sem_origem';
RAISE NOTICE '     → Clientes sem origem mapeada';
RAISE NOTICE '';
RAISE NOTICE '  7. marketing.v_top_canais_por_loja';
RAISE NOTICE '     → Top 5 canais por loja';
RAISE NOTICE '';
RAISE NOTICE '  8. marketing.v_dashboard_executivo';
RAISE NOTICE '     → Dashboard executivo com métricas principais';
RAISE NOTICE '';
RAISE NOTICE 'Exemplos de uso:';
RAISE NOTICE '  SELECT * FROM marketing.v_dashboard_executivo;';
RAISE NOTICE '  SELECT * FROM marketing.v_ranking_canais LIMIT 10;';
RAISE NOTICE '  SELECT * FROM marketing.v_evolucao_temporal;';
END $$;