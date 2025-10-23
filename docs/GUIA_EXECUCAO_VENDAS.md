# 📋 Guia de Execução: Povoamento de Vendas

**Data**: 2025-10-23  
**Objetivo**: Migrar 22.579 vendas (19.930 Vixen + 2.649 OS) e 51.660 itens de venda

---

## 📊 Resumo dos Dados Gerados

| Tipo       | Origem | Quantidade | Arquivos SQL     |
| ---------- | ------ | ---------- | ---------------- |
| **Vendas** | Vixen  | 19.930     | 200 arquivos     |
| **Vendas** | OS     | 2.649      | 27 arquivos      |
| **Itens**  | Vixen  | 51.660     | 517 arquivos     |
| **TOTAL**  | -      | **74.239** | **744 arquivos** |

### 💰 Valor Total das Vendas

- **R$ 15.564.551,92** (apenas Vixen - OS sem valores)
- **Período**: Abril/2002 até Janeiro/2024
- **Ticket Médio**: ~R$ 781,00

---

## 🗂️ Estrutura de Arquivos

```
povoamento/
├── 10_criar_tabelas_vendas.sql          ← 1º Criar schema
├── 20_validacao_vendas.sql              ← Último: Validar
└── dados/vendas/
    ├── vendas_vixen_bloco_001.sql       ← 2º Executar (200 blocos)
    ├── vendas_vixen_bloco_002.sql
    ├── ... (até 200)
    ├── vendas_os_bloco_001.sql          ← 3º Executar (27 blocos)
    ├── vendas_os_bloco_002.sql
    ├── ... (até 027)
    ├── itens_venda_bloco_001.sql        ← 4º Executar (517 blocos)
    ├── itens_venda_bloco_002.sql
    └── ... (até 517)
```

---

## ⚠️ IMPORTANTE: Pré-requisitos

Antes de começar, **CERTIFIQUE-SE** que:

✅ As tabelas `core.clientes`, `core.lojas` e `core.telefones` já estão povoadas  
✅ Você possui **13.646 clientes** e **6 lojas** no banco  
✅ Backup do banco foi realizado (se necessário)

---

## 🚀 Passo a Passo de Execução

### **Passo 1: Criar Tabelas de Vendas** 🏗️

Execute no Supabase SQL Editor:

```bash
povoamento/10_criar_tabelas_vendas.sql
```

**O que este script faz:**

- Cria tabela `core.vendas` (campos: id, cliente_id, loja_id, valores, datas, etc)
- Cria tabela `core.itens_venda` (campos: id, venda_id, produto, quantidade, valores)
- Cria índices para performance
- Adiciona constraints de integridade referencial

**Tempo estimado**: 10 segundos

---

### **Passo 2: Inserir Vendas Vixen** 📦

Execute os 200 arquivos **EM ORDEM NUMÉRICA**:

```bash
povoamento/dados/vendas/vendas_vixen_bloco_001.sql
povoamento/dados/vendas/vendas_vixen_bloco_002.sql
...
povoamento/dados/vendas/vendas_vixen_bloco_200.sql
```

**Dica**: No Supabase SQL Editor, você pode:

1. Abrir o primeiro bloco
2. Clicar em "Run"
3. Aguardar confirmação (Success)
4. Repetir para os próximos blocos

**Tempo estimado**: 30-45 minutos (200 blocos × ~10 segundos cada)

**Progresso esperado:**

- Bloco 001-050: 5.000 vendas
- Bloco 051-100: 5.000 vendas
- Bloco 101-150: 5.000 vendas
- Bloco 151-200: 4.930 vendas

---

### **Passo 3: Inserir Vendas OS** 📦

Execute os 27 arquivos **EM ORDEM NUMÉRICA**:

```bash
povoamento/dados/vendas/vendas_os_bloco_001.sql
povoamento/dados/vendas/vendas_os_bloco_002.sql
...
povoamento/dados/vendas/vendas_os_bloco_027.sql
```

**Tempo estimado**: 3-5 minutos (27 blocos)

---

### **Passo 4: Inserir Itens de Venda** 📦

Execute os 517 arquivos **EM ORDEM NUMÉRICA**:

```bash
povoamento/dados/vendas/itens_venda_bloco_001.sql
povoamento/dados/vendas/itens_venda_bloco_002.sql
...
povoamento/dados/vendas/itens_venda_bloco_517.sql
```

**⚠️ ATENÇÃO**: Este é o passo mais demorado!

**Tempo estimado**: 60-90 minutos (517 blocos × ~8 segundos cada)

**Dica para acelerar**:

- Execute em lotes de 50 arquivos
- Monitore o progresso pelo console do Supabase
- Verifique se não há erros antes de continuar

---

### **Passo 5: Validar Dados** ✅

Execute as queries de validação:

```bash
povoamento/20_validacao_vendas.sql
```

**O que este script valida:**

