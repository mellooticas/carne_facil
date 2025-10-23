-- ============================================================================
-- CRIAÇÃO DAS TABELAS DO SCHEMA CORE
-- Execute ANTES de povoar os dados
-- ============================================================================
-- 1. Criar schema se não existir
CREATE SCHEMA IF NOT EXISTS core;
-- 2. Criar tabela de lojas
CREATE TABLE IF NOT EXISTS core.lojas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(10) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    cidade VARCHAR(100),
    estado VARCHAR(2),
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- 3. Criar tabela de clientes
CREATE TABLE IF NOT EXISTS core.clientes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_legado VARCHAR(50) UNIQUE NOT NULL,
    nome VARCHAR(200) NOT NULL,
    nome_normalizado VARCHAR(200) GENERATED ALWAYS AS (LOWER(nome)) STORED,
    cpf VARCHAR(14) UNIQUE,
    email VARCHAR(100),
    status VARCHAR(20) DEFAULT 'ATIVO',
    created_by VARCHAR(100),
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- 4. Criar tabela de telefones
CREATE TABLE IF NOT EXISTS core.telefones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id UUID NOT NULL REFERENCES core.clientes(id) ON DELETE CASCADE,
    numero VARCHAR(15) NOT NULL,
    tipo VARCHAR(10) CHECK (tipo IN ('CELULAR', 'FIXO')),
    principal BOOLEAN DEFAULT FALSE,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- 5. Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_clientes_id_legado ON core.clientes(id_legado);
CREATE INDEX IF NOT EXISTS idx_clientes_cpf ON core.clientes(cpf);
CREATE INDEX IF NOT EXISTS idx_clientes_nome_normalizado ON core.clientes(nome_normalizado);
CREATE INDEX IF NOT EXISTS idx_telefones_cliente_id ON core.telefones(cliente_id);
CREATE INDEX IF NOT EXISTS idx_telefones_numero ON core.telefones(numero);
CREATE INDEX IF NOT EXISTS idx_lojas_codigo ON core.lojas(codigo);
-- 6. Comentários nas tabelas
COMMENT ON TABLE core.lojas IS 'Lojas do sistema (009=Perus, 010=Rio Pequeno, 011=São Mateus, 012=Suzano 2, 042=Mauá, 048=Suzano)';
COMMENT ON TABLE core.clientes IS 'Clientes unificados (Vixen + OS)';
COMMENT ON TABLE core.telefones IS 'Telefones dos clientes';
-- 7. Comentários nas colunas importantes
COMMENT ON COLUMN core.clientes.id_legado IS 'ID original do sistema legado para rastreabilidade';
COMMENT ON COLUMN core.clientes.nome_normalizado IS 'Nome em lowercase, gerado automaticamente';
COMMENT ON COLUMN core.clientes.created_by IS 'Origem: MIGRACAO_VIXEN ou MIGRACAO_OS';