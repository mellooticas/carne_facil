-- ============================================================================
-- BANCO DE DADOS - SISTEMA ÓTICAS (SUPABASE)
-- Script 05: Schema MARKETING - CRM e Campanhas
-- ============================================================================
-- IMPORTANTE: Execute APÓS o script 04_schema_optica_supabase.sql
-- ============================================================================

-- ============================================================================
-- TABELA: marketing.cliente_info
-- Descrição: Informações de marketing e histórico do cliente
-- ============================================================================

CREATE TABLE IF NOT EXISTS marketing.cliente_info (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cliente_id UUID NOT NULL REFERENCES core.clientes(id) ON DELETE CASCADE,
    
    -- Preferências
    preferencia_comunicacao VARCHAR(50) CHECK (preferencia_comunicacao IN (
        'EMAIL', 'SMS', 'WHATSAPP', 'TELEFONE', 'NAO_PERTURBAR'
    )),
    frequencia_preferida VARCHAR(50) CHECK (frequencia_preferida IN (
        'DIARIA', 'SEMANAL', 'QUINZENAL', 'MENSAL', 'OCASIONAL'
    )),
    
    -- Segmentação
    segmento VARCHAR(100) CHECK (segmento IN (
        'VIP', 'REGULAR', 'OCASIONAL', 'INATIVO', 'NOVO'
    )),
    tags TEXT[],  -- Array de tags para segmentação
    
    -- Estatísticas de Compra
    primeira_compra DATE,
    ultima_compra DATE,
    total_compras INTEGER DEFAULT 0,
    total_gasto DECIMAL(12,2) DEFAULT 0,
    ticket_medio DECIMAL(12,2) DEFAULT 0,
    
    -- Comportamento (calculados via view)
    dias_desde_ultima_compra INTEGER,  -- Calculado via view
    risco_churn BOOLEAN,  -- Calculado via view
    
    -- Indicações
    indicou_clientes INTEGER DEFAULT 0,
    foi_indicado_por UUID REFERENCES core.clientes(id) ON DELETE SET NULL,
    
    -- Satisfação
    nps_score INTEGER CHECK (nps_score BETWEEN 0 AND 10),
    data_ultimo_nps DATE,
    avaliacoes_positivas INTEGER DEFAULT 0,
    avaliacoes_negativas INTEGER DEFAULT 0,
    
    -- Opt-in/Opt-out
    aceita_marketing BOOLEAN DEFAULT true,
    aceita_email BOOLEAN DEFAULT true,
    aceita_sms BOOLEAN DEFAULT true,
    aceita_whatsapp BOOLEAN DEFAULT true,
    data_opt_in TIMESTAMP,
    data_opt_out TIMESTAMP,
    
    -- Observações
    observacoes TEXT,
    
    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    
    -- Constraint: Cliente único
    CONSTRAINT uq_cliente_info_cliente UNIQUE(cliente_id)
);

-- Índices
CREATE INDEX idx_cliente_info_cliente_id ON marketing.cliente_info(cliente_id);
CREATE INDEX idx_cliente_info_segmento ON marketing.cliente_info(segmento);
CREATE INDEX idx_cliente_info_ultima_compra ON marketing.cliente_info(ultima_compra);
CREATE INDEX idx_cliente_info_risco_churn ON marketing.cliente_info(risco_churn) WHERE risco_churn = true;
CREATE INDEX idx_cliente_info_aceita_marketing ON marketing.cliente_info(aceita_marketing) WHERE aceita_marketing = true;
CREATE INDEX idx_cliente_info_tags ON marketing.cliente_info USING GIN(tags);
CREATE INDEX idx_cliente_info_deleted_at ON marketing.cliente_info(deleted_at) WHERE deleted_at IS NULL;

-- Trigger
CREATE TRIGGER trigger_cliente_info_updated_at
    BEFORE UPDATE ON marketing.cliente_info
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_updated_at();

