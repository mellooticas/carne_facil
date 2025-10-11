-- ============================================================================
-- BANCO DE DADOS - SISTEMA ÓTICAS (SUPABASE)
-- Script 08: VIEWS & FUNCTIONS - Dashboards e Relatórios
-- ============================================================================
-- IMPORTANTE: Execute APÓS o script 07_rls_policies_supabase.sql
-- Este é o ÚLTIMO script da estrutura do banco de dados!
-- ============================================================================

-- ============================================================================
-- VIEW: Dashboard Executivo
-- ============================================================================

CREATE OR REPLACE VIEW public.v_dashboard_executivo AS
SELECT 
    -- Totais Gerais
    (SELECT COUNT(*) FROM core.clientes WHERE deleted_at IS NULL) as total_clientes,
    (SELECT COUNT(*) FROM vendas.vendas WHERE deleted_at IS NULL AND cancelado = false) as total_vendas,
    (SELECT COUNT(*) FROM optica.ordens_servico WHERE deleted_at IS NULL AND cancelada = false) as total_os,
    (SELECT COUNT(*) FROM marketing.leads WHERE deleted_at IS NULL AND convertido = false) as total_leads_ativos,
    
    -- Valores
    (SELECT COALESCE(SUM(valor_total), 0) FROM vendas.vendas WHERE deleted_at IS NULL AND cancelado = false) as valor_total_vendas,
    (SELECT COALESCE(SUM(valor_parcela), 0) FROM vendas.recebimentos_carne WHERE deleted_at IS NULL) as valor_total_recebido,
    (SELECT COALESCE(SUM(valor_restante), 0) FROM vendas.restantes_entrada WHERE deleted_at IS NULL AND valor_restante > 0) as valor_a_receber,
    
    -- Médias
    (SELECT COALESCE(AVG(valor_total), 0) FROM vendas.vendas WHERE deleted_at IS NULL AND cancelado = false) as ticket_medio,
    (SELECT COALESCE(AVG(valor_final), 0) FROM optica.ordens_servico WHERE deleted_at IS NULL AND cancelada = false) as ticket_medio_os,
    
    -- Hoje
    (SELECT COUNT(*) FROM vendas.vendas WHERE data_venda = CURRENT_DATE AND deleted_at IS NULL AND cancelado = false) as vendas_hoje,
    (SELECT COALESCE(SUM(valor_total), 0) FROM vendas.vendas WHERE data_venda = CURRENT_DATE AND deleted_at IS NULL AND cancelado = false) as valor_vendas_hoje,
    (SELECT COUNT(*) FROM optica.ordens_servico WHERE data_abertura = CURRENT_DATE AND deleted_at IS NULL AND cancelada = false) as os_abertas_hoje,
    
    -- Este Mês
    (SELECT COUNT(*) FROM vendas.vendas WHERE DATE_TRUNC('month', data_venda) = DATE_TRUNC('month', CURRENT_DATE) AND deleted_at IS NULL AND cancelado = false) as vendas_mes,
    (SELECT COALESCE(SUM(valor_total), 0) FROM vendas.vendas WHERE DATE_TRUNC('month', data_venda) = DATE_TRUNC('month', CURRENT_DATE) AND deleted_at IS NULL AND cancelado = false) as valor_vendas_mes,
    
    -- Pendências
    (SELECT COUNT(*) FROM optica.ordens_servico WHERE status != 'ENTREGUE' AND data_entrega_real IS NULL AND deleted_at IS NULL AND cancelada = false) as os_pendentes,
    (SELECT COUNT(*) FROM optica.ordens_servico WHERE data_prevista_entrega < CURRENT_DATE AND data_entrega_real IS NULL AND deleted_at IS NULL AND cancelada = false) as os_atrasadas;

GRANT SELECT ON public.v_dashboard_executivo TO authenticated, anon;

COMMENT ON VIEW public.v_dashboard_executivo IS 'Dashboard executivo com KPIs principais';

