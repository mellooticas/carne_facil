-- ============================================================================
-- BANCO DE DADOS - SISTEMA ÓTICAS (SUPABASE)
-- Script 02: Schema CORE - Tabelas Principais
-- ============================================================================
-- IMPORTANTE: Execute APÓS o script 01_inicial_config_supabase.sql
-- ============================================================================

-- ============================================================================
-- TABELA: core.clientes
-- Descrição: Cadastro central de clientes (espinha dorsal do sistema)
-- ============================================================================

CREATE TABLE IF NOT EXISTS core.clientes (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_legado VARCHAR(50) UNIQUE,  -- ID antigo para migração
    
    -- Integração Supabase Auth (opcional - se cliente tiver login)
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    
    -- Dados Pessoais
    nome VARCHAR(200) NOT NULL,
    nome_normalizado VARCHAR(200) GENERATED ALWAYS AS (normalizar_texto(nome)) STORED,
    cpf VARCHAR(14) UNIQUE,
    rg VARCHAR(20),
    data_nascimento DATE,
    sexo CHAR(1) CHECK (sexo IN ('M', 'F', 'O')),
    
    -- Contato
    email VARCHAR(100),
    
    -- Status e Controle
    status status_type DEFAULT 'ATIVO',
    
    -- Auditoria (padrão para todas as tabelas)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP NULL,  -- Soft delete
    version INT DEFAULT 1,       -- Controle de versão otimista
    
    -- Constraints
    CONSTRAINT chk_clientes_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' OR email IS NULL),
    CONSTRAINT chk_clientes_data_nasc CHECK (data_nascimento IS NULL OR data_nascimento <= CURRENT_DATE),
    CONSTRAINT chk_clientes_cpf_valido CHECK (validar_cpf(cpf))
);

