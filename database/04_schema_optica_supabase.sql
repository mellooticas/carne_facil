-- ============================================================================
-- BANCO DE DADOS - SISTEMA ÓTICAS (SUPABASE)
-- Script 04: Schema OPTICA - Ordens de Serviço
-- ============================================================================
-- IMPORTANTE: Execute APÓS o script 03_schema_vendas_supabase.sql
-- ============================================================================

-- ============================================================================
-- TABELA: optica.ordens_servico
-- Descrição: Ordens de Serviço (OS) - registro principal
-- Dados reais: 5.974 OS registradas (fonte: aba 'os_entr_dia')
-- ============================================================================

CREATE TABLE IF NOT EXISTS optica.ordens_servico (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero_os VARCHAR(50) NOT NULL,  -- Número da OS no sistema
    
    -- Relacionamentos
    cliente_id UUID REFERENCES core.clientes(id) ON DELETE SET NULL,
    loja_id UUID NOT NULL REFERENCES core.lojas(id) ON DELETE RESTRICT,
    vendedor_id UUID REFERENCES core.vendedores(id) ON DELETE SET NULL,
    venda_id UUID REFERENCES vendas.vendas(id) ON DELETE SET NULL,  -- FK para VENDAS!
    
    -- Dados da OS
    data_abertura DATE NOT NULL,
    data_prevista_entrega DATE,
    data_entrega_real DATE,
    
    -- Status da OS
    status status_os_type DEFAULT 'ABERTA',
    prioridade VARCHAR(20) DEFAULT 'NORMAL' CHECK (prioridade IN ('BAIXA', 'NORMAL', 'ALTA', 'URGENTE')),
    
    -- Dados Clínicos
    medico_responsavel VARCHAR(200),
    crm_medico VARCHAR(50),
    data_receita DATE,
    validade_receita DATE,
    
    -- Tipo de Serviço
    tipo_servico VARCHAR(100) CHECK (tipo_servico IN (
        'ÓCULOS COMPLETO',
        'TROCA DE LENTES',
        'ARMAÇÃO',
        'LENTES DE CONTATO',
        'ÓCULOS DE SOL',
        'MANUTENÇÃO',
        'AJUSTE',
        'OUTROS'
    )),
    
    -- Valores
    valor_total DECIMAL(12,2) NOT NULL CHECK (valor_total >= 0),
    valor_desconto DECIMAL(12,2) DEFAULT 0 CHECK (valor_desconto >= 0),
    valor_final DECIMAL(12,2) GENERATED ALWAYS AS (valor_total - valor_desconto) STORED,
    
    -- Informações Adicionais
    nome_cliente_temp VARCHAR(200),  -- Nome temporário se cliente não cadastrado
    observacoes TEXT,
    observacoes_internas TEXT,  -- Notas internas não visíveis ao cliente
    
    -- Cancelamento
    cancelada BOOLEAN DEFAULT false,
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
    CONSTRAINT uq_os_loja_numero UNIQUE(loja_id, numero_os),
    CONSTRAINT chk_os_data_entrega CHECK (data_entrega_real IS NULL OR data_entrega_real >= data_abertura),
    CONSTRAINT chk_os_desconto_menor_total CHECK (valor_desconto <= valor_total)
);