-- ============================================================================
-- VIEW: Performance por Loja (Mensal)
-- ============================================================================

CREATE OR REPLACE VIEW public.v_performance_lojas_mensal AS
SELECT 
    l.codigo as loja_codigo,
    l.nome as loja_nome,
    DATE_TRUNC('month', v.data_venda) as mes_ano,
    
    -- Vendas
    COUNT(DISTINCT v.id) as total_vendas,
    COALESCE(SUM(v.valor_total), 0) as valor_vendas,
    COALESCE(AVG(v.valor_total), 0) as ticket_medio,
    
    -- OS
    COUNT(DISTINCT os.id) as total_os,
    COALESCE(SUM(os.valor_final), 0) as valor_os,
    
    -- Recebimentos
    COUNT(DISTINCT r.id) as total_recebimentos,
    COALESCE(SUM(r.valor_parcela), 0) as valor_recebido,
    
    -- Clientes Únicos
    COUNT(DISTINCT v.cliente_id) as clientes_unicos,
    
    -- A Receber
    COALESCE(SUM(re.valor_restante), 0) as valor_a_receber

FROM core.lojas l
LEFT JOIN vendas.vendas v ON v.loja_id = l.id AND v.deleted_at IS NULL AND v.cancelado = false
LEFT JOIN optica.ordens_servico os ON os.loja_id = l.id AND os.deleted_at IS NULL AND os.cancelada = false
    AND DATE_TRUNC('month', os.data_abertura) = DATE_TRUNC('month', v.data_venda)
LEFT JOIN vendas.recebimentos_carne r ON r.loja_id = l.id AND r.deleted_at IS NULL
    AND DATE_TRUNC('month', r.data_recebimento) = DATE_TRUNC('month', v.data_venda)
LEFT JOIN vendas.restantes_entrada re ON re.loja_id = l.id AND re.deleted_at IS NULL
    AND DATE_TRUNC('month', re.data_registro) = DATE_TRUNC('month', v.data_venda)
WHERE l.deleted_at IS NULL
  AND l.ativo = true
GROUP BY l.codigo, l.nome, DATE_TRUNC('month', v.data_venda)
ORDER BY mes_ano DESC, valor_vendas DESC;

GRANT SELECT ON public.v_performance_lojas_mensal TO authenticated, anon;

COMMENT ON VIEW public.v_performance_lojas_mensal IS 'Performance mensal por loja (vendas, OS, recebimentos)';

-- ============================================================================
-- VIEW: Top 20 Clientes VIP
-- ============================================================================

CREATE OR REPLACE VIEW public.v_top_clientes_vip AS
SELECT 
    c.id,
    c.nome,
    c.cpf,
    (SELECT t.numero FROM core.telefones t 
     WHERE t.cliente_id = c.id AND t.principal = true AND t.deleted_at IS NULL 
     LIMIT 1) as telefone_principal,
    c.email,
    ci.segmento,
    ci.total_compras,
    ci.total_gasto,
    ci.ticket_medio,
    ci.ultima_compra,
    ci.dias_desde_ultima_compra,
    ci.nps_score,
    -- Última venda
    (
        SELECT v.data_venda 
        FROM vendas.vendas v 
        WHERE v.cliente_id = c.id 
          AND v.deleted_at IS NULL 
          AND v.cancelado = false
        ORDER BY v.data_venda DESC 
        LIMIT 1
    ) as data_ultima_venda,
    -- Última OS
    (
        SELECT os.data_abertura 
        FROM optica.ordens_servico os 
        WHERE os.cliente_id = c.id 
          AND os.deleted_at IS NULL 
          AND os.cancelada = false
        ORDER BY os.data_abertura DESC 
        LIMIT 1
    ) as data_ultima_os
FROM core.clientes c
INNER JOIN marketing.cliente_info ci ON ci.cliente_id = c.id
WHERE c.deleted_at IS NULL
  AND ci.deleted_at IS NULL
  AND ci.total_gasto > 0
