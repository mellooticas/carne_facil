-- ============================================================================
-- DIAGNÓSTICO: Formato de Números de OS
-- ============================================================================
-- 1. Exemplos de OS no staging (vixen)
SELECT 'OS no staging (vixen)' as fonte,
    os_n,
    loja,
    nome,
    cpf
FROM staging.marketing_origens_vixen
LIMIT 10;
-- 2. Padrão de OS no staging
SELECT 'Padrão OS staging' as metrica,
    MIN(os_n) as os_minima,
    MAX(os_n) as os_maxima,
    COUNT(DISTINCT os_n) as os_distintas
FROM staging.marketing_origens_vixen;
-- 3. Verificar se existe tabela ordens_servico
SELECT table_schema,
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'core'
    AND table_name LIKE '%ordem%'
ORDER BY table_name,
    ordinal_position;
-- 4. Se existir, ver exemplos de OS no core
DO $$ BEGIN IF EXISTS (
    SELECT 1
    FROM information_schema.tables
    WHERE table_schema = 'core'
        AND table_name = 'ordens_servico'
) THEN RAISE NOTICE 'Tabela core.ordens_servico EXISTE';
ELSE RAISE NOTICE 'Tabela core.ordens_servico NÃO EXISTE';
END IF;
END $$;
-- 5. Ver match de OS entre staging e core (se existir a tabela)
-- Descomente se a tabela existir:
/*
 SELECT 
 COUNT(*) as total_staging,
 COUNT(DISTINCT mkt.os_n) as os_distintas_staging,
 COUNT(DISTINCT os.numero) as os_encontradas_core
 FROM staging.marketing_origens_vixen mkt
 LEFT JOIN core.ordens_servico os ON os.numero = mkt.os_n;
 */
-- 6. Alternativa: buscar cliente por nome + loja
SELECT 'Match por nome+loja' as metrica,
    COUNT(DISTINCT mkt.cpf) as total_staging,
    COUNT(DISTINCT c.id) as encontrados
FROM staging.marketing_origens_vixen mkt
    INNER JOIN core.lojas l ON l.codigo = mkt.loja
    LEFT JOIN core.clientes c ON UPPER(TRIM(c.nome)) = UPPER(TRIM(mkt.nome))
    AND c.loja_id = l.id;
-- 7. Testar variações de CPF (com/sem zeros à esquerda)
SELECT 'CPFs exatos' as tipo_match,
    COUNT(DISTINCT mkt.cpf) as total
FROM staging.marketing_origens_vixen mkt
    INNER JOIN core.clientes c ON c.cpf = mkt.cpf
UNION ALL
SELECT 'CPFs convertidos para numeric' as tipo_match,
    COUNT(DISTINCT mkt.cpf) as total
FROM staging.marketing_origens_vixen mkt
    INNER JOIN core.clientes c ON c.cpf::BIGINT = mkt.cpf::BIGINT;