# 🔧 Correção: Coluna `ativo` Faltante na Tabela `telefones`

## 🐛 Problema Identificado

Ao executar os SQLs de povoamento de telefones, ocorreu o erro:

```sql
ERROR: 42703: column "ativo" of relation "telefones" does not exist
LINE 2: INSERT INTO core.telefones (cliente_id, numero, tipo, principal, ativo)
```

## 🔍 Causa

A tabela `core.telefones` foi criada **SEM a coluna `ativo`**, mas:
- O script `00_criar_tabelas.sql` **inclui** a coluna `ativo`
- Os scripts de INSERT de telefones **tentam inserir** dados nesta coluna

**Hipótese**: A tabela foi criada manualmente ou com um script antigo que não incluía esta coluna.

## ✅ Solução

Execute o arquivo **`02_adicionar_coluna_ativo_telefones.sql`** antes de inserir telefones.

Este script:
1. Verifica se a coluna já existe
2. Se não existir, adiciona: `ALTER TABLE core.telefones ADD COLUMN ativo BOOLEAN DEFAULT TRUE`
3. É seguro executar múltiplas vezes (idempotente)

## 📋 Ordem de Execução Corrigida

```
1. ✅ 00_criar_tabelas.sql (tabelas básicas)
2. ✅ 03_inserir_lojas.sql (6 lojas)
3. ✅ clientes_bloco_001.sql até clientes_bloco_069.sql (13.646 clientes)
4. 🔧 02_adicionar_coluna_ativo_telefones.sql (NOVO - adiciona coluna faltante)
5. ✅ telefones_bloco_001.sql até telefones_bloco_047.sql (9.393 telefones)
6. ✅ 06_validacao.sql (validação)
```

## 🎯 Status

- ✅ **Lojas**: 6 inseridas
- ✅ **Clientes**: 13.646 inseridos
- 🔧 **Telefones**: Aguardando correção da coluna
- ⏳ **Próximo passo**: Executar `02_adicionar_coluna_ativo_telefones.sql`
