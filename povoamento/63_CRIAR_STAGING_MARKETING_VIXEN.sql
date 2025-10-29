-- ============================================================================
-- 63_CRIAR_STAGING_MARKETING_VIXEN.sql
-- Tabela staging para importar dados de vendas_os_completo.csv
-- Contém campo como_conheceu bruto para posterior normalização
-- ============================================================================
-- ============================================================================
-- TABELA STAGING: marketing_origens_vixen
-- Armazena dados brutos do arquivo CSV antes da normalização
-- ============================================================================
DROP TABLE IF EXISTS staging.marketing_origens_vixen CASCADE;
CREATE TABLE staging.marketing_origens_vixen (
    id SERIAL PRIMARY KEY,
    -- Identificadores da OS original
    os_n VARCHAR(50),
    -- Número da OS no sistema vixen
    loja VARCHAR(10),
    -- Código da loja (042, 048)
    -- Dados do cliente
    nome VARCHAR(200),
    cpf VARCHAR(11),
    -- CPF limpo, somente números
    -- Origem/Marketing
    como_conheceu_codigo VARCHAR(10),
    -- Código extraído (ex: "04", "15", "138")
    como_conheceu_raw VARCHAR(200),
    -- Valor bruto do CSV
    -- Datas
    data_de_compra TIMESTAMP,
    prev_de_entr TIMESTAMP,
    -- Dados adicionais
    consultor VARCHAR(100),
    venda VARCHAR(50),
    total NUMERIC(10, 2),
    -- Metadados
    origem VARCHAR(50) DEFAULT 'VIXEN_CSV',
    importado_em TIMESTAMP DEFAULT NOW(),
    processado BOOLEAN DEFAULT false,
    -- Campos de controle para normalização
    canal_normalizado_id INTEGER,
    -- FK para marketing.canais_aquisicao (após normalização)
    observacoes TEXT
);
-- Índices para performance
CREATE INDEX idx_mkt_vixen_cpf ON staging.marketing_origens_vixen(cpf);
CREATE INDEX idx_mkt_vixen_os_n ON staging.marketing_origens_vixen(os_n);
CREATE INDEX idx_mkt_vixen_loja ON staging.marketing_origens_vixen(loja);
CREATE INDEX idx_mkt_vixen_processado ON staging.marketing_origens_vixen(processado);
CREATE INDEX idx_mkt_vixen_como_conheceu ON staging.marketing_origens_vixen(como_conheceu_raw);
CREATE INDEX idx_mkt_vixen_como_conheceu_cod ON staging.marketing_origens_vixen(como_conheceu_codigo);
-- Comentários
COMMENT ON TABLE staging.marketing_origens_vixen IS 'Staging table para dados de origem de clientes do arquivo vendas_os_completo.csv';
COMMENT ON COLUMN staging.marketing_origens_vixen.como_conheceu_codigo IS 'Código numérico extraído do campo como_conheceu (ex: 04, 15, 138)';
COMMENT ON COLUMN staging.marketing_origens_vixen.como_conheceu_raw IS 'Valor original do campo como_conheceu do CSV (com códigos numéricos)';
COMMENT ON COLUMN staging.marketing_origens_vixen.canal_normalizado_id IS 'ID do canal após normalização (FK para marketing.canais_aquisicao)';
COMMENT ON COLUMN staging.marketing_origens_vixen.processado IS 'Flag indicando se o registro já foi processado e normalizado';
DO $$ BEGIN RAISE NOTICE '';
RAISE NOTICE '✓ Tabela staging.marketing_origens_vixen criada';
RAISE NOTICE '';
RAISE NOTICE '============================================================';
RAISE NOTICE 'PRÓXIMO PASSO: IMPORTAR CSV';
RAISE NOTICE '============================================================';
RAISE NOTICE '';
RAISE NOTICE 'Use o seguinte comando para importar via DBeaver/pgAdmin:';
RAISE NOTICE '';
RAISE NOTICE 'COPY staging.marketing_origens_vixen (';
RAISE NOTICE '    os_n, loja, data_de_compra, consultor, venda,';
RAISE NOTICE '    nome, cpf, como_conheceu_raw, prev_de_entr, total';
RAISE NOTICE ') FROM ''d:/projetos/carne_facil/povoamento/dados/csv/vendas_os_completo.csv''';
RAISE NOTICE 'DELIMITER '',''';
RAISE NOTICE 'CSV HEADER';
RAISE NOTICE 'ENCODING ''UTF8'';';
RAISE NOTICE '';
RAISE NOTICE 'OU use a interface gráfica do DBeaver para importar o CSV.';
RAISE NOTICE '';
RAISE NOTICE '============================================================';
END $$;