COMMENT ON TABLE marketing.cliente_info IS 'Informações de marketing e perfil do cliente';
COMMENT ON COLUMN marketing.cliente_info.dias_desde_ultima_compra IS 'Dias desde última compra (calculado)';
COMMENT ON COLUMN marketing.cliente_info.risco_churn IS 'Cliente em risco de churn (>365 dias)';

-- ============================================================================
-- TABELA: marketing.campanhas
-- Descrição: Campanhas de marketing
-- ============================================================================

CREATE TABLE IF NOT EXISTS marketing.campanhas (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome VARCHAR(200) NOT NULL,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    
    -- Tipo e Canal
    tipo_campanha VARCHAR(100) CHECK (tipo_campanha IN (
        'EMAIL', 'SMS', 'WHATSAPP', 'PUSH', 'MALA_DIRETA', 
        'REDES_SOCIAIS', 'BANNER', 'OUTDOOR', 'RADIO', 'TV', 'OUTROS'
    )),
    objetivo VARCHAR(100) CHECK (objetivo IN (
        'VENDAS', 'ENGAJAMENTO', 'FIDELIZACAO', 'RECONQUISTA',
        'LANCAMENTO', 'PROMOCAO', 'ANIVERSARIO', 'SAZONALIDADE'
    )),
    
    -- Período
    data_inicio DATE NOT NULL,
    data_fim DATE,
    ativa BOOLEAN DEFAULT true,
    
    -- Segmentação
    segmento_alvo TEXT[],  -- Array: ['VIP', 'REGULAR']
    tags_alvo TEXT[],
    loja_id UUID REFERENCES core.lojas(id) ON DELETE SET NULL,  -- NULL = todas as lojas
    
    -- Conteúdo
    assunto VARCHAR(300),
    mensagem TEXT,
    link_destino VARCHAR(500),
    imagem_url VARCHAR(500),
    
    -- Orçamento
    orcamento DECIMAL(12,2),
    custo_real DECIMAL(12,2) DEFAULT 0,
    
    -- Métricas
    total_enviados INTEGER DEFAULT 0,
    total_entregues INTEGER DEFAULT 0,
    total_abertos INTEGER DEFAULT 0,
    total_cliques INTEGER DEFAULT 0,
    total_conversoes INTEGER DEFAULT 0,
    receita_gerada DECIMAL(12,2) DEFAULT 0,
    
    -- KPIs Calculados
    taxa_entrega DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN total_enviados > 0 
        THEN ROUND((total_entregues::DECIMAL / total_enviados) * 100, 2)
        ELSE 0 END
    ) STORED,
    taxa_abertura DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN total_entregues > 0 
        THEN ROUND((total_abertos::DECIMAL / total_entregues) * 100, 2)
        ELSE 0 END
    ) STORED,
    taxa_clique DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN total_abertos > 0 
        THEN ROUND((total_cliques::DECIMAL / total_abertos) * 100, 2)
        ELSE 0 END
    ) STORED,
    taxa_conversao DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE WHEN total_cliques > 0 
        THEN ROUND((total_conversoes::DECIMAL / total_cliques) * 100, 2)
        ELSE 0 END
    ) STORED,
    roi DECIMAL(10,2) GENERATED ALWAYS AS (
        CASE WHEN custo_real > 0 
        THEN ROUND(((receita_gerada - custo_real) / custo_real) * 100, 2)
        ELSE 0 END
    ) STORED,
    
    -- Responsável
    criada_por VARCHAR(100),
    responsavel VARCHAR(100),
    
    -- Observações
    observacoes TEXT,
    
    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    
    -- Constraints
    CONSTRAINT chk_campanhas_periodo CHECK (data_fim IS NULL OR data_fim >= data_inicio)
);

