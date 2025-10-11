-- ============================================================================
-- BANCO DE DADOS - SISTEMA ÓTICAS (SUPABASE)
-- Script 07: RLS POLICIES - Políticas Avançadas de Segurança
-- ============================================================================
-- IMPORTANTE: Execute APÓS o script 06_schema_auditoria_supabase.sql
-- ============================================================================
-- Este script adiciona políticas RLS avançadas com base em:
-- - Hierarquia de usuários (ADMIN, GERENTE, VENDEDOR, CLIENTE)
-- - Loja do usuário (acesso restrito por loja)
-- - Proprietário do registro (created_by)
-- ============================================================================

-- ============================================================================
-- TABELA DE APOIO: Roles e Permissões de Usuários
-- ============================================================================

CREATE TABLE IF NOT EXISTS core.user_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('ADMIN', 'GERENTE', 'VENDEDOR', 'ATENDENTE', 'CLIENTE')),
    loja_id UUID REFERENCES core.lojas(id) ON DELETE SET NULL,
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_role UNIQUE(user_id, role, loja_id)
);

CREATE INDEX idx_user_roles_user_id ON core.user_roles(user_id);
CREATE INDEX idx_user_roles_role ON core.user_roles(role);
CREATE INDEX idx_user_roles_loja_id ON core.user_roles(loja_id);
CREATE INDEX idx_user_roles_ativo ON core.user_roles(ativo) WHERE ativo = true;

ALTER TABLE core.user_roles ENABLE ROW LEVEL SECURITY;

-- Admins e usuários podem ver seus próprios roles
CREATE POLICY "Usuários podem ver seus roles"
ON core.user_roles FOR SELECT
TO authenticated
USING (user_id = auth.uid());

-- Apenas admins podem gerenciar roles
CREATE POLICY "Admins podem gerenciar roles"
ON core.user_roles FOR ALL
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM core.user_roles ur
        WHERE ur.user_id = auth.uid() AND ur.role = 'ADMIN' AND ur.ativo = true
    )
);

GRANT SELECT, INSERT, UPDATE, DELETE ON core.user_roles TO authenticated;

COMMENT ON TABLE core.user_roles IS 'Roles e permissões dos usuários por loja';

-- ============================================================================
-- HELPER FUNCTIONS PARA RLS
-- ============================================================================

-- Function: Verificar se usuário tem role específico
CREATE OR REPLACE FUNCTION core.user_has_role(p_role VARCHAR)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM core.user_roles
        WHERE user_id = auth.uid()
          AND role = p_role
          AND ativo = true
    );
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION core.user_has_role(VARCHAR) TO authenticated;

-- Function: Verificar se usuário pertence à loja
CREATE OR REPLACE FUNCTION core.user_belongs_to_loja(p_loja_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM core.user_roles
        WHERE user_id = auth.uid()
          AND loja_id = p_loja_id
          AND ativo = true
    );
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION core.user_belongs_to_loja(UUID) TO authenticated;

-- Function: Obter loja_id do usuário
CREATE OR REPLACE FUNCTION core.get_user_loja_id()
RETURNS UUID AS $$
BEGIN
    RETURN (
        SELECT loja_id FROM core.user_roles
        WHERE user_id = auth.uid()
          AND ativo = true
        ORDER BY 
            CASE role
                WHEN 'ADMIN' THEN 1
                WHEN 'GERENTE' THEN 2
                WHEN 'VENDEDOR' THEN 3
                ELSE 4
            END
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION core.get_user_loja_id() TO authenticated;

-- Function: Verificar se usuário é admin ou gerente
CREATE OR REPLACE FUNCTION core.user_is_admin_or_manager()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM core.user_roles
        WHERE user_id = auth.uid()
          AND role IN ('ADMIN', 'GERENTE')
          AND ativo = true
    );
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION core.user_is_admin_or_manager() TO authenticated;

COMMENT ON FUNCTION core.user_has_role IS 'Verifica se usuário possui role específico';
COMMENT ON FUNCTION core.user_belongs_to_loja IS 'Verifica se usuário pertence a loja específica';
COMMENT ON FUNCTION core.get_user_loja_id IS 'Retorna loja_id do usuário';
COMMENT ON FUNCTION core.user_is_admin_or_manager IS 'Verifica se usuário é ADMIN ou GERENTE';

-- ============================================================================
-- RLS AVANÇADO: CLIENTES
-- ============================================================================

-- DROP políticas básicas existentes
DROP POLICY IF EXISTS "Permitir leitura de clientes para autenticados" ON core.clientes;
DROP POLICY IF EXISTS "Permitir inserção de clientes para autenticados" ON core.clientes;
DROP POLICY IF EXISTS "Permitir atualização de clientes para autenticados" ON core.clientes;

