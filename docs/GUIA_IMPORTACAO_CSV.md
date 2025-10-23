# 🚀 Guia Rápido: Importação de Vendas via CSV

**Tempo estimado**: 15-20 minutos ⏱️  
**Muito mais rápido que executar 744 SQLs!**

---

## 📂 Arquivos CSV Gerados

| Arquivo | Registros | Tamanho | Descrição |
|---------|-----------|---------|-----------|
| `vendas_vixen.csv` | 19.930 | 4.08 MB | Vendas do sistema Vixen |
| `vendas_os.csv` | 2.649 | 0.19 MB | Vendas do sistema OS |
| `itens_venda.csv` | 51.660 | 4.66 MB | Itens de todas as vendas |

**Total**: 74.239 registros | 8.93 MB

---

## 🎯 Método 1: Upload Direto via Supabase Dashboard (RECOMENDADO)

### **Passo 1: Criar as tabelas** (se ainda não existir)

No Supabase SQL Editor, execute:

```sql
povoamento/10_criar_tabelas_vendas.sql
```

---

### **Passo 2: Criar tabelas temporárias**

Execute no SQL Editor:

```sql
-- Vendas Vixen temporária
CREATE TEMP TABLE tmp_vendas_vixen (
    id_legado VARCHAR(50),
    id_legado_cliente VARCHAR(50),
    id_loja_codigo VARCHAR(10),
    origem VARCHAR(20),
    tipo VARCHAR(30),
    status VARCHAR(20),
    descricao VARCHAR(100),
    valor_bruto DECIMAL(10, 2),
    valor_acrescimo DECIMAL(10, 2),
    valor_desconto DECIMAL(10, 2),
    valor_liquido DECIMAL(10, 2),
    percentual_adiantamento DECIMAL(5, 2),
    valor_adiantamento DECIMAL(10, 2),
    data_venda TIMESTAMPTZ,
    data_previsao_entrega DATE,
    data_entrega DATE,
    id_vendedor VARCHAR(50),
    nome_vendedor VARCHAR(200),
    id_operador VARCHAR(50),
    nome_operador VARCHAR(200),
    id_caixa VARCHAR(50),
    eh_garantia BOOLEAN,
    meios_contato VARCHAR(100),
    mes_referencia VARCHAR(7),
    arquivo_origem VARCHAR(100)
);

-- Vendas OS temporária
CREATE TEMP TABLE tmp_vendas_os (
    id_legado VARCHAR(50),
    id_legado_cliente VARCHAR(50),
    id_loja_codigo VARCHAR(10),
    origem VARCHAR(20),
    tipo VARCHAR(30),
    status VARCHAR(20),
    valor_liquido DECIMAL(10, 2),
    data_venda TIMESTAMPTZ
);

-- Itens temporária
CREATE TEMP TABLE tmp_itens_venda (
    id_legado_venda VARCHAR(50),
    id_loja_codigo VARCHAR(10),
    item_numero INTEGER,
    id_produto VARCHAR(50),
    descricao_produto TEXT,
    modelo VARCHAR(200),
    grupo VARCHAR(100),
    detalhe VARCHAR(200),
    quantidade DECIMAL(10, 3),
    valor_unitario DECIMAL(10, 2),
    valor_total DECIMAL(10, 2),
    mes_referencia VARCHAR(7),
    arquivo_origem VARCHAR(100)
);
```

---

### **Passo 3: Importar CSVs via Table Editor**

#### 3.1 Importar `vendas_vixen.csv`

1. Vá para **Table Editor** → **tmp_vendas_vixen**
2. Clique em **Insert** → **Import data from CSV**
3. Selecione `povoamento/dados/csv/vendas_vixen.csv`
4. Confirme que as colunas batem com o schema
5. Clique em **Import**
6. Aguarde (~30 segundos)

#### 3.2 Importar `vendas_os.csv`

1. Vá para **Table Editor** → **tmp_vendas_os**
2. Clique em **Insert** → **Import data from CSV**
3. Selecione `povoamento/dados/csv/vendas_os.csv`
4. Confirme as colunas
5. Clique em **Import**
6. Aguarde (~5 segundos)

#### 3.3 Importar `itens_venda.csv`

1. Vá para **Table Editor** → **tmp_itens_venda**
2. Clique em **Insert** → **Import data from CSV**
3. Selecione `povoamento/dados/csv/itens_venda.csv`
4. Confirme as colunas
5. Clique em **Import**
6. Aguarde (~1 minuto)

---

### **Passo 4: Migrar dados das tabelas temporárias para definitivas**

Execute no SQL Editor:

