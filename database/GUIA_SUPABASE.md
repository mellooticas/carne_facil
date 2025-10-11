# 🚀 Guia Rápido - Executar no Supabase

## 📋 Pré-requisitos

1. ✅ Conta no Supabase: https://supabase.com
2. ✅ Projeto criado no Supabase
3. ✅ Acesso ao SQL Editor

---

## 🎯 Passo a Passo

### 1️⃣ Acessar SQL Editor

1. Entre no seu projeto: https://app.supabase.com
2. No menu lateral, clique em **"SQL Editor"**
3. Clique em **"New query"**

### 2️⃣ Executar Scripts na Ordem

#### Script 1: Configuração Inicial ⚙️
```sql
-- Copie TODO o conteúdo de: 01_inicial_config_supabase.sql
-- Cole no SQL Editor
-- Clique em "RUN" ou pressione Ctrl+Enter
```

**Tempo**: ~5 segundos  
**Resultado**: Schemas, tipos e funções criados

#### Script 2: Schema CORE 👥
```sql
-- Copie TODO o conteúdo de: 02_schema_core_supabase.sql
-- Cole no SQL Editor
-- Clique em "RUN"
```

**Tempo**: ~10 segundos  
**Resultado**: Tabelas core.clientes, core.telefones, core.endereco_cliente, core.lojas, core.vendedores

#### Script 3: Schema VENDAS 💰
```sql
-- Copie TODO o conteúdo de: 03_schema_vendas_supabase.sql
-- Cole no SQL Editor
-- Clique em "RUN"
```

**Tempo**: ~10 segundos  
**Resultado**: Tabelas de vendas, recebimentos, entregas

#### Script 4: Schema OPTICA 👁️
```sql
-- Copie TODO o conteúdo de: 04_schema_optica_supabase.sql
-- Cole no SQL Editor
-- Clique em "RUN"
```

**Tempo**: ~10 segundos  
**Resultado**: Tabelas de OS, dioptrias, produtos

#### Script 5: Schema MARKETING 📢
```sql
-- Copie TODO o conteúdo de: 05_schema_marketing_supabase.sql
-- Cole no SQL Editor
-- Clique em "RUN"
```

**Tempo**: ~5 segundos  
**Resultado**: Tabelas de CRM, campanhas

#### Script 6: Schema AUDITORIA 📝
```sql
-- Copie TODO o conteúdo de: 06_schema_auditoria_supabase.sql
-- Cole no SQL Editor
-- Clique em "RUN"
```

**Tempo**: ~5 segundos  
**Resultado**: Tabelas de logs e histórico

#### Script 7: RLS Policies 🔐
```sql
-- Copie TODO o conteúdo de: 07_rls_policies_supabase.sql
-- Cole no SQL Editor
-- Clique em "RUN"
```

**Tempo**: ~30 segundos  
**Resultado**: Row Level Security configurado

#### Script 8: Views e Functions 📊
```sql
-- Copie TODO o conteúdo de: 08_views_functions_supabase.sql
-- Cole no SQL Editor
-- Clique em "RUN"
```

**Tempo**: ~15 segundos  
**Resultado**: Views materializadas e functions de relatório

---

## ✅ Verificar Instalação

### Via SQL Editor:

```sql
-- 1. Verificar schemas
SELECT schema_name 
FROM information_schema.schemata 
WHERE schema_name IN ('core', 'vendas', 'optica', 'marketing', 'auditoria');

-- 2. Verificar tabelas
SELECT schemaname, tablename 
FROM pg_tables 
WHERE schemaname IN ('core', 'vendas', 'optica', 'marketing', 'auditoria')
ORDER BY schemaname, tablename;

-- 3. Verificar tipos
SELECT typname 
FROM pg_type 
WHERE typname LIKE '%_type';

-- 4. Verificar funções
SELECT proname 
FROM pg_proc 
WHERE pronamespace::regnamespace::text IN ('core', 'vendas', 'optica', 'marketing', 'auditoria', 'public');

-- 5. Testar inserção
INSERT INTO core.lojas (codigo, nome, cidade, ativo)
VALUES ('TESTE', 'Loja Teste', 'São Paulo', true)
RETURNING *;

-- Deletar teste
DELETE FROM core.lojas WHERE codigo = 'TESTE';
```

