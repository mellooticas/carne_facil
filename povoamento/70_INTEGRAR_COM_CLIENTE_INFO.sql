-- ============================================================================
-- 70_INTEGRAR_COM_CLIENTE_INFO.sql
-- Integração do sistema de origem com marketing.cliente_info existente
-- Popula campo 'segmento' baseado no canal de aquisição
-- ============================================================================
DO $$ BEGIN RAISE NOTICE '';
RAISE NOTICE '=== INTEGRAÇÃO COM marketing.cliente_info ===';
RAISE NOTICE 'Objetivo: Popular campo segmento com canal de origem';
RAISE NOTICE '';
END $$;
-- ============================================================================
-- ETAPA 1: VERIFICAR ESTRUTURA EXISTENTE
-- ============================================================================
DO $$ BEGIN RAISE NOTICE '=== VERIFICANDO ESTRUTURA EXISTENTE ===';
END $$;
-- Verificar se tabela cliente_info existe
SELECT CASE
        WHEN EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'marketing'
                AND table_name = 'cliente_info'
        ) THEN '✓ Tabela marketing.cliente_info existe'
        ELSE '✗ Tabela marketing.cliente_info NÃO existe'
    END as status;
-- Verificar estrutura do campo segmento
SELECT column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'marketing'
    AND table_name = 'cliente_info'
    AND column_name = 'segmento';
-- Contagem de registros
SELECT COUNT(*) as total_registros,
    COUNT(*) FILTER (
        WHERE segmento IS NOT NULL
    ) as com_segmento,
    COUNT(*) FILTER (
        WHERE segmento IS NULL
    ) as sem_segmento,
    COUNT(DISTINCT segmento) as segmentos_distintos
FROM marketing.cliente_info;
-- Valores atuais de segmento
SELECT segmento,
    COUNT(*) as quantidade,
    ROUND(
        COUNT(*) * 100.0 / (
            SELECT COUNT(*)
            FROM marketing.cliente_info
        ),
        2
    ) as percentual
FROM marketing.cliente_info
WHERE segmento IS NOT NULL
GROUP BY segmento
ORDER BY quantidade DESC;
-- ============================================================================
-- ETAPA 2: CRIAR TABELA DE MAPEAMENTO ORIGEM → SEGMENTO
-- ============================================================================
DO $$ BEGIN RAISE NOTICE '';
RAISE NOTICE '=== CRIANDO TABELA DE MAPEAMENTO ===';
END $$;
-- Tabela auxiliar para armazenar origem de cada cliente
CREATE TABLE IF NOT EXISTS marketing.clientes_canal_origem (
    id SERIAL PRIMARY KEY,
    cliente_id UUID NOT NULL,
    canal_id INTEGER NOT NULL,
    como_conheceu_original TEXT,
    data_aquisicao DATE,
    valor_primeira_compra NUMERIC(10, 2),
    loja_id UUID,
    os_numero VARCHAR(50),
    fonte_dados VARCHAR(50) DEFAULT 'VIXEN_CSV',
    criado_em TIMESTAMP DEFAULT NOW(),
    -- Foreign Keys
    CONSTRAINT fk_canal_origem_cliente FOREIGN KEY (cliente_id) REFERENCES core.clientes(id) ON DELETE CASCADE,
    CONSTRAINT fk_canal_origem_canal FOREIGN KEY (canal_id) REFERENCES marketing.canais_aquisicao(id) ON DELETE RESTRICT,
    CONSTRAINT fk_canal_origem_loja FOREIGN KEY (loja_id) REFERENCES core.lojas(id) ON DELETE
    SET NULL,
        -- Garantir 1 origem por cliente
        CONSTRAINT uk_canal_origem_cliente UNIQUE (cliente_id)
);
-- Índices
CREATE INDEX IF NOT EXISTS idx_canal_origem_cliente ON marketing.clientes_canal_origem(cliente_id);
CREATE INDEX IF NOT EXISTS idx_canal_origem_canal ON marketing.clientes_canal_origem(canal_id);
CREATE INDEX IF NOT EXISTS idx_canal_origem_data ON marketing.clientes_canal_origem(data_aquisicao);
COMMENT ON TABLE marketing.clientes_canal_origem IS 'Tabela auxiliar que armazena o canal de origem/aquisição de cada cliente antes de popular cliente_info';
-- ============================================================================
-- ETAPA 3: POPULAR TABELA DE ORIGEM A PARTIR DO STAGING
-- ============================================================================
DO $$ BEGIN RAISE NOTICE '';
RAISE NOTICE '=== POPULANDO ORIGENS A PARTIR DO STAGING ===';
END $$;
-- Verificar se staging tem dados processados
DO $$
DECLARE total_staging INTEGER;
total_processados INTEGER;
BEGIN
SELECT COUNT(*),
    COUNT(*) FILTER (
        WHERE processado = true
            AND canal_normalizado_id IS NOT NULL
    ) INTO total_staging,
    total_processados
