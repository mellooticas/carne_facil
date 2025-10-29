-- ============================================================================
-- DIAGNÓSTICO: Por que só 1749 clientes foram mapeados?
-- ============================================================================
-- 1. Total de registros no staging
SELECT 'Registros no staging' as metrica,
    COUNT(*) as quantidade
FROM staging.marketing_origens_vixen;
-- 2. CPFs únicos no staging
SELECT 'CPFs únicos no staging' as metrica,
    COUNT(DISTINCT cpf) as quantidade
FROM staging.marketing_origens_vixen;
-- 3. Total de clientes no sistema
SELECT 'Clientes no sistema (core.clientes)' as metrica,
    COUNT(*) as quantidade
FROM core.clientes;
-- 4. CPFs do staging que EXISTEM em core.clientes
SELECT 'CPFs do staging encontrados em clientes' as metrica,
    COUNT(DISTINCT mkt.cpf) as quantidade
FROM staging.marketing_origens_vixen mkt
WHERE EXISTS (
        SELECT 1
        FROM core.clientes c
        WHERE c.cpf = mkt.cpf
    );
-- 5. CPFs do staging que NÃO EXISTEM em core.clientes
SELECT 'CPFs do staging NÃO encontrados' as metrica,
    COUNT(DISTINCT mkt.cpf) as quantidade
FROM staging.marketing_origens_vixen mkt
WHERE NOT EXISTS (
        SELECT 1
        FROM core.clientes c
        WHERE c.cpf = mkt.cpf
    );
-- 6. Exemplos de CPFs não encontrados (primeiros 20)
SELECT mkt.cpf,
    mkt.nome,
    mkt.loja,
    COUNT(*) as ocorrencias
FROM staging.marketing_origens_vixen mkt
WHERE NOT EXISTS (
        SELECT 1
        FROM core.clientes c
        WHERE c.cpf = mkt.cpf
    )
GROUP BY mkt.cpf,
    mkt.nome,
    mkt.loja
ORDER BY ocorrencias DESC
LIMIT 20;
-- 7. Verificar se há problema de formatação de CPF
SELECT 'CPFs com 11 dígitos no staging' as metrica,
    COUNT(DISTINCT cpf) as quantidade
FROM staging.marketing_origens_vixen
WHERE LENGTH(cpf) = 11;
-- 8. Verificar CPFs no core.clientes
SELECT 'CPFs com 11 dígitos em core.clientes' as metrica,
    COUNT(*) as quantidade
FROM core.clientes
WHERE LENGTH(cpf) = 11;
-- 9. Match rate por loja
SELECT mkt.loja,
    COUNT(DISTINCT mkt.cpf) as cpfs_no_staging,
    COUNT(
        DISTINCT CASE
            WHEN c.id IS NOT NULL THEN mkt.cpf
        END
    ) as cpfs_encontrados,
    ROUND(
        COUNT(
            DISTINCT CASE
                WHEN c.id IS NOT NULL THEN mkt.cpf
            END
        ) * 100.0 / COUNT(DISTINCT mkt.cpf),
        2
    ) as percentual_match
FROM staging.marketing_origens_vixen mkt
    LEFT JOIN core.clientes c ON c.cpf = mkt.cpf
GROUP BY mkt.loja
ORDER BY mkt.loja;
-- 10. Comparar formato de CPFs
SELECT 'Formato staging' as fonte,
    MIN(cpf) as exemplo_min,
    MAX(cpf) as exemplo_max,
    AVG(LENGTH(cpf)) as tamanho_medio
FROM staging.marketing_origens_vixen
WHERE cpf IS NOT NULL
    AND cpf != ''
UNION ALL
SELECT 'Formato core.clientes' as fonte,
    MIN(cpf) as exemplo_min,
    MAX(cpf) as exemplo_max,
    AVG(LENGTH(cpf)) as tamanho_medio
FROM core.clientes
WHERE cpf IS NOT NULL
    AND cpf != '';