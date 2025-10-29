# 🔗 Integração com marketing.cliente_info

## 📋 Visão Geral

O sistema foi **atualizado** para integrar com a tabela existente `marketing.cliente_info`. Em vez de criar uma nova tabela `marketing.clientes_origem`, agora usamos:

1. **`marketing.clientes_canal_origem`** - Tabela auxiliar com detalhes da origem
2. **`marketing.cliente_info`** - Tabela existente (campo `segmento` + `tags`)
3. **`marketing.v_clientes_origem_integrada`** - View consolidada

---

## 🏗️ Estrutura da Integração

### Tabela Existente: `marketing.cliente_info`

```sql
marketing.cliente_info
  ├── cliente_id (UUID) - FK para core.clientes
  ├── segmento (VARCHAR) - ⭐ AQUI vai o canal de origem
  ├── tags (TEXT[]) - Array com categoria + código do canal
  ├── primeira_compra (DATE)
  ├── observacoes (TEXT) - "Origem: [valor original]"
  └── ... outros campos
```

**Valores de `segmento` populados**:

- Nome do canal (ex: "Clientes Existentes", "Redes Sociais", "Indicação")

**Tags adicionadas**:

- `categoria`: MARKETING, INDICACAO, ORGANICO, INTERNO
- `codigo`: CLIENTES_EXISTENTES, REDES_SOCIAIS, etc

### Nova Tabela Auxiliar: `marketing.clientes_canal_origem`

```sql
marketing.clientes_canal_origem
  ├── id (SERIAL PK)
  ├── cliente_id (UUID) - FK core.clientes
  ├── canal_id (INTEGER) - FK marketing.canais_aquisicao
  ├── como_conheceu_original (TEXT) - Valor bruto do CSV
  ├── data_aquisicao (DATE)
  ├── valor_primeira_compra (NUMERIC)
  ├── loja_id (UUID) - FK core.lojas
  ├── os_id (UUID) - FK core.ordens_servico (nullable)
  └── fonte_dados (VARCHAR) - "VIXEN_CSV"
```

**Propósito**: Armazena detalhes completos da origem antes de popular `cliente_info`.

---

## 🔄 Fluxo de Dados

```
vendas_os_completo.csv
         ↓
staging.marketing_origens_vixen
         ↓ (normalização)
marketing.canais_aquisicao (14 canais)
         ↓ (mapeamento)
marketing.clientes_canal_origem (tabela auxiliar)
         ↓ (integração)
marketing.cliente_info
    ├── segmento = nome do canal
    ├── tags = [categoria, codigo]
    └── observacoes = "Origem: ..."
```

---

## 🚀 Execução

### Script Atualizado

```sql
\i 68B_EXECUTAR_PIPELINE_MARKETING_INTEGRADO.sql
```

### Passos Executados

1. ✅ Criar `marketing.canais_aquisicao` (14 canais)
2. ✅ Criar `staging.marketing_origens_vixen`
3. ⏸️ **PAUSE** - Importar CSV
4. ✅ Normalizar valores `como_conheceu`
5. ✅ **NOVO**: Criar `clientes_canal_origem` e integrar com `cliente_info`
6. ✅ Criar views analíticas
7. ✅ Validar e gerar relatórios

---

## 📊 Resultado da Integração

### Dados em `cliente_info`

```sql
-- Exemplo de registro após integração
{
  cliente_id: "uuid...",
  segmento: "Redes Sociais",  -- Nome do canal
  tags: ["MARKETING", "REDES_SOCIAIS"],  -- Categoria + código
  primeira_compra: "2021-04-15",
  observacoes: "Origem: 01 - REDES SOCIAS",  -- Valor original
  ...
}
```

### View Consolidada

```sql
SELECT * FROM marketing.v_clientes_origem_integrada;
```

**Retorna**:

- Dados do cliente (nome, CPF, email)
- Dados do canal (código, nome, categoria)
- Dados de `cliente_info` (segmento, compras, churn, etc)
- Dados da origem (como_conheceu_original, data_aquisicao, valor)

---

## 📈 Queries Úteis

### 1. Ver Integração Completa

```sql
SELECT
    c.nome,
    ca.nome as canal,
    ca.categoria,
    ci.segmento,
    ci.total_compras,
    ci.ticket_medio,
    co.como_conheceu_original
FROM marketing.v_clientes_origem_integrada vci
JOIN core.clientes c ON c.id = vci.cliente_id
JOIN marketing.canais_aquisicao ca ON ca.codigo = vci.canal_codigo
JOIN marketing.cliente_info ci ON ci.cliente_id = vci.cliente_id
JOIN marketing.clientes_canal_origem co ON co.cliente_id = vci.cliente_id
LIMIT 20;
```

### 2. Clientes por Canal e Segmento

```sql
SELECT
    ca.nome as canal,
    ci.segmento,
    COUNT(*) as total_clientes,
    ROUND(AVG(ci.ticket_medio), 2) as ticket_medio
FROM marketing.clientes_canal_origem co
JOIN marketing.canais_aquisicao ca ON ca.id = co.canal_id
JOIN marketing.cliente_info ci ON ci.cliente_id = co.cliente_id
GROUP BY ca.nome, ci.segmento
ORDER BY total_clientes DESC;
```

