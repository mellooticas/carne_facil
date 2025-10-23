-- =====================================================
-- PASSO 2: ADICIONAR COLUNA ATIVO NA TABELA TELEFONES
-- =====================================================
-- Objetivo: Adicionar coluna 'ativo' que está faltando na tabela telefones
-- Razão: A tabela foi criada sem esta coluna, mas os INSERTs a utilizam
-- =====================================================
-- Adicionar coluna ativo se não existir
DO $$ BEGIN IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'core'
        AND table_name = 'telefones'
        AND column_name = 'ativo'
) THEN
ALTER TABLE core.telefones
ADD COLUMN ativo BOOLEAN DEFAULT TRUE;
RAISE NOTICE 'Coluna ativo adicionada com sucesso!';
ELSE RAISE NOTICE 'Coluna ativo já existe!';
END IF;
END $$;