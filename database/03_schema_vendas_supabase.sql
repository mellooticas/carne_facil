-- ============================================================================
-- BANCO DE DADOS - SISTEMA ÓTICAS (SUPABASE)
-- Script 03: Schema VENDAS - Transações Comerciais
-- ============================================================================
-- IMPORTANTE: Execute APÓS o script 02_schema_core_supabase.sql
-- ============================================================================

-- ============================================================================
-- TABELA: vendas.vendas
-- Descrição: Vendas realizadas (fonte: todos_os_caixas.xlsx - aba 'vend')
-- Dados reais: 7.547 vendas | R$ 6.032.727,49
-- ============================================================================

CREATE TABLE IF NOT EXISTS vendas.vendas (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero_venda VARCHAR(50) NOT NULL,  -- Nº Venda do sistema
    
    -- Relacionamentos
    cliente_id UUID REFERENCES core.clientes(id) ON DELETE SET NULL,
    loja_id UUID NOT NULL REFERENCES core.lojas(id) ON DELETE RESTRICT,
    vendedor_id UUID REFERENCES core.vendedores(id) ON DELETE SET NULL,
    
    -- Dados da Venda
    data_venda DATE NOT NULL,
    valor_total DECIMAL(12,2) NOT NULL CHECK (valor_total >= 0),
    valor_entrada DECIMAL(12,2) DEFAULT 0 CHECK (valor_entrada >= 0),
    valor_restante DECIMAL(12,2) GENERATED ALWAYS AS (valor_total - valor_entrada) STORED,
    
    -- Informações Adicionais
    nome_cliente_temp VARCHAR(200),  -- Nome informado na venda (pode não estar cadastrado)
    observacoes TEXT,
    
    -- Status
    status status_type DEFAULT 'ATIVO',
    cancelado BOOLEAN DEFAULT false,
    data_cancelamento TIMESTAMP,
    motivo_cancelamento TEXT,
    
    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP NULL,
    version INT DEFAULT 1,
    
    -- Constraints
    CONSTRAINT chk_vendas_entrada_menor_total CHECK (valor_entrada <= valor_total),
    CONSTRAINT uq_vendas_loja_numero UNIQUE(loja_id, numero_venda)
);

