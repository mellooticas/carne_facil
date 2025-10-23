-- =====================================================
-- PASSO 3: INSERIR LOJAS
-- =====================================================
-- Objetivo: Inserir registros fixos de lojas no sistema
-- Dados: 6 lojas ativas (009, 010, 011, 012, 042, 048)
-- =====================================================

INSERT INTO core.lojas (codigo, nome, cidade, estado, ativo)
VALUES 
    ('009', 'Perus', 'São Paulo', 'SP', TRUE),
    ('010', 'Rio Pequeno', 'São Paulo', 'SP', TRUE),
    ('011', 'São Mateus', 'São Paulo', 'SP', TRUE),
    ('012', 'Suzano 2', 'São Paulo', 'SP', TRUE),
    ('042', 'Mauá', 'Mauá', 'SP', TRUE),
    ('048', 'Suzano', 'Suzano', 'SP', TRUE)
ON CONFLICT (codigo) DO NOTHING;
