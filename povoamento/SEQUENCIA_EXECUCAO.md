# 🎯 SEQUÊNCIA DE EXECUÇÃO - Schema Marketing

## ⚡ OPÇÃO 1: Execução Automática (RECOMENDADO)

### Um único comando executa tudo:

```sql
\i 68B_EXECUTAR_PIPELINE_MARKETING_INTEGRADO.sql
```

**Tempo**: 5-10 minutos  
**Dificuldade**: ⭐☆☆☆☆  
**O que faz**: Executa automaticamente os scripts 62 → 63 → [PAUSE CSV] → 64 → 70 → 69

---

## 📋 OPÇÃO 2: Execução Manual (Passo a Passo)

### Execute APENAS estes scripts NA ORDEM:

### **Passo 1**: Criar Canais

```sql
\i 62_CRIAR_TABELA_CANAIS.sql
```

✅ Cria `marketing.canais_aquisicao` com 14 canais normalizados

---

### **Passo 2**: Criar Staging

```sql
\i 63_CRIAR_STAGING_MARKETING_VIXEN.sql
```

✅ Cria `staging.marketing_origens_vixen` para importar CSV

---

### **Passo 3**: ⏸️ IMPORTAR CSV (MANUAL)

**Via DBeaver**:

1. Clique direito em `staging.marketing_origens_vixen`
2. Import Data
3. Selecione `vendas_os_completo.csv`
4. Delimiter: `,` | Header: YES | Encoding: UTF-8
5. Execute

**Via SQL** (se tiver permissões):

```sql
COPY staging.marketing_origens_vixen (
    os_n, loja, data_de_compra, consultor, venda,
    nome, cpf, como_conheceu_raw, prev_de_entr, total
)
FROM 'd:/projetos/carne_facil/povoamento/dados/csv/vendas_os_completo.csv'
DELIMITER ',' CSV HEADER ENCODING 'UTF8';
```

✅ Importa ~6.100 registros

---

### **Passo 4**: Normalizar Dados

```sql
\i 64_NORMALIZAR_COMO_CONHECEU.sql
```

✅ Cria função de normalização  
✅ Mapeia valores brutos → canais normalizados  
✅ Popula campo `canal_normalizado_id`

---

### **Passo 5**: Integrar com cliente_info

```sql
\i 70_INTEGRAR_COM_CLIENTE_INFO.sql
```

✅ Cria `marketing.clientes_canal_origem` (tabela auxiliar)  
✅ Vincula por CPF com `core.clientes`  
✅ Vincula OSs quando possível  
✅ Popula/atualiza `marketing.cliente_info`:

- `segmento` = nome do canal
- `tags` = [categoria, código]
- `observacoes` = origem original

---

### **Passo 6**: Criar Views (OPCIONAL)

```sql
\i 69_CRIAR_VIEWS_MARKETING.sql
```

✅ Cria 8 views analíticas  
✅ Dashboard executivo  
✅ Rankings e relatórios

---

## 📊 Resumo da Sequência

```
62_CRIAR_TABELA_CANAIS.sql          ← Passo 1
         ↓
63_CRIAR_STAGING_MARKETING_VIXEN.sql ← Passo 2
         ↓
   [IMPORTAR CSV]                    ← Passo 3 (MANUAL)
         ↓
64_NORMALIZAR_COMO_CONHECEU.sql      ← Passo 4
         ↓
70_INTEGRAR_COM_CLIENTE_INFO.sql     ← Passo 5 ⭐
         ↓
69_CRIAR_VIEWS_MARKETING.sql         ← Passo 6 (opcional)
```

---

## ❌ Scripts que NÃO precisa executar

### ❌ `61_ANALISE_DADOS_MARKETING.sql`

**Por quê**: Apenas análise/diagnóstico. Não cria nada.  
**Quando usar**: Se quiser investigar a estrutura antes de começar.

### ❌ `65_CRIAR_TABELA_CLIENTES_ORIGEM.sql`

**Por quê**: Abordagem antiga (criava tabela separada).  
**Substituído por**: Script 70 que integra com `cliente_info`

