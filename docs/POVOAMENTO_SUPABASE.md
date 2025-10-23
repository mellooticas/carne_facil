# 🚀 GUIA COMPLETO: Povoamento do Banco Supabase

## ✅ Resumo do que temos pronto:

- **13,646 clientes** unificados (Vixen + OSs)
- **29,441 vendas** enriquecidas com id_cliente (66.2% de cobertura)
- **Schema SQL** completo gerado
- **Script Python** de migração criado

---

## 📋 Passo a Passo para Povoar o Banco

### ETAPA 1: Criar Tabelas no Supabase (5 min)

1. **Abra o SQL Editor do Supabase:**

   ```
   https://supabase.com/dashboard/project/jrhevexrzaoeyhmpwvgs/editor
   ```

2. **Crie uma Nova Query:**

   - Clique em "+ New Query" (ou "SQL Editor" → "New Query")

3. **Cole o SQL do schema:**
   - O arquivo está em: `scripts/supabase_schema.sql`
   - Ou copie abaixo:

```sql
-- Script gerado automaticamente em scripts/supabase_schema.sql
-- Execute no SQL Editor do Supabase
```

4. **Execute o SQL:**

   - Clique em "Run" ou pressione `Ctrl+Enter`
   - Verifique se todas as tabelas foram criadas sem erros

5. **Confirme as tabelas:**
   - Vá em "Table Editor" no menu lateral
   - Deve ver: `dim_cliente`, `dim_loja`, `dim_forma_pagto`, `f_vendas`, `f_pagamentos`

---

### ETAPA 2: Executar Script de Migração (10-15 min)

Após criar as tabelas, execute:

```bash
cd /d/projetos/carne_facil
.venv/Scripts/python.exe scripts/migrar_para_supabase.py
```

O script irá:

1. ✅ Conectar ao Supabase
2. ✅ Importar 13,646 clientes (dim_cliente)
3. ✅ Importar ~29,441 vendas (f_vendas)
4. ✅ Criar views analíticas
5. ✅ Gerar relatório JSON

**Tempo estimado:** 10-15 minutos dependendo da conexão

---

### ETAPA 3: Criar Views Analíticas (2 min)

Depois da importação, execute as views:

1. **Abra novamente o SQL Editor**
2. **Cole o SQL das views:**
   - Arquivo: `scripts/supabase_views.sql`
3. **Execute**
4. **Verifique:** As views devem aparecer em "Table Editor" → "Views"

Views criadas:

- `vw_vendas_por_cliente` - Resumo de vendas por cliente
- `vw_vendas_por_loja` - Resumo por loja
- `vw_vendas_por_mes` - Evolução mensal
- `vw_clientes_ativos` - Clientes com compras nos últimos 12 meses

---

## 📊 Estrutura do Banco Após Migração

```
Supabase Database
├── DIMENSÕES
│   ├── dim_cliente (13,646 registros)
│   │   ├── id_cliente (PK)
│   │   ├── nome, cpf, telefone1, telefone2, email
│   │   └── origem (VIXEN ou OS)
│   │
│   ├── dim_loja (4 registros)
│   │   ├── id_loja (PK): '042', '048', '011', '012'
│   │   └── nome_loja, cidade, estado
│   │
│   └── dim_forma_pagto (5 registros)
│       ├── codigo_forma_pagto (PK): 'DN', 'PIX', 'CTD', 'CTC', 'OUT'
│       └── descricao, tipo
│
├── FATOS
│   ├── f_vendas (~29,441 registros)
│   │   ├── id_venda (PK auto-increment)
│   │   ├── id_cliente (FK → dim_cliente)
│   │   ├── id_loja (FK → dim_loja)
│   │   ├── nro_dav, data_venda
│   │   ├── vl_total, vl_adiantamento, qtd_itens
│   │   └── origem_dados (LISTA_DAV ou CONF_DAV)
│   │
│   └── f_pagamentos (a implementar depois)
│
└── VIEWS ANALÍTICAS
    ├── vw_vendas_por_cliente
    ├── vw_vendas_por_loja
    ├── vw_vendas_por_mes
    └── vw_clientes_ativos
```

---

## 🔍 Consultas SQL Úteis Após Importação