-- Novas políticas avançadas
-- SELECT: Admin/Gerente vê todos, Vendedor vê apenas de sua loja
CREATE POLICY "rls_clientes_select_avancado"
ON core.clientes FOR SELECT
TO authenticated
USING (
    deleted_at IS NULL
    AND (
        -- Admin vê tudo
        core.user_has_role('ADMIN')
        OR
        -- Gerente vê tudo
        core.user_has_role('GERENTE')
        OR
        -- Vendedor vê apenas clientes com vendas em sua loja
        EXISTS (
            SELECT 1 FROM vendas.vendas v
            INNER JOIN core.user_roles ur ON ur.loja_id = v.loja_id
            WHERE v.cliente_id = clientes.id
              AND ur.user_id = auth.uid()
              AND ur.ativo = true
        )
    )
);

-- INSERT: Todos autenticados podem criar
CREATE POLICY "rls_clientes_insert_avancado"
ON core.clientes FOR INSERT
TO authenticated
WITH CHECK (true);

-- UPDATE: Admin/Gerente atualiza todos, Vendedor atualiza apenas de sua loja
CREATE POLICY "rls_clientes_update_avancado"
ON core.clientes FOR UPDATE
TO authenticated
USING (
    deleted_at IS NULL
    AND (
        core.user_is_admin_or_manager()
        OR
        EXISTS (
            SELECT 1 FROM vendas.vendas v
            INNER JOIN core.user_roles ur ON ur.loja_id = v.loja_id
            WHERE v.cliente_id = clientes.id
              AND ur.user_id = auth.uid()
              AND ur.ativo = true
        )
    )
)
WITH CHECK (deleted_at IS NULL);

-- DELETE: Apenas Admin
CREATE POLICY "rls_clientes_delete_avancado"
ON core.clientes FOR DELETE
TO authenticated
USING (core.user_has_role('ADMIN'));

-- ============================================================================
-- RLS AVANÇADO: VENDAS
-- ============================================================================

DROP POLICY IF EXISTS "Permitir leitura de vendas para autenticados" ON vendas.vendas;
DROP POLICY IF EXISTS "Permitir inserção de vendas para autenticados" ON vendas.vendas;
DROP POLICY IF EXISTS "Permitir atualização de vendas para autenticados" ON vendas.vendas;

-- SELECT: Admin/Gerente vê tudo, Vendedor vê apenas de sua loja
CREATE POLICY "rls_vendas_select_avancado"
ON vendas.vendas FOR SELECT
TO authenticated
USING (
    deleted_at IS NULL
    AND cancelado = false
    AND (
        core.user_is_admin_or_manager()
        OR
        core.user_belongs_to_loja(loja_id)
    )
);

-- INSERT: Apenas vendas da própria loja (exceto Admin)
CREATE POLICY "rls_vendas_insert_avancado"
ON vendas.vendas FOR INSERT
TO authenticated
WITH CHECK (
    core.user_has_role('ADMIN')
    OR
    core.user_belongs_to_loja(loja_id)
);

-- UPDATE: Admin/Gerente atualiza tudo, Vendedor atualiza apenas de sua loja
CREATE POLICY "rls_vendas_update_avancado"
ON vendas.vendas FOR UPDATE
TO authenticated
USING (
    deleted_at IS NULL
    AND (
        core.user_is_admin_or_manager()
        OR
        (core.user_belongs_to_loja(loja_id) AND cancelado = false)
    )
)
WITH CHECK (deleted_at IS NULL);

-- DELETE: Apenas Admin
CREATE POLICY "rls_vendas_delete_avancado"
ON vendas.vendas FOR DELETE
TO authenticated
USING (core.user_has_role('ADMIN'));

-- ============================================================================
-- RLS AVANÇADO: ORDENS DE SERVIÇO
-- ============================================================================

DROP POLICY IF EXISTS "Permitir leitura de OS para autenticados" ON optica.ordens_servico;
DROP POLICY IF EXISTS "Permitir inserção de OS para autenticados" ON optica.ordens_servico;
DROP POLICY IF EXISTS "Permitir atualização de OS para autenticados" ON optica.ordens_servico;

-- SELECT: Por loja
CREATE POLICY "rls_os_select_avancado"
ON optica.ordens_servico FOR SELECT
TO authenticated
USING (
    deleted_at IS NULL
    AND cancelada = false
    AND (
        core.user_is_admin_or_manager()
        OR
        core.user_belongs_to_loja(loja_id)
    )
);

-- INSERT: Apenas da própria loja
CREATE POLICY "rls_os_insert_avancado"
ON optica.ordens_servico FOR INSERT
TO authenticated
WITH CHECK (
    core.user_has_role('ADMIN')
    OR
    core.user_belongs_to_loja(loja_id)
);