### ❌ `66_POPULAR_CLIENTES_ORIGEM.sql`

**Por quê**: Populava a tabela antiga `clientes_origem`.  
**Substituído por**: Script 70 (integração com `cliente_info`)

### ❌ `67_VALIDAR_MARKETING.sql`

**Por quê**: Validações da abordagem antiga.  
**Substituído por**: Validações no próprio script 70

### ❌ `68_EXECUTAR_PIPELINE_MARKETING_COMPLETO.sql`

**Por quê**: Script mestre da abordagem antiga.  
**Substituído por**: `68B_EXECUTAR_PIPELINE_MARKETING_INTEGRADO.sql`

---

## ✅ Scripts ATIVOS (Use estes)

| #       | Script                                              | Status             | Descrição                |
| ------- | --------------------------------------------------- | ------------------ | ------------------------ |
| 62      | `62_CRIAR_TABELA_CANAIS.sql`                        | ✅ USAR            | Cria canais normalizados |
| 63      | `63_CRIAR_STAGING_MARKETING_VIXEN.sql`              | ✅ USAR            | Cria staging             |
| 64      | `64_NORMALIZAR_COMO_CONHECEU.sql`                   | ✅ USAR            | Normaliza dados          |
| **70**  | **`70_INTEGRAR_COM_CLIENTE_INFO.sql`**              | ✅ **USAR**        | **Integração principal** |
| 69      | `69_CRIAR_VIEWS_MARKETING.sql`                      | ✅ USAR (opcional) | Views analíticas         |
| **68B** | **`68B_EXECUTAR_PIPELINE_MARKETING_INTEGRADO.sql`** | ⭐ **RECOMENDADO** | **Script mestre**        |

---

## 🎯 Recomendação Final

### Para implementar AGORA no banco:

```sql
-- Opção A: Automático (mais fácil)
\i 68B_EXECUTAR_PIPELINE_MARKETING_INTEGRADO.sql

-- Opção B: Manual (se preferir controle)
\i 62_CRIAR_TABELA_CANAIS.sql
\i 63_CRIAR_STAGING_MARKETING_VIXEN.sql
-- [IMPORTAR CSV AQUI]
\i 64_NORMALIZAR_COMO_CONHECEU.sql
\i 70_INTEGRAR_COM_CLIENTE_INFO.sql
\i 69_CRIAR_VIEWS_MARKETING.sql  -- opcional
```

---

## 📦 Checklist de Validação

Após executar, verificar:

```sql
-- 1. Canais criados?
SELECT COUNT(*) FROM marketing.canais_aquisicao;
-- Esperado: 14

-- 2. CSV importado?
SELECT COUNT(*) FROM staging.marketing_origens_vixen;
-- Esperado: ~6100

-- 3. Dados normalizados?
SELECT COUNT(*) FROM staging.marketing_origens_vixen
WHERE processado = true AND canal_normalizado_id IS NOT NULL;
-- Esperado: ~6100 (98%+)

-- 4. Origens mapeadas?
SELECT COUNT(*) FROM marketing.clientes_canal_origem;
-- Esperado: ~3000-4000 (depende de CPFs válidos)

-- 5. cliente_info integrado?
SELECT COUNT(*) FROM marketing.cliente_info
WHERE tags && ARRAY['MARKETING', 'INDICACAO', 'ORGANICO', 'INTERNO'];
-- Esperado: mesmo número do item 4

-- 6. View funcionando?
SELECT * FROM marketing.v_clientes_origem_integrada LIMIT 5;
-- Esperado: Retornar dados
```

---

## 🆘 Em Caso de Dúvida

**Use a Opção 1** (script mestre `68B`):

- Automático
- Testado
- Inclui validações
- Mostra progresso

**Tempo total**: 5-10 minutos  
**Complexidade**: Baixa

---

**Status**: ✅ Pronto para produção  
**Scripts ativos**: 5 (+ 1 mestre)  
**Scripts obsoletos**: 5 (ignorar)