```sql
-- 4.1 Inserir vendas Vixen
INSERT INTO core.vendas (
    id_legado, origem, cliente_id, loja_id,
    tipo, status, descricao,
    valor_bruto, valor_acrescimo, valor_desconto, valor_liquido,
    percentual_adiantamento, valor_adiantamento,
    data_venda, data_previsao_entrega, data_entrega,
    id_vendedor, nome_vendedor, id_operador, nome_operador, id_caixa,
    eh_garantia, meios_contato,
    mes_referencia, arquivo_origem
)
SELECT 
    tv.id_legado, tv.origem,
    c.id AS cliente_id, l.id AS loja_id,
    tv.tipo, tv.status, tv.descricao,
    tv.valor_bruto, tv.valor_acrescimo, tv.valor_desconto, tv.valor_liquido,
    tv.percentual_adiantamento, tv.valor_adiantamento,
    tv.data_venda, tv.data_previsao_entrega, tv.data_entrega,
    tv.id_vendedor, tv.nome_vendedor, tv.id_operador, tv.nome_operador, tv.id_caixa,
    tv.eh_garantia, tv.meios_contato,
    tv.mes_referencia, tv.arquivo_origem
FROM tmp_vendas_vixen tv
INNER JOIN core.clientes c 
    ON c.id_legado = tv.id_legado_cliente 
    AND c.created_by = 'MIGRACAO_VIXEN'
INNER JOIN core.lojas l 
    ON l.codigo = tv.id_loja_codigo;

-- 4.2 Inserir vendas OS
INSERT INTO core.vendas (
    id_legado, origem, cliente_id, loja_id,
    tipo, status, valor_liquido, data_venda
)
SELECT 
    tos.id_legado, tos.origem,
    c.id AS cliente_id, l.id AS loja_id,
    tos.tipo, tos.status, tos.valor_liquido, tos.data_venda
FROM tmp_vendas_os tos
INNER JOIN core.clientes c 
    ON c.id_legado = tos.id_legado_cliente 
    AND c.created_by = 'MIGRACAO_OS'
INNER JOIN core.lojas l 
    ON l.codigo = tos.id_loja_codigo;

-- 4.3 Inserir itens
INSERT INTO core.itens_venda (
    venda_id, item_numero, id_produto, descricao_produto,
    modelo, grupo, detalhe,
    quantidade, valor_unitario, valor_total,
    mes_referencia, arquivo_origem
)
SELECT 
    v.id AS venda_id,
    ti.item_numero, ti.id_produto, ti.descricao_produto,
    ti.modelo, ti.grupo, ti.detalhe,
    ti.quantidade, ti.valor_unitario, ti.valor_total,
    ti.mes_referencia, ti.arquivo_origem
FROM tmp_itens_venda ti
INNER JOIN core.vendas v 
    ON v.id_legado = ti.id_legado_venda 
    AND v.origem = 'VIXEN';
```

---

### **Passo 5: Validar**

Execute no SQL Editor:

```sql
-- Total por origem
SELECT origem, COUNT(*) as total, SUM(valor_liquido) as valor_total
FROM core.vendas
GROUP BY origem;

-- Total de itens
SELECT COUNT(*) as total_itens, COUNT(DISTINCT venda_id) as vendas_com_itens
FROM core.itens_venda;

-- Verificar integridade (deve retornar 0 em ambos)
SELECT 'Vendas sem cliente' as check, COUNT(*) as total
FROM core.vendas v
LEFT JOIN core.clientes c ON v.cliente_id = c.id
WHERE c.id IS NULL

UNION ALL

SELECT 'Itens sem venda' as check, COUNT(*) as total
FROM core.itens_venda i
LEFT JOIN core.vendas v ON i.venda_id = v.id
WHERE v.id IS NULL;
```

**Resultado esperado:**
- Vendas VIXEN: 19.930
- Vendas OS: 2.649
- Itens: 51.660
- Órfãos: 0

---

## 🎯 Método 2: Via psql (Linha de Comando)

Se tiver acesso direto ao PostgreSQL:

```bash
# 1. Conectar ao Supabase
psql "postgresql://postgres:[SENHA]@db.[PROJETO].supabase.co:5432/postgres"

# 2. Criar tabelas temporárias (mesmo SQL do Método 1, Passo 2)

# 3. Importar CSVs
\copy tmp_vendas_vixen FROM 'D:/projetos/carne_facil/povoamento/dados/csv/vendas_vixen.csv' DELIMITER ',' CSV HEADER;
\copy tmp_vendas_os FROM 'D:/projetos/carne_facil/povoamento/dados/csv/vendas_os.csv' DELIMITER ',' CSV HEADER;
\copy tmp_itens_venda FROM 'D:/projetos/carne_facil/povoamento/dados/csv/itens_venda.csv' DELIMITER ',' CSV HEADER;

# 4. Executar INSERTs (mesmo SQL do Método 1, Passo 4)
```

---

## 🎯 Método 3: Via Script SQL Completo

Execute o arquivo:

```sql
povoamento/11_importar_vendas_csv.sql
```

Este arquivo contém **TODOS** os comandos acima em sequência.

---

## ✅ Checklist de Execução

- [ ] Tabelas `core.vendas` e `core.itens_venda` criadas
- [ ] Clientes e lojas já povoados (13.646 e 6)
- [ ] CSVs gerados (3 arquivos)
- [ ] Tabelas temporárias criadas
- [ ] CSVs importados para tabelas temp
- [ ] Vendas Vixen inseridas (19.930)
- [ ] Vendas OS inseridas (2.649)
- [ ] Itens inseridos (51.660)
- [ ] Validação executada (0 órfãos)
- [ ] Tabelas temporárias limpas

---

## 🐛 Troubleshooting

### Erro: "relation tmp_vendas_vixen does not exist"
**Solução**: Execute o Passo 2 para criar as tabelas temporárias

### Erro: "duplicate key value violates unique constraint"
**Solução**: Vendas já foram importadas. Limpe a tabela ou adicione `ON CONFLICT DO NOTHING`

### Erro: "foreign key violation"
**Solução**: Verifique se clientes e lojas estão povoados corretamente

### Import muito lento
**Solução**: Use psql ao invés do Table Editor para arquivos grandes

---

## 🎉 Resultado Final

Após conclusão, você terá:

✅ **22.579 vendas** no banco (2002-2024)  
✅ **51.660 itens** vinculados  
✅ **R$ 15,5 milhões** em histórico  
✅ **100% integridade** referencial  
✅ **15-20 minutos** de execução (vs 2-3 horas com SQLs)

---

**Pronto para começar! 🚀**

Escolha o método que preferir e siga o passo a passo.
