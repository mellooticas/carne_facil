-- 1. Garantir que o schema core existe
CREATE SCHEMA IF NOT EXISTS core;
-- 2. Configurar o search_path para incluir core e public
ALTER DATABASE postgres
SET search_path TO core,
    public;
-- 3. Garantir permissões para os usuários anon e authenticated
GRANT USAGE ON SCHEMA core TO anon,
    authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA core TO anon,
    authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA core TO anon,
    authenticated;
-- 4. Alterar o owner das tabelas do schema core para postgres
DO $$
DECLARE r RECORD;
BEGIN FOR r IN
SELECT tablename
FROM pg_tables
WHERE schemaname = 'core' LOOP EXECUTE 'ALTER TABLE core.' || quote_ident(r.tablename) || ' OWNER TO postgres';
END LOOP;
END $$;
-- 5. Desabilitar RLS temporariamente para povoamento
DO $$
DECLARE r RECORD;
BEGIN FOR r IN
SELECT tablename
FROM pg_tables
WHERE schemaname = 'core' LOOP EXECUTE 'ALTER TABLE core.' || quote_ident(r.tablename) || ' DISABLE ROW LEVEL SECURITY';
END LOOP;
END $$;