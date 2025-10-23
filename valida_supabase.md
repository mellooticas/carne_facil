# Validação de Dados - Supabase Carnê Fácil

Este documento serve para registrar os testes de validação dos dados povoados no Supabase. Copie e cole os resultados das queries abaixo após executar no Supabase SQL Editor.

---

## 1. Contagem de clientes por origem

```sql
SELECT created_by, COUNT(*) AS total
FROM core.clientes
GROUP BY created_by;


Success. No rows returned



```

**Resultado:**

---

## 2. Total de clientes

```sql
SELECT COUNT(*) AS total_clientes FROM core.clientes;


| total_clientes |
| -------------- |
| 0              |
```

**Resultado:**

---

## 3. Lojas inseridas

```sql
SELECT * FROM core.lojas;

Success. No rows returned



```

**Resultado:**

---

## 4. Telefones por tipo

```sql
SELECT tipo, COUNT(*) AS total
FROM core.telefones
GROUP BY tipo;

Success. No rows returned



```

**Resultado:**

---

## 5. CPFs duplicados

```sql
SELECT cpf, COUNT(*) AS qtd
FROM core.clientes
WHERE cpf IS NOT NULL AND cpf <> ''
GROUP BY cpf
HAVING COUNT(*) > 1;

Success. No rows returned



```

**Resultado:**

---

## 6. Telefones sem cliente correspondente

```sql
SELECT t.*
FROM core.telefones t
LEFT JOIN core.clientes c ON t.cliente_id = c.id
WHERE c.id IS NULL;


Success. No rows returned



```

**Resultado:**

---

## 7. Total de telefones

```sql
SELECT COUNT(*) AS total_telefones FROM core.telefones;


| total_telefones |
| --------------- |
| 0               |
```

**Resultado:**

---

## Observações

(Adicione aqui qualquer observação, erro ou comportamento inesperado)