-- UPDATE: Por loja
CREATE POLICY "rls_os_update_avancado"
ON optica.ordens_servico FOR UPDATE
TO authenticated
USING (
    deleted_at IS NULL
    AND (
        core.user_is_admin_or_manager()
        OR
        core.user_belongs_to_loja(loja_id)
    )
)
WITH CHECK (deleted_at IS NULL);

-- DELETE: Apenas Admin
CREATE POLICY "rls_os_delete_avancado"
ON optica.ordens_servico FOR DELETE
TO authenticated
USING (core.user_has_role('ADMIN'));

-- ============================================================================
-- RLS AVANÇADO: RECEBIMENTOS
-- ============================================================================

DROP POLICY IF EXISTS "Acesso a recebimentos para autenticados" ON vendas.recebimentos_carne;

CREATE POLICY "rls_recebimentos_select_avancado"
ON vendas.recebimentos_carne FOR SELECT
TO authenticated
USING (
    deleted_at IS NULL
    AND (
        core.user_is_admin_or_manager()
        OR
        core.user_belongs_to_loja(loja_id)
    )
);

CREATE POLICY "rls_recebimentos_insert_avancado"
ON vendas.recebimentos_carne FOR INSERT
TO authenticated
WITH CHECK (
    core.user_has_role('ADMIN')
    OR
    core.user_belongs_to_loja(loja_id)
);

CREATE POLICY "rls_recebimentos_update_avancado"
ON vendas.recebimentos_carne FOR UPDATE
TO authenticated
USING (
    deleted_at IS NULL
    AND (
        core.user_is_admin_or_manager()
        OR
        core.user_belongs_to_loja(loja_id)
    )
);

-- ============================================================================
-- RLS AVANÇADO: ENTREGAS CARNÊ
-- ============================================================================

DROP POLICY IF EXISTS "Acesso a entregas para autenticados" ON vendas.entregas_carne;

CREATE POLICY "rls_entregas_select_avancado"
ON vendas.entregas_carne FOR SELECT
TO authenticated
USING (
    deleted_at IS NULL
    AND (
        core.user_is_admin_or_manager()
        OR
        core.user_belongs_to_loja(loja_id)
    )
);

CREATE POLICY "rls_entregas_insert_avancado"
ON vendas.entregas_carne FOR INSERT
TO authenticated
WITH CHECK (
    core.user_has_role('ADMIN')
    OR
    core.user_belongs_to_loja(loja_id)
);

-- ============================================================================
-- RLS AVANÇADO: RESTANTES ENTRADA
-- ============================================================================

DROP POLICY IF EXISTS "Acesso a restantes para autenticados" ON vendas.restantes_entrada;

CREATE POLICY "rls_restantes_select_avancado"
ON vendas.restantes_entrada FOR SELECT
TO authenticated
USING (
    deleted_at IS NULL
    AND (
        core.user_is_admin_or_manager()
        OR
        core.user_belongs_to_loja(loja_id)
    )
);

CREATE POLICY "rls_restantes_insert_avancado"
ON vendas.restantes_entrada FOR INSERT
TO authenticated
WITH CHECK (
    core.user_has_role('ADMIN')
    OR
    core.user_belongs_to_loja(loja_id)
);

-- ============================================================================
-- RLS AVANÇADO: MARKETING
-- ============================================================================

-- Cliente Info: Apenas Admin/Gerente
DROP POLICY IF EXISTS "Acesso a cliente_info para autenticados" ON marketing.cliente_info;

CREATE POLICY "rls_cliente_info_select_avancado"
ON marketing.cliente_info FOR SELECT
TO authenticated
USING (
    deleted_at IS NULL
    AND core.user_is_admin_or_manager()
);

CREATE POLICY "rls_cliente_info_manipulate_avancado"
ON marketing.cliente_info FOR ALL
TO authenticated
USING (core.user_is_admin_or_manager())
WITH CHECK (core.user_is_admin_or_manager());

-- Campanhas: Apenas Admin/Gerente
DROP POLICY IF EXISTS "Acesso a campanhas para autenticados" ON marketing.campanhas;

CREATE POLICY "rls_campanhas_select_avancado"
ON marketing.campanhas FOR SELECT
TO authenticated
USING (
    deleted_at IS NULL
    AND (
        core.user_has_role('ADMIN')
        OR
        (core.user_has_role('GERENTE') AND (loja_id IS NULL OR core.user_belongs_to_loja(loja_id)))
    )
);

CREATE POLICY "rls_campanhas_manipulate_avancado"
ON marketing.campanhas FOR ALL
TO authenticated
USING (core.user_is_admin_or_manager())
WITH CHECK (core.user_is_admin_or_manager());

-- Leads: Admin/Gerente vê tudo, Vendedor vê apenas de sua loja
DROP POLICY IF EXISTS "Acesso a leads para autenticados" ON marketing.leads;