FROM staging.marketing_origens_vixen;
RAISE NOTICE 'Registros no staging: %',
total_staging;
RAISE NOTICE 'Registros processados: %',
total_processados;
IF total_processados = 0 THEN RAISE WARNING 'Nenhum registro processado no staging. Execute primeiro o script 64_NORMALIZAR_COMO_CONHECEU.sql';
END IF;
END $$;
-- Inserir origens (não duplicar se já existe)
INSERT INTO marketing.clientes_canal_origem (
        cliente_id,
        canal_id,
        como_conheceu_original,
        data_aquisicao,
        valor_primeira_compra,
        loja_id,
        os_numero,
        fonte_dados
    )
SELECT DISTINCT ON (c.id) c.id as cliente_id,
    mkt.canal_normalizado_id as canal_id,
    mkt.como_conheceu_raw as como_conheceu_original,
    mkt.data_de_compra::DATE as data_aquisicao,
    mkt.total as valor_primeira_compra,
    l.id as loja_id,
    mkt.os_n as os_numero,
    'VIXEN_CSV' as fonte_dados
FROM staging.marketing_origens_vixen mkt
    INNER JOIN core.clientes c ON c.cpf = mkt.cpf
    INNER JOIN core.lojas l ON l.codigo = mkt.loja
WHERE mkt.canal_normalizado_id IS NOT NULL
    AND mkt.processado = true
ORDER BY c.id,
    mkt.data_de_compra ASC ON CONFLICT (cliente_id) DO NOTHING;
-- Estatísticas da população
SELECT COUNT(*) as total_origens_cadastradas,
    COUNT(DISTINCT cliente_id) as clientes_unicos,
    COUNT(*) FILTER (
        WHERE os_numero IS NOT NULL
    ) as com_os_numero,
    ROUND(AVG(valor_primeira_compra), 2) as ticket_medio
FROM marketing.clientes_canal_origem;
-- ============================================================================
-- ETAPA 4: CRIAR/ATUALIZAR REGISTROS EM cliente_info
-- ============================================================================
DO $$ BEGIN RAISE NOTICE '';
RAISE NOTICE '=== POPULANDO marketing.cliente_info ===';
END $$;
-- Primeiro, remover a constraint de segmento se existir
DO $$ BEGIN IF EXISTS (
    SELECT 1
    FROM information_schema.table_constraints
    WHERE constraint_schema = 'marketing'
        AND table_name = 'cliente_info'
        AND constraint_name = 'cliente_info_segmento_check'
) THEN
ALTER TABLE marketing.cliente_info DROP CONSTRAINT cliente_info_segmento_check;
RAISE NOTICE '✓ Constraint de segmento removida para permitir valores de canais';
END IF;
END $$;
-- Desabilitar trigger problemático temporariamente
DO $$ BEGIN -- Desabilitar apenas triggers de usuário (não system triggers)
ALTER TABLE marketing.cliente_info DISABLE TRIGGER USER;
RAISE NOTICE '✓ Triggers de usuário desabilitados temporariamente';
END $$;
-- Inserir registros que não existem em cliente_info
INSERT INTO marketing.cliente_info (
        cliente_id,
        segmento,
        primeira_compra,
        tags,
        observacoes
    )