ORDER BY ci.total_gasto DESC
LIMIT 20;

GRANT SELECT ON public.v_top_clientes_vip TO authenticated;

COMMENT ON VIEW public.v_top_clientes_vip IS 'Top 20 clientes por valor gasto';

-- ============================================================================
-- VIEW: Análise de Inadimplência
-- ============================================================================

CREATE OR REPLACE VIEW public.v_analise_inadimplencia AS
SELECT 
    l.codigo as loja_codigo,
    l.nome as loja_nome,
    COUNT(DISTINCT re.id) as total_pendencias,
    COUNT(DISTINCT v.cliente_id) as clientes_inadimplentes,
    COALESCE(SUM(re.valor_restante), 0) as valor_total_pendente,
    COALESCE(AVG(re.valor_restante), 0) as valor_medio_pendente,
    MIN(re.data_registro) as pendencia_mais_antiga,
    
    -- Por faixa de atraso
    COUNT(CASE WHEN (CURRENT_DATE - re.data_registro) <= 30 THEN 1 END) as ate_30_dias,
    COUNT(CASE WHEN (CURRENT_DATE - re.data_registro) BETWEEN 31 AND 60 THEN 1 END) as de_31_a_60_dias,
    COUNT(CASE WHEN (CURRENT_DATE - re.data_registro) BETWEEN 61 AND 90 THEN 1 END) as de_61_a_90_dias,
    COUNT(CASE WHEN (CURRENT_DATE - re.data_registro) > 90 THEN 1 END) as acima_90_dias,
    
    -- Valores por faixa
    COALESCE(SUM(CASE WHEN (CURRENT_DATE - re.data_registro) <= 30 THEN re.valor_restante END), 0) as valor_ate_30_dias,
    COALESCE(SUM(CASE WHEN (CURRENT_DATE - re.data_registro) BETWEEN 31 AND 60 THEN re.valor_restante END), 0) as valor_31_a_60_dias,
    COALESCE(SUM(CASE WHEN (CURRENT_DATE - re.data_registro) BETWEEN 61 AND 90 THEN re.valor_restante END), 0) as valor_61_a_90_dias,
    COALESCE(SUM(CASE WHEN (CURRENT_DATE - re.data_registro) > 90 THEN re.valor_restante END), 0) as valor_acima_90_dias

FROM core.lojas l
LEFT JOIN vendas.restantes_entrada re ON re.loja_id = l.id AND re.deleted_at IS NULL AND re.valor_restante > 0
LEFT JOIN vendas.vendas v ON v.id = re.venda_id AND v.deleted_at IS NULL
WHERE l.deleted_at IS NULL
  AND l.ativo = true
GROUP BY l.codigo, l.nome
ORDER BY valor_total_pendente DESC;

GRANT SELECT ON public.v_analise_inadimplencia TO authenticated;

COMMENT ON VIEW public.v_analise_inadimplencia IS 'Análise de inadimplência por loja e faixa de atraso';

-- ============================================================================
-- VIEW: Funil de Vendas (Leads → Clientes)
-- ============================================================================

CREATE OR REPLACE VIEW public.v_funil_vendas AS
SELECT 
    DATE_TRUNC('month', COALESCE(l.created_at, c.created_at)) as mes_ano,
    
    -- Leads
    COUNT(DISTINCT l.id) as total_leads,
    COUNT(DISTINCT CASE WHEN l.status = 'NOVO' THEN l.id END) as leads_novos,
    COUNT(DISTINCT CASE WHEN l.status = 'CONTATADO' THEN l.id END) as leads_contatados,
    COUNT(DISTINCT CASE WHEN l.status = 'QUALIFICADO' THEN l.id END) as leads_qualificados,
    COUNT(DISTINCT CASE WHEN l.status = 'NEGOCIACAO' THEN l.id END) as leads_negociacao,
    COUNT(DISTINCT CASE WHEN l.convertido = true THEN l.id END) as leads_convertidos,
    COUNT(DISTINCT CASE WHEN l.status = 'PERDIDO' THEN l.id END) as leads_perdidos,
    
    -- Conversão
    CASE 
        WHEN COUNT(DISTINCT l.id) > 0 
        THEN ROUND((COUNT(DISTINCT CASE WHEN l.convertido = true THEN l.id END)::DECIMAL / COUNT(DISTINCT l.id)) * 100, 2)
        ELSE 0 
    END as taxa_conversao_leads,
    
    -- Clientes Novos
    COUNT(DISTINCT c.id) as clientes_novos,
    
    -- Primeira Compra
    COUNT(DISTINCT v.id) as primeiras_compras,
    COALESCE(SUM(v.valor_total), 0) as valor_primeiras_compras,
    COALESCE(AVG(v.valor_total), 0) as ticket_medio_primeira_compra

