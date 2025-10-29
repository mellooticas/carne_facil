-- ============================================================================
-- 68B_EXECUTAR_PIPELINE_MARKETING_INTEGRADO.sql
-- Script mestre ATUALIZADO para integração com marketing.cliente_info
-- Executa todos os scripts na ordem correta + integração
-- ============================================================================
DO $$ BEGIN RAISE NOTICE '';
RAISE NOTICE '════════════════════════════════════════════════════════════';
RAISE NOTICE '   PIPELINE COMPLETO - SCHEMA MARKETING';
RAISE NOTICE '   Sistema de Rastreamento de Origem de Clientes';
RAISE NOTICE '   + INTEGRAÇÃO COM marketing.cliente_info';
RAISE NOTICE '════════════════════════════════════════════════════════════';
RAISE NOTICE '';
RAISE NOTICE 'Este pipeline irá:';
RAISE NOTICE '  1. Criar tabelas de canais normalizados';
RAISE NOTICE '  2. Criar tabela staging para dados vixen';
RAISE NOTICE '  3. Normalizar valores de como_conheceu';
RAISE NOTICE '  4. Popular tabela auxiliar de origens';
RAISE NOTICE '  5. INTEGRAR com marketing.cliente_info existente';
RAISE NOTICE '  6. Validar integridade e gerar relatórios';
RAISE NOTICE '';
RAISE NOTICE '════════════════════════════════════════════════════════════';
RAISE NOTICE '';
END $$;
-- ============================================================================
-- PASSO 1: CRIAR TABELA DE CANAIS NORMALIZADOS
-- ============================================================================
\ echo '' \ echo '>>> PASSO 1/6: Criando tabela de canais de aquisição...' \ i 62_CRIAR_TABELA_CANAIS.sql -- ============================================================================
-- PASSO 2: CRIAR TABELA STAGING
-- ============================================================================
\ echo '' \ echo '>>> PASSO 2/6: Criando tabela staging...' \ i 63_CRIAR_STAGING_MARKETING_VIXEN.sql -- ============================================================================
-- PASSO 2.5: IMPORTAR CSV (MANUAL)
-- ============================================================================
\ echo '' \ echo '>>> PASSO 2.5/6: IMPORTAÇÃO DE CSV NECESSÁRIA' \ echo 'ATENÇÃO: Execute a importação do CSV manualmente:' \ echo '' \ echo 'Opção 1 - Via COPY (se tiver permissões):' \ echo "COPY staging.marketing_origens_vixen (os_n, loja, data_de_compra, consultor, venda, nome, cpf, como_conheceu_raw, prev_de_entr, total)" \ echo "FROM 'd:/projetos/carne_facil/povoamento/dados/csv/vendas_os_completo.csv'" \ echo "DELIMITER ',' CSV HEADER ENCODING 'UTF8';" \ echo '' \ echo 'Opção 2 - Via DBeaver/pgAdmin:' \ echo '  1. Clique com botão direito em staging.marketing_origens_vixen' \ echo '  2. Escolha "Import Data"' \ echo '  3. Selecione vendas_os_completo.csv' \ echo '  4. Mapeie as colunas corretamente' \ echo '' \ echo 'Pressione ENTER depois de importar o CSV para continuar...' \ prompt 'Pressione ENTER para continuar' _dummy -- Verificar se CSV foi importado
DO $$
DECLARE total_registros INTEGER;
BEGIN
SELECT COUNT(*) INTO total_registros
FROM staging.marketing_origens_vixen;
IF total_registros = 0 THEN RAISE WARNING 'ATENÇÃO: Nenhum registro encontrado em staging.marketing_origens_vixen';
RAISE WARNING 'Certifique-se de importar o CSV antes de continuar';
RAISE EXCEPTION 'Importação de CSV pendente';
ELSE RAISE NOTICE '✓ CSV importado com sucesso: % registros',
total_registros;
END IF;
END $$;
-- ============================================================================
-- PASSO 3: NORMALIZAR VALORES DE como_conheceu
-- ============================================================================
\ echo '' \ echo '>>> PASSO 3/6: Normalizando valores de como_conheceu...' \ i 64_NORMALIZAR_COMO_CONHECEU.sql -- ============================================================================
-- PASSO 4: INTEGRAR COM marketing.cliente_info
-- ============================================================================
\ echo '' \ echo '>>> PASSO 4/6: Integrando com marketing.cliente_info...' \ i 70_INTEGRAR_COM_CLIENTE_INFO.sql -- ============================================================================
-- PASSO 5: CRIAR VIEWS ANALÍTICAS (OPCIONAL)
-- ============================================================================
\ echo '' \ echo '>>> PASSO 5/6: Criando views analíticas...' \ i 69_CRIAR_VIEWS_MARKETING.sql -- ============================================================================
-- PASSO 6: VALIDAÇÃO E RELATÓRIOS
-- ============================================================================
\ echo '' \ echo '>>> PASSO 6/6: Executando validações...' -- Validações específicas para integração
DO $$ BEGIN RAISE NOTICE '';
RAISE NOTICE '=== VALIDAÇÃO DA INTEGRAÇÃO ===';
END $$;
-- Estatísticas gerais
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
SELECT 'cliente_info integrado com origem' as metrica,
    COUNT(*) as quantidade
