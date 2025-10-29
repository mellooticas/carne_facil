-- ============================================================================
-- 62_CRIAR_TABELA_CANAIS.sql
-- Criação de tabela de mapeamento de canais de aquisição
-- Normaliza os valores brutos de como_conheceu
-- ============================================================================
-- Criar schema marketing se não existir
CREATE SCHEMA IF NOT EXISTS marketing;
-- ============================================================================
-- TABELA: marketing.canais_aquisicao
-- Definição dos canais normalizados para origem de clientes
-- ============================================================================
CREATE TABLE IF NOT EXISTS marketing.canais_aquisicao (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    categoria VARCHAR(50),
    -- 'ORGANICO', 'INDICACAO', 'MARKETING', 'INTERNO'
    ativo BOOLEAN DEFAULT true,
    criado_em TIMESTAMP DEFAULT NOW(),
    atualizado_em TIMESTAMP DEFAULT NOW()
);
-- Criar índices
CREATE INDEX IF NOT EXISTS idx_canais_codigo ON marketing.canais_aquisicao(codigo);
CREATE INDEX IF NOT EXISTS idx_canais_categoria ON marketing.canais_aquisicao(categoria);
CREATE INDEX IF NOT EXISTS idx_canais_ativo ON marketing.canais_aquisicao(ativo);
-- Comentários
COMMENT ON TABLE marketing.canais_aquisicao IS 'Tabela de referência para canais de aquisição de clientes normalizados';
COMMENT ON COLUMN marketing.canais_aquisicao.codigo IS 'Código único do canal (ex: CLIENTES_EXISTENTES)';
COMMENT ON COLUMN marketing.canais_aquisicao.nome IS 'Nome amigável do canal';
COMMENT ON COLUMN marketing.canais_aquisicao.categoria IS 'Categoria do canal: ORGANICO, INDICACAO, MARKETING, INTERNO';
-- ============================================================================
-- POPULAR CANAIS NORMALIZADOS
-- Baseado na análise dos dados de vendas_os_completo.csv
-- ============================================================================
INSERT INTO marketing.canais_aquisicao (codigo, nome, descricao, categoria)
VALUES (
        'CLIENTES_EXISTENTES',
        'Clientes Existentes',
        'Cliente já cadastrado retornando para nova compra',
        'INTERNO'
    ),
    (
        'ORCAMENTO',
        'Orçamento',
        'Cliente que veio através de orçamento prévio',
        'INTERNO'
    ),
    (
        'INDICACAO',
        'Indicação',
        'Indicação genérica de terceiros',
        'INDICACAO'
    ),
    (
        'SAUDE_OLHOS',
        'Saúde dos Olhos',
        'Programa/campanha Saúde dos Olhos',
        'MARKETING'
    ),
    (
        'ABORDAGEM',
        'Abordagem Direta',
        'Abordagem direta na loja ou evento',
        'ORGANICO'
    ),
    (
        'TELEMARKETING',
        'Telemarketing',
        'Contato ativo via telefone',
        'MARKETING'
    ),
    (
        'DIVULGADOR',
        'Divulgador',
        'Divulgador externo/parceiro',
        'INDICACAO'
    ),
    (
        'REDES_SOCIAIS',
        'Redes Sociais',
        'Facebook, Instagram, etc',
        'MARKETING'
    ),
    (
        'AMIGO_INDICACAO',
        'Indicação de Amigo',
        'Indicação específica de amigo',
        'INDICACAO'
    ),
    (
        'WHATSAPP',
        'WhatsApp',
        'Contato via WhatsApp',
        'MARKETING'
    ),
    (
        'CARTAO',
        'Cartão de Visita',
        'Cartão de visita ou material impresso',
        'MARKETING'
    ),
    (
        'GOOGLE',
        'Google/Busca Online',
        'Busca no Google ou internet',
        'MARKETING'
    ),
    (
        'NAO_INFORMADO',
        'Não Informado',
        'Cliente não informou ou dado em branco',
        'INTERNO'
    ),
    (
        'OUTROS',
        'Outros',
        'Outros canais não categorizados',
        'INTERNO'
    ) ON CONFLICT (codigo) DO NOTHING;
-- Verificar inserção
SELECT codigo,
    nome,
    categoria,
    ativo
FROM marketing.canais_aquisicao
ORDER BY categoria,
    nome;
-- Estatísticas
SELECT categoria,
    COUNT(*) as total_canais,
    COUNT(*) FILTER (
        WHERE ativo = true
    ) as canais_ativos
FROM marketing.canais_aquisicao
GROUP BY categoria
ORDER BY categoria;
DO $$ BEGIN RAISE NOTICE '';
RAISE NOTICE '✓ Schema marketing criado';
RAISE NOTICE '✓ Tabela marketing.canais_aquisicao criada';
RAISE NOTICE '✓ % canais normalizados inseridos',
(
    SELECT COUNT(*)
    FROM marketing.canais_aquisicao
);
RAISE NOTICE '';
RAISE NOTICE 'Próximo passo: Criar tabela staging.marketing_origens_vixen';
END $$;
| categoria | total_canais | canais_ativos | | --------- | ------------ | ------------- |
| INDICACAO | 3 | 3 | | INTERNO | 4 | 4 | | MARKETING | 6 | 6 | | ORGANICO | 1 | 1 |