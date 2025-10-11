-- ============================================================================
-- BANCO DE DADOS - SISTEMA ÓTICAS (SUPABASE)
-- Script 01: Configuração Inicial para Supabase
-- ============================================================================
-- IMPORTANTE: Execute no SQL Editor do Supabase Dashboard
-- URL: https://app.supabase.com/project/SEU-PROJETO/sql
-- ============================================================================

-- ============================================================================
-- PARTE 1: EXTENSÕES
-- ============================================================================
-- Nota: Supabase já tem a maioria instalada, mas vamos garantir

-- UUID Generation (já instalado no Supabase)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Fuzzy Search / Trigrams (já instalado no Supabase)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Remove acentos (já instalado no Supabase)
CREATE EXTENSION IF NOT EXISTS unaccent;

-- GIN indexes para arrays e textos
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- Criptografia (já instalado no Supabase)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

COMMENT ON EXTENSION "uuid-ossp" IS 'Geração de UUIDs (Supabase native)';
COMMENT ON EXTENSION pg_trgm IS 'Busca fuzzy com trigramas (Supabase native)';
COMMENT ON EXTENSION unaccent IS 'Remoção de acentos para normalização (Supabase native)';
COMMENT ON EXTENSION btree_gin IS 'Índices GIN otimizados (Supabase native)';

-- ============================================================================
-- PARTE 2: SCHEMAS CUSTOMIZADOS
-- ============================================================================
-- Nota: Evitar usar 'public' no Supabase (é o schema padrão e pode ter conflitos)

-- Schema CORE: Dados mestres (clientes, lojas, vendedores)
CREATE SCHEMA IF NOT EXISTS core;
COMMENT ON SCHEMA core IS 'Dados mestres - clientes, lojas, vendedores, configurações';

-- Schema VENDAS: Transações comerciais
CREATE SCHEMA IF NOT EXISTS vendas;
COMMENT ON SCHEMA vendas IS 'Vendas, recebimentos, carnês, formas de pagamento';

-- Schema OPTICA: Dados específicos de óticas
CREATE SCHEMA IF NOT EXISTS optica;
COMMENT ON SCHEMA optica IS 'Ordens de serviço, dioptrias, produtos óticos';

-- Schema MARKETING: CRM e campanhas
CREATE SCHEMA IF NOT EXISTS marketing;
COMMENT ON SCHEMA marketing IS 'CRM, campanhas, comunicações, aniversariantes';

-- Schema AUDITORIA: Logs e histórico
CREATE SCHEMA IF NOT EXISTS auditoria;
COMMENT ON SCHEMA auditoria IS 'Logs de alterações, histórico, snapshots, auditoria completa';

-- ============================================================================
-- PARTE 3: TIPOS PERSONALIZADOS (ENUMs)
-- ============================================================================

-- Status geral (ativo/inativo)
DO $$ BEGIN
    CREATE TYPE status_type AS ENUM ('ATIVO', 'INATIVO', 'PENDENTE', 'BLOQUEADO');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
COMMENT ON TYPE status_type IS 'Status geral para entidades (ativo, inativo, pendente, bloqueado)';

