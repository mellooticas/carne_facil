# 📋 GUIA DE POVOAMENTO DO SUPABASE

## ✅ Geração de SQLs Concluída!

Foram gerados **47 arquivos SQL** com todos os dados consolidados:

- **28 arquivos** de clientes (13,646 registros)
- **19 arquivos** de telefones (9,393 registros)

---

## 📁 Estrutura dos Arquivos

```
povoamento/
├── 01_schema_permissoes.sql   ← Execute PRIMEIRO
├── 02_truncate_tabelas.sql    ← Execute SEGUNDO
├── 03_inserir_lojas.sql       ← Execute TERCEIRO
├── dados/
│   ├── clientes_bloco_001.sql até clientes_bloco_028.sql
│   └── telefones_bloco_001.sql até telefones_bloco_019.sql
└── 06_validacao.sql           ← Execute POR ÚLTIMO
```

---

## 🚀 PASSO A PASSO

### 1️⃣ Configurar Schema e Permissões

```sql
-- Execute no Supabase SQL Editor:
povoamento/01_schema_permissoes.sql
```

⏱️ **Aguarde 2-3 minutos** para o cache do PostgREST atualizar.

---

### 2️⃣ Limpar Tabelas

```sql
-- Execute no Supabase SQL Editor:
povoamento/02_truncate_tabelas.sql
```

---

### 3️⃣ Inserir Lojas

```sql
-- Execute no Supabase SQL Editor:
povoamento/03_inserir_lojas.sql
```

---

### 4️⃣ Inserir Clientes (28 arquivos)

Execute **EM ORDEM** no Supabase SQL Editor:

```
povoamento/dados/clientes_bloco_001.sql
povoamento/dados/clientes_bloco_002.sql
...
povoamento/dados/clientes_bloco_028.sql
```

💡 **Dica**: Copie e cole o conteúdo de cada arquivo no SQL Editor e execute.

---

### 5️⃣ Inserir Telefones (19 arquivos)

Execute **EM ORDEM** no Supabase SQL Editor:

```
povoamento/dados/telefones_bloco_001.sql
povoamento/dados/telefones_bloco_002.sql
...
povoamento/dados/telefones_bloco_019.sql
```

---

### 6️⃣ Validar Dados

```sql
-- Execute no Supabase SQL Editor:
povoamento/06_validacao.sql
```

**Resultados esperados:**

- ✅ 13,646 clientes
- ✅ 4 lojas
- ✅ 9,393 telefones
- ✅ 0 CPFs duplicados
- ✅ 0 telefones órfãos

---

## 📊 Dados Consolidados

### Clientes por Origem

- **VIXEN**: ~9,260 clientes
- **OS**: ~4,386 clientes

### Lojas

- 042, 048, 011, 012

### Telefones

- CELULAR e FIXO
- Principal e secundário

---

## 🎯 Próximos Passos (após povoamento)

1. ✅ Validar integridade dos dados
2. 🔒 Reabilitar RLS (Row Level Security)
3. 📊 Popular vendas.vendas com dados consolidados
4. 🔗 Criar relacionamentos vendas ↔ clientes

---

## ❓ Problemas Comuns

### Erro: "relation does not exist"

→ Execute `01_schema_permissoes.sql` e aguarde 2-3 minutos.

### Erro: "permission denied"

→ Certifique-se de que RLS está desabilitado durante o povoamento.

### Erro: "duplicate key value"

→ Execute `02_truncate_tabelas.sql` para limpar dados anteriores.

---

## 📞 Suporte

Se encontrar erros durante a execução:

1. Copie a mensagem de erro completa
2. Informe qual arquivo SQL estava executando
3. Compartilhe o número do bloco que falhou
