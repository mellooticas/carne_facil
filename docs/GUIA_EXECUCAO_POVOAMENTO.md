# 🚀 Guia de Execução - Povoamento do Supabase

**Data:** 23/10/2025  
**Objetivo:** Limpar clientes existentes e popular com dados consolidados

---

## 📊 Situação Atual

✅ **Dados consolidados prontos:**

- 13,646 clientes unificados (Vixen 9,260 + OS 4,386)
- 29,441 vendas com id_cliente (66.2% coverage)

⚠️ **Banco Supabase atual:**

- core.clientes: **12,845 registros** (serão substituídos)
- Todas outras tabelas: **vazias**

---

## 🎯 Plano de Execução

### ✅ Etapa 1: PREPARAÇÃO (JÁ FEITO)

- [x] Mapeamento completo do banco
- [x] Verificação da estrutura core.clientes
- [x] Script de povoamento criado e ajustado

### 🔄 Etapa 2: LIMPEZA (SEM BACKUP)

**Script:** `scripts/limpar_e_povoar_supabase.py`

⚠️ **IMPORTANTE:** Não será feito backup dos 12,845 clientes existentes.

- Os dados atuais foram povoados **incorretamente**
- Precisam ser **substituídos** pelos dados consolidados corretos
- **Sem backup** pois esses dados estão errados

**O que vai acontecer:**

1. **Pedirá confirmação** antes de deletar

   - Você precisa digitar **"S"** para continuar
   - Qualquer outra tecla cancela

2. **Limpeza da tabela** core.clientes
   - Remove todos os 12,845 registros existentes (incorretos)
   - Tabela fica vazia para receber novos dados corretos

### 📥 Etapa 3: POVOAMENTO

**O que será inserido:**

1. **core.lojas** (6 lojas)

   ```
   - 009: Perus
   - 010: Rio Pequeno
   - 011: São Mateus
   - 012: Suzano 2
   - 042: Mauá
   - 048: Suzano
   ```

2. **core.clientes** (13,646 clientes)

   - Campos mapeados:
     - `id_legado`: ID original (1-13646) - rastreabilidade
     - `nome`: Nome completo (max 200 chars)
     - `nome_normalizado`: Nome lowercase
     - `cpf`: CPF formatado (000.000.000-00) se válido
     - `email`: Email válido (max 100 chars)
     - `status`: ATIVO
     - `created_by`: MIGRACAO_VIXEN ou MIGRACAO_OS
     - `version`: 1

3. **core.telefones** (estimado ~20,000 telefones)
   - Vinculados aos clientes via `cliente_id` (UUID)
   - Telefone1: marcado como principal
   - Telefone2: marcado como secundário
   - Tipo: CELULAR (11 dígitos) ou FIXO (10 dígitos)

### ✅ Etapa 4: VALIDAÇÃO

**Verificações automáticas:**

- Contagem de clientes inseridos (esperado: 13,646)
- Contagem de lojas inseridas (esperado: 6)
- Contagem de telefones inseridos
- Percentual de sucesso (mínimo 95%)

---

## 🖥️ Como Executar

### Comando:

```bash
cd /d/projetos/carne_facil
D:/projetos/carne_facil/.venv/Scripts/python.exe scripts/limpar_e_povoar_supabase.py
```

### Interação Esperada:

```
====================================================================================================
LIMPEZA E POVOAMENTO DO BANCO SUPABASE
====================================================================================================

Conectado: https://jrhevexrzaoeyhmpwvgs.supabase.co

====================================================================================================
ETAPA 1: BACKUP DOS CLIENTES EXISTENTES (12,845 registros)
====================================================================================================

[Baixando clientes existentes...]
  Baixados: 12845 registros...
[OK] Total baixado: 12845 clientes
[OK] Backup salvo em: data\backup_clientes_supabase.json
[OK] Backup CSV salvo em: data\backup_clientes_supabase.csv

====================================================================================================
ETAPA 2: LIMPEZA DE CLIENTES EXISTENTES
====================================================================================================

[ATENÇÃO] Isso vai DELETAR todos os 12,845 clientes existentes!
Backup já foi feito em: data/backup_clientes_supabase.json

Deseja continuar? (S/n): _
```

**👉 Digite "S" e pressione Enter para continuar**

---

## ⚠️ IMPORTANTE

### Antes de Executar:

1. ✅ Certifique-se que tem conexão estável com internet
2. ✅ Verifique que `.env` está configurado corretamente
3. ✅ Feche outros scripts que possam estar usando o banco

### Durante a Execução:

- ⏱️ **Tempo estimado:** 5-10 minutos
- 📊 Você verá progresso em tempo real
- ❌ Se houver erros, o script para e mostra mensagem clara

### Após a Execução:

1. Verificar no Supabase Table Editor:

   - core.clientes deve ter ~13,646 registros
   - core.lojas deve ter 4 registros
   - core.telefones deve ter registros

2. Testar queries:

   ```sql
   -- Ver clientes migrados
   SELECT created_by, COUNT(*)
   FROM core.clientes
   GROUP BY created_by;

   -- Ver clientes com telefone
   SELECT c.nome, t.numero, t.tipo
   FROM core.clientes c
   JOIN core.telefones t ON t.cliente_id = c.id
   LIMIT 10;
   ```

---

## 🆘 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'supabase'"

```bash
D:/projetos/carne_facil/.venv/Scripts/python.exe -m pip install supabase python-dotenv
```

### Erro: "Arquivo não encontrado: clientes_unificados.parquet"

Certifique-se que o arquivo existe em:

```
data/clientes/_consolidado/clientes_unificados.parquet
```

### Erro: "could not translate host name"

- Conexão externa bloqueada
- Tente de outra rede ou use VPN

### Erro: "UNIQUE constraint violation on cpf"

- Algum CPF duplicado nos dados
- Script automaticamente coloca NULL em CPFs inválidos
- Se persistir, verificar dados de entrada

### Backup não funcionou:

- **NÃO CONTINUE** sem backup!
- Baixe manualmente via SQL Editor:
  ```sql
  COPY (SELECT * FROM core.clientes) TO STDOUT WITH CSV HEADER;
  ```

---

## 📋 Checklist de Execução

- [ ] Backup automático concluído
- [ ] Confirmação "S" digitada
- [ ] Limpeza concluída (12,845 deletados)
- [ ] 4 lojas inseridas
- [ ] ~13,646 clientes inseridos (95%+ sucesso)
- [ ] Telefones inseridos
- [ ] Validação OK
- [ ] Verificação manual no Table Editor
- [ ] Queries de teste executadas

---

## 🎯 Próximos Passos (Após Clientes OK)

1. **Popular vendas.vendas**

   - Mapear lista_dav + conf_dav para vendas.vendas
   - Vincular com clientes via id_legado
   - ~29,441 vendas

2. **Popular vendas.formas_pagamento_venda**

   - Vincular formas de pagamento às vendas

3. **Popular vendas.recebimentos_carne**

   - Parcelas e recebimentos

4. **Validar integridade**
   - Foreign keys
   - Totalizadores
   - Consistência de valores

---

**Pronto para executar?** 🚀

Execute o comando acima e acompanhe o processo!