### 1. Verificar quantos registros foram importados:

```sql
SELECT
  'dim_cliente' as tabela, COUNT(*) as registros FROM dim_cliente
UNION ALL
SELECT 'dim_loja', COUNT(*) FROM dim_loja
UNION ALL
SELECT 'f_vendas', COUNT(*) FROM f_vendas;
```

### 2. Top 10 clientes que mais compraram:

```sql
SELECT * FROM vw_vendas_por_cliente
ORDER BY total_vendido DESC
LIMIT 10;
```

### 3. Vendas por loja:

```sql
SELECT * FROM vw_vendas_por_loja
ORDER BY total_vendido DESC;
```

### 4. Evolução de vendas nos últimos 12 meses:

```sql
SELECT * FROM vw_vendas_por_mes
WHERE mes_ano >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY mes_ano;
```

### 5. Clientes sem vendas (cadastrados mas não compraram):

```sql
SELECT c.id_cliente, c.nome, c.cpf, c.origem
FROM dim_cliente c
LEFT JOIN f_vendas v ON c.id_cliente = v.id_cliente
WHERE v.id_venda IS NULL;
```

---

## ⚡ Próximas Etapas (Depois da Importação)

### PRIORIDADE ALTA:

1. **Enriquecer CXS V2** (~6,521 vendas sem id_cliente)

   - Usar fuzzy matching de nomes
   - Ou extrair CPF dos arquivos originais
   - Aumentaria cobertura para ~68-70%

2. **Importar f_pagamentos**
   - Dados de trans_financ e mov_cx
   - Relacionar com f_vendas quando possível

### PRIORIDADE MÉDIA:

3. **Preencher dim_data** (calendário)

   - Gerar datas de 2015-01-01 até hoje + 1 ano
   - Marcar feriados brasileiros
   - Marcar fins de semana e dias úteis

4. **Configurar RLS (Row Level Security)**

   - Definir políticas de acesso
   - Segurança por usuário/role

5. **Criar dashboards no Metabase/Grafana**
   - Conectar ao Supabase via PostgreSQL
   - Criar visualizações

---

## 🐛 Troubleshooting

### Erro: "Could not find the table 'public.dim_cliente'"

**Solução:** Execute primeiro o `supabase_schema.sql` no SQL Editor

### Erro: "KeyError: 'data_venda' not in index"

**Solução:** Script foi atualizado para usar colunas corretas. Use versão mais recente.

### Erro: "duplicate key value violates unique constraint"

**Solução:** Tabela já tem dados. Limpe antes:

```sql
TRUNCATE TABLE f_vendas CASCADE;
TRUNCATE TABLE dim_cliente CASCADE;
```

### Importação muito lenta

**Solução:**

- Aumente batch_size no script (atual: 500)
- Verifique conexão de internet
- Execute em horário de menor tráfego

---

## 📈 Métricas Esperadas Após Importação

| Métrica            | Valor Esperado                |
| ------------------ | ----------------------------- |
| Total clientes     | ~13,646                       |
| Clientes Vixen     | ~9,260 (68%)                  |
| Clientes OS        | ~4,386 (32%)                  |
| Total vendas       | ~29,441                       |
| Vendas com cliente | ~29,441 (100% das importadas) |
| Cobertura geral    | ~66% (sem CXS V2)             |
| Ticket médio       | ~R$ 1,500 - 3,000             |
| Lojas ativas       | 4 (042, 048, 011, 012)        |

---

## 🎯 Checklist Final

Antes de considerar a migração completa:

- [ ] SQL schema executado sem erros no Supabase
- [ ] Tabelas criadas visíveis no Table Editor
- [ ] Script de migração executado com sucesso
- [ ] dim_cliente tem ~13,646 registros
- [ ] f_vendas tem ~29,441 registros
- [ ] Views analíticas criadas e funcionando
- [ ] Consultas de teste retornando dados corretos
- [ ] Relatório JSON gerado (data/supabase_migracao_relatorio.json)

---

**Última atualização:** 2025-10-22  
**Responsável:** Script `scripts/migrar_para_supabase.py`  
**Status:** ⏳ Aguardando execução do SQL schema no Supabase