-- Status de Ordem de Serviço
DO $$ BEGIN
    CREATE TYPE status_os_type AS ENUM (
        'ABERTA',
        'EM_PRODUCAO',
        'PRONTA',
        'ENTREGUE',
        'CANCELADA'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
COMMENT ON TYPE status_os_type IS 'Status do ciclo de vida de uma OS';

-- Tipo de telefone
DO $$ BEGIN
    CREATE TYPE tipo_telefone_type AS ENUM (
        'CELULAR',
        'RESIDENCIAL',
        'COMERCIAL',
        'RECADO'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
COMMENT ON TYPE tipo_telefone_type IS 'Classificação de tipos de telefone';

-- Tipo de endereço
DO $$ BEGIN
    CREATE TYPE tipo_endereco_type AS ENUM (
        'RESIDENCIAL',
        'COMERCIAL',
        'COBRANCA',
        'ENTREGA'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
COMMENT ON TYPE tipo_endereco_type IS 'Classificação de tipos de endereço';

-- Formas de pagamento
DO $$ BEGIN
    CREATE TYPE forma_pagamento_type AS ENUM (
        'DINHEIRO',
        'PIX',
        'DEBITO',
        'CREDITO',
        'CARNE',
        'CONVENIO',
        'CHEQUE',
        'TRANSFERENCIA'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
COMMENT ON TYPE forma_pagamento_type IS 'Formas de pagamento aceitas';

-- Tipo de visão (para dioptrias)
DO $$ BEGIN
    CREATE TYPE tipo_visao_type AS ENUM ('LONGE', 'PERTO', 'INTERMEDIARIO');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
COMMENT ON TYPE tipo_visao_type IS 'Tipo de visão para prescrição ótica';

-- Olho (esquerdo/direito)
DO $$ BEGIN
    CREATE TYPE olho_type AS ENUM ('OD', 'OE');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
COMMENT ON TYPE olho_type IS 'Identificação de olho (OD=Direito, OE=Esquerdo)';

-- ============================================================================
-- PARTE 4: FUNÇÕES AUXILIARES
-- ============================================================================

-- Função: Atualizar updated_at automaticamente (ADAPTADA PARA SUPABASE)
CREATE OR REPLACE FUNCTION atualizar_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    
    -- Tentar pegar o usuário autenticado do Supabase
    BEGIN
        NEW.updated_by = COALESCE(
            auth.uid()::TEXT,  -- ID do usuário Supabase
            current_user,      -- Fallback para usuário PostgreSQL
            'system'           -- Fallback final
        );
    EXCEPTION
        WHEN OTHERS THEN
            NEW.updated_by = COALESCE(current_user, 'system');
    END;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION atualizar_updated_at() IS 'Atualiza automaticamente updated_at e updated_by (integrado com Supabase Auth)';

-- Função: Normalizar texto (remover acentos, lowercase, trim)
CREATE OR REPLACE FUNCTION normalizar_texto(texto TEXT)
RETURNS TEXT AS $$
BEGIN
    IF texto IS NULL THEN
        RETURN NULL;
    END IF;
    
    RETURN LOWER(TRIM(unaccent(texto)));
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION normalizar_texto(TEXT) IS 'Normaliza texto: remove acentos, converte para minúsculas, remove espaços';

-- Função: Normalizar telefone (apenas números)
CREATE OR REPLACE FUNCTION normalizar_telefone(telefone TEXT)
RETURNS TEXT AS $$
BEGIN
    IF telefone IS NULL THEN
        RETURN NULL;
    END IF;
    
    RETURN regexp_replace(telefone, '[^0-9]', '', 'g');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION normalizar_telefone(TEXT) IS 'Remove todos os caracteres não numéricos do telefone';

-- Função: Validar CPF
CREATE OR REPLACE FUNCTION validar_cpf(cpf TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    cpf_numeros TEXT;
    soma INTEGER;
    resto INTEGER;
    dv1 INTEGER;
    dv2 INTEGER;
BEGIN
    IF cpf IS NULL THEN
        RETURN TRUE;  -- NULL é válido (campo opcional)
    END IF;
    
    -- Remove caracteres não numéricos
    cpf_numeros := regexp_replace(cpf, '[^0-9]', '', 'g');
    
    -- Verifica se tem 11 dígitos
    IF LENGTH(cpf_numeros) != 11 THEN
        RETURN FALSE;
    END IF;
    
    -- Verifica se todos os dígitos são iguais (ex: 111.111.111-11)
    IF cpf_numeros ~ '^(\d)\1{10}$' THEN
        RETURN FALSE;
    END IF;
    
    -- Calcula primeiro dígito verificador
    soma := 0;
    FOR i IN 1..9 LOOP
        soma := soma + CAST(SUBSTRING(cpf_numeros FROM i FOR 1) AS INTEGER) * (11 - i);
    END LOOP;
    resto := (soma * 10) % 11;
    IF resto = 10 THEN resto := 0; END IF;
    dv1 := resto;
    
    -- Verifica primeiro dígito
    IF dv1 != CAST(SUBSTRING(cpf_numeros FROM 10 FOR 1) AS INTEGER) THEN
        RETURN FALSE;
    END IF;
    
    -- Calcula segundo dígito verificador
    soma := 0;
    FOR i IN 1..10 LOOP
        soma := soma + CAST(SUBSTRING(cpf_numeros FROM i FOR 1) AS INTEGER) * (12 - i);
    END LOOP;
    resto := (soma * 10) % 11;
    IF resto = 10 THEN resto := 0; END IF;
    dv2 := resto;
    
    -- Verifica segundo dígito
    IF dv2 != CAST(SUBSTRING(cpf_numeros FROM 11 FOR 1) AS INTEGER) THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION validar_cpf(TEXT) IS 'Valida CPF brasileiro com dígitos verificadores';

-- Função: Formatar CPF
CREATE OR REPLACE FUNCTION formatar_cpf(cpf TEXT)
RETURNS TEXT AS $$
DECLARE
    cpf_numeros TEXT;
BEGIN
    IF cpf IS NULL THEN
        RETURN NULL;
    END IF;
    
    cpf_numeros := regexp_replace(cpf, '[^0-9]', '', 'g');
    
    IF LENGTH(cpf_numeros) != 11 THEN
        RETURN cpf;  -- Retorna original se inválido
    END IF;
    
    RETURN SUBSTRING(cpf_numeros FROM 1 FOR 3) || '.' ||
           SUBSTRING(cpf_numeros FROM 4 FOR 3) || '.' ||
           SUBSTRING(cpf_numeros FROM 7 FOR 3) || '-' ||
           SUBSTRING(cpf_numeros FROM 10 FOR 2);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION formatar_cpf(TEXT) IS 'Formata CPF no padrão XXX.XXX.XXX-XX';

-- Função: Validar telefone brasileiro
CREATE OR REPLACE FUNCTION validar_telefone_br(telefone TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    telefone_numeros TEXT;
BEGIN
    IF telefone IS NULL THEN
        RETURN TRUE;  -- NULL é válido
    END IF;
    
    telefone_numeros := normalizar_telefone(telefone);
    
    -- Celular: 11 dígitos (DD + 9XXXX-XXXX)
    -- Fixo: 10 dígitos (DD + XXXX-XXXX)
    RETURN LENGTH(telefone_numeros) IN (10, 11);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION validar_telefone_br(TEXT) IS 'Valida telefone brasileiro (10 ou 11 dígitos)';

-- Função: Calcular idade
CREATE OR REPLACE FUNCTION calcular_idade(data_nascimento DATE)
RETURNS INTEGER AS $$
BEGIN
    IF data_nascimento IS NULL THEN
        RETURN NULL;
    END IF;
    
    RETURN DATE_PART('year', AGE(CURRENT_DATE, data_nascimento))::INTEGER;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION calcular_idade(DATE) IS 'Calcula idade em anos a partir da data de nascimento';

-- Função: Gerar código único (para OS, vendas, etc)
CREATE OR REPLACE FUNCTION gerar_codigo_sequencial(prefixo TEXT, loja_codigo TEXT)
RETURNS TEXT AS $$
DECLARE
    ano TEXT;
    sequencia TEXT;
BEGIN
    ano := TO_CHAR(CURRENT_DATE, 'YY');
    sequencia := LPAD(FLOOR(RANDOM() * 99999)::TEXT, 5, '0');
    
    RETURN prefixo || '-' || loja_codigo || '-' || ano || '-' || sequencia;
END;
$$ LANGUAGE plpgsql VOLATILE;

COMMENT ON FUNCTION gerar_codigo_sequencial(TEXT, TEXT) IS 'Gera código sequencial: PREFIXO-LOJA-ANO-XXXXX';

-- ============================================================================
-- PARTE 5: CONFIGURAÇÕES ESPECÍFICAS DO SUPABASE
-- ============================================================================

-- Habilitar Row Level Security (RLS) será feito nas tabelas individuais
-- Isso é OBRIGATÓRIO no Supabase para segurança da API

-- Grant de permissões para schemas customizados
-- Nota: 'authenticated' e 'anon' são roles do Supabase

GRANT USAGE ON SCHEMA core TO authenticated, anon;
GRANT USAGE ON SCHEMA vendas TO authenticated, anon;
GRANT USAGE ON SCHEMA optica TO authenticated, anon;
GRANT USAGE ON SCHEMA marketing TO authenticated, anon;
GRANT USAGE ON SCHEMA auditoria TO authenticated;  -- Apenas autenticados

-- Permissões para tipos customizados
GRANT USAGE ON TYPE status_type TO authenticated, anon;
GRANT USAGE ON TYPE status_os_type TO authenticated, anon;
GRANT USAGE ON TYPE tipo_telefone_type TO authenticated, anon;
GRANT USAGE ON TYPE tipo_endereco_type TO authenticated, anon;
GRANT USAGE ON TYPE forma_pagamento_type TO authenticated, anon;
GRANT USAGE ON TYPE tipo_visao_type TO authenticated, anon;
GRANT USAGE ON TYPE olho_type TO authenticated, anon;

-- Permissões para funções
GRANT EXECUTE ON FUNCTION normalizar_texto(TEXT) TO authenticated, anon;
GRANT EXECUTE ON FUNCTION normalizar_telefone(TEXT) TO authenticated, anon;
GRANT EXECUTE ON FUNCTION validar_cpf(TEXT) TO authenticated, anon;
GRANT EXECUTE ON FUNCTION formatar_cpf(TEXT) TO authenticated, anon;
GRANT EXECUTE ON FUNCTION validar_telefone_br(TEXT) TO authenticated, anon;
GRANT EXECUTE ON FUNCTION calcular_idade(DATE) TO authenticated, anon;
GRANT EXECUTE ON FUNCTION gerar_codigo_sequencial(TEXT, TEXT) TO authenticated, anon;

-- ============================================================================
-- FIM DO SCRIPT 01
-- ============================================================================

-- Verificar instalação
DO $$
BEGIN
    RAISE NOTICE '✅ Script 01 executado com sucesso!';
    RAISE NOTICE '📦 Extensões: uuid-ossp, pg_trgm, unaccent, btree_gin';
    RAISE NOTICE '📂 Schemas: core, vendas, optica, marketing, auditoria';
    RAISE NOTICE '🏷️ Tipos: 7 ENUMs criados';
    RAISE NOTICE '⚙️ Funções: 8 funções auxiliares';
    RAISE NOTICE '🔐 Permissões: Configuradas para roles do Supabase';
    RAISE NOTICE '🚀 Próximo: Execute 02_schema_core_supabase.sql';
END $$;