-- Índices
CREATE INDEX idx_clientes_nome_normalizado ON core.clientes USING GIN (nome_normalizado gin_trgm_ops);
CREATE INDEX idx_clientes_cpf ON core.clientes(cpf) WHERE cpf IS NOT NULL;
CREATE INDEX idx_clientes_email ON core.clientes(email) WHERE email IS NOT NULL;
CREATE INDEX idx_clientes_id_legado ON core.clientes(id_legado) WHERE id_legado IS NOT NULL;
CREATE INDEX idx_clientes_user_id ON core.clientes(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_clientes_status ON core.clientes(status);
CREATE INDEX idx_clientes_data_nasc ON core.clientes(data_nascimento) WHERE data_nascimento IS NOT NULL;
CREATE INDEX idx_clientes_deleted_at ON core.clientes(deleted_at) WHERE deleted_at IS NULL;

-- Trigger para atualizar updated_at
CREATE TRIGGER trigger_clientes_updated_at
    BEFORE UPDATE ON core.clientes
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_updated_at();

-- Comentários
COMMENT ON TABLE core.clientes IS 'Cadastro central de clientes - espinha dorsal do sistema';
COMMENT ON COLUMN core.clientes.id IS 'UUID único do cliente';
COMMENT ON COLUMN core.clientes.user_id IS 'Referência ao usuário Supabase Auth (se tiver login)';
COMMENT ON COLUMN core.clientes.nome_normalizado IS 'Nome normalizado para busca (sem acentos, lowercase)';
COMMENT ON COLUMN core.clientes.deleted_at IS 'Soft delete - data de exclusão lógica';

-- ============================================================================
-- TABELA: core.telefones
-- Descrição: Telefones dos clientes (1:N)
-- ============================================================================

CREATE TABLE IF NOT EXISTS core.telefones (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cliente_id UUID NOT NULL REFERENCES core.clientes(id) ON DELETE CASCADE,
    
    -- Dados do Telefone
    tipo tipo_telefone_type NOT NULL,
    numero VARCHAR(20) NOT NULL,
    numero_normalizado VARCHAR(20) GENERATED ALWAYS AS (normalizar_telefone(numero)) STORED,
    whatsapp BOOLEAN DEFAULT false,
    principal BOOLEAN DEFAULT false,
    observacao TEXT,
    
    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    
    -- Constraints
    CONSTRAINT chk_telefones_numero_valido CHECK (validar_telefone_br(numero)),
    CONSTRAINT uq_telefones_cliente_numero UNIQUE(cliente_id, numero_normalizado)
);

-- Índices
CREATE INDEX idx_telefones_cliente_id ON core.telefones(cliente_id);
CREATE INDEX idx_telefones_numero_normalizado ON core.telefones(numero_normalizado);
CREATE INDEX idx_telefones_whatsapp ON core.telefones(whatsapp) WHERE whatsapp = true;
CREATE INDEX idx_telefones_deleted_at ON core.telefones(deleted_at) WHERE deleted_at IS NULL;

-- Trigger
CREATE TRIGGER trigger_telefones_updated_at
    BEFORE UPDATE ON core.telefones
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_updated_at();

COMMENT ON TABLE core.telefones IS 'Telefones dos clientes (relação 1:N)';
COMMENT ON COLUMN core.telefones.numero_normalizado IS 'Número sem formatação (apenas dígitos)';
COMMENT ON COLUMN core.telefones.whatsapp IS 'Indica se o número tem WhatsApp';
COMMENT ON COLUMN core.telefones.principal IS 'Indica se é o telefone principal do cliente';

-- ============================================================================
-- TABELA: core.endereco_cliente
-- Descrição: Endereços dos clientes (1:N)
-- ============================================================================

CREATE TABLE IF NOT EXISTS core.endereco_cliente (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cliente_id UUID NOT NULL REFERENCES core.clientes(id) ON DELETE CASCADE,
    
    -- Dados do Endereço
    tipo tipo_endereco_type DEFAULT 'RESIDENCIAL',
    cep VARCHAR(10),
    logradouro VARCHAR(200),
    numero VARCHAR(20),
    complemento VARCHAR(100),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    estado CHAR(2),
    pais VARCHAR(50) DEFAULT 'Brasil',
    principal BOOLEAN DEFAULT false,
    
    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    
    -- Constraints
    CONSTRAINT chk_endereco_estado CHECK (estado ~ '^[A-Z]{2}$' OR estado IS NULL)
);

-- Índices
CREATE INDEX idx_endereco_cliente_id ON core.endereco_cliente(cliente_id);
CREATE INDEX idx_endereco_cep ON core.endereco_cliente(cep) WHERE cep IS NOT NULL;
CREATE INDEX idx_endereco_cidade_estado ON core.endereco_cliente(cidade, estado);
CREATE INDEX idx_endereco_deleted_at ON core.endereco_cliente(deleted_at) WHERE deleted_at IS NULL;

-- Trigger
CREATE TRIGGER trigger_endereco_updated_at
    BEFORE UPDATE ON core.endereco_cliente
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_updated_at();

COMMENT ON TABLE core.endereco_cliente IS 'Endereços dos clientes (relação 1:N)';
COMMENT ON COLUMN core.endereco_cliente.principal IS 'Indica se é o endereço principal do cliente';

-- ============================================================================
-- TABELA: core.lojas
-- Descrição: Cadastro de lojas/filiais
-- ============================================================================

CREATE TABLE IF NOT EXISTS core.lojas (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo VARCHAR(20) UNIQUE NOT NULL,
    
    -- Dados da Loja
    nome VARCHAR(100) NOT NULL,
    nome_fantasia VARCHAR(100),
    cnpj VARCHAR(18),
    
    -- Localização
    cidade VARCHAR(100),
    estado CHAR(2),
    endereco_completo TEXT,
    
    -- Contato
    telefone VARCHAR(20),
    email VARCHAR(100),
    
    -- Status
    ativo BOOLEAN DEFAULT true,
    data_abertura DATE,
    data_fechamento DATE,
    
    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Índices
CREATE INDEX idx_lojas_codigo ON core.lojas(codigo);
CREATE INDEX idx_lojas_ativo ON core.lojas(ativo);
CREATE INDEX idx_lojas_cidade_estado ON core.lojas(cidade, estado);

-- Trigger
CREATE TRIGGER trigger_lojas_updated_at
    BEFORE UPDATE ON core.lojas
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_updated_at();

COMMENT ON TABLE core.lojas IS 'Cadastro de lojas/filiais da rede';
COMMENT ON COLUMN core.lojas.codigo IS 'Código identificador da loja (ex: MAUA, SUZANO)';

-- Inserir lojas iniciais
INSERT INTO core.lojas (codigo, nome, cidade, estado, ativo, data_abertura) VALUES
('MAUA', 'Mauá', 'Mauá', 'SP', true, '2020-01-01'),
('SUZANO', 'Suzano', 'Suzano', 'SP', true, '2020-01-01'),
('SUZANO2', 'Suzano 2', 'Suzano', 'SP', true, '2022-01-01'),
('RIO_PEQUENO', 'Rio Pequeno', 'São Paulo', 'SP', true, '2020-01-01'),
('PERUS', 'Perus', 'São Paulo', 'SP', true, '2021-01-01'),
('SAO_MATEUS', 'São Mateus', 'São Paulo', 'SP', false, '2020-01-01')
ON CONFLICT (codigo) DO NOTHING;

-- ============================================================================
-- TABELA: core.vendedores
-- Descrição: Cadastro de vendedores/consultores
-- ============================================================================

CREATE TABLE IF NOT EXISTS core.vendedores (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_legado VARCHAR(50) UNIQUE,
    
    -- Integração Supabase Auth
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    
    -- Dados Pessoais
    nome VARCHAR(200) NOT NULL,
    nome_normalizado VARCHAR(200) GENERATED ALWAYS AS (normalizar_texto(nome)) STORED,
    cpf VARCHAR(14) UNIQUE,
    
    -- Vínculo
    loja_id UUID REFERENCES core.lojas(id) ON DELETE SET NULL,
    codigo_vendedor VARCHAR(20),
    
    -- Contato
    telefone VARCHAR(20),
    email VARCHAR(100),
    
    -- Status
    ativo BOOLEAN DEFAULT true,
    data_admissao DATE,
    data_demissao DATE,
    
    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Índices
CREATE INDEX idx_vendedores_nome_normalizado ON core.vendedores USING GIN (nome_normalizado gin_trgm_ops);
CREATE INDEX idx_vendedores_loja_id ON core.vendedores(loja_id);
CREATE INDEX idx_vendedores_user_id ON core.vendedores(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_vendedores_ativo ON core.vendedores(ativo);
CREATE INDEX idx_vendedores_codigo ON core.vendedores(codigo_vendedor);

-- Trigger
CREATE TRIGGER trigger_vendedores_updated_at
    BEFORE UPDATE ON core.vendedores
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_updated_at();

COMMENT ON TABLE core.vendedores IS 'Cadastro de vendedores/consultores';
COMMENT ON COLUMN core.vendedores.user_id IS 'Referência ao usuário Supabase Auth';
COMMENT ON COLUMN core.vendedores.codigo_vendedor IS 'Código do vendedor no sistema legado';

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) - SUPABASE
-- ============================================================================

-- Habilitar RLS em todas as tabelas
ALTER TABLE core.clientes ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.telefones ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.endereco_cliente ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.lojas ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.vendedores ENABLE ROW LEVEL SECURITY;

-- POLÍTICAS BÁSICAS (podem ser refinadas depois)

-- core.clientes - Leitura para autenticados
CREATE POLICY "Permitir leitura de clientes para autenticados"
ON core.clientes FOR SELECT
TO authenticated
USING (deleted_at IS NULL);

-- core.clientes - Inserção para autenticados
CREATE POLICY "Permitir inserção de clientes para autenticados"
ON core.clientes FOR INSERT
TO authenticated
WITH CHECK (true);

-- core.clientes - Atualização para autenticados
CREATE POLICY "Permitir atualização de clientes para autenticados"
ON core.clientes FOR UPDATE
TO authenticated
USING (deleted_at IS NULL)
WITH CHECK (deleted_at IS NULL);

-- core.telefones - Acesso completo para autenticados
CREATE POLICY "Permitir acesso a telefones para autenticados"
ON core.telefones FOR ALL
TO authenticated
USING (deleted_at IS NULL)
WITH CHECK (deleted_at IS NULL);

-- core.endereco_cliente - Acesso completo para autenticados
CREATE POLICY "Permitir acesso a endereços para autenticados"
ON core.endereco_cliente FOR ALL
TO authenticated
USING (deleted_at IS NULL)
WITH CHECK (deleted_at IS NULL);

-- core.lojas - Leitura pública (lojas são informação pública)
CREATE POLICY "Permitir leitura de lojas para todos"
ON core.lojas FOR SELECT
TO authenticated, anon
USING (ativo = true AND deleted_at IS NULL);

-- core.vendedores - Leitura para autenticados
CREATE POLICY "Permitir leitura de vendedores para autenticados"
ON core.vendedores FOR SELECT
TO authenticated
USING (ativo = true AND deleted_at IS NULL);

-- ============================================================================
-- GRANTS - Permissões
-- ============================================================================

-- Tabela clientes
GRANT SELECT, INSERT, UPDATE ON core.clientes TO authenticated;
GRANT SELECT ON core.clientes TO anon;

-- Tabela telefones
GRANT SELECT, INSERT, UPDATE, DELETE ON core.telefones TO authenticated;

-- Tabela endereços
GRANT SELECT, INSERT, UPDATE, DELETE ON core.endereco_cliente TO authenticated;

-- Tabela lojas
GRANT SELECT ON core.lojas TO authenticated, anon;
GRANT INSERT, UPDATE ON core.lojas TO authenticated;

-- Tabela vendedores
GRANT SELECT ON core.vendedores TO authenticated;
GRANT INSERT, UPDATE ON core.vendedores TO authenticated;

-- Sequências (para IDs)
GRANT USAGE ON ALL SEQUENCES IN SCHEMA core TO authenticated;

-- ============================================================================
-- VIEW: Clientes com contatos (facilitar queries)
-- ============================================================================

CREATE OR REPLACE VIEW core.v_clientes_completo AS
SELECT 
    c.id,
    c.nome,
    c.cpf,
    c.email,
    c.data_nascimento,
    calcular_idade(c.data_nascimento) as idade,
    c.status,
    c.created_at,
    
    -- Telefone principal
    (SELECT t.numero 
     FROM core.telefones t 
     WHERE t.cliente_id = c.id 
       AND t.deleted_at IS NULL 
       AND t.principal = true 
     LIMIT 1) as telefone_principal,
    
    -- WhatsApp
    (SELECT t.numero 
     FROM core.telefones t 
     WHERE t.cliente_id = c.id 
       AND t.deleted_at IS NULL 
       AND t.whatsapp = true 
     LIMIT 1) as whatsapp,
    
    -- Endereço principal
    (SELECT e.cidade || ' - ' || e.estado 
     FROM core.endereco_cliente e 
     WHERE e.cliente_id = c.id 
       AND e.deleted_at IS NULL 
       AND e.principal = true 
     LIMIT 1) as cidade_estado,
    
    -- Contadores
    (SELECT COUNT(*) FROM core.telefones t WHERE t.cliente_id = c.id AND t.deleted_at IS NULL) as total_telefones,
    (SELECT COUNT(*) FROM core.endereco_cliente e WHERE e.cliente_id = c.id AND e.deleted_at IS NULL) as total_enderecos

FROM core.clientes c
WHERE c.deleted_at IS NULL;

COMMENT ON VIEW core.v_clientes_completo IS 'View com dados completos do cliente (contatos, endereços)';

-- Permitir acesso à view
GRANT SELECT ON core.v_clientes_completo TO authenticated, anon;

-- ============================================================================
-- FIM DO SCRIPT 02
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Script 02 executado com sucesso!';
    RAISE NOTICE '📊 Tabelas criadas:';
    RAISE NOTICE '   - core.clientes (com RLS)';
    RAISE NOTICE '   - core.telefones (com RLS)';
    RAISE NOTICE '   - core.endereco_cliente (com RLS)';
    RAISE NOTICE '   - core.lojas (com RLS) - 6 lojas inseridas';
    RAISE NOTICE '   - core.vendedores (com RLS)';
    RAISE NOTICE '🔐 Row Level Security habilitado';
    RAISE NOTICE '👁️ View criada: core.v_clientes_completo';
    RAISE NOTICE '🚀 Próximo: Execute 03_schema_vendas_supabase.sql';
END $$;