-- Índices
CREATE INDEX idx_campanhas_codigo ON marketing.campanhas(codigo);
CREATE INDEX idx_campanhas_tipo ON marketing.campanhas(tipo_campanha);
CREATE INDEX idx_campanhas_objetivo ON marketing.campanhas(objetivo);
CREATE INDEX idx_campanhas_ativa ON marketing.campanhas(ativa) WHERE ativa = true;
CREATE INDEX idx_campanhas_periodo ON marketing.campanhas(data_inicio, data_fim);
CREATE INDEX idx_campanhas_loja_id ON marketing.campanhas(loja_id);
CREATE INDEX idx_campanhas_segmento ON marketing.campanhas USING GIN(segmento_alvo);
CREATE INDEX idx_campanhas_deleted_at ON marketing.campanhas(deleted_at) WHERE deleted_at IS NULL;

-- Trigger
CREATE TRIGGER trigger_campanhas_updated_at
    BEFORE UPDATE ON marketing.campanhas
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_updated_at();

COMMENT ON TABLE marketing.campanhas IS 'Campanhas de marketing com métricas';
COMMENT ON COLUMN marketing.campanhas.roi IS 'ROI da campanha (calculado)';

-- ============================================================================
-- TABELA: marketing.comunicacoes
-- Descrição: Histórico de comunicações enviadas aos clientes
-- ============================================================================

