# 🚀 Setup Supabase - Sistema Óticas

## 📋 Informações do Projeto

**Plataforma**: Supabase (PostgreSQL 15 + Extensões)  
**URL**: https://seu-projeto.supabase.co  
**Região**: Recomendado: São Paulo (South America East)

---

## 🎯 Características do Supabase

### ✅ O que o Supabase JÁ fornece:

1. **PostgreSQL 15+** com extensões principais
2. **auth.users** - Sistema de autenticação pronto
3. **storage.buckets** - Armazenamento de arquivos
4. **Realtime** - WebSockets para mudanças em tempo real
5. **PostgREST** - API REST automática
6. **pg_graphql** - GraphQL automático
7. **Dashboard Web** - Interface administrativa

### 🔧 Extensões já instaladas:

- ✅ `uuid-ossp` - Geração de UUIDs
- ✅ `pg_trgm` - Busca fuzzy/trigrams
- ✅ `unaccent` - Remoção de acentos
- ✅ `pgcrypto` - Criptografia
- ✅ `pgjwt` - JSON Web Tokens
- ✅ `pg_stat_statements` - Estatísticas

---

## 🏗️ Arquitetura Adaptada para Supabase

```
Supabase Database
├── 🔐 auth (schema do Supabase)
│   └── users (tabela gerenciada pelo Supabase)
│
├── 🗄️ public (schema padrão)
│   └── (evitar usar - usar schemas customizados)
│
├── 📦 storage (schema do Supabase)
│   └── buckets, objects
│
└── 📂 NOSSOS SCHEMAS:
    ├── core (clientes, lojas, vendedores)
    ├── vendas (vendas, recebimentos, entregas)
    ├── optica (OS, dioptrias, produtos)
    ├── marketing (CRM, campanhas)
    └── auditoria (logs, histórico)
```

---

## 🔐 Row Level Security (RLS)

**IMPORTANTE**: Supabase exige RLS em todas as tabelas expostas via API!

```sql
-- Habilitar RLS em uma tabela
ALTER TABLE core.clientes ENABLE ROW LEVEL SECURITY;

-- Criar políticas de acesso
CREATE POLICY "Permitir leitura para usuários autenticados"
ON core.clientes
FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Permitir inserção para usuários autenticados"
ON core.clientes
FOR INSERT
TO authenticated
WITH CHECK (true);
```

---

## 🔗 Integração com auth.users

```sql
-- Adicionar coluna de referência ao usuário Supabase
ALTER TABLE core.clientes
ADD COLUMN user_id UUID REFERENCES auth.users(id);

-- Auditoria automática com usuário Supabase
CREATE OR REPLACE FUNCTION atualizar_updated_at_supabase()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    NEW.updated_by = auth.uid()::TEXT;  -- ID do usuário Supabase
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

## 📡 Realtime (Opcional)

Ativar para tabelas que precisam de updates em tempo real:

```sql
-- Via Dashboard Supabase:
-- Database > Replication > Enable para tabelas específicas

-- Ou via SQL:
ALTER PUBLICATION supabase_realtime ADD TABLE core.clientes;
ALTER PUBLICATION supabase_realtime ADD TABLE vendas.vendas;
ALTER PUBLICATION supabase_realtime ADD TABLE optica.ordens_servico;
```

---

## 📦 Storage (para Excel, PDFs, imagens)

```sql
-- Criar bucket para uploads
INSERT INTO storage.buckets (id, name, public)
VALUES ('documentos-clientes', 'documentos-clientes', false);

-- Política de acesso ao storage
CREATE POLICY "Acesso autenticado a documentos"
ON storage.objects
FOR SELECT
TO authenticated
USING (bucket_id = 'documentos-clientes');
```

---

## 🚀 Ordem de Execução dos Scripts

1. ✅ **Supabase já instalou**: PostgreSQL + Extensões básicas
2. **Executar nossos scripts**:
   ```bash
   # No SQL Editor do Supabase Dashboard:
   
   1. 01_inicial_config_supabase.sql   # Schemas + Functions customizadas
   2. 02_schema_core.sql               # Tabelas core
   3. 03_schema_vendas.sql             # Tabelas vendas
   4. 04_schema_optica.sql             # Tabelas ótica
   5. 05_schema_marketing.sql          # Tabelas marketing
   6. 06_schema_auditoria.sql          # Tabelas auditoria
   7. 07_rls_policies.sql              # Row Level Security
   8. 08_views_functions.sql           # Views e Functions
   ```

---

## 🔑 Variáveis de Ambiente (.env)

```bash
# Supabase Config
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Database Direct Connection (para scripts Python)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.seu-projeto.supabase.co:5432/postgres
```

---

## 🐍 Conectar Python ao Supabase

### Via Supabase Client (recomendado):

```python
from supabase import create_client, Client

url = "https://seu-projeto.supabase.co"
key = "sua-anon-key"
supabase: Client = create_client(url, key)

# Inserir dados
data = supabase.table("core.clientes").insert({
    "nome": "João Silva",
    "cpf": "123.456.789-00"
}).execute()

# Buscar dados
clientes = supabase.table("core.clientes").select("*").execute()
```

### Via SQLAlchemy (para ETL):

```python
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:senha@db.projeto.supabase.co:5432/postgres"
engine = create_engine(DATABASE_URL)

# Usar pandas
import pandas as pd
df = pd.read_sql("SELECT * FROM core.clientes", engine)
```

---

## ⚠️ Diferenças Importantes vs PostgreSQL Local

| Recurso | PostgreSQL Local | Supabase |
|---------|------------------|----------|
| **Conexão** | localhost:5432 | db.projeto.supabase.co:5432 |
| **Autenticação** | Roles customizados | auth.users + RLS |
| **API REST** | Criar manualmente | Automática (PostgREST) |
| **Dashboard** | pgAdmin | Supabase Dashboard |
| **Backup** | pg_dump | Dashboard > Database > Backups |
| **Extensões** | Instalar manualmente | Já instaladas |
| **RLS** | Opcional | Obrigatório para segurança |

---

## 🛡️ Segurança no Supabase

### 1. Nunca expor service_role_key no frontend
```javascript
// ❌ ERRADO
const supabase = createClient(url, service_role_key)

// ✅ CORRETO
const supabase = createClient(url, anon_key)
```

### 2. Sempre usar RLS
```sql
-- Sem RLS = qualquer um pode acessar!
ALTER TABLE core.clientes ENABLE ROW LEVEL SECURITY;
```

### 3. Validar dados no backend
```sql
-- Constraints e checks são essenciais
ALTER TABLE core.clientes
ADD CONSTRAINT chk_cpf_valido
CHECK (validar_cpf(cpf));
```

---

## 📊 Monitoramento

### Via Dashboard:
- **Database** > Reports > Performance
- **Database** > Roles > Permissions
- **Logs** > Postgres Logs

### Via SQL:
```sql
-- Ver queries lentas
SELECT * FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Ver tamanho das tabelas
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 🎯 Próximos Passos

1. ✅ Criar projeto no Supabase
2. ✅ Copiar URL e Keys
3. ✅ Executar scripts SQL adaptados
4. ✅ Configurar RLS policies
5. ✅ Testar API via Postman/Thunder Client
6. ✅ Conectar Python (ETL)
7. ✅ Conectar FastAPI app

---

**Documentação Oficial**: https://supabase.com/docs  
**PostgreSQL no Supabase**: https://supabase.com/docs/guides/database
