-- ============================================================================
-- 64_NORMALIZAR_COMO_CONHECEU.sql
-- Normalização dos valores brutos de como_conheceu
-- Mapeia valores do CSV para canais padronizados
-- ============================================================================
-- ============================================================================
-- ETAPA 1: VERIFICAR DADOS BRUTOS
-- ============================================================================
DO $$ BEGIN RAISE NOTICE '';
RAISE NOTICE '=== ANALISANDO DADOS BRUTOS ===';
END $$;
-- Contagem total de registros
SELECT COUNT(*) as total_registros,
    COUNT(DISTINCT cpf) as clientes_distintos,
    COUNT(*) FILTER (
        WHERE como_conheceu_raw IS NOT NULL
            AND como_conheceu_raw != ''
    ) as com_origem,
    COUNT(*) FILTER (
        WHERE como_conheceu_raw IS NULL
            OR como_conheceu_raw = ''
    ) as sem_origem
FROM staging.marketing_origens_vixen;
-- Distribuição por loja
SELECT loja,
    COUNT(*) as total,
    COUNT(*) FILTER (
        WHERE como_conheceu_raw IS NOT NULL
            AND como_conheceu_raw != ''
    ) as com_origem
FROM staging.marketing_origens_vixen
GROUP BY loja
ORDER BY loja;
-- Top 20 valores brutos mais comuns
SELECT como_conheceu_raw,
    COUNT(*) as quantidade,
    ROUND(
        COUNT(*) * 100.0 / (
            SELECT COUNT(*)
            FROM staging.marketing_origens_vixen
        ),
        2
    ) as percentual
FROM staging.marketing_origens_vixen
WHERE como_conheceu_raw IS NOT NULL
    AND como_conheceu_raw != ''
GROUP BY como_conheceu_raw
ORDER BY quantidade DESC
LIMIT 20;
-- ============================================================================
-- ETAPA 2: CRIAR FUNÇÃO DE NORMALIZAÇÃO
-- ============================================================================
CREATE OR REPLACE FUNCTION marketing.normalizar_como_conheceu(texto_bruto TEXT) RETURNS VARCHAR(50) LANGUAGE plpgsql IMMUTABLE AS $$
DECLARE texto_limpo TEXT;
BEGIN -- Retornar NULL se entrada for nula ou vazia
IF texto_bruto IS NULL
OR TRIM(texto_bruto) = '' THEN RETURN 'NAO_INFORMADO';
END IF;
-- Limpar e normalizar texto
texto_limpo := UPPER(TRIM(texto_bruto));
-- Remover prefixos numéricos (ex: "04 CLIENTES" -> "CLIENTES")
texto_limpo := REGEXP_REPLACE(texto_limpo, '^[0-9]+\s*-?\s*', '');
-- Mapeamento para códigos normalizados
CASE
    -- Clientes existentes
    WHEN texto_limpo LIKE '%CLIENTE%' THEN RETURN 'CLIENTES_EXISTENTES';
-- Orçamento
WHEN texto_limpo LIKE '%ORCAMENTO%'
OR texto_limpo LIKE '%ORÇAMENTO%' THEN RETURN 'ORCAMENTO';
-- Indicações
WHEN texto_limpo LIKE '%INDICAC%'
OR texto_limpo LIKE '%INDIC%' THEN RETURN 'INDICACAO';
WHEN texto_limpo LIKE '%AMIGO%' THEN RETURN 'AMIGO_INDICACAO';
-- Programa Saúde dos Olhos
WHEN texto_limpo LIKE '%SAUDE%OLHO%' THEN RETURN 'SAUDE_OLHOS';
-- Abordagem
WHEN texto_limpo LIKE '%ABORDAGEM%' THEN RETURN 'ABORDAGEM';
-- Telemarketing
WHEN texto_limpo LIKE '%TELEMARKETING%'
OR texto_limpo LIKE '%TELE%MARKETING%' THEN RETURN 'TELEMARKETING';
-- Divulgador
WHEN texto_limpo LIKE '%DIVULGADOR%' THEN RETURN 'DIVULGADOR';
-- Redes Sociais
WHEN texto_limpo LIKE '%REDE%SOCIAL%'
OR texto_limpo LIKE '%REDES%SOCIA%' THEN RETURN 'REDES_SOCIAIS';
WHEN texto_limpo LIKE '%FACEBOOK%'
OR texto_limpo LIKE '%INSTAGRAM%' THEN RETURN 'REDES_SOCIAIS';
-- WhatsApp
WHEN texto_limpo LIKE '%WHATSAPP%'
OR texto_limpo LIKE '%WHATS%'
OR texto_limpo LIKE '%ZAP%' THEN RETURN 'WHATSAPP';
-- Cartão
WHEN texto_limpo LIKE '%CARTAO%'
OR texto_limpo LIKE '%CARTÃO%' THEN RETURN 'CARTAO';
-- Google/Internet
WHEN texto_limpo LIKE '%GOOGLE%'
OR texto_limpo LIKE '%INTERNET%'
OR texto_limpo LIKE '%BUSCA%' THEN RETURN 'GOOGLE';
-- Valores específicos
WHEN texto_limpo IN ('NAO', 'NÃO', 'SIM') THEN RETURN 'NAO_INFORMADO';
-- Outros
ELSE RETURN 'OUTROS';
END CASE
;
END;
$$;
-- Comentário
COMMENT ON FUNCTION marketing.normalizar_como_conheceu IS 'Normaliza valores brutos de como_conheceu para códigos padronizados';
-- ============================================================================
-- ETAPA 3: TESTAR FUNÇÃO DE NORMALIZAÇÃO
-- ============================================================================
DO $$ BEGIN RAISE NOTICE '';
RAISE NOTICE '=== TESTANDO NORMALIZAÇÃO ===';
END $$;
SELECT como_conheceu_raw as valor_original,
    marketing.normalizar_como_conheceu(como_conheceu_raw) as valor_normalizado,
    COUNT(*) as quantidade