CREATE POLICY "rls_leads_select_avancado"
ON marketing.leads FOR SELECT
TO authenticated
USING (
    deleted_at IS NULL
    AND (
        core.user_is_admin_or_manager()
        OR
        (loja_id IS NOT NULL AND core.user_belongs_to_loja(loja_id))
    )
);

CREATE POLICY "rls_leads_manipulate_avancado"
ON marketing.leads FOR ALL
TO authenticated
USING (
    core.user_is_admin_or_manager()
    OR
    (loja_id IS NOT NULL AND core.user_belongs_to_loja(loja_id))
)
WITH CHECK (
    core.user_is_admin_or_manager()
    OR
    (loja_id IS NOT NULL AND core.user_belongs_to_loja(loja_id))
);

-- ============================================================================
-- RLS AVANÇADO: AUDITORIA
-- ============================================================================

-- Auditoria: Apenas leitura, Admin/Gerente vê tudo
DROP POLICY IF EXISTS "Permitir leitura de logs para autenticados" ON auditoria.log_alteracoes;

CREATE POLICY "rls_log_alteracoes_select_avancado"
ON auditoria.log_alteracoes FOR SELECT
TO authenticated
USING (core.user_is_admin_or_manager());

-- Histórico de Valores: Apenas Admin/Gerente
DROP POLICY IF EXISTS "Permitir leitura de histórico para autenticados" ON auditoria.historico_valores;

CREATE POLICY "rls_historico_valores_select_avancado"
ON auditoria.historico_valores FOR SELECT
TO authenticated
USING (core.user_is_admin_or_manager());

-- Snapshots: Apenas Admin
DROP POLICY IF EXISTS "Permitir leitura de snapshots para autenticados" ON auditoria.snapshots_diarios;

CREATE POLICY "rls_snapshots_select_avancado"
ON auditoria.snapshots_diarios FOR SELECT
TO authenticated
USING (core.user_has_role('ADMIN'));

-- Acesso Usuários: Usuário vê apenas seus próprios acessos, Admin vê tudo
DROP POLICY IF EXISTS "Permitir leitura de acessos para autenticados" ON auditoria.acesso_usuarios;

CREATE POLICY "rls_acesso_usuarios_select_avancado"
ON auditoria.acesso_usuarios FOR SELECT
TO authenticated
USING (
    usuario_id = auth.uid()
    OR
    core.user_has_role('ADMIN')
);

-- ============================================================================
-- VIEW: Permissões do Usuário Atual
-- ============================================================================

CREATE OR REPLACE VIEW core.v_user_permissions AS
SELECT 
    auth.uid() as user_id,
    ur.role,
    ur.loja_id,
    l.codigo as loja_codigo,
    l.nome as loja_nome,
    ur.ativo,
    CASE 
        WHEN ur.role = 'ADMIN' THEN true
        ELSE false
    END as is_admin,
    CASE 
        WHEN ur.role IN ('ADMIN', 'GERENTE') THEN true
        ELSE false
    END as is_manager,
    CASE 
        WHEN ur.role = 'VENDEDOR' THEN true
        ELSE false
    END as is_vendedor
FROM core.user_roles ur
LEFT JOIN core.lojas l ON l.id = ur.loja_id
WHERE ur.user_id = auth.uid()
  AND ur.ativo = true;

GRANT SELECT ON core.v_user_permissions TO authenticated;

COMMENT ON VIEW core.v_user_permissions IS 'Permissões do usuário autenticado atual';

-- ============================================================================
-- FIM DO SCRIPT 07
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Script 07 executado com sucesso!';
    RAISE NOTICE '🔐 RLS Policies Avançadas criadas:';
    RAISE NOTICE '   - Hierarquia: ADMIN > GERENTE > VENDEDOR > ATENDENTE > CLIENTE';
    RAISE NOTICE '   - Segregação por loja implementada';
    RAISE NOTICE '   - 4 Helper Functions criadas (verificação de roles)';
    RAISE NOTICE '   - 1 Tabela core.user_roles criada';
    RAISE NOTICE '   - Políticas aplicadas em: clientes, vendas, OS, recebimentos, marketing, auditoria';
    RAISE NOTICE '👁️ 1 View criada (v_user_permissions)';
    RAISE NOTICE '';
    RAISE NOTICE '⚠️  IMPORTANTE:';
    RAISE NOTICE '   Para funcionar, você precisa inserir roles em core.user_roles:';
    RAISE NOTICE '   INSERT INTO core.user_roles (user_id, role, loja_id) ';
    RAISE NOTICE '   VALUES (''<user_uuid>'', ''ADMIN'', NULL);';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Próximo: Execute 08_views_functions_supabase.sql';
END $$;