-- Índices
CREATE INDEX idx_vendas_cliente_id ON vendas.vendas(cliente_id);
CREATE INDEX idx_vendas_loja_id ON vendas.vendas(loja_id);
CREATE INDEX idx_vendas_vendedor_id ON vendas.vendas(vendedor_id);
CREATE INDEX idx_vendas_data_venda ON vendas.vendas(data_venda);
CREATE INDEX idx_vendas_numero ON vendas.vendas(numero_venda);
CREATE INDEX idx_vendas_status ON vendas.vendas(status);
CREATE INDEX idx_vendas_cancelado ON vendas.vendas(cancelado) WHERE cancelado = false;
CREATE INDEX idx_vendas_deleted_at ON vendas.vendas(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_vendas_valor_total ON vendas.vendas(valor_total);
CREATE INDEX idx_vendas_data_venda_loja ON vendas.vendas(data_venda, loja_id);

-- Trigger
CREATE TRIGGER trigger_vendas_updated_at
    BEFORE UPDATE ON vendas.vendas
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_updated_at();

COMMENT ON TABLE vendas.vendas IS 'Vendas realizadas (7.547 registros | R$ 6.032.727,49)';
COMMENT ON COLUMN vendas.vendas.numero_venda IS 'Número da venda no sistema legado';
COMMENT ON COLUMN vendas.vendas.nome_cliente_temp IS 'Nome informado no momento da venda';
COMMENT ON COLUMN vendas.vendas.valor_entrada IS 'Valor pago na entrada';
COMMENT ON COLUMN vendas.vendas.valor_restante IS 'Valor restante a pagar (calculado)';

-- ============================================================================
-- TABELA: vendas.formas_pagamento_venda
-- Descrição: Formas de pagamento utilizadas em cada venda (N:M)
-- ============================================================================

CREATE TABLE IF NOT EXISTS vendas.formas_pagamento_venda (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    venda_id UUID NOT NULL REFERENCES vendas.vendas(id) ON DELETE CASCADE,
    
    -- Dados do Pagamento
    forma_pagamento forma_pagamento_type NOT NULL,
    valor DECIMAL(12,2) NOT NULL CHECK (valor > 0),
    parcelas INTEGER DEFAULT 1 CHECK (parcelas > 0),
    
    -- Detalhes específicos
    numero_autorizacao VARCHAR(50),  -- Para cartão
    numero_cheque VARCHAR(50),        -- Para cheque
    banco VARCHAR(100),                -- Para cheque/transferência
    
    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Índices
CREATE INDEX idx_formas_pagamento_venda_id ON vendas.formas_pagamento_venda(venda_id);
CREATE INDEX idx_formas_pagamento_forma ON vendas.formas_pagamento_venda(forma_pagamento);
CREATE INDEX idx_formas_pagamento_deleted_at ON vendas.formas_pagamento_venda(deleted_at) WHERE deleted_at IS NULL;

COMMENT ON TABLE vendas.formas_pagamento_venda IS 'Formas de pagamento por venda (relação N:M)';
COMMENT ON COLUMN vendas.formas_pagamento_venda.parcelas IS 'Quantidade de parcelas (se parcelado)';

-- ============================================================================
-- TABELA: vendas.recebimentos_carne
-- Descrição: Recebimentos de carnê (fonte: aba 'rec_carn')
-- Dados reais: 3.108 recebimentos | R$ 379.671,97
-- ============================================================================

CREATE TABLE IF NOT EXISTS vendas.recebimentos_carne (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Relacionamentos
    venda_id UUID REFERENCES vendas.vendas(id) ON DELETE SET NULL,
    loja_id UUID NOT NULL REFERENCES core.lojas(id) ON DELETE RESTRICT,
    
    -- Dados do Recebimento
    os_numero VARCHAR(50),  -- Número da OS associada
    numero_parcela INTEGER NOT NULL CHECK (numero_parcela > 0),
    data_recebimento DATE NOT NULL,
    valor_parcela DECIMAL(12,2) NOT NULL CHECK (valor_parcela > 0),
    
    -- Forma de Pagamento
    forma_pagamento forma_pagamento_type,
    
    -- Informações Adicionais
    nome_cliente_temp VARCHAR(200),
    observacoes TEXT,
    
    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Índices
CREATE INDEX idx_recebimentos_venda_id ON vendas.recebimentos_carne(venda_id);
CREATE INDEX idx_recebimentos_loja_id ON vendas.recebimentos_carne(loja_id);
CREATE INDEX idx_recebimentos_os_numero ON vendas.recebimentos_carne(os_numero);
CREATE INDEX idx_recebimentos_data ON vendas.recebimentos_carne(data_recebimento);
CREATE INDEX idx_recebimentos_parcela ON vendas.recebimentos_carne(numero_parcela);
CREATE INDEX idx_recebimentos_deleted_at ON vendas.recebimentos_carne(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_recebimentos_data_loja ON vendas.recebimentos_carne(data_recebimento, loja_id);

-- Trigger
CREATE TRIGGER trigger_recebimentos_updated_at
    BEFORE UPDATE ON vendas.recebimentos_carne
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_updated_at();

COMMENT ON TABLE vendas.recebimentos_carne IS 'Recebimentos de carnê (3.108 registros | R$ 379.671,97)';
COMMENT ON COLUMN vendas.recebimentos_carne.numero_parcela IS 'Número da parcela recebida';

-- ============================================================================
-- TABELA: vendas.entregas_carne
-- Descrição: Entregas de carnê (fonte: aba 'entr_carn')
-- Dados reais: 678 entregas | R$ 411.087,49
-- ============================================================================

CREATE TABLE IF NOT EXISTS vendas.entregas_carne (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Relacionamentos
    venda_id UUID REFERENCES vendas.vendas(id) ON DELETE SET NULL,
    loja_id UUID NOT NULL REFERENCES core.lojas(id) ON DELETE RESTRICT,
    
    -- Dados da Entrega
    os_numero VARCHAR(50),
    parcela VARCHAR(50),  -- Pode ser texto (ex: "1/12", "primeira")
    data_entrega DATE NOT NULL,
    valor_total DECIMAL(12,2) NOT NULL CHECK (valor_total > 0),
    
    -- Informações Adicionais
    observacoes TEXT,
    
    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Índices
CREATE INDEX idx_entregas_carne_venda_id ON vendas.entregas_carne(venda_id);
CREATE INDEX idx_entregas_carne_loja_id ON vendas.entregas_carne(loja_id);
CREATE INDEX idx_entregas_carne_os_numero ON vendas.entregas_carne(os_numero);
CREATE INDEX idx_entregas_carne_data ON vendas.entregas_carne(data_entrega);
CREATE INDEX idx_entregas_carne_deleted_at ON vendas.entregas_carne(deleted_at) WHERE deleted_at IS NULL;

-- Trigger
CREATE TRIGGER trigger_entregas_carne_updated_at
    BEFORE UPDATE ON vendas.entregas_carne
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_updated_at();

COMMENT ON TABLE vendas.entregas_carne IS 'Entregas de carnê (678 registros | R$ 411.087,49)';

-- ============================================================================
-- TABELA: vendas.restantes_entrada
-- Descrição: Valores restantes de entrada (fonte: aba 'rest_entr')
-- Dados reais: 2.868 registros | R$ 929.201,55
-- ============================================================================

CREATE TABLE IF NOT EXISTS vendas.restantes_entrada (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Relacionamentos
    venda_id UUID REFERENCES vendas.vendas(id) ON DELETE SET NULL,
    loja_id UUID NOT NULL REFERENCES core.lojas(id) ON DELETE RESTRICT,
    
    -- Dados
    numero_venda VARCHAR(50),
    data_registro DATE NOT NULL,
    valor_venda DECIMAL(12,2) NOT NULL CHECK (valor_venda >= 0),
    valor_entrada DECIMAL(12,2) NOT NULL CHECK (valor_entrada >= 0),
    valor_restante DECIMAL(12,2) GENERATED ALWAYS AS (valor_venda - valor_entrada) STORED,
    
    -- Forma de Pagamento
    forma_pagamento forma_pagamento_type,
    
    -- Informações Adicionais
    nome_cliente_temp VARCHAR(200),
    observacoes TEXT,
    
    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Índices
CREATE INDEX idx_restantes_venda_id ON vendas.restantes_entrada(venda_id);
CREATE INDEX idx_restantes_loja_id ON vendas.restantes_entrada(loja_id);
CREATE INDEX idx_restantes_numero_venda ON vendas.restantes_entrada(numero_venda);
CREATE INDEX idx_restantes_data ON vendas.restantes_entrada(data_registro);
CREATE INDEX idx_restantes_deleted_at ON vendas.restantes_entrada(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_restantes_valor_restante ON vendas.restantes_entrada(valor_restante) WHERE valor_restante > 0;

-- Trigger
CREATE TRIGGER trigger_restantes_updated_at
    BEFORE UPDATE ON vendas.restantes_entrada
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_updated_at();

COMMENT ON TABLE vendas.restantes_entrada IS 'Valores restantes de entrada (2.868 registros | R$ 929.201,55)';
COMMENT ON COLUMN vendas.restantes_entrada.valor_restante IS 'Saldo a receber (calculado)';

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

ALTER TABLE vendas.vendas ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendas.formas_pagamento_venda ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendas.recebimentos_carne ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendas.entregas_carne ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendas.restantes_entrada ENABLE ROW LEVEL SECURITY;

-- Políticas: Autenticados podem ler e inserir vendas
CREATE POLICY "Permitir leitura de vendas para autenticados"
ON vendas.vendas FOR SELECT
TO authenticated
USING (deleted_at IS NULL AND cancelado = false);

CREATE POLICY "Permitir inserção de vendas para autenticados"
ON vendas.vendas FOR INSERT
TO authenticated
WITH CHECK (true);

CREATE POLICY "Permitir atualização de vendas para autenticados"
ON vendas.vendas FOR UPDATE
TO authenticated
USING (deleted_at IS NULL)
WITH CHECK (deleted_at IS NULL);

-- Políticas para formas de pagamento
CREATE POLICY "Acesso a formas de pagamento para autenticados"
ON vendas.formas_pagamento_venda FOR ALL
TO authenticated
USING (deleted_at IS NULL)
WITH CHECK (deleted_at IS NULL);

-- Políticas para recebimentos
CREATE POLICY "Acesso a recebimentos para autenticados"
ON vendas.recebimentos_carne FOR ALL
TO authenticated
USING (deleted_at IS NULL)
WITH CHECK (deleted_at IS NULL);

-- Políticas para entregas
CREATE POLICY "Acesso a entregas para autenticados"
ON vendas.entregas_carne FOR ALL
TO authenticated
USING (deleted_at IS NULL)
WITH CHECK (deleted_at IS NULL);

-- Políticas para restantes
CREATE POLICY "Acesso a restantes para autenticados"
ON vendas.restantes_entrada FOR ALL
TO authenticated
USING (deleted_at IS NULL)
WITH CHECK (deleted_at IS NULL);

-- ============================================================================
-- GRANTS
-- ============================================================================

GRANT SELECT, INSERT, UPDATE ON vendas.vendas TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON vendas.formas_pagamento_venda TO authenticated;
GRANT SELECT, INSERT, UPDATE ON vendas.recebimentos_carne TO authenticated;
GRANT SELECT, INSERT, UPDATE ON vendas.entregas_carne TO authenticated;
GRANT SELECT, INSERT, UPDATE ON vendas.restantes_entrada TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA vendas TO authenticated;

-- ============================================================================
-- VIEWS ÚTEIS
-- ============================================================================

-- View: Vendas com código completo (JOIN com loja)
CREATE OR REPLACE VIEW vendas.v_vendas_completo AS
SELECT 
    v.id,
    v.numero_venda,
    'VENDA-' || l.codigo || '-' || v.numero_venda as codigo_completo,
    v.cliente_id,
    c.nome as cliente_nome,
    v.loja_id,
    l.codigo as loja_codigo,
    l.nome as loja_nome,
    v.vendedor_id,
    vd.nome as vendedor_nome,
    v.data_venda,
    v.valor_total,
    v.valor_entrada,
    v.valor_restante,
    v.status,
    v.cancelado,
    v.created_at
FROM vendas.vendas v
LEFT JOIN core.lojas l ON l.id = v.loja_id
LEFT JOIN core.clientes c ON c.id = v.cliente_id
LEFT JOIN core.vendedores vd ON vd.id = v.vendedor_id
WHERE v.deleted_at IS NULL;

GRANT SELECT ON vendas.v_vendas_completo TO authenticated, anon;

COMMENT ON VIEW vendas.v_vendas_completo IS 'Vendas com código completo e JOINs';

-- View: Resumo de vendas por loja
CREATE OR REPLACE VIEW vendas.v_resumo_vendas_loja AS
SELECT 
    l.codigo as loja_codigo,
    l.nome as loja_nome,
    COUNT(v.id) as total_vendas,
    SUM(v.valor_total) as valor_total,
    SUM(v.valor_entrada) as total_entradas,
    SUM(v.valor_restante) as total_restante,
    AVG(v.valor_total) as ticket_medio,
    DATE_TRUNC('month', v.data_venda) as mes_ano
FROM vendas.vendas v
JOIN core.lojas l ON l.id = v.loja_id
WHERE v.deleted_at IS NULL AND v.cancelado = false
GROUP BY l.codigo, l.nome, DATE_TRUNC('month', v.data_venda)
ORDER BY mes_ano DESC, total_vendas DESC;

GRANT SELECT ON vendas.v_resumo_vendas_loja TO authenticated, anon;

-- View: Resumo de recebimentos por loja
CREATE OR REPLACE VIEW vendas.v_resumo_recebimentos_loja AS
SELECT 
    l.codigo as loja_codigo,
    l.nome as loja_nome,
    COUNT(r.id) as total_recebimentos,
    SUM(r.valor_parcela) as valor_total_recebido,
    DATE_TRUNC('month', r.data_recebimento) as mes_ano
FROM vendas.recebimentos_carne r
JOIN core.lojas l ON l.id = r.loja_id
WHERE r.deleted_at IS NULL
GROUP BY l.codigo, l.nome, DATE_TRUNC('month', r.data_recebimento)
ORDER BY mes_ano DESC, valor_total_recebido DESC;

GRANT SELECT ON vendas.v_resumo_recebimentos_loja TO authenticated, anon;

-- View: Saldo a receber (restantes com valor > 0)
CREATE OR REPLACE VIEW vendas.v_saldo_a_receber AS
SELECT 
    l.codigo as loja_codigo,
    l.nome as loja_nome,
    COUNT(r.id) as quantidade,
    SUM(r.valor_restante) as saldo_total,
    AVG(r.valor_restante) as saldo_medio,
    MIN(r.data_registro) as data_mais_antiga,
    MAX(r.data_registro) as data_mais_recente
FROM vendas.restantes_entrada r
JOIN core.lojas l ON l.id = r.loja_id
WHERE r.deleted_at IS NULL AND r.valor_restante > 0
GROUP BY l.codigo, l.nome
ORDER BY saldo_total DESC;

GRANT SELECT ON vendas.v_saldo_a_receber TO authenticated, anon;

-- ============================================================================
-- FUNCTION: Calcular total de vendas por período
-- ============================================================================

CREATE OR REPLACE FUNCTION vendas.calcular_total_vendas_periodo(
    data_inicio DATE,
    data_fim DATE,
    p_loja_id UUID DEFAULT NULL
)
RETURNS TABLE (
    loja_codigo VARCHAR,
    total_vendas BIGINT,
    valor_total NUMERIC,
    valor_entrada NUMERIC,
    valor_restante NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        l.codigo,
        COUNT(v.id)::BIGINT,
        COALESCE(SUM(v.valor_total), 0),
        COALESCE(SUM(v.valor_entrada), 0),
        COALESCE(SUM(v.valor_restante), 0)
    FROM vendas.vendas v
    JOIN core.lojas l ON l.id = v.loja_id
    WHERE v.data_venda BETWEEN data_inicio AND data_fim
      AND v.deleted_at IS NULL
      AND v.cancelado = false
      AND (p_loja_id IS NULL OR v.loja_id = p_loja_id)
    GROUP BY l.codigo;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION vendas.calcular_total_vendas_periodo(DATE, DATE, UUID) TO authenticated;

COMMENT ON FUNCTION vendas.calcular_total_vendas_periodo IS 'Calcula totais de vendas por período e loja';

-- ============================================================================
-- FIM DO SCRIPT 03
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Script 03 executado com sucesso!';
    RAISE NOTICE '📊 Tabelas criadas:';
    RAISE NOTICE '   - vendas.vendas (7.547 registros esperados)';
    RAISE NOTICE '   - vendas.formas_pagamento_venda';
    RAISE NOTICE '   - vendas.recebimentos_carne (3.108 registros esperados)';
    RAISE NOTICE '   - vendas.entregas_carne (678 registros esperados)';
    RAISE NOTICE '   - vendas.restantes_entrada (2.868 registros esperados)';
    RAISE NOTICE '🔐 Row Level Security habilitado';
    RAISE NOTICE '👁️ 3 Views criadas';
    RAISE NOTICE '⚙️ 1 Function criada';
    RAISE NOTICE '💰 Total esperado: R$ 7.752.688,50';
    RAISE NOTICE '🚀 Próximo: Execute 04_schema_optica_supabase.sql';
END $$;
