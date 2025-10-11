-- ============================================================================
-- BANCO DE DADOS - SISTEMA ÓTICAS (SUPABASE)
-- Script 06: Schema AUDITORIA - Logs e Histórico
-- ============================================================================
-- IMPORTANTE: Execute APÓS o script 05_schema_marketing_supabase.sql
-- ============================================================================

-- ============================================================================
-- TABELA: auditoria.log_alteracoes
-- Descrição: Log completo de todas as alterações (INSERT/UPDATE/DELETE)
-- ============================================================================

CREATE TABLE IF NOT EXISTS auditoria.log_alteracoes (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Origem
    schema_nome VARCHAR(100) NOT NULL,
    tabela_nome VARCHAR(100) NOT NULL,
    registro_id UUID,  -- ID do registro alterado
    
    -- Operação
    operacao VARCHAR(10) NOT NULL CHECK (operacao IN ('INSERT', 'UPDATE', 'DELETE')),
    
    -- Dados
    dados_antigos JSONB,  -- Registro ANTES da alteração
    dados_novos JSONB,    -- Registro APÓS a alteração
    campos_alterados TEXT[],  -- Array com nomes dos campos alterados
    
    -- Usuário
    usuario_id UUID,  -- Referência para auth.users
    usuario_nome VARCHAR(200),
    usuario_email VARCHAR(200),
    usuario_role VARCHAR(50),
    
    -- Contexto
    ip_address VARCHAR(50),
    user_agent TEXT,
    origem VARCHAR(100),  -- 'WEB', 'MOBILE', 'API', 'SISTEMA'
    
    -- Timestamp
    data_alteracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Observações
    observacoes TEXT,
    
    -- Índice para performance
    data_particao DATE GENERATED ALWAYS AS (data_alteracao::DATE) STORED
);

-- Índices
CREATE INDEX idx_log_schema_tabela ON auditoria.log_alteracoes(schema_nome, tabela_nome);
CREATE INDEX idx_log_registro_id ON auditoria.log_alteracoes(registro_id);
CREATE INDEX idx_log_operacao ON auditoria.log_alteracoes(operacao);
CREATE INDEX idx_log_usuario_id ON auditoria.log_alteracoes(usuario_id);
CREATE INDEX idx_log_data_alteracao ON auditoria.log_alteracoes(data_alteracao);
CREATE INDEX idx_log_data_particao ON auditoria.log_alteracoes(data_particao);
CREATE INDEX idx_log_dados_novos ON auditoria.log_alteracoes USING GIN(dados_novos);
CREATE INDEX idx_log_dados_antigos ON auditoria.log_alteracoes USING GIN(dados_antigos);

COMMENT ON TABLE auditoria.log_alteracoes IS 'Log completo de INSERT/UPDATE/DELETE em todas as tabelas';
COMMENT ON COLUMN auditoria.log_alteracoes.dados_antigos IS 'JSON com dados ANTES da alteração';
COMMENT ON COLUMN auditoria.log_alteracoes.dados_novos IS 'JSON com dados APÓS a alteração';

-- ============================================================================
-- TABELA: auditoria.historico_valores
-- Descrição: Histórico de alterações de valores (preços, descontos, etc)
-- ============================================================================

CREATE TABLE IF NOT EXISTS auditoria.historico_valores (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Origem
    entidade_tipo VARCHAR(100) NOT NULL,  -- 'VENDA', 'OS', 'PRODUTO', etc
    entidade_id UUID NOT NULL,
    campo_nome VARCHAR(100) NOT NULL,
    
    -- Valores
    valor_anterior DECIMAL(12,2),
    valor_novo DECIMAL(12,2),
    diferenca DECIMAL(12,2) GENERATED ALWAYS AS (valor_novo - valor_anterior) STORED,
    percentual_variacao DECIMAL(10,2) GENERATED ALWAYS AS (
        CASE WHEN valor_anterior > 0 
        THEN ROUND(((valor_novo - valor_anterior) / valor_anterior) * 100, 2)
        ELSE NULL END
    ) STORED,
    
    -- Motivo
    motivo VARCHAR(200),
    tipo_ajuste VARCHAR(100) CHECK (tipo_ajuste IN (
        'DESCONTO', 'ACRESCIMO', 'CORRECAO', 'PROMOCAO',
        'AJUSTE_MANUAL', 'REAJUSTE', 'ERRO', 'OUTROS'
    )),
    
    -- Autorização
    autorizado_por VARCHAR(200),
    requer_aprovacao BOOLEAN DEFAULT false,
    aprovado BOOLEAN,
    aprovado_por VARCHAR(200),
    data_aprovacao TIMESTAMP,
    
    -- Usuário
    usuario_id UUID,
    usuario_nome VARCHAR(200),
    
    -- Timestamp
    data_alteracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Observações
    observacoes TEXT
);