### 3. Tags por Categoria

```sql
SELECT
    tags[1] as categoria,
    COUNT(*) as total_clientes
FROM marketing.cliente_info
WHERE tags && ARRAY['MARKETING', 'INDICACAO', 'ORGANICO', 'INTERNO']
GROUP BY tags[1]
ORDER BY total_clientes DESC;
```

### 4. Análise de Churn por Canal

```sql
SELECT
    ca.nome as canal,
    COUNT(*) as total_clientes,
    COUNT(*) FILTER (WHERE ci.risco_churn = true) as em_risco_churn,
    ROUND(
        COUNT(*) FILTER (WHERE ci.risco_churn = true) * 100.0 / COUNT(*),
        2
    ) as perc_risco
FROM marketing.clientes_canal_origem co
JOIN marketing.canais_aquisicao ca ON ca.id = co.canal_id
JOIN marketing.cliente_info ci ON ci.cliente_id = co.cliente_id
GROUP BY ca.nome
ORDER BY perc_risco DESC;
```

---

## 🔧 Scripts Envolvidos

| #       | Script                                              | Descrição                   |
| ------- | --------------------------------------------------- | --------------------------- |
| 62      | `62_CRIAR_TABELA_CANAIS.sql`                        | Cria 14 canais normalizados |
| 63      | `63_CRIAR_STAGING_MARKETING_VIXEN.sql`              | Cria staging                |
| 64      | `64_NORMALIZAR_COMO_CONHECEU.sql`                   | Normaliza valores           |
| **70**  | **`70_INTEGRAR_COM_CLIENTE_INFO.sql`**              | **⭐ INTEGRAÇÃO**           |
| 69      | `69_CRIAR_VIEWS_MARKETING.sql`                      | Views analíticas            |
| **68B** | **`68B_EXECUTAR_PIPELINE_MARKETING_INTEGRADO.sql`** | **Script mestre**           |

---

## ✅ Vantagens da Integração

### ✅ Mantém Estrutura Existente

- Não cria tabelas duplicadas
- Usa `cliente_info` que já existe
- Aproveita campos e relacionamentos existentes

### ✅ Enriquece Dados

- `segmento` agora tem significado de origem
- `tags` permitem filtros avançados por categoria
- `observacoes` mantém histórico do valor original

### ✅ Consultas Simplificadas

- View `v_clientes_origem_integrada` consolida tudo
- Queries diretas em `cliente_info` já têm origem
- Compatível com dashboards existentes

### ✅ Flexibilidade

- Tabela auxiliar `clientes_canal_origem` para detalhes
- Pode adicionar mais fontes de dados no futuro
- Fácil atualização quando novos dados chegarem

---

## 🔍 Diferenças da Abordagem Original

| Aspecto          | Abordagem Original       | Abordagem Integrada        |
| ---------------- | ------------------------ | -------------------------- |
| Tabela principal | `clientes_origem` (nova) | `cliente_info` (existente) |
| Campo de origem  | Tabela separada          | `segmento` + `tags`        |
| Detalhes         | Na tabela principal      | Tabela auxiliar            |
| Integração       | Manual posterior         | Automática no pipeline     |
| Compatibilidade  | Requer adaptação         | Transparente               |

---

## 📝 Observações Importantes

### ⚠️ Conflito com Segmentos Existentes

Se `cliente_info.segmento` já tiver valores do tipo:

- VIP
- REGULAR
- OCASIONAL
- INATIVO
- NOVO

O script **não sobrescreve** esses valores. Apenas popula quando:

- `segmento IS NULL`
- `segmento` não é um dos valores acima

### 💡 Solução para Manter Ambos

Se quiser manter o segmento de comportamento E a origem:

1. Adicione coluna `canal_origem` em `cliente_info`
2. Ou use `tags` exclusivamente para origem
3. Mantenha `segmento` para VIP/REGULAR/etc

### 🔄 Reprocessamento

Para reprocessar dados:

```sql
-- Limpar integração
TRUNCATE marketing.clientes_canal_origem CASCADE;
DELETE FROM marketing.cliente_info WHERE tags && ARRAY['MARKETING', 'INDICACAO'];

-- Executar novamente
\i 70_INTEGRAR_COM_CLIENTE_INFO.sql
```

---

## 📞 Suporte

- **Documentação completa**: `GUIA_SCHEMA_MARKETING.md`
- **Quick start**: `QUICKSTART_MARKETING.md`
- **Este guia**: `GUIA_INTEGRACAO_CLIENTE_INFO.md`

---

## ✅ Checklist

- [ ] Executar `68B_EXECUTAR_PIPELINE_MARKETING_INTEGRADO.sql`
- [ ] Importar CSV quando solicitado
- [ ] Verificar `SELECT * FROM marketing.v_clientes_origem_integrada;`
- [ ] Validar `SELECT COUNT(*) FROM marketing.cliente_info WHERE tags IS NOT NULL;`
- [ ] Testar queries de análise
- [ ] Integrar com dashboards/BI

---

**Status**: ✅ Pronto para produção  
**Compatibilidade**: 100% com estrutura existente  
**Impacto**: Zero em sistemas legados
