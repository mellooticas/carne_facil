# ⚡ Importação de Vendas - Método SUPER Simplificado

**Status dos CSVs**: ✅ **ATUALIZADOS** (campos `_id_legado_cliente` e `_id_loja_codigo` para lookup)

---

## 🎯 Método Recomendado: Upload via Table Editor + SQL

### **Passo 1: Preparar no Supabase**

Execute no SQL Editor:

```sql
-- Criar tabelas de vendas
\i povoamento/10_criar_tabelas_vendas.sql
```

---

### **Passo 2: Criar Tabelas Temporárias**

Execute no SQL Editor:

```sql
CREATE TEMP TABLE tmp_vendas_vixen (
    id_legado VARCHAR(50), origem VARCHAR(20), tipo VARCHAR(30), status VARCHAR(20),
    descricao VARCHAR(100), valor_bruto DECIMAL(10,2), valor_acrescimo DECIMAL(10,2),
    valor_desconto DECIMAL(10,2), valor_liquido DECIMAL(10,2), percentual_adiantamento DECIMAL(5,2),
    valor_adiantamento DECIMAL(10,2), data_venda TIMESTAMP, data_previsao_entrega DATE,
    data_entrega DATE, id_vendedor VARCHAR(50), nome_vendedor VARCHAR(200), id_operador VARCHAR(50),
    nome_operador VARCHAR(200), id_caixa VARCHAR(50), eh_garantia BOOLEAN, meios_contato VARCHAR(100),
    mes_referencia VARCHAR(7), arquivo_origem VARCHAR(100), _id_legado_cliente VARCHAR(50), _id_loja_codigo VARCHAR(10)
);

CREATE TEMP TABLE tmp_vendas_os (
    id_legado VARCHAR(50), origem VARCHAR(20), tipo VARCHAR(30), status VARCHAR(20),
    valor_liquido DECIMAL(10,2), data_venda TIMESTAMP, _id_legado_cliente VARCHAR(50), _id_loja_codigo VARCHAR(10)
);

CREATE TEMP TABLE tmp_itens_venda (
    item_numero INTEGER, id_produto VARCHAR(50), descricao_produto TEXT, modelo VARCHAR(200),
    grupo VARCHAR(100), detalhe VARCHAR(200), quantidade DECIMAL(10,3), valor_unitario DECIMAL(10,2),
    valor_total DECIMAL(10,2), mes_referencia VARCHAR(7), arquivo_origem VARCHAR(100),
    _id_legado_venda VARCHAR(50), _id_loja_codigo VARCHAR(10)
);
```

---

### **Passo 3: Importar CSVs via Table Editor**

Para cada CSV:

1. **Table Editor** → Selecione a tabela `tmp_vendas_vixen`
2. **Insert** → **Import data from CSV**
3. Selecione `povoamento/dados/csv/vendas_vixen.csv`
4. Confirme que as colunas batem
5. **Import**

Repita para:

- `tmp_vendas_os` ← `vendas_os.csv`
- `tmp_itens_venda` ← `itens_venda.csv`

---

### **Passo 4: Migrar para Tabelas Definitivas**

Execute no SQL Editor:

```sql
-- 4.1 Vendas Vixen
INSERT INTO core.vendas (
    id_legado, origem, cliente_id, loja_id, tipo, status, descricao,
    valor_bruto, valor_acrescimo, valor_desconto, valor_liquido,
    percentual_adiantamento, valor_adiantamento, data_venda,
    data_previsao_entrega, data_entrega, id_vendedor, nome_vendedor,
    id_operador, nome_operador, id_caixa, eh_garantia, meios_contato,
    mes_referencia, arquivo_origem
)
SELECT
    tv.id_legado, tv.origem,
    (SELECT id FROM core.clientes WHERE id_legado = tv._id_legado_cliente AND created_by = 'MIGRACAO_VIXEN' LIMIT 1),
    (SELECT id FROM core.lojas WHERE codigo = tv._id_loja_codigo LIMIT 1),
    tv.tipo, tv.status, tv.descricao,
    tv.valor_bruto, tv.valor_acrescimo, tv.valor_desconto, tv.valor_liquido,
    tv.percentual_adiantamento, tv.valor_adiantamento, tv.data_venda,
    tv.data_previsao_entrega, tv.data_entrega, tv.id_vendedor, tv.nome_vendedor,
    tv.id_operador, tv.nome_operador, tv.id_caixa, tv.eh_garantia, tv.meios_contato,
    tv.mes_referencia, tv.arquivo_origem
FROM tmp_vendas_vixen tv;

-- 4.2 Vendas OS
INSERT INTO core.vendas (
    id_legado, origem, cliente_id, loja_id, tipo, status, valor_liquido, data_venda
)
SELECT
    tos.id_legado, tos.origem,
    (SELECT id FROM core.clientes WHERE id_legado = tos._id_legado_cliente AND created_by = 'MIGRACAO_OS' LIMIT 1),
    (SELECT id FROM core.lojas WHERE codigo = tos._id_loja_codigo LIMIT 1),
    tos.tipo, tos.status, tos.valor_liquido, tos.data_venda
FROM tmp_vendas_os tos;

-- 4.3 Itens
INSERT INTO core.itens_venda (
    venda_id, item_numero, id_produto, descricao_produto,
    modelo, grupo, detalhe, quantidade, valor_unitario, valor_total,
    mes_referencia, arquivo_origem
)
SELECT
    (SELECT id FROM core.vendas WHERE id_legado = ti._id_legado_venda AND origem = 'VIXEN' LIMIT 1),
    ti.item_numero, ti.id_produto, ti.descricao_produto,
    ti.modelo, ti.grupo, ti.detalhe, ti.quantidade, ti.valor_unitario, ti.valor_total,
    ti.mes_referencia, ti.arquivo_origem
FROM tmp_itens_venda ti;
```

---

### **Passo 5: Validar**

```sql
-- Contar vendas
SELECT origem, COUNT(*) as total, SUM(valor_liquido) as valor_total
FROM core.vendas
GROUP BY origem;

-- Contar itens
SELECT COUNT(*) as total_itens, COUNT(DISTINCT venda_id) as vendas_com_itens
FROM core.itens_venda;

-- Verificar órfãos (deve retornar 0 em ambos)
SELECT
    (SELECT COUNT(*) FROM core.vendas v LEFT JOIN core.clientes c ON v.cliente_id = c.id WHERE c.id IS NULL) as vendas_sem_cliente,
    (SELECT COUNT(*) FROM core.itens_venda i LEFT JOIN core.vendas v ON i.venda_id = v.id WHERE v.id IS NULL) as itens_sem_venda;
```

**Esperado:**

```
vendas_vixen: 19930 | R$ 15.564.551,92
vendas_os: 2649
itens: 51660
órfãos: 0
```

---

## 📋 Checklist Rápido

- [ ] Tabelas `core.vendas` e `core.itens_venda` criadas
- [ ] Tabelas temporárias criadas
- [ ] CSV `vendas_vixen.csv` importado para `tmp_vendas_vixen`
- [ ] CSV `vendas_os.csv` importado para `tmp_vendas_os`
- [ ] CSV `itens_venda.csv` importado para `tmp_itens_venda`
- [ ] INSERT de vendas Vixen executado
- [ ] INSERT de vendas OS executado
- [ ] INSERT de itens executado
- [ ] Validação executada (0 órfãos)

---

## 🐛 Erros Comuns

| Erro                    | Causa                    | Solução                                                  |
| ----------------------- | ------------------------ | -------------------------------------------------------- |
| "column does not match" | CSV com colunas erradas  | Regere o CSV com script atualizado                       |
| "foreign key violation" | Cliente/loja não existe  | Verifique se clientes e lojas estão povoados             |
| "duplicate key"         | Vendas já importadas     | Use `ON CONFLICT DO NOTHING` ou limpe a tabela           |
| Lookup retorna NULL     | ID legado não encontrado | Verifique se `id_legado` está correto na tabela clientes |

---

## ⚡ Tempo Total

- Upload CSVs: 2-3 min
- Migração SQL: 5-10 min
- Validação: 1 min

**Total: 10-15 minutos** ⏱️

---

**Pronto! 🚀** Siga os 5 passos acima e suas vendas estarão importadas!