-- Índices
CREATE INDEX idx_historico_valores_entidade ON auditoria.historico_valores(entidade_tipo, entidade_id);
CREATE INDEX idx_historico_valores_campo ON auditoria.historico_valores(campo_nome);
CREATE INDEX idx_historico_valores_tipo_ajuste ON auditoria.historico_valores(tipo_ajuste);
CREATE INDEX idx_historico_valores_data ON auditoria.historico_valores(data_alteracao);
CREATE INDEX idx_historico_valores_usuario_id ON auditoria.historico_valores(usuario_id);
CREATE INDEX idx_historico_valores_aprovacao ON auditoria.historico_valores(requer_aprovacao, aprovado);

COMMENT ON TABLE auditoria.historico_valores IS 'Histórico de alterações de valores monetários';
COMMENT ON COLUMN auditoria.historico_valores.diferenca IS 'Diferença entre valor novo e anterior';
COMMENT ON COLUMN auditoria.historico_valores.percentual_variacao IS 'Percentual de variação';

-- ============================================================================
-- TABELA: auditoria.snapshots_diarios
-- Descrição: Snapshots diários para backup e análise temporal
-- ============================================================================

CREATE TABLE IF NOT EXISTS auditoria.snapshots_diarios (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    data_snapshot DATE NOT NULL DEFAULT CURRENT_DATE,
    tipo_snapshot VARCHAR(100) NOT NULL,
    
    -- Dados Agregados
    total_clientes INTEGER,
    total_vendas INTEGER,
    total_os INTEGER,
    total_leads INTEGER,
    
    -- Valores
    valor_total_vendas DECIMAL(12,2),
    valor_total_recebido DECIMAL(12,2),
    valor_a_receber DECIMAL(12,2),
    
    -- Por Loja (JSONB para flexibilidade)
    dados_por_loja JSONB,
    
    -- Métricas de Vendas
    ticket_medio DECIMAL(12,2),
    os_abertas INTEGER,
    os_entregues INTEGER,
    taxa_conversao_leads DECIMAL(5,2),
    
    -- Métricas de Marketing
    total_comunicacoes_enviadas INTEGER,
    taxa_abertura_media DECIMAL(5,2),
    nps_medio DECIMAL(5,2),
    
    -- Snapshot Completo (opcional - para backup)
    snapshot_completo JSONB,  -- JSON com dados detalhados
    
    -- Processamento
    data_processamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tempo_processamento_segundos INTEGER,
    
    -- Observações
    observacoes TEXT,
    
    -- Constraint: Um snapshot por dia por tipo
    CONSTRAINT uq_snapshot_data_tipo UNIQUE(data_snapshot, tipo_snapshot)
);

-- Índices
CREATE INDEX idx_snapshots_data ON auditoria.snapshots_diarios(data_snapshot);
CREATE INDEX idx_snapshots_tipo ON auditoria.snapshots_diarios(tipo_snapshot);
CREATE INDEX idx_snapshots_dados_loja ON auditoria.snapshots_diarios USING GIN(dados_por_loja);
CREATE INDEX idx_snapshots_snapshot_completo ON auditoria.snapshots_diarios USING GIN(snapshot_completo);

COMMENT ON TABLE auditoria.snapshots_diarios IS 'Snapshots diários para backup e análise temporal';
COMMENT ON COLUMN auditoria.snapshots_diarios.dados_por_loja IS 'Dados agregados por loja em JSON';

-- ============================================================================
-- TABELA: auditoria.acesso_usuarios
-- Descrição: Log de acessos e ações dos usuários no sistema
-- ============================================================================