### Via Dashboard:

1. **Database** > **Tables** - Ver todas as tabelas
2. **Database** > **Extensions** - Verificar extensões
3. **Database** > **Roles** - Ver permissões
4. **Database** > **Replication** - (Opcional) Ativar Realtime

---

## 🔑 Copiar Credenciais

### Passo 1: Ir em Settings
1. No menu lateral: **Settings**
2. Clique em **API**

### Passo 2: Copiar Keys
```bash
# URL do Projeto
SUPABASE_URL=https://SEU-PROJETO.supabase.co

# Public (Anon) Key - Use no frontend
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Service Role Key - Use APENAS no backend (NUNCA expor!)
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Passo 3: Copiar Database URL
1. Em **Settings** > **Database**
2. Na seção **Connection string**
3. Copiar **URI**:
```bash
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.SEU-PROJETO.supabase.co:5432/postgres
```

⚠️ **Substituir [PASSWORD]** pela senha do projeto!

---

## 🐍 Conectar Python

### Instalar dependências:
```bash
pip install supabase
pip install python-dotenv
```

### Criar .env:
```bash
# .env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-anon-key-aqui
DATABASE_URL=postgresql://postgres:senha@db.projeto.supabase.co:5432/postgres
```

### Código Python:
```python
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Conectar via Supabase Client (API REST)
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Exemplo: Buscar lojas
response = supabase.table("core.lojas").select("*").execute()
print(response.data)

# Exemplo: Inserir cliente
data = supabase.table("core.clientes").insert({
    "nome": "João Silva",
    "cpf": "123.456.789-00",
    "status": "ATIVO"
}).execute()

print(data)
```

---

## 🌐 Conectar FastAPI

```python
from fastapi import FastAPI, Depends
from supabase import create_client, Client
import os

app = FastAPI()

def get_supabase() -> Client:
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

@app.get("/clientes")
async def get_clientes(supabase: Client = Depends(get_supabase)):
    response = supabase.table("core.clientes").select("*").execute()
    return response.data

@app.post("/clientes")
async def create_cliente(
    nome: str,
    cpf: str,
    supabase: Client = Depends(get_supabase)
):
    data = supabase.table("core.clientes").insert({
        "nome": nome,
        "cpf": cpf
    }).execute()
    return data.data
```

---

## 📊 Testar API (Thunder Client / Postman)

### GET Clientes
```
GET https://SEU-PROJETO.supabase.co/rest/v1/core.clientes
Headers:
  apikey: SUA-ANON-KEY
  Authorization: Bearer SUA-ANON-KEY
```

### POST Cliente
```
POST https://SEU-PROJETO.supabase.co/rest/v1/core.clientes
Headers:
  apikey: SUA-ANON-KEY
  Authorization: Bearer SUA-ANON-KEY
  Content-Type: application/json
Body:
{
  "nome": "Maria Silva",
  "cpf": "987.654.321-00",
  "status": "ATIVO"
}
```

---

## ⚠️ Troubleshooting

### Erro: "permission denied for schema core"
**Solução**: Execute novamente o Script 1 (permissões)

### Erro: "relation does not exist"
**Solução**: Verifique se executou os scripts na ordem correta

### Erro: "RLS policy violation"
**Solução**: Execute o Script 7 (RLS Policies)

### Erro: "new row violates check constraint"
**Solução**: Verifique os dados enviados (CPF válido, telefone válido, etc)

---

## 🎯 Próximos Passos

1. ✅ Banco criado
2. ✅ RLS configurado
3. ✅ API testada
4. 🔄 Importar dados via ETL Python
5. 🔄 Conectar frontend
6. 🔄 Ativar Realtime (opcional)
7. 🔄 Configurar backup automático

---

## 📚 Recursos

- 📖 Docs Supabase: https://supabase.com/docs
- 🎓 Tutoriais: https://supabase.com/docs/guides/getting-started
- 💬 Discord: https://discord.supabase.com
- 🐛 Issues: https://github.com/supabase/supabase/issues

---

**Tempo total de setup**: ~15 minutos  
**Dificuldade**: Média  
**Resultado**: Banco enterprise pronto para produção! 🚀