1. ✅ Total de vendas (esperado: 22.579)
2. ✅ Total de itens (esperado: 51.660)
3. ✅ Integridade referencial (0 órfãos)
4. ✅ Duplicações (0 duplicados)
5. ✅ Distribuição por loja
6. ✅ Distribuição por período
7. ✅ Top clientes e produtos

**Tempo estimado**: 1-2 minutos

---

## 📊 Resultados Esperados da Validação

### 1. Contagem Geral

| Tabela      | Total  | Clientes Únicos | Valor Total      |
| ----------- | ------ | --------------- | ---------------- |
| vendas      | 22.579 | ~8.000          | R$ 15.564.551,92 |
| itens_venda | 51.660 | -               | -                |

### 2. Vendas por Origem

| Origem | Total  | %     |
| ------ | ------ | ----- |
| VIXEN  | 19.930 | 88,3% |
| OS     | 2.649  | 11,7% |

### 3. Vendas por Loja

| Loja | Nome        | Total Vendas |
| ---- | ----------- | ------------ |
| 042  | Mauá        | ~7.000       |
| 048  | Suzano      | ~6.000       |
| 011  | São Mateus  | ~4.000       |
| 012  | Suzano 2    | ~3.000       |
| 009  | Perus       | ~1.500       |
| 010  | Rio Pequeno | ~1.000       |

### 4. Integridade Referencial

| Validação          | Resultado Esperado |
| ------------------ | ------------------ |
| Vendas sem cliente | ✅ 0               |
| Vendas sem loja    | ✅ 0               |
| Itens sem venda    | ✅ 0               |
| Vendas duplicadas  | ✅ 0               |

---

## 🐛 Possíveis Erros e Soluções

### **Erro 1: "relation does not exist"**

**Causa**: Tabelas de vendas não foram criadas

**Solução**: Execute o script `10_criar_tabelas_vendas.sql`

---

### **Erro 2: "foreign key violation" (23503)**

**Causa**: Cliente ou loja referenciados não existem

**Solução**:

1. Verifique se todas as lojas estão inseridas (6 lojas)
2. Verifique se todos os clientes estão inseridos (13.646 clientes)
3. Execute novamente o script de clientes se necessário

---

### **Erro 3: "duplicate key value" (23505)**

**Causa**: Tentativa de inserir venda duplicada

**Solução**:

1. Verifique se já executou este bloco anteriormente
2. Pule para o próximo bloco
3. Se o erro persistir, verifique a constraint `idx_vendas_origem_id_legado`

---

### **Erro 4: Timeout no Supabase**

**Causa**: Bloco SQL muito grande ou banco lento

**Solução**:

1. Aguarde alguns segundos e tente novamente
2. Reduza o BATCH_SIZE no script Python e regenere os SQLs
3. Execute em horários de menor carga

---

## 📈 Métricas de Qualidade

Após a execução, você deve ter:

✅ **22.579 vendas** inseridas  
✅ **51.660 itens** vinculados às vendas  
✅ **0 registros órfãos** (integridade referencial perfeita)  
✅ **0 duplicações** de vendas  
✅ **~95% match** entre vendas e clientes migrados  
✅ **Período completo**: 2002-2024 (22 anos de histórico)

---

## 🎯 Próximos Passos

Após concluir o povoamento de vendas:

1. **Migrar Movimentações Financeiras** (carne_acordo, trans_financ)
2. **Criar Views de Análise** (vendas por período, top produtos, etc)
3. **Configurar RLS Policies** (segurança de acesso)
4. **Indexar campos de busca** (otimização)
5. **Criar Dashboard no Frontend** (visualização de dados)

---

## 📝 Notas Importantes

### Vendas sem Cliente (⚠️ ~1.500 excluídas)

- **Vixen**: 832 vendas sem `id_cliente` válido
- **OS**: 711 vendas sem match com clientes migrados
- **Total**: 1.543 vendas (~6,4%) não migraram por falta de cliente

### Itens sem Venda (⚠️ ~10.700 excluídos)

- 10.726 itens (~17,2%) não puderam ser vinculados a uma venda válida
- Causa provável: vendas antigas excluídas ou inconsistências nos dados originais

### Vendas OS Simplificadas

- Vendas OS possuem apenas dados básicos (loja, cliente, nro_dav)
- Não possuem valores, datas detalhadas ou vendedores
- Servem apenas para registrar a ordem de serviço

---

## ✅ Checklist de Execução

- [ ] Backup do banco realizado
- [ ] Pré-requisitos verificados (clientes e lojas povoados)
- [ ] Script `10_criar_tabelas_vendas.sql` executado
- [ ] 200 blocos de vendas Vixen executados
- [ ] 27 blocos de vendas OS executados
- [ ] 517 blocos de itens de venda executados
- [ ] Script `20_validacao_vendas.sql` executado
- [ ] Resultados validados e conferidos
- [ ] Documentação atualizada

---

**Boa execução! 🚀**

Se encontrar problemas, consulte a seção de erros acima ou entre em contato.