FROM marketing.cliente_info ci
    INNER JOIN marketing.clientes_canal_origem co ON co.cliente_id = ci.cliente_id;
-- Top 10 canais
SELECT ca.nome as canal,
    ca.categoria,
    COUNT(*) as total_clientes,
    ROUND(AVG(co.valor_primeira_compra), 2) as ticket_medio
FROM marketing.clientes_canal_origem co
    INNER JOIN marketing.canais_aquisicao ca ON ca.id = co.canal_id
GROUP BY ca.nome,
    ca.categoria
ORDER BY total_clientes DESC
LIMIT 10;
-- Distribuição por loja
SELECT l.nome as loja,
    COUNT(*) as total_origens,
    COUNT(DISTINCT ca.id) as canais_distintos
FROM marketing.clientes_canal_origem co
    INNER JOIN core.clientes c ON c.id = co.cliente_id
    INNER JOIN core.lojas l ON l.id = c.loja_id
    INNER JOIN marketing.canais_aquisicao ca ON ca.id = co.canal_id
GROUP BY l.nome
ORDER BY total_origens DESC;
-- ============================================================================
-- RESUMO FINAL
-- ============================================================================
DO $$
DECLARE total_origens INTEGER;
total_clientes INTEGER;
total_cliente_info INTEGER;
total_integrados INTEGER;
cobertura NUMERIC;
canais_ativos INTEGER;
BEGIN
SELECT COUNT(*) INTO total_origens
FROM marketing.clientes_canal_origem;
SELECT COUNT(*) INTO total_clientes
FROM core.clientes;
SELECT COUNT(*) INTO total_cliente_info
FROM marketing.cliente_info;
SELECT COUNT(*) INTO total_integrados
FROM marketing.cliente_info ci
    INNER JOIN marketing.clientes_canal_origem co ON co.cliente_id = ci.cliente_id;
SELECT COUNT(*) INTO canais_ativos
FROM marketing.canais_aquisicao
WHERE ativo = true;
cobertura := ROUND(
    total_origens * 100.0 / NULLIF(total_clientes, 0),
    2
);
RAISE NOTICE '';
RAISE NOTICE '════════════════════════════════════════════════════════════';
RAISE NOTICE '   PIPELINE CONCLUÍDO COM SUCESSO';
RAISE NOTICE '════════════════════════════════════════════════════════════';
RAISE NOTICE '';
RAISE NOTICE 'RESULTADOS:';
RAISE NOTICE '  ✓ Schema marketing criado/atualizado';
RAISE NOTICE '  ✓ % canais de aquisição cadastrados',
canais_ativos;
RAISE NOTICE '  ✓ % origens de clientes mapeadas',
total_origens;
RAISE NOTICE '  ✓ Cobertura: % %% dos clientes',
cobertura;
RAISE NOTICE '';
RAISE NOTICE 'INTEGRAÇÃO COM cliente_info:';
RAISE NOTICE '  ✓ Registros em marketing.cliente_info: %',
total_cliente_info;
RAISE NOTICE '  ✓ Clientes integrados (origem + info): %',
total_integrados;
RAISE NOTICE '';
RAISE NOTICE 'ESTRUTURA CRIADA:';
RAISE NOTICE '  • marketing.canais_aquisicao (14 canais)';
RAISE NOTICE '  • marketing.clientes_canal_origem (tabela auxiliar)';
RAISE NOTICE '  • marketing.cliente_info (populado/atualizado)';
RAISE NOTICE '  • staging.marketing_origens_vixen';
RAISE NOTICE '  • marketing.v_clientes_origem_integrada (view)';
RAISE NOTICE '  • + 8 views analíticas';
RAISE NOTICE '';
RAISE NOTICE 'PRÓXIMOS PASSOS:';
RAISE NOTICE '  • SELECT * FROM marketing.v_clientes_origem_integrada;';
RAISE NOTICE '  • SELECT * FROM marketing.v_dashboard_executivo;';
RAISE NOTICE '  • Configurar dashboards de BI';
RAISE NOTICE '';
RAISE NOTICE '════════════════════════════════════════════════════════════';
END $$;