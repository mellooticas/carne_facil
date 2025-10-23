-- ============================================
-- SCRIPT: 10_criar_tabelas_vendas.sql
-- OBJETIVO: Criar tabelas de vendas no schema core
-- DATA: 2025-10-23
-- ============================================
-- ============================================
-- 1. TABELA: core.vendas
-- ============================================
CREATE TABLE IF NOT EXISTS core.vendas (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_legado VARCHAR(50) NOT NULL,
    -- id_dav (Vixen) ou nro_dav (OS)
    origem VARCHAR(20) NOT NULL CHECK (origem IN ('VIXEN', 'OS')),
    -- Relacionamentos
    cliente_id UUID NOT NULL REFERENCES core.clientes(id) ON DELETE RESTRICT,
    loja_id UUID NOT NULL REFERENCES core.lojas(id) ON DELETE RESTRICT,
    -- Dados da Venda
    tipo VARCHAR(30),
    -- 'ORDEM DE SERVIÇO PDV', 'DAV', etc
    status VARCHAR(20),
    -- 'FINALIZADO', 'PENDENTE', 'ABERTA', etc
    descricao VARCHAR(100),
    -- 'SAÚDE DOS OLHOS', 'ORÇAMENTO', etc
    -- Valores
    valor_bruto DECIMAL(10, 2),
    valor_acrescimo DECIMAL(10, 2),
    valor_desconto DECIMAL(10, 2),
    valor_liquido DECIMAL(10, 2) NOT NULL,
    -- Adiantamento
    percentual_adiantamento DECIMAL(5, 2),
    valor_adiantamento DECIMAL(10, 2),
    -- Datas
    data_venda TIMESTAMPTZ NOT NULL,
    data_previsao_entrega DATE,
    data_entrega DATE,
    -- Vendedor e Operador (Vixen)
    id_vendedor VARCHAR(50),
    nome_vendedor VARCHAR(200),
    id_operador VARCHAR(50),
    nome_operador VARCHAR(200),
    id_caixa VARCHAR(50),
    -- Observações
    eh_garantia BOOLEAN DEFAULT FALSE,
    meios_contato VARCHAR(100),
    -- Metadados
    mes_referencia VARCHAR(7),
    -- 'YYYY-MM'
    arquivo_origem VARCHAR(100),
    migrado_em TIMESTAMPTZ DEFAULT NOW(),
    -- Auditoria
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    version INTEGER DEFAULT 1
);
-- Índices para core.vendas
CREATE INDEX IF NOT EXISTS idx_vendas_id_legado ON core.vendas(id_legado);
CREATE INDEX IF NOT EXISTS idx_vendas_cliente_id ON core.vendas(cliente_id);
CREATE INDEX IF NOT EXISTS idx_vendas_loja_id ON core.vendas(loja_id);
CREATE INDEX IF NOT EXISTS idx_vendas_origem ON core.vendas(origem);
CREATE INDEX IF NOT EXISTS idx_vendas_status ON core.vendas(status);
CREATE INDEX IF NOT EXISTS idx_vendas_data_venda ON core.vendas(data_venda);
CREATE INDEX IF NOT EXISTS idx_vendas_mes_referencia ON core.vendas(mes_referencia);
-- Constraint de unicidade: origem + id_legado
CREATE UNIQUE INDEX IF NOT EXISTS idx_vendas_origem_id_legado ON core.vendas(origem, id_legado);
-- ============================================
-- 2. TABELA: core.itens_venda
-- ============================================
CREATE TABLE IF NOT EXISTS core.itens_venda (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    venda_id UUID NOT NULL REFERENCES core.vendas(id) ON DELETE CASCADE,
    item_numero INTEGER NOT NULL,
    -- ordem do item na venda
    -- Produto
    id_produto VARCHAR(50),
    descricao_produto TEXT NOT NULL,
    modelo VARCHAR(200),
    grupo VARCHAR(100),
    detalhe VARCHAR(200),
    -- Valores
    quantidade DECIMAL(10, 3) NOT NULL DEFAULT 1,
    valor_unitario DECIMAL(10, 2),
    valor_total DECIMAL(10, 2) NOT NULL,
    -- Metadados
    arquivo_origem VARCHAR(100),
    mes_referencia VARCHAR(7),
    -- Auditoria
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
-- Índices para core.itens_venda
CREATE INDEX IF NOT EXISTS idx_itens_venda_venda_id ON core.itens_venda(venda_id);
CREATE INDEX IF NOT EXISTS idx_itens_venda_id_produto ON core.itens_venda(id_produto);
CREATE INDEX IF NOT EXISTS idx_itens_venda_grupo ON core.itens_venda(grupo);
-- Constraint de unicidade: venda_id + item_numero
CREATE UNIQUE INDEX IF NOT EXISTS idx_itens_venda_venda_item ON core.itens_venda(venda_id, item_numero);
-- ============================================
-- 3. COMENTÁRIOS
-- ============================================
COMMENT ON TABLE core.vendas IS 'Vendas migradas dos sistemas Vixen e OS';
COMMENT ON COLUMN core.vendas.id_legado IS 'id_dav (Vixen) ou nro_dav (OS) do sistema legado';
COMMENT ON COLUMN core.vendas.origem IS 'Sistema de origem: VIXEN ou OS';
COMMENT ON COLUMN core.vendas.tipo IS 'Tipo da venda: ORDEM DE SERVIÇO PDV, DAV, etc';
COMMENT ON COLUMN core.vendas.eh_garantia IS 'Indica se é uma venda de garantia';
COMMENT ON TABLE core.itens_venda IS 'Itens (produtos) das vendas';
COMMENT ON COLUMN core.itens_venda.item_numero IS 'Número sequencial do item na venda';
COMMENT ON COLUMN core.itens_venda.id_produto IS 'Código do produto no sistema legado';
-- ============================================
-- FIM DO SCRIPT
-- ============================================