SELECT co.cliente_id,
    ca.nome as segmento,
    -- Usar nome do canal como segmento
    co.data_aquisicao as primeira_compra,
    ARRAY [ca.categoria, ca.codigo] as tags,
    -- Tags com categoria e código do canal
    'Origem: ' || co.como_conheceu_original as observacoes
FROM marketing.clientes_canal_origem co
    INNER JOIN marketing.canais_aquisicao ca ON ca.id = co.canal_id
WHERE NOT EXISTS (
        SELECT 1
        FROM marketing.cliente_info ci
        WHERE ci.cliente_id = co.cliente_id
    ) ON CONFLICT (cliente_id) DO NOTHING;
-- Atualizar registros existentes que não têm origem definida
UPDATE marketing.cliente_info ci
SET segmento = ca.nome,
    tags = CASE
        WHEN ci.tags IS NULL THEN ARRAY [ca.categoria, ca.codigo]
        ELSE ci.tags || ARRAY [ca.categoria, ca.codigo]
    END,
    observacoes = COALESCE(ci.observacoes || E'\n', '') || 'Origem: ' || co.como_conheceu_original
FROM marketing.clientes_canal_origem co
    INNER JOIN marketing.canais_aquisicao ca ON ca.id = co.canal_id
WHERE ci.cliente_id = co.cliente_id
    AND (
        ci.segmento IS NULL
        OR ci.segmento NOT IN ('VIP', 'REGULAR', 'OCASIONAL', 'INATIVO', 'NOVO')
    );
-- Reabilitar trigger
DO $$ BEGIN -- Reabilitar apenas triggers de usuário
ALTER TABLE marketing.cliente_info ENABLE TRIGGER USER;
RAISE NOTICE '✓ Triggers de usuário reabilitados';
END $$;
-- ============================================================================
-- ETAPA 5: CRIAR VIEW PARA ANÁLISE INTEGRADA
-- ============================================================================
DO $$ BEGIN RAISE NOTICE '';
RAISE NOTICE '=== CRIANDO VIEW DE ANÁLISE INTEGRADA ===';
END $$;
CREATE OR REPLACE VIEW marketing.v_clientes_origem_integrada AS
SELECT c.id as cliente_id,
    c.nome as cliente_nome,
    c.cpf,
    c.email,
    l.nome as loja_nome,
    -- Dados da origem
    ca.codigo as canal_codigo,
    ca.nome as canal_nome,
    ca.categoria as canal_categoria,
    co.como_conheceu_original,
    co.data_aquisicao,
    co.valor_primeira_compra,
    -- Dados de cliente_info
    ci.segmento,
    ci.primeira_compra,
    ci.ultima_compra,
    ci.total_compras,
    ci.total_gasto,
    ci.ticket_medio,
    ci.dias_desde_ultima_compra,
    ci.risco_churn,
    ci.tags,
    -- Campos calculados
    EXTRACT(
        YEAR
        FROM co.data_aquisicao
    ) as ano_aquisicao,
    TO_CHAR(co.data_aquisicao, 'YYYY-MM') as periodo_aquisicao
FROM marketing.clientes_canal_origem co
    INNER JOIN core.clientes c ON c.id = co.cliente_id
    LEFT JOIN core.lojas l ON l.id = co.loja_id
    INNER JOIN marketing.canais_aquisicao ca ON ca.id = co.canal_id
    LEFT JOIN marketing.cliente_info ci ON ci.cliente_id = co.cliente_id;