FROM marketing.leads l
FULL OUTER JOIN core.clientes c ON c.id = l.cliente_id
LEFT JOIN vendas.vendas v ON v.cliente_id = c.id 
    AND v.data_venda = (
        SELECT MIN(v2.data_venda) 
        FROM vendas.vendas v2 
        WHERE v2.cliente_id = c.id 
          AND v2.deleted_at IS NULL 
          AND v2.cancelado = false
    )
WHERE (l.deleted_at IS NULL OR l.deleted_at IS NULL)
  AND (c.deleted_at IS NULL OR c.deleted_at IS NULL)
GROUP BY DATE_TRUNC('month', COALESCE(l.created_at, c.created_at))
ORDER BY mes_ano DESC;

GRANT SELECT ON public.v_funil_vendas TO authenticated;

COMMENT ON VIEW public.v_funil_vendas IS 'Funil de conversão de leads para clientes';

-- ============================================================================
-- VIEW: Ranking de Vendedores
-- ============================================================================

CREATE OR REPLACE VIEW public.v_ranking_vendedores AS
SELECT 
    vd.id,
    vd.nome as vendedor_nome,
    vd.cpf,
    l.codigo as loja_codigo,
    l.nome as loja_nome,
    DATE_TRUNC('month', v.data_venda) as mes_ano,
    
    -- Vendas
    COUNT(DISTINCT v.id) as total_vendas,
    COALESCE(SUM(v.valor_total), 0) as valor_total_vendas,
    COALESCE(AVG(v.valor_total), 0) as ticket_medio,
    
    -- OS
    COUNT(DISTINCT os.id) as total_os,
    COALESCE(SUM(os.valor_final), 0) as valor_total_os,
    
    -- Clientes Únicos
    COUNT(DISTINCT v.cliente_id) as clientes_atendidos,
    
    -- Ranking
    RANK() OVER (
        PARTITION BY l.id, DATE_TRUNC('month', v.data_venda)
        ORDER BY COALESCE(SUM(v.valor_total), 0) DESC
    ) as ranking_loja,
    RANK() OVER (
        PARTITION BY DATE_TRUNC('month', v.data_venda)
        ORDER BY COALESCE(SUM(v.valor_total), 0) DESC
    ) as ranking_geral

FROM core.vendedores vd
LEFT JOIN core.lojas l ON l.id = vd.loja_id
LEFT JOIN vendas.vendas v ON v.vendedor_id = vd.id AND v.deleted_at IS NULL AND v.cancelado = false
LEFT JOIN optica.ordens_servico os ON os.vendedor_id = vd.id AND os.deleted_at IS NULL AND os.cancelada = false
WHERE vd.deleted_at IS NULL
  AND vd.ativo = true
GROUP BY vd.id, vd.nome, vd.cpf, l.id, l.codigo, l.nome, DATE_TRUNC('month', v.data_venda)
ORDER BY mes_ano DESC NULLS LAST, valor_total_vendas DESC;

GRANT SELECT ON public.v_ranking_vendedores TO authenticated;

COMMENT ON VIEW public.v_ranking_vendedores IS 'Ranking de vendedores por performance';