CREATE TABLE IF NOT EXISTS marketing.comunicacoes (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campanha_id UUID REFERENCES marketing.campanhas(id) ON DELETE SET NULL,
    cliente_id UUID NOT NULL REFERENCES core.clientes(id) ON DELETE CASCADE,
    
    -- Tipo
    tipo_comunicacao VARCHAR(50) NOT NULL CHECK (tipo_comunicacao IN (
        'EMAIL', 'SMS', 'WHATSAPP', 'PUSH', 'TELEFONE', 'MALA_DIRETA'
    )),
    
    -- Conteúdo
    assunto VARCHAR(300),
    mensagem TEXT NOT NULL,
    destinatario VARCHAR(200) NOT NULL,  -- email ou telefone
    
    -- Status
    status VARCHAR(50) DEFAULT 'PENDENTE' CHECK (status IN (
        'PENDENTE', 'ENVIADO', 'ENTREGUE', 'ABERTO', 'CLICADO',
        'RESPONDIDO', 'FALHA', 'BOUNCE', 'SPAM', 'CANCELADO'
    )),
    
    -- Datas
    data_agendamento TIMESTAMP,
    data_envio TIMESTAMP,
    data_entrega TIMESTAMP,
    data_abertura TIMESTAMP,
    data_clique TIMESTAMP,
    data_resposta TIMESTAMP,
    
    -- Rastreamento
    id_externo VARCHAR(200),  -- ID do provedor (SendGrid, Twilio, etc)
    link_rastreamento VARCHAR(500),
    ip_abertura VARCHAR(50),
    user_agent TEXT,
    
    -- Resultado
    houve_conversao BOOLEAN DEFAULT false,
    valor_conversao DECIMAL(12,2),
    data_conversao TIMESTAMP,
    
    -- Erro/Rejeição
    codigo_erro VARCHAR(50),
    mensagem_erro TEXT,
    motivo_rejeicao VARCHAR(200),
    
    -- Custo
    custo DECIMAL(10,4) DEFAULT 0,  -- Custo unitário do envio
    
    -- Observações
    observacoes TEXT,
    
    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Índices
CREATE INDEX idx_comunicacoes_campanha_id ON marketing.comunicacoes(campanha_id);
CREATE INDEX idx_comunicacoes_cliente_id ON marketing.comunicacoes(cliente_id);
CREATE INDEX idx_comunicacoes_tipo ON marketing.comunicacoes(tipo_comunicacao);
CREATE INDEX idx_comunicacoes_status ON marketing.comunicacoes(status);
CREATE INDEX idx_comunicacoes_data_envio ON marketing.comunicacoes(data_envio);
CREATE INDEX idx_comunicacoes_conversao ON marketing.comunicacoes(houve_conversao) WHERE houve_conversao = true;
CREATE INDEX idx_comunicacoes_id_externo ON marketing.comunicacoes(id_externo);
CREATE INDEX idx_comunicacoes_deleted_at ON marketing.comunicacoes(deleted_at) WHERE deleted_at IS NULL;

-- Trigger
CREATE TRIGGER trigger_comunicacoes_updated_at
    BEFORE UPDATE ON marketing.comunicacoes
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_updated_at();

COMMENT ON TABLE marketing.comunicacoes IS 'Histórico de comunicações com clientes';
COMMENT ON COLUMN marketing.comunicacoes.id_externo IS 'ID do provedor externo (SendGrid, Twilio)';

-- ============================================================================
-- TABELA: marketing.leads
-- Descrição: Potenciais clientes ainda não convertidos
-- ============================================================================

CREATE TABLE IF NOT EXISTS marketing.leads (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Dados Básicos
    nome VARCHAR(200) NOT NULL,
    email VARCHAR(200),
    telefone VARCHAR(20),
    cpf VARCHAR(14),
    
    -- Origem
    origem VARCHAR(100) CHECK (origem IN (
        'SITE', 'LANDING_PAGE', 'REDES_SOCIAIS', 'INDICACAO',
        'EVENTO', 'LOJA_FISICA', 'LIGACAO', 'CHAT', 'OUTROS'
    )),
    campanha_origem_id UUID REFERENCES marketing.campanhas(id) ON DELETE SET NULL,
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100),
    
    -- Status
    status VARCHAR(50) DEFAULT 'NOVO' CHECK (status IN (
        'NOVO', 'CONTATADO', 'QUALIFICADO', 'NEGOCIACAO',
        'CONVERTIDO', 'PERDIDO', 'DESCARTADO'
    )),
    
    -- Interesse
    interesse TEXT,  -- Descrição do interesse
    produto_interesse VARCHAR(200),
    faixa_valor VARCHAR(50),
    
    -- Conversão
    convertido BOOLEAN DEFAULT false,
    cliente_id UUID REFERENCES core.clientes(id) ON DELETE SET NULL,
    data_conversao TIMESTAMP,
    valor_primeira_compra DECIMAL(12,2),
    
    -- Atribuição
    responsavel VARCHAR(100),
    loja_id UUID REFERENCES core.lojas(id) ON DELETE SET NULL,
    
    -- Score
    score INTEGER DEFAULT 0 CHECK (score BETWEEN 0 AND 100),
    temperatura VARCHAR(20) CHECK (temperatura IN ('FRIO', 'MORNO', 'QUENTE')),
    
    -- Follow-up
    ultima_interacao TIMESTAMP,
    proxima_interacao TIMESTAMP,
    tentativas_contato INTEGER DEFAULT 0,
    
    -- Observações
    observacoes TEXT,
    motivo_perda TEXT,
    
    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Índices
CREATE INDEX idx_leads_email ON marketing.leads(email);
CREATE INDEX idx_leads_telefone ON marketing.leads(telefone);
CREATE INDEX idx_leads_cpf ON marketing.leads(cpf);
CREATE INDEX idx_leads_status ON marketing.leads(status);
CREATE INDEX idx_leads_origem ON marketing.leads(origem);
CREATE INDEX idx_leads_convertido ON marketing.leads(convertido);
CREATE INDEX idx_leads_cliente_id ON marketing.leads(cliente_id);
CREATE INDEX idx_leads_temperatura ON marketing.leads(temperatura);
CREATE INDEX idx_leads_score ON marketing.leads(score);
CREATE INDEX idx_leads_proxima_interacao ON marketing.leads(proxima_interacao);
CREATE INDEX idx_leads_deleted_at ON marketing.leads(deleted_at) WHERE deleted_at IS NULL;

-- Trigger
CREATE TRIGGER trigger_leads_updated_at
    BEFORE UPDATE ON marketing.leads
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_updated_at();

COMMENT ON TABLE marketing.leads IS 'Potenciais clientes não convertidos';
COMMENT ON COLUMN marketing.leads.score IS 'Score de qualificação (0-100)';

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

ALTER TABLE marketing.cliente_info ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketing.campanhas ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketing.comunicacoes ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketing.leads ENABLE ROW LEVEL SECURITY;

-- Políticas básicas para autenticados
CREATE POLICY "Acesso a cliente_info para autenticados"
ON marketing.cliente_info FOR ALL
TO authenticated
USING (deleted_at IS NULL)
WITH CHECK (deleted_at IS NULL);

CREATE POLICY "Acesso a campanhas para autenticados"
ON marketing.campanhas FOR ALL
TO authenticated
USING (deleted_at IS NULL)
WITH CHECK (deleted_at IS NULL);

CREATE POLICY "Acesso a comunicacoes para autenticados"
ON marketing.comunicacoes FOR ALL
TO authenticated
USING (deleted_at IS NULL)
WITH CHECK (deleted_at IS NULL);

CREATE POLICY "Acesso a leads para autenticados"
ON marketing.leads FOR ALL
TO authenticated
USING (deleted_at IS NULL)
WITH CHECK (deleted_at IS NULL);

-- ============================================================================
-- GRANTS
-- ============================================================================

GRANT SELECT, INSERT, UPDATE ON marketing.cliente_info TO authenticated;
GRANT SELECT, INSERT, UPDATE ON marketing.campanhas TO authenticated;
GRANT SELECT, INSERT, UPDATE ON marketing.comunicacoes TO authenticated;
GRANT SELECT, INSERT, UPDATE ON marketing.leads TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA marketing TO authenticated;

-- ============================================================================
-- VIEWS ÚTEIS
-- ============================================================================

-- View: Clientes VIP
CREATE OR REPLACE VIEW marketing.v_clientes_vip AS
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
    -- Calcular dinamicamente
    CASE WHEN ci.ultima_compra IS NOT NULL 
        THEN (CURRENT_DATE - ci.ultima_compra)::INTEGER
        ELSE NULL 
    END as dias_desde_ultima_compra,
    CASE WHEN ci.ultima_compra IS NOT NULL AND (CURRENT_DATE - ci.ultima_compra) > 365
        THEN true
        ELSE false
    END as risco_churn,
    ci.nps_score
FROM core.clientes c
JOIN marketing.cliente_info ci ON ci.cliente_id = c.id
WHERE c.deleted_at IS NULL
  AND ci.deleted_at IS NULL
  AND ci.segmento = 'VIP'
ORDER BY ci.total_gasto DESC;

GRANT SELECT ON marketing.v_clientes_vip TO authenticated, anon;

-- View: Clientes em Risco de Churn
CREATE OR REPLACE VIEW marketing.v_clientes_churn AS
SELECT 
    c.id,
    c.nome,
    c.cpf,
    (SELECT t.numero FROM core.telefones t 
     WHERE t.cliente_id = c.id AND t.principal = true AND t.deleted_at IS NULL 
     LIMIT 1) as telefone_principal,
    c.email,
    ci.ultima_compra,
    -- Calcular dinamicamente
    CASE WHEN ci.ultima_compra IS NOT NULL 
        THEN (CURRENT_DATE - ci.ultima_compra)::INTEGER
        ELSE NULL 
    END as dias_desde_ultima_compra,
    ci.total_compras,
    ci.total_gasto,
    ci.segmento
FROM core.clientes c
JOIN marketing.cliente_info ci ON ci.cliente_id = c.id
WHERE c.deleted_at IS NULL
  AND ci.deleted_at IS NULL
  AND ci.ultima_compra IS NOT NULL
  AND (CURRENT_DATE - ci.ultima_compra) > 365
  AND ci.aceita_marketing = true
ORDER BY (CURRENT_DATE - ci.ultima_compra) DESC;

GRANT SELECT ON marketing.v_clientes_churn TO authenticated, anon;

-- View: Performance de Campanhas
CREATE OR REPLACE VIEW marketing.v_performance_campanhas AS
SELECT 
    codigo,
    nome,
    tipo_campanha,
    objetivo,
    data_inicio,
    data_fim,
    ativa,
    total_enviados,
    total_entregues,
    total_abertos,
    total_cliques,
    total_conversoes,
    taxa_entrega,
    taxa_abertura,
    taxa_clique,
    taxa_conversao,
    orcamento,
    custo_real,
    receita_gerada,
    roi
FROM marketing.campanhas
WHERE deleted_at IS NULL
ORDER BY roi DESC, receita_gerada DESC;

GRANT SELECT ON marketing.v_performance_campanhas TO authenticated, anon;

-- View: Leads Quentes
CREATE OR REPLACE VIEW marketing.v_leads_quentes AS
SELECT 
    id,
    nome,
    email,
    telefone,
    origem,
    status,
    temperatura,
    score,
    interesse,
    produto_interesse,
    proxima_interacao,
    responsavel,
    created_at
FROM marketing.leads
WHERE deleted_at IS NULL
  AND convertido = false
  AND temperatura = 'QUENTE'
  AND status NOT IN ('PERDIDO', 'DESCARTADO')
ORDER BY score DESC, proxima_interacao ASC;

GRANT SELECT ON marketing.v_leads_quentes TO authenticated, anon;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function: Atualizar estatísticas do cliente
CREATE OR REPLACE FUNCTION marketing.atualizar_estatisticas_cliente(
    p_cliente_id UUID
)
RETURNS VOID AS $$
DECLARE
    v_primeira_compra DATE;
    v_ultima_compra DATE;
    v_total_compras INTEGER;
    v_total_gasto DECIMAL(12,2);
    v_ticket_medio DECIMAL(12,2);
BEGIN
    -- Buscar estatísticas de vendas
    SELECT 
        MIN(data_venda),
        MAX(data_venda),
        COUNT(*)::INTEGER,
        SUM(valor_total),
        AVG(valor_total)
    INTO 
        v_primeira_compra,
        v_ultima_compra,
        v_total_compras,
        v_total_gasto,
        v_ticket_medio
    FROM vendas.vendas
    WHERE cliente_id = p_cliente_id
      AND deleted_at IS NULL
      AND cancelado = false;
    
    -- Atualizar ou inserir em cliente_info
    INSERT INTO marketing.cliente_info (
        cliente_id,
        primeira_compra,
        ultima_compra,
        total_compras,
        total_gasto,
        ticket_medio
    ) VALUES (
        p_cliente_id,
        v_primeira_compra,
        v_ultima_compra,
        COALESCE(v_total_compras, 0),
        COALESCE(v_total_gasto, 0),
        COALESCE(v_ticket_medio, 0)
    )
    ON CONFLICT (cliente_id) DO UPDATE SET
        primeira_compra = EXCLUDED.primeira_compra,
        ultima_compra = EXCLUDED.ultima_compra,
        total_compras = EXCLUDED.total_compras,
        total_gasto = EXCLUDED.total_gasto,
        ticket_medio = EXCLUDED.ticket_medio,
        updated_at = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION marketing.atualizar_estatisticas_cliente(UUID) TO authenticated;

COMMENT ON FUNCTION marketing.atualizar_estatisticas_cliente IS 'Atualiza estatísticas de compras do cliente';

-- ============================================================================
-- FIM DO SCRIPT 05
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Script 05 executado com sucesso!';
    RAISE NOTICE '📊 Schema MARKETING criado:';
    RAISE NOTICE '   - marketing.cliente_info (perfil e histórico)';
    RAISE NOTICE '   - marketing.campanhas (com métricas e ROI)';
    RAISE NOTICE '   - marketing.comunicacoes (histórico de envios)';
    RAISE NOTICE '   - marketing.leads (funil de vendas)';
    RAISE NOTICE '🔐 Row Level Security habilitado';
    RAISE NOTICE '👁️ 4 Views criadas (VIP, churn, performance, leads quentes)';
    RAISE NOTICE '⚙️ 1 Function criada (atualizar estatísticas)';
    RAISE NOTICE '🚀 Próximo: Execute 06_schema_auditoria_supabase.sql';
END $$;