FROM staging.marketing_origens_vixen
GROUP BY como_conheceu_raw
ORDER BY quantidade DESC
LIMIT 20;
-- ============================================================================
-- ETAPA 4: APLICAR NORMALIZAÇÃO E MAPEAR IDs DOS CANAIS
-- ============================================================================
DO $$ BEGIN RAISE NOTICE '';
RAISE NOTICE '=== APLICANDO NORMALIZAÇÃO ===';
END $$;
-- Atualizar campo canal_normalizado_id
UPDATE staging.marketing_origens_vixen mkt
SET canal_normalizado_id = c.id,
    processado = true
FROM marketing.canais_aquisicao c
WHERE c.codigo = marketing.normalizar_como_conheceu(mkt.como_conheceu_raw)
    AND mkt.processado = false;
-- ============================================================================
-- ETAPA 5: VERIFICAR RESULTADO DA NORMALIZAÇÃO
-- ============================================================================
DO $$ BEGIN RAISE NOTICE '';
RAISE NOTICE '=== RESULTADO DA NORMALIZAÇÃO ===';
END $$;
-- Estatísticas gerais
SELECT COUNT(*) as total_registros,
    COUNT(*) FILTER (
        WHERE processado = true
    ) as processados,
    COUNT(*) FILTER (
        WHERE processado = false
    ) as nao_processados,
    COUNT(*) FILTER (
        WHERE canal_normalizado_id IS NOT NULL
    ) as com_canal_mapeado,
    ROUND(
        COUNT(*) FILTER (
            WHERE canal_normalizado_id IS NOT NULL
        ) * 100.0 / COUNT(*),
        2
    ) as percentual_mapeado
FROM staging.marketing_origens_vixen;
-- Distribuição por canal normalizado
SELECT c.codigo,
    c.nome,
    c.categoria,
    COUNT(*) as quantidade,
    ROUND(
        COUNT(*) * 100.0 / (
            SELECT COUNT(*)
            FROM staging.marketing_origens_vixen
        ),
        2
    ) as percentual
FROM staging.marketing_origens_vixen mkt
    JOIN marketing.canais_aquisicao c ON c.id = mkt.canal_normalizado_id
GROUP BY c.id,
    c.codigo,
    c.nome,
    c.categoria
ORDER BY quantidade DESC;
-- Registros não mapeados (se houver)
SELECT como_conheceu_raw,
    COUNT(*) as quantidade
FROM staging.marketing_origens_vixen
WHERE canal_normalizado_id IS NULL
GROUP BY como_conheceu_raw
ORDER BY quantidade DESC;
DO $$
DECLARE total_registros INTEGER;
registros_mapeados INTEGER;
percentual NUMERIC;
BEGIN
SELECT COUNT(*),
    COUNT(*) FILTER (
        WHERE canal_normalizado_id IS NOT NULL
    ) INTO total_registros,
    registros_mapeados
FROM staging.marketing_origens_vixen;
percentual := ROUND(registros_mapeados * 100.0 / total_registros, 2);
RAISE NOTICE '';
RAISE NOTICE '============================================================';
RAISE NOTICE 'RESUMO DA NORMALIZAÇÃO';
RAISE NOTICE '============================================================';
RAISE NOTICE 'Total de registros: %',
total_registros;
RAISE NOTICE 'Registros mapeados: % (% %%)',
registros_mapeados,
percentual;
RAISE NOTICE '';
RAISE NOTICE '✓ Normalização concluída';
RAISE NOTICE '';
RAISE NOTICE 'Próximo passo: Criar tabela marketing.clientes_origem';
RAISE NOTICE '============================================================';
END $$;