-- Índices
CREATE INDEX idx_os_cliente_id ON optica.ordens_servico(cliente_id);
CREATE INDEX idx_os_loja_id ON optica.ordens_servico(loja_id);
CREATE INDEX idx_os_vendedor_id ON optica.ordens_servico(vendedor_id);
CREATE INDEX idx_os_venda_id ON optica.ordens_servico(venda_id);
CREATE INDEX idx_os_numero ON optica.ordens_servico(numero_os);
CREATE INDEX idx_os_data_abertura ON optica.ordens_servico(data_abertura);
CREATE INDEX idx_os_data_entrega ON optica.ordens_servico(data_entrega_real);
CREATE INDEX idx_os_status ON optica.ordens_servico(status);
CREATE INDEX idx_os_cancelada ON optica.ordens_servico(cancelada) WHERE cancelada = false;
CREATE INDEX idx_os_deleted_at ON optica.ordens_servico(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_os_tipo_servico ON optica.ordens_servico(tipo_servico);
CREATE INDEX idx_os_prioridade ON optica.ordens_servico(prioridade) WHERE prioridade IN ('ALTA', 'URGENTE');
CREATE INDEX idx_os_data_loja ON optica.ordens_servico(data_abertura, loja_id);

-- Trigger
CREATE TRIGGER trigger_os_updated_at
    BEFORE UPDATE ON optica.ordens_servico
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_updated_at();

COMMENT ON TABLE optica.ordens_servico IS 'Ordens de Serviço (5.974 registros esperados)';
COMMENT ON COLUMN optica.ordens_servico.numero_os IS 'Número da OS no sistema legado';
COMMENT ON COLUMN optica.ordens_servico.venda_id IS 'FK para vendas.vendas - vincula OS à venda';
COMMENT ON COLUMN optica.ordens_servico.valor_final IS 'Valor final após desconto (calculado)';

-- ============================================================================
-- TABELA: optica.dioptrias
-- Descrição: Grau (dioptrias) de cada OS para OD (direito) e OE (esquerdo)
-- ============================================================================

CREATE TABLE IF NOT EXISTS optica.dioptrias (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    os_id UUID NOT NULL REFERENCES optica.ordens_servico(id) ON DELETE CASCADE,
    
    -- Olho Direito (OD)
    od_esferico DECIMAL(5,2),      -- Ex: -2.50, +1.75
    od_cilindrico DECIMAL(5,2),    -- Ex: -0.50, -1.25
    od_eixo INTEGER CHECK (od_eixo BETWEEN 0 AND 180),  -- 0 a 180 graus
    od_adicao DECIMAL(5,2),        -- Para lentes multifocais
    od_dnp DECIMAL(5,2),           -- Distância Naso-Pupilar
    
    -- Olho Esquerdo (OE)
    oe_esferico DECIMAL(5,2),
    oe_cilindrico DECIMAL(5,2),
    oe_eixo INTEGER CHECK (oe_eixo BETWEEN 0 AND 180),
    oe_adicao DECIMAL(5,2),
    oe_dnp DECIMAL(5,2),
    
    -- Distância Pupilar Total
    dp_total DECIMAL(5,2),
    
    -- Altura da Montagem (para progressivas)
    altura_montagem DECIMAL(5,2),
    
    -- Tipo de Lente
    tipo_lente VARCHAR(100) CHECK (tipo_lente IN (
        'VISÃO SIMPLES',
        'BIFOCAL',
        'MULTIFOCAL',
        'PROGRESSIVA',
        'ANTIRREFLEXO',
        'TRANSITIONS',
        'FOTOCROMÁTICA',
        'POLICARBONATO',
        'OUTROS'
    )),
    
    -- Observações
    observacoes TEXT,
    
    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    
    -- Constraint: Pelo menos um olho deve ter dados
    CONSTRAINT chk_dioptrias_dados CHECK (
        od_esferico IS NOT NULL OR oe_esferico IS NOT NULL
    )
);

-- Índices
CREATE INDEX idx_dioptrias_os_id ON optica.dioptrias(os_id);
CREATE INDEX idx_dioptrias_tipo_lente ON optica.dioptrias(tipo_lente);
CREATE INDEX idx_dioptrias_deleted_at ON optica.dioptrias(deleted_at) WHERE deleted_at IS NULL;

-- Trigger
CREATE TRIGGER trigger_dioptrias_updated_at
    BEFORE UPDATE ON optica.dioptrias
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_updated_at();

COMMENT ON TABLE optica.dioptrias IS 'Grau (dioptrias) OD/OE para cada OS';
COMMENT ON COLUMN optica.dioptrias.od_esferico IS 'Grau esférico olho direito';
COMMENT ON COLUMN optica.dioptrias.oe_esferico IS 'Grau esférico olho esquerdo';
COMMENT ON COLUMN optica.dioptrias.dp_total IS 'Distância pupilar total';

-- ============================================================================
-- TABELA: optica.produtos_os
-- Descrição: Produtos vendidos em cada OS (armação, lentes, acessórios)
-- ============================================================================

CREATE TABLE IF NOT EXISTS optica.produtos_os (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    os_id UUID NOT NULL REFERENCES optica.ordens_servico(id) ON DELETE CASCADE,
    
    -- Dados do Produto
    tipo_produto VARCHAR(100) NOT NULL CHECK (tipo_produto IN (
        'ARMAÇÃO',
        'LENTE',
        'LENTE DE CONTATO',
        'ESTOJO',
        'CORDÃO',
        'FLANELA',
        'SPRAY LIMPEZA',
        'ACESSÓRIO',
        'OUTROS'
    )),
    
    -- Detalhes
    descricao VARCHAR(300) NOT NULL,
    marca VARCHAR(100),
    modelo VARCHAR(100),
    codigo_produto VARCHAR(100),
    codigo_barras VARCHAR(50),
    
    -- Especificações (para armações)
    cor VARCHAR(50),
    tamanho VARCHAR(50),  -- Ex: 52-18-140
    material VARCHAR(100), -- Ex: Acetato, Metal, Titanio
    
    -- Fornecedor
    fornecedor VARCHAR(200),
    codigo_fornecedor VARCHAR(100),
    
    -- Valores
    quantidade INTEGER NOT NULL DEFAULT 1 CHECK (quantidade > 0),
    valor_unitario DECIMAL(12,2) NOT NULL CHECK (valor_unitario >= 0),
    valor_desconto DECIMAL(12,2) DEFAULT 0 CHECK (valor_desconto >= 0),
    valor_total DECIMAL(12,2) GENERATED ALWAYS AS (
        (quantidade * valor_unitario) - valor_desconto
    ) STORED,
    
    -- Controle de Estoque
    possui_estoque BOOLEAN DEFAULT true,
    requer_encomenda BOOLEAN DEFAULT false,
    data_encomenda DATE,
    data_prevista_chegada DATE,
    
    -- Observações
    observacoes TEXT,
    
    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Índices
CREATE INDEX idx_produtos_os_os_id ON optica.produtos_os(os_id);
CREATE INDEX idx_produtos_os_tipo ON optica.produtos_os(tipo_produto);
CREATE INDEX idx_produtos_os_marca ON optica.produtos_os(marca);
CREATE INDEX idx_produtos_os_codigo ON optica.produtos_os(codigo_produto);
CREATE INDEX idx_produtos_os_encomenda ON optica.produtos_os(requer_encomenda) WHERE requer_encomenda = true;
CREATE INDEX idx_produtos_os_deleted_at ON optica.produtos_os(deleted_at) WHERE deleted_at IS NULL;

-- Trigger
CREATE TRIGGER trigger_produtos_os_updated_at
    BEFORE UPDATE ON optica.produtos_os
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_updated_at();

COMMENT ON TABLE optica.produtos_os IS 'Produtos vendidos em cada OS (armação, lentes, etc)';
COMMENT ON COLUMN optica.produtos_os.valor_total IS 'Valor total calculado (qtd * unitário - desconto)';

-- ============================================================================
-- TABELA: optica.entregas_os
-- Descrição: Controle de entregas de OS ao cliente
-- ============================================================================

CREATE TABLE IF NOT EXISTS optica.entregas_os (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    os_id UUID NOT NULL REFERENCES optica.ordens_servico(id) ON DELETE CASCADE,
    
    -- Dados da Entrega
    data_entrega TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    entregue_por VARCHAR(200),  -- Nome do vendedor/atendente
    recebido_por VARCHAR(200),  -- Nome de quem recebeu
    
    -- Tipo de Entrega
    tipo_entrega VARCHAR(50) CHECK (tipo_entrega IN (
        'LOJA',
        'DELIVERY',
        'CORREIOS',
        'TRANSPORTADORA',
        'RETIRADA'
    )),
    
    -- Informações de Envio
    endereco_entrega TEXT,
    codigo_rastreio VARCHAR(100),
    transportadora VARCHAR(100),
    valor_frete DECIMAL(12,2) DEFAULT 0 CHECK (valor_frete >= 0),
    
    -- Validação
    assinatura_recebimento TEXT,  -- Base64 da assinatura digital
    documento_recebedor VARCHAR(50), -- CPF/RG de quem recebeu
    foto_comprovante TEXT,  -- URL ou Base64 da foto
    
    -- Status
    entrega_confirmada BOOLEAN DEFAULT false,
    data_confirmacao TIMESTAMP,
    
    -- Garantia
    prazo_garantia_dias INTEGER DEFAULT 90,
    data_vencimento_garantia DATE,  -- Calculada via trigger
    
    -- Observações
    observacoes TEXT,
    avaliacao_cliente INTEGER CHECK (avaliacao_cliente BETWEEN 1 AND 5),
    comentario_cliente TEXT,
    
    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Índices
CREATE INDEX idx_entregas_os_os_id ON optica.entregas_os(os_id);
CREATE INDEX idx_entregas_os_data ON optica.entregas_os(data_entrega);
CREATE INDEX idx_entregas_os_tipo ON optica.entregas_os(tipo_entrega);
CREATE INDEX idx_entregas_os_confirmada ON optica.entregas_os(entrega_confirmada);
CREATE INDEX idx_entregas_os_codigo_rastreio ON optica.entregas_os(codigo_rastreio);
CREATE INDEX idx_entregas_os_deleted_at ON optica.entregas_os(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_entregas_os_avaliacao ON optica.entregas_os(avaliacao_cliente) WHERE avaliacao_cliente IS NOT NULL;

-- Trigger
CREATE TRIGGER trigger_entregas_os_updated_at
    BEFORE UPDATE ON optica.entregas_os
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_updated_at();

-- Trigger: Calcular data de vencimento da garantia
CREATE OR REPLACE FUNCTION optica.calcular_vencimento_garantia()
RETURNS TRIGGER AS $$
BEGIN
    -- Calcular data de vencimento com base no prazo
    IF NEW.prazo_garantia_dias IS NOT NULL THEN
        NEW.data_vencimento_garantia := (NEW.data_entrega + (NEW.prazo_garantia_dias || ' days')::INTERVAL)::DATE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_entregas_os_calcular_garantia
    BEFORE INSERT OR UPDATE ON optica.entregas_os
    FOR EACH ROW
    EXECUTE FUNCTION optica.calcular_vencimento_garantia();

COMMENT ON TABLE optica.entregas_os IS 'Controle de entregas de OS ao cliente';
COMMENT ON COLUMN optica.entregas_os.data_vencimento_garantia IS 'Data de vencimento da garantia (calculada via trigger)';

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

ALTER TABLE optica.ordens_servico ENABLE ROW LEVEL SECURITY;
ALTER TABLE optica.dioptrias ENABLE ROW LEVEL SECURITY;
ALTER TABLE optica.produtos_os ENABLE ROW LEVEL SECURITY;
ALTER TABLE optica.entregas_os ENABLE ROW LEVEL SECURITY;

-- Políticas: Autenticados podem ler e manipular OS
CREATE POLICY "Permitir leitura de OS para autenticados"
ON optica.ordens_servico FOR SELECT
TO authenticated
USING (deleted_at IS NULL AND cancelada = false);

CREATE POLICY "Permitir inserção de OS para autenticados"
ON optica.ordens_servico FOR INSERT
TO authenticated
WITH CHECK (true);

CREATE POLICY "Permitir atualização de OS para autenticados"
ON optica.ordens_servico FOR UPDATE
TO authenticated
USING (deleted_at IS NULL)
WITH CHECK (deleted_at IS NULL);

-- Políticas para dioptrias
CREATE POLICY "Acesso a dioptrias para autenticados"
ON optica.dioptrias FOR ALL
TO authenticated
USING (deleted_at IS NULL)
WITH CHECK (deleted_at IS NULL);

-- Políticas para produtos OS
CREATE POLICY "Acesso a produtos OS para autenticados"
ON optica.produtos_os FOR ALL
TO authenticated
USING (deleted_at IS NULL)
WITH CHECK (deleted_at IS NULL);

-- Políticas para entregas OS
CREATE POLICY "Acesso a entregas OS para autenticados"
ON optica.entregas_os FOR ALL
TO authenticated
USING (deleted_at IS NULL)
WITH CHECK (deleted_at IS NULL);

-- ============================================================================
-- GRANTS
-- ============================================================================

GRANT SELECT, INSERT, UPDATE ON optica.ordens_servico TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON optica.dioptrias TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON optica.produtos_os TO authenticated;
GRANT SELECT, INSERT, UPDATE ON optica.entregas_os TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA optica TO authenticated;

-- ============================================================================
-- VIEWS ÚTEIS
-- ============================================================================

-- View: OS Completas com todos os dados relacionados
CREATE OR REPLACE VIEW optica.v_os_completo AS
SELECT 
    os.id,
    os.numero_os,
    'OS-' || l.codigo || '-' || os.numero_os as codigo_completo,
    os.cliente_id,
    c.nome as cliente_nome,
    c.cpf as cliente_cpf,
    (SELECT t.numero FROM core.telefones t 
     WHERE t.cliente_id = c.id AND t.principal = true AND t.deleted_at IS NULL 
     LIMIT 1) as cliente_telefone,
    os.loja_id,
    l.codigo as loja_codigo,
    l.nome as loja_nome,
    os.vendedor_id,
    v.nome as vendedor_nome,
    os.venda_id,
    os.data_abertura,
    os.data_prevista_entrega,
    os.data_entrega_real,
    os.status,
    os.prioridade,
    os.tipo_servico,
    os.valor_final,
    os.medico_responsavel,
    os.cancelada,
    os.created_at,
    -- Dados de dioptria (se existir)
    d.od_esferico,
    d.od_cilindrico,
    d.od_eixo,
    d.oe_esferico,
    d.oe_cilindrico,
    d.oe_eixo,
    d.tipo_lente,
    -- Status de entrega
    CASE 
        WHEN e.id IS NOT NULL THEN true 
        ELSE false 
    END as foi_entregue,
    e.data_entrega,
    e.avaliacao_cliente
FROM optica.ordens_servico os
LEFT JOIN core.lojas l ON l.id = os.loja_id
LEFT JOIN core.clientes c ON c.id = os.cliente_id
LEFT JOIN core.vendedores v ON v.id = os.vendedor_id
LEFT JOIN optica.dioptrias d ON d.os_id = os.id AND d.deleted_at IS NULL
LEFT JOIN optica.entregas_os e ON e.os_id = os.id AND e.deleted_at IS NULL
WHERE os.deleted_at IS NULL;

GRANT SELECT ON optica.v_os_completo TO authenticated, anon;

COMMENT ON VIEW optica.v_os_completo IS 'OS completas com dados de cliente, loja, dioptrias e entrega';

-- View: OS Pendentes de Entrega
CREATE OR REPLACE VIEW optica.v_os_pendentes AS
SELECT 
    l.codigo as loja_codigo,
    l.nome as loja_nome,
    os.numero_os,
    os.data_abertura,
    os.data_prevista_entrega,
    CURRENT_DATE - os.data_prevista_entrega as dias_atraso,
    os.prioridade,
    os.tipo_servico,
    c.nome as cliente_nome,
    (SELECT t.numero FROM core.telefones t 
     WHERE t.cliente_id = c.id AND t.principal = true AND t.deleted_at IS NULL 
     LIMIT 1) as cliente_telefone,
    os.valor_final,
    os.status
FROM optica.ordens_servico os
JOIN core.lojas l ON l.id = os.loja_id
LEFT JOIN core.clientes c ON c.id = os.cliente_id
WHERE os.deleted_at IS NULL
  AND os.cancelada = false
  AND os.status != 'ENTREGUE'
  AND os.data_entrega_real IS NULL
ORDER BY os.prioridade DESC, os.data_prevista_entrega ASC;

GRANT SELECT ON optica.v_os_pendentes TO authenticated, anon;

-- View: Resumo de OS por Loja
CREATE OR REPLACE VIEW optica.v_resumo_os_loja AS
SELECT 
    l.codigo as loja_codigo,
    l.nome as loja_nome,
    COUNT(os.id) as total_os,
    COUNT(CASE WHEN os.status = 'ABERTA' THEN 1 END) as os_abertas,
    COUNT(CASE WHEN os.status = 'EM_PRODUCAO' THEN 1 END) as os_producao,
    COUNT(CASE WHEN os.status = 'PRONTA' THEN 1 END) as os_prontas,
    COUNT(CASE WHEN os.status = 'ENTREGUE' THEN 1 END) as os_entregues,
    COUNT(CASE WHEN os.cancelada = true THEN 1 END) as os_canceladas,
    SUM(os.valor_final) as valor_total,
    AVG(os.valor_final) as ticket_medio,
    DATE_TRUNC('month', os.data_abertura) as mes_ano
FROM optica.ordens_servico os
JOIN core.lojas l ON l.id = os.loja_id
WHERE os.deleted_at IS NULL
GROUP BY l.codigo, l.nome, DATE_TRUNC('month', os.data_abertura)
ORDER BY mes_ano DESC, total_os DESC;

GRANT SELECT ON optica.v_resumo_os_loja TO authenticated, anon;

-- View: OS com Atraso na Entrega
CREATE OR REPLACE VIEW optica.v_os_atrasadas AS
SELECT 
    l.codigo as loja_codigo,
    os.numero_os,
    c.nome as cliente_nome,
    (SELECT t.numero FROM core.telefones t 
     WHERE t.cliente_id = c.id AND t.principal = true AND t.deleted_at IS NULL 
     LIMIT 1) as cliente_telefone,
    os.data_prevista_entrega,
    CURRENT_DATE - os.data_prevista_entrega as dias_atraso,
    os.prioridade,
    os.status,
    os.valor_final
FROM optica.ordens_servico os
JOIN core.lojas l ON l.id = os.loja_id
LEFT JOIN core.clientes c ON c.id = os.cliente_id
WHERE os.deleted_at IS NULL
  AND os.cancelada = false
  AND os.data_entrega_real IS NULL
  AND os.data_prevista_entrega < CURRENT_DATE
ORDER BY dias_atraso DESC;

GRANT SELECT ON optica.v_os_atrasadas TO authenticated, anon;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function: Calcular prazo médio de entrega por loja
CREATE OR REPLACE FUNCTION optica.calcular_prazo_medio_entrega(
    p_loja_id UUID DEFAULT NULL,
    p_data_inicio DATE DEFAULT NULL,
    p_data_fim DATE DEFAULT NULL
)
RETURNS TABLE (
    loja_codigo VARCHAR,
    total_os_entregues BIGINT,
    prazo_medio_dias NUMERIC,
    prazo_minimo_dias INTEGER,
    prazo_maximo_dias INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        l.codigo,
        COUNT(os.id)::BIGINT,
        AVG(os.data_entrega_real - os.data_abertura)::NUMERIC,
        MIN(os.data_entrega_real - os.data_abertura)::INTEGER,
        MAX(os.data_entrega_real - os.data_abertura)::INTEGER
    FROM optica.ordens_servico os
    JOIN core.lojas l ON l.id = os.loja_id
    WHERE os.deleted_at IS NULL
      AND os.cancelada = false
      AND os.data_entrega_real IS NOT NULL
      AND (p_loja_id IS NULL OR os.loja_id = p_loja_id)
      AND (p_data_inicio IS NULL OR os.data_abertura >= p_data_inicio)
      AND (p_data_fim IS NULL OR os.data_abertura <= p_data_fim)
    GROUP BY l.codigo;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION optica.calcular_prazo_medio_entrega(UUID, DATE, DATE) TO authenticated;

COMMENT ON FUNCTION optica.calcular_prazo_medio_entrega IS 'Calcula prazo médio de entrega de OS por loja';

-- Function: Buscar OS por cliente (CPF ou nome)
CREATE OR REPLACE FUNCTION optica.buscar_os_cliente(
    p_busca VARCHAR
)
RETURNS TABLE (
    os_id UUID,
    numero_os VARCHAR,
    cliente_nome VARCHAR,
    cliente_cpf VARCHAR,
    loja_nome VARCHAR,
    data_abertura DATE,
    status status_os_type,
    valor_final NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        os.id,
        os.numero_os,
        c.nome,
        c.cpf,
        l.nome,
        os.data_abertura,
        os.status,
        os.valor_final
    FROM optica.ordens_servico os
    JOIN core.lojas l ON l.id = os.loja_id
    LEFT JOIN core.clientes c ON c.id = os.cliente_id
    WHERE os.deleted_at IS NULL
      AND os.cancelada = false
      AND (
          c.cpf ILIKE '%' || p_busca || '%'
          OR normalizar_texto(c.nome) ILIKE '%' || normalizar_texto(p_busca) || '%'
          OR normalizar_texto(os.nome_cliente_temp) ILIKE '%' || normalizar_texto(p_busca) || '%'
      )
    ORDER BY os.data_abertura DESC
    LIMIT 50;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION optica.buscar_os_cliente(VARCHAR) TO authenticated;

COMMENT ON FUNCTION optica.buscar_os_cliente IS 'Busca OS por CPF ou nome do cliente';

-- ============================================================================
-- FIM DO SCRIPT 04
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Script 04 executado com sucesso!';
    RAISE NOTICE '📊 Schema OPTICA criado:';
    RAISE NOTICE '   - optica.ordens_servico (5.974 registros esperados)';
    RAISE NOTICE '   - optica.dioptrias (graus OD/OE)';
    RAISE NOTICE '   - optica.produtos_os (armações, lentes, etc)';
    RAISE NOTICE '   - optica.entregas_os (controle de entregas)';
    RAISE NOTICE '🔐 Row Level Security habilitado';
    RAISE NOTICE '👁️ 4 Views criadas (OS completas, pendentes, resumo, atrasadas)';
    RAISE NOTICE '⚙️ 2 Functions criadas (prazo médio, busca cliente)';
    RAISE NOTICE '🔗 FK para vendas.vendas (integração venda-OS)';
    RAISE NOTICE '🚀 Próximo: Execute 05_schema_marketing_supabase.sql';
END $$;