-- ============================================================================
-- VIEW: Análise de Produtos (OS)
-- ============================================================================

CREATE OR REPLACE VIEW public.v_analise_produtos_os AS
SELECT 
    p.tipo_produto,
    p.marca,
    COUNT(*) as quantidade_vendida,
    COALESCE(SUM(p.valor_total), 0) as valor_total_vendido,
    COALESCE(AVG(p.valor_total), 0) as valor_medio,
    MIN(p.valor_unitario) as menor_preco,
    MAX(p.valor_unitario) as maior_preco,
    COUNT(DISTINCT p.os_id) as os_utilizadas
FROM optica.produtos_os p
WHERE p.deleted_at IS NULL
GROUP BY p.tipo_produto, p.marca
ORDER BY quantidade_vendida DESC, valor_total_vendido DESC;

GRANT SELECT ON public.v_analise_produtos_os TO authenticated;

COMMENT ON VIEW public.v_analise_produtos_os IS 'Análise de produtos mais vendidos em OS';

-- ============================================================================
-- FUNCTION: Relatório de Vendas Consolidado
-- ============================================================================

CREATE OR REPLACE FUNCTION public.relatorio_vendas_consolidado(
    p_data_inicio DATE,
    p_data_fim DATE,
    p_loja_id UUID DEFAULT NULL
)
RETURNS TABLE (
    loja_codigo VARCHAR,
    loja_nome VARCHAR,
    periodo_inicio DATE,
    periodo_fim DATE,
    total_vendas BIGINT,
    valor_bruto NUMERIC,
    valor_descontos NUMERIC,
    valor_liquido NUMERIC,
    valor_entrada NUMERIC,
    valor_restante NUMERIC,
    valor_recebido NUMERIC,
    ticket_medio NUMERIC,
    clientes_unicos BIGINT,
    vendas_por_dia NUMERIC,
    maior_venda NUMERIC,
    menor_venda NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        l.codigo,
        l.nome,
        p_data_inicio,
        p_data_fim,
        COUNT(v.id)::BIGINT,
        COALESCE(SUM(v.valor_total), 0),
        COALESCE(SUM(v.valor_total - v.valor_entrada), 0),
        COALESCE(SUM(v.valor_entrada), 0),
        COALESCE(SUM(v.valor_entrada), 0),
        COALESCE(SUM(v.valor_restante), 0),
        COALESCE(SUM(r.valor_parcela), 0),
        COALESCE(AVG(v.valor_total), 0),
        COUNT(DISTINCT v.cliente_id)::BIGINT,
        ROUND(COUNT(v.id)::NUMERIC / GREATEST((p_data_fim - p_data_inicio + 1), 1), 2),
        COALESCE(MAX(v.valor_total), 0),
        COALESCE(MIN(v.valor_total), 0)
    FROM core.lojas l
    LEFT JOIN vendas.vendas v ON v.loja_id = l.id
        AND v.data_venda BETWEEN p_data_inicio AND p_data_fim
        AND v.deleted_at IS NULL
        AND v.cancelado = false
    LEFT JOIN vendas.recebimentos_carne r ON r.loja_id = l.id
        AND r.data_recebimento BETWEEN p_data_inicio AND p_data_fim
        AND r.deleted_at IS NULL
    WHERE l.deleted_at IS NULL
      AND l.ativo = true
      AND (p_loja_id IS NULL OR l.id = p_loja_id)
    GROUP BY l.codigo, l.nome;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION public.relatorio_vendas_consolidado(DATE, DATE, UUID) TO authenticated;

COMMENT ON FUNCTION public.relatorio_vendas_consolidado IS 'Relatório consolidado de vendas por período';

-- ============================================================================
-- FUNCTION: Calcular LTV (Lifetime Value) do Cliente
-- ============================================================================

CREATE OR REPLACE FUNCTION public.calcular_ltv_cliente(
    p_cliente_id UUID
)
RETURNS TABLE (
    cliente_id UUID,
    cliente_nome VARCHAR,
    primeira_compra DATE,
    ultima_compra DATE,
    meses_ativo INTEGER,
    total_compras BIGINT,
    valor_total_gasto NUMERIC,
    ticket_medio NUMERIC,
    frequencia_compra_meses NUMERIC,
    ltv_12_meses NUMERIC,
    ltv_24_meses NUMERIC,
    ltv_projetado NUMERIC
) AS $$
DECLARE
    v_meses_ativo INTEGER;
    v_frequencia NUMERIC;
BEGIN
    RETURN QUERY
    WITH cliente_stats AS (
        SELECT 
            c.id,
            c.nome,
            MIN(v.data_venda) as primeira_compra,
            MAX(v.data_venda) as ultima_compra,
            EXTRACT(MONTH FROM AGE(MAX(v.data_venda), MIN(v.data_venda)))::INTEGER as meses,
            COUNT(v.id)::BIGINT as compras,
            COALESCE(SUM(v.valor_total), 0) as gasto,
            COALESCE(AVG(v.valor_total), 0) as ticket
        FROM core.clientes c
        LEFT JOIN vendas.vendas v ON v.cliente_id = c.id
            AND v.deleted_at IS NULL
            AND v.cancelado = false
        WHERE c.id = p_cliente_id
        GROUP BY c.id, c.nome
    )
    SELECT 
        cs.id,
        cs.nome,
        cs.primeira_compra,
        cs.ultima_compra,
        GREATEST(cs.meses, 1),
        cs.compras,
        cs.gasto,
        cs.ticket,
        CASE WHEN cs.meses > 0 AND cs.compras > 0
            THEN ROUND(cs.meses::NUMERIC / cs.compras, 2)
            ELSE 0
        END as freq,
        -- LTV 12 meses (média * 12 / frequência)
        CASE WHEN cs.meses > 0 AND cs.compras > 0
            THEN ROUND((cs.gasto / cs.meses) * 12, 2)
            ELSE 0
        END,
        -- LTV 24 meses
        CASE WHEN cs.meses > 0 AND cs.compras > 0
            THEN ROUND((cs.gasto / cs.meses) * 24, 2)
            ELSE 0
        END,
        -- LTV Projetado (ticket médio * frequência * 36 meses)
        CASE WHEN cs.meses > 0 AND cs.compras > 0
            THEN ROUND(cs.ticket * (cs.compras::NUMERIC / cs.meses) * 36, 2)
            ELSE 0
        END
    FROM cliente_stats cs;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION public.calcular_ltv_cliente(UUID) TO authenticated;

COMMENT ON FUNCTION public.calcular_ltv_cliente IS 'Calcula Lifetime Value (LTV) de um cliente';

-- ============================================================================
-- FUNCTION: Prever Churn (Risco de Perda de Cliente)
-- ============================================================================

CREATE OR REPLACE FUNCTION public.prever_churn()
RETURNS TABLE (
    cliente_id UUID,
    cliente_nome VARCHAR,
    ultima_compra DATE,
    dias_sem_comprar INTEGER,
    total_compras BIGINT,
    risco_churn VARCHAR,
    acao_recomendada TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.nome,
        ci.ultima_compra,
        ci.dias_desde_ultima_compra,
        ci.total_compras,
        CASE 
            WHEN ci.dias_desde_ultima_compra > 365 THEN 'ALTO'
            WHEN ci.dias_desde_ultima_compra > 180 THEN 'MÉDIO'
            WHEN ci.dias_desde_ultima_compra > 90 THEN 'BAIXO'
            ELSE 'SEM RISCO'
        END,
        CASE 
            WHEN ci.dias_desde_ultima_compra > 365 THEN 'Cliente em risco ALTO de churn. Ação imediata: Ligar + oferta especial.'
            WHEN ci.dias_desde_ultima_compra > 180 THEN 'Cliente em risco MÉDIO. Ação: Email com promoção personalizada.'
            WHEN ci.dias_desde_ultima_compra > 90 THEN 'Cliente em risco BAIXO. Ação: WhatsApp lembrando check-up.'
            ELSE 'Cliente ativo. Manter relacionamento.'
        END
    FROM core.clientes c
    INNER JOIN marketing.cliente_info ci ON ci.cliente_id = c.id
    WHERE c.deleted_at IS NULL
      AND ci.deleted_at IS NULL
      AND ci.aceita_marketing = true
      AND ci.dias_desde_ultima_compra > 90
    ORDER BY ci.dias_desde_ultima_compra DESC;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION public.prever_churn() TO authenticated;

COMMENT ON FUNCTION public.prever_churn IS 'Identifica clientes em risco de churn com ações recomendadas';

-- ============================================================================
-- FUNCTION: Análise ABC de Clientes (Curva de Pareto)
-- ============================================================================

CREATE OR REPLACE FUNCTION public.analise_abc_clientes()
RETURNS TABLE (
    cliente_id UUID,
    cliente_nome VARCHAR,
    total_gasto NUMERIC,
    percentual_individual NUMERIC,
    percentual_acumulado NUMERIC,
    classificacao VARCHAR,
    descricao_classe TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH cliente_gasto AS (
        SELECT 
            c.id,
            c.nome,
            COALESCE(SUM(v.valor_total), 0) as gasto
        FROM core.clientes c
        LEFT JOIN vendas.vendas v ON v.cliente_id = c.id
            AND v.deleted_at IS NULL
            AND v.cancelado = false
        WHERE c.deleted_at IS NULL
        GROUP BY c.id, c.nome
        HAVING COALESCE(SUM(v.valor_total), 0) > 0
    ),
    cliente_percentual AS (
        SELECT 
            cg.*,
            ROUND((cg.gasto / SUM(cg.gasto) OVER ()) * 100, 2) as perc_individual,
            ROUND(SUM(cg.gasto) OVER (ORDER BY cg.gasto DESC) / SUM(cg.gasto) OVER () * 100, 2) as perc_acum
        FROM cliente_gasto cg
    )
    SELECT 
        cp.id,
        cp.nome,
        cp.gasto,
        cp.perc_individual,
        cp.perc_acum,
        CASE 
            WHEN cp.perc_acum <= 80 THEN 'A'
            WHEN cp.perc_acum <= 95 THEN 'B'
            ELSE 'C'
        END,
        CASE 
            WHEN cp.perc_acum <= 80 THEN 'Classe A: Clientes VIP - 80% do faturamento'
            WHEN cp.perc_acum <= 95 THEN 'Classe B: Clientes importantes - 15% do faturamento'
            ELSE 'Classe C: Clientes ocasionais - 5% do faturamento'
        END
    FROM cliente_percentual cp
    ORDER BY cp.gasto DESC;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION public.analise_abc_clientes() TO authenticated;

COMMENT ON FUNCTION public.analise_abc_clientes IS 'Análise ABC de clientes (Curva de Pareto 80-20)';

-- ============================================================================
-- FIM DO SCRIPT 08 - BANCO DE DADOS COMPLETO! 🎉
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '╔═══════════════════════════════════════════════════════════════════════════╗';
    RAISE NOTICE '║                    ✅ BANCO DE DADOS COMPLETO! 🎉                         ║';
    RAISE NOTICE '╚═══════════════════════════════════════════════════════════════════════════╝';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Script 08 executado com sucesso!';
    RAISE NOTICE '';
    RAISE NOTICE '👁️ VIEWS CRIADAS:';
    RAISE NOTICE '   - v_dashboard_executivo (KPIs principais)';
    RAISE NOTICE '   - v_performance_lojas_mensal (performance mensal)';
    RAISE NOTICE '   - v_top_clientes_vip (top 20 clientes)';
    RAISE NOTICE '   - v_analise_inadimplencia (inadimplência por faixa)';
    RAISE NOTICE '   - v_funil_vendas (conversão leads → clientes)';
    RAISE NOTICE '   - v_ranking_vendedores (ranking por performance)';
    RAISE NOTICE '   - v_analise_produtos_os (produtos mais vendidos)';
    RAISE NOTICE '';
    RAISE NOTICE '⚙️ FUNCTIONS CRIADAS:';
    RAISE NOTICE '   - relatorio_vendas_consolidado() (relatório completo)';
    RAISE NOTICE '   - calcular_ltv_cliente() (lifetime value)';
    RAISE NOTICE '   - prever_churn() (risco de perda)';
    RAISE NOTICE '   - analise_abc_clientes() (curva de Pareto)';
    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════════════';
    RAISE NOTICE '';
    RAISE NOTICE '📋 RESUMO FINAL DO BANCO DE DADOS:';
    RAISE NOTICE '';
    RAISE NOTICE '   📁 5 Schemas:';
    RAISE NOTICE '      - core (clientes, lojas, vendedores)';
    RAISE NOTICE '      - vendas (vendas, recebimentos, carnês)';
    RAISE NOTICE '      - optica (OS, dioptrias, produtos, entregas)';
    RAISE NOTICE '      - marketing (CRM, campanhas, leads)';
    RAISE NOTICE '      - auditoria (logs, histórico, snapshots)';
    RAISE NOTICE '';
    RAISE NOTICE '   📊 23 Tabelas criadas';
    RAISE NOTICE '   👁️ 27 Views criadas';
    RAISE NOTICE '   ⚙️ 16 Functions criadas';
    RAISE NOTICE '   🔐 RLS habilitado em TODAS as tabelas';
    RAISE NOTICE '   🔗 Foreign Keys entre schemas';
    RAISE NOTICE '   ⚡ Triggers de auditoria';
    RAISE NOTICE '   📈 Campos calculados (GENERATED)';
    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════════════';
    RAISE NOTICE '';
    RAISE NOTICE '🎯 PRÓXIMOS PASSOS:';
    RAISE NOTICE '';
    RAISE NOTICE '   1. ✅ Validar estrutura: SELECT * FROM v_dashboard_executivo;';
    RAISE NOTICE '   2. 📥 Popular dados: Executar scripts ETL Python';
    RAISE NOTICE '   3. 👥 Criar usuários: INSERT INTO core.user_roles';
    RAISE NOTICE '   4. 🧪 Testar RLS: Testar com diferentes roles';
    RAISE NOTICE '   5. 🔌 Conectar API: FastAPI + Supabase client';
    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════════════';
    RAISE NOTICE '';
    RAISE NOTICE '💡 EXEMPLO DE USO:';
    RAISE NOTICE '';
    RAISE NOTICE '   -- Ver dashboard';
    RAISE NOTICE '   SELECT * FROM v_dashboard_executivo;';
    RAISE NOTICE '';
    RAISE NOTICE '   -- Performance mensal';
    RAISE NOTICE '   SELECT * FROM v_performance_lojas_mensal';
    RAISE NOTICE '   WHERE mes_ano >= ''2024-01-01'';';
    RAISE NOTICE '';
    RAISE NOTICE '   -- LTV de um cliente';
    RAISE NOTICE '   SELECT * FROM calcular_ltv_cliente(''<cliente_uuid>'');';
    RAISE NOTICE '';
    RAISE NOTICE '   -- Prever churn';
    RAISE NOTICE '   SELECT * FROM prever_churn() LIMIT 10;';
    RAISE NOTICE '';
    RAISE NOTICE '   -- Análise ABC';
    RAISE NOTICE '   SELECT * FROM analise_abc_clientes() LIMIT 20;';
    RAISE NOTICE '';
    RAISE NOTICE '╔═══════════════════════════════════════════════════════════════════════════╗';
    RAISE NOTICE '║              BANCO DE DADOS PRONTO PARA PRODUÇÃO! 🚀                      ║';
    RAISE NOTICE '╚═══════════════════════════════════════════════════════════════════════════╝';
    RAISE NOTICE '';
END $$;