COMMENT ON VIEW marketing.v_clientes_origem_integrada IS 'View consolidada integrando origem do cliente com informações de marketing.cliente_info';
-- ============================================================================
-- ETAPA 6: ESTATÍSTICAS E VALIDAÇÃO
-- ============================================================================
DO $$ BEGIN RAISE NOTICE '';
RAISE NOTICE '=== ESTATÍSTICAS FINAIS ===';
END $$;
-- Resumo geral
SELECT 'Total clientes no sistema' as metrica,
    COUNT(*) as quantidade
FROM core.clientes
UNION ALL
SELECT 'Clientes com origem mapeada' as metrica,
    COUNT(*) as quantidade
FROM marketing.clientes_canal_origem
UNION ALL
SELECT 'Registros em cliente_info' as metrica,
    COUNT(*) as quantidade
FROM marketing.cliente_info
UNION ALL
SELECT 'cliente_info com origem nos tags' as metrica,
    COUNT(*) as quantidade
FROM marketing.cliente_info
WHERE tags && ARRAY ['MARKETING', 'INDICACAO', 'ORGANICO', 'INTERNO'];
-- Distribuição por canal
SELECT ca.categoria,
    ca.nome as canal,
    COUNT(*) as clientes,
    ROUND(
        COUNT(*) * 100.0 / (
            SELECT COUNT(*)
            FROM marketing.clientes_canal_origem
        ),
        2
    ) as percentual
FROM marketing.clientes_canal_origem co
    INNER JOIN marketing.canais_aquisicao ca ON ca.id = co.canal_id
GROUP BY ca.categoria,
    ca.nome
ORDER BY clientes DESC;
-- Verificar integração com cliente_info
SELECT 'Clientes com origem' as grupo,
    COUNT(*) as total
FROM marketing.clientes_canal_origem
UNION ALL
SELECT 'Já em cliente_info' as grupo,
    COUNT(DISTINCT ci.cliente_id) as total
FROM marketing.cliente_info ci
    INNER JOIN marketing.clientes_canal_origem co ON co.cliente_id = ci.cliente_id;
-- ============================================================================
-- RESUMO FINAL
-- ============================================================================
DO $$
DECLARE total_origens INTEGER;
total_cliente_info INTEGER;
total_integrados INTEGER;
BEGIN
SELECT COUNT(*) INTO total_origens
FROM marketing.clientes_canal_origem;
SELECT COUNT(*) INTO total_cliente_info
FROM marketing.cliente_info;
SELECT COUNT(*) INTO total_integrados
FROM marketing.cliente_info ci
    INNER JOIN marketing.clientes_canal_origem co ON co.cliente_id = ci.cliente_id;
RAISE NOTICE '';
RAISE NOTICE '============================================================';
RAISE NOTICE 'INTEGRAÇÃO CONCLUÍDA';
RAISE NOTICE '============================================================';
RAISE NOTICE '';
RAISE NOTICE 'ESTRUTURA CRIADA:';
RAISE NOTICE '  ✓ marketing.clientes_canal_origem (tabela auxiliar)';
RAISE NOTICE '  ✓ marketing.v_clientes_origem_integrada (view)';
RAISE NOTICE '';
RAISE NOTICE 'DADOS POPULADOS:';
RAISE NOTICE '  • Origens mapeadas: %',
total_origens;
RAISE NOTICE '  • Registros em cliente_info: %',
total_cliente_info;
RAISE NOTICE '  • Integrados (com origem): %',
total_integrados;
RAISE NOTICE '';
RAISE NOTICE 'USO:';
RAISE NOTICE '  SELECT * FROM marketing.v_clientes_origem_integrada;';
RAISE NOTICE '  SELECT canal_categoria, COUNT(*) FROM marketing.v_clientes_origem_integrada GROUP BY canal_categoria;';
RAISE NOTICE '';
RAISE NOTICE '============================================================';
END $$;