CREATE TABLE IF NOT EXISTS auditoria.acesso_usuarios (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Usuário
    usuario_id UUID,
    usuario_email VARCHAR(200),
    usuario_nome VARCHAR(200),
    usuario_role VARCHAR(50),
    
    -- Acesso
    tipo_acesso VARCHAR(50) CHECK (tipo_acesso IN (
        'LOGIN', 'LOGOUT', 'LOGIN_FAILED', 'SESSION_EXPIRED',
        'PASSWORD_RESET', 'PASSWORD_CHANGE', 'ACCOUNT_LOCKED'
    )),
    
    -- Ação
    acao VARCHAR(200),  -- 'Visualizou relatório', 'Editou venda', etc
    modulo VARCHAR(100), -- 'VENDAS', 'CLIENTES', 'OS', 'RELATORIOS'
    recurso VARCHAR(200), -- Recurso específico acessado
    
    -- Contexto
    ip_address VARCHAR(50),
    user_agent TEXT,
    dispositivo VARCHAR(100),
    navegador VARCHAR(100),
    sistema_operacional VARCHAR(100),
    
    -- Localização
    cidade VARCHAR(100),
    estado VARCHAR(50),
    pais VARCHAR(50),
    
    -- Sucesso/Falha
    sucesso BOOLEAN DEFAULT true,
    codigo_erro VARCHAR(50),
    mensagem_erro TEXT,
    
    -- Tempo
    data_acesso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duracao_sessao_segundos INTEGER,
    
    -- Sessão
    session_id VARCHAR(200),
    
    -- Observações
    observacoes TEXT,
    
    -- Índice para performance
    data_particao DATE GENERATED ALWAYS AS (data_acesso::DATE) STORED
);

-- Índices
CREATE INDEX idx_acesso_usuario_id ON auditoria.acesso_usuarios(usuario_id);
CREATE INDEX idx_acesso_tipo ON auditoria.acesso_usuarios(tipo_acesso);
CREATE INDEX idx_acesso_data ON auditoria.acesso_usuarios(data_acesso);
CREATE INDEX idx_acesso_data_particao ON auditoria.acesso_usuarios(data_particao);
CREATE INDEX idx_acesso_sucesso ON auditoria.acesso_usuarios(sucesso) WHERE sucesso = false;
CREATE INDEX idx_acesso_ip ON auditoria.acesso_usuarios(ip_address);
CREATE INDEX idx_acesso_session ON auditoria.acesso_usuarios(session_id);
CREATE INDEX idx_acesso_modulo ON auditoria.acesso_usuarios(modulo);

COMMENT ON TABLE auditoria.acesso_usuarios IS 'Log de acessos e ações dos usuários';
COMMENT ON COLUMN auditoria.acesso_usuarios.data_particao IS 'Data para particionamento';

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

ALTER TABLE auditoria.log_alteracoes ENABLE ROW LEVEL SECURITY;
ALTER TABLE auditoria.historico_valores ENABLE ROW LEVEL SECURITY;
ALTER TABLE auditoria.snapshots_diarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE auditoria.acesso_usuarios ENABLE ROW LEVEL SECURITY;

-- Políticas: Apenas leitura para autenticados
CREATE POLICY "Permitir leitura de logs para autenticados"
ON auditoria.log_alteracoes FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Permitir leitura de histórico para autenticados"
ON auditoria.historico_valores FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Permitir leitura de snapshots para autenticados"
ON auditoria.snapshots_diarios FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Permitir leitura de acessos para autenticados"
ON auditoria.acesso_usuarios FOR SELECT
TO authenticated
USING (true);

-- Políticas de INSERT (sistema pode inserir)
CREATE POLICY "Sistema pode inserir logs"
ON auditoria.log_alteracoes FOR INSERT
TO authenticated
WITH CHECK (true);

CREATE POLICY "Sistema pode inserir histórico"
ON auditoria.historico_valores FOR INSERT
TO authenticated
WITH CHECK (true);

CREATE POLICY "Sistema pode inserir snapshots"
ON auditoria.snapshots_diarios FOR INSERT
TO authenticated
WITH CHECK (true);

CREATE POLICY "Sistema pode inserir acessos"
ON auditoria.acesso_usuarios FOR INSERT
TO authenticated
WITH CHECK (true);

-- ============================================================================
-- GRANTS
-- ============================================================================

GRANT SELECT ON auditoria.log_alteracoes TO authenticated;
GRANT SELECT ON auditoria.historico_valores TO authenticated;
GRANT SELECT ON auditoria.snapshots_diarios TO authenticated;
GRANT SELECT ON auditoria.acesso_usuarios TO authenticated;

GRANT INSERT ON auditoria.log_alteracoes TO authenticated;
GRANT INSERT ON auditoria.historico_valores TO authenticated;
GRANT INSERT ON auditoria.snapshots_diarios TO authenticated;
GRANT INSERT ON auditoria.acesso_usuarios TO authenticated;

GRANT USAGE ON ALL SEQUENCES IN SCHEMA auditoria TO authenticated;

-- ============================================================================
-- VIEWS ÚTEIS
-- ============================================================================

-- View: Últimas Alterações (últimas 1000)
CREATE OR REPLACE VIEW auditoria.v_ultimas_alteracoes AS
SELECT 
    id,
    schema_nome || '.' || tabela_nome as tabela_completa,
    operacao,
    registro_id,
    usuario_nome,
    usuario_email,
    data_alteracao,
    campos_alterados,
    ip_address,
    origem
FROM auditoria.log_alteracoes
ORDER BY data_alteracao DESC
LIMIT 1000;

GRANT SELECT ON auditoria.v_ultimas_alteracoes TO authenticated, anon;

-- View: Alterações por Usuário
CREATE OR REPLACE VIEW auditoria.v_alteracoes_por_usuario AS
SELECT 
    usuario_nome,
    usuario_email,
    COUNT(*) as total_alteracoes,
    COUNT(CASE WHEN operacao = 'INSERT' THEN 1 END) as total_inserts,
    COUNT(CASE WHEN operacao = 'UPDATE' THEN 1 END) as total_updates,
    COUNT(CASE WHEN operacao = 'DELETE' THEN 1 END) as total_deletes,
    MAX(data_alteracao) as ultima_alteracao
FROM auditoria.log_alteracoes
WHERE data_alteracao >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY usuario_nome, usuario_email
ORDER BY total_alteracoes DESC;

GRANT SELECT ON auditoria.v_alteracoes_por_usuario TO authenticated, anon;

-- View: Histórico de Ajustes de Valores Recentes
CREATE OR REPLACE VIEW auditoria.v_ajustes_valores_recentes AS
SELECT 
    entidade_tipo,
    entidade_id,
    campo_nome,
    valor_anterior,
    valor_novo,
    diferenca,
    percentual_variacao,
    tipo_ajuste,
    motivo,
    usuario_nome,
    data_alteracao
FROM auditoria.historico_valores
WHERE data_alteracao >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY ABS(diferenca) DESC
LIMIT 100;

GRANT SELECT ON auditoria.v_ajustes_valores_recentes TO authenticated, anon;

-- View: Tentativas de Login Falhadas
CREATE OR REPLACE VIEW auditoria.v_login_falhados AS
SELECT 
    usuario_email,
    ip_address,
    COUNT(*) as tentativas,
    MAX(data_acesso) as ultima_tentativa,
    array_agg(DISTINCT mensagem_erro) as erros
FROM auditoria.acesso_usuarios
WHERE tipo_acesso = 'LOGIN_FAILED'
  AND data_acesso >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY usuario_email, ip_address
HAVING COUNT(*) >= 3
ORDER BY tentativas DESC, ultima_tentativa DESC;

GRANT SELECT ON auditoria.v_login_falhados TO authenticated;

-- View: Resumo de Snapshots
CREATE OR REPLACE VIEW auditoria.v_resumo_snapshots AS
SELECT 
    data_snapshot,
    tipo_snapshot,
    total_clientes,
    total_vendas,
    total_os,
    valor_total_vendas,
    valor_a_receber,
    ticket_medio,
    nps_medio,
    data_processamento
FROM auditoria.snapshots_diarios
ORDER BY data_snapshot DESC, tipo_snapshot
LIMIT 90;  -- Últimos 90 dias

GRANT SELECT ON auditoria.v_resumo_snapshots TO authenticated, anon;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function: Registrar Log de Alteração (genérica)
CREATE OR REPLACE FUNCTION auditoria.registrar_log(
    p_schema VARCHAR,
    p_tabela VARCHAR,
    p_registro_id UUID,
    p_operacao VARCHAR,
    p_dados_antigos JSONB,
    p_dados_novos JSONB,
    p_observacoes TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_log_id UUID;
    v_campos_alterados TEXT[];
BEGIN
    -- Identificar campos alterados (se UPDATE)
    IF p_operacao = 'UPDATE' AND p_dados_antigos IS NOT NULL AND p_dados_novos IS NOT NULL THEN
        SELECT array_agg(key)
        INTO v_campos_alterados
        FROM jsonb_each(p_dados_novos)
        WHERE p_dados_antigos->key IS DISTINCT FROM p_dados_novos->key;
    END IF;
    
    -- Inserir log
    INSERT INTO auditoria.log_alteracoes (
        schema_nome,
        tabela_nome,
        registro_id,
        operacao,
        dados_antigos,
        dados_novos,
        campos_alterados,
        usuario_id,
        observacoes
    ) VALUES (
        p_schema,
        p_tabela,
        p_registro_id,
        p_operacao,
        p_dados_antigos,
        p_dados_novos,
        v_campos_alterados,
        auth.uid(),
        p_observacoes
    ) RETURNING id INTO v_log_id;
    
    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION auditoria.registrar_log TO authenticated;

COMMENT ON FUNCTION auditoria.registrar_log IS 'Registra log de alteração em qualquer tabela';

-- Function: Gerar Snapshot Diário
CREATE OR REPLACE FUNCTION auditoria.gerar_snapshot_diario(
    p_data_snapshot DATE DEFAULT CURRENT_DATE
)
RETURNS UUID AS $$
DECLARE
    v_snapshot_id UUID;
    v_tempo_inicio TIMESTAMP;
    v_total_clientes INTEGER;
    v_total_vendas INTEGER;
    v_total_os INTEGER;
    v_valor_vendas DECIMAL(12,2);
BEGIN
    v_tempo_inicio := CURRENT_TIMESTAMP;
    
    -- Contar registros
    SELECT COUNT(*) INTO v_total_clientes FROM core.clientes WHERE deleted_at IS NULL;
    SELECT COUNT(*) INTO v_total_vendas FROM vendas.vendas WHERE deleted_at IS NULL AND cancelado = false;
    SELECT COUNT(*) INTO v_total_os FROM optica.ordens_servico WHERE deleted_at IS NULL AND cancelada = false;
    
    -- Calcular valores
    SELECT COALESCE(SUM(valor_total), 0) 
    INTO v_valor_vendas 
    FROM vendas.vendas 
    WHERE deleted_at IS NULL 
      AND cancelado = false 
      AND data_venda = p_data_snapshot;
    
    -- Inserir snapshot
    INSERT INTO auditoria.snapshots_diarios (
        data_snapshot,
        tipo_snapshot,
        total_clientes,
        total_vendas,
        total_os,
        valor_total_vendas,
        tempo_processamento_segundos
    ) VALUES (
        p_data_snapshot,
        'DIARIO_COMPLETO',
        v_total_clientes,
        v_total_vendas,
        v_total_os,
        v_valor_vendas,
        EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - v_tempo_inicio))::INTEGER
    )
    ON CONFLICT (data_snapshot, tipo_snapshot) DO UPDATE SET
        total_clientes = EXCLUDED.total_clientes,
        total_vendas = EXCLUDED.total_vendas,
        total_os = EXCLUDED.total_os,
        valor_total_vendas = EXCLUDED.valor_total_vendas,
        data_processamento = CURRENT_TIMESTAMP,
        tempo_processamento_segundos = EXCLUDED.tempo_processamento_segundos
    RETURNING id INTO v_snapshot_id;
    
    RETURN v_snapshot_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION auditoria.gerar_snapshot_diario(DATE) TO authenticated;

COMMENT ON FUNCTION auditoria.gerar_snapshot_diario IS 'Gera snapshot diário do sistema';

-- Function: Buscar Histórico de Registro
CREATE OR REPLACE FUNCTION auditoria.buscar_historico_registro(
    p_schema VARCHAR,
    p_tabela VARCHAR,
    p_registro_id UUID
)
RETURNS TABLE (
    data_alteracao TIMESTAMP,
    operacao VARCHAR,
    usuario_nome VARCHAR,
    campos_alterados TEXT[],
    dados_antigos JSONB,
    dados_novos JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        l.data_alteracao,
        l.operacao,
        l.usuario_nome,
        l.campos_alterados,
        l.dados_antigos,
        l.dados_novos
    FROM auditoria.log_alteracoes l
    WHERE l.schema_nome = p_schema
      AND l.tabela_nome = p_tabela
      AND l.registro_id = p_registro_id
    ORDER BY l.data_alteracao DESC;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION auditoria.buscar_historico_registro TO authenticated;

COMMENT ON FUNCTION auditoria.buscar_historico_registro IS 'Busca histórico completo de alterações de um registro';

-- ============================================================================
-- FIM DO SCRIPT 06
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Script 06 executado com sucesso!';
    RAISE NOTICE '📊 Schema AUDITORIA criado:';
    RAISE NOTICE '   - auditoria.log_alteracoes (log completo de mudanças)';
    RAISE NOTICE '   - auditoria.historico_valores (histórico de preços)';
    RAISE NOTICE '   - auditoria.snapshots_diarios (backups diários)';
    RAISE NOTICE '   - auditoria.acesso_usuarios (log de acessos)';
    RAISE NOTICE '🔐 Row Level Security habilitado (somente leitura)';
    RAISE NOTICE '👁️ 5 Views criadas (alterações, ajustes, logins, snapshots)';
    RAISE NOTICE '⚙️ 3 Functions criadas (registrar_log, gerar_snapshot, buscar_historico)';
    RAISE NOTICE '🚀 Próximo: Execute 07_rls_policies_supabase.sql';
END $$;
