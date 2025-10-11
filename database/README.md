# 🗄️ Banco de Dados - Sistema Óticas Carne Fácil

## 📋 Visão Geral

Sistema de banco de dados completo e profissional para gestão de óticas, com foco em:
- **Clientes**: Cadastro unificado e normalizado
- **Vendas**: Controle completo de vendas e formas de pagamento  
- **Ótica**: Ordens de serviço, dioptrias e receitas
- **Marketing**: CRM, campanhas e aniversários
- **Auditoria**: Logs completos e histórico

## 🏗️ Arquitetura

### Schemas Organizados

```
oticas_db/
├── core/          # Dados centrais (clientes, lojas, vendedores)
├── vendas/        # Vendas, pagamentos e carnês
├── optica/        # Ordens de serviço e dioptrias
├── marketing/     # CRM e campanhas
└── auditoria/     # Logs e histórico
```

### Características Principais

✅ **UUIDs** como chaves primárias  
✅ **Soft Delete** em todas as tabelas  
✅ **Timestamps** automáticos (created_at, updated_at)  
✅ **Triggers** para auditoria automática  
✅ **Índices** otimizados para performance  
✅ **Busca Fuzzy** com pg_trgm  
✅ **Normalização** de nomes e telefones  
✅ **Validação** de CPF  
✅ **Types personalizados** (ENUMs)  
✅ **Constraints** para integridade  

## 📊 Modelo de Dados

### Core (Espinha Dorsal)

#### `core.clientes`
**Cadastro central de clientes - fonte única da verdade**

```sql
- id: UUID (PK)
- id_legado: VARCHAR(50) -- ID antigo para migração
- nome: VARCHAR(200)
- nome_normalizado: VARCHAR(200) -- Gerado automaticamente
- cpf: VARCHAR(14) UNIQUE
- data_nascimento: DATE
- email: VARCHAR(100)
- status: ENUM('ATIVO', 'INATIVO', 'BLOQUEADO')
```

**Índices**:
- GIN para busca fuzzy em `nome_normalizado`
- B-tree em `cpf`, `id_legado`, `status`

#### `core.endereco_cliente`
**Endereços dos clientes (1:N)**

```sql
- id: UUID (PK)
- cliente_id: UUID (FK → core.clientes)
- cep, logradouro, numero, complemento
- bairro, cidade, uf, pais
- tipo: ENUM('RESIDENCIAL', 'COMERCIAL', 'ENTREGA')
- principal: BOOLEAN
```

#### `core.telefones`
**Telefones dos clientes (1:N)**

```sql
- id: UUID (PK)
- cliente_id: UUID (FK → core.clientes)
- ddd, numero, numero_normalizado
- tipo: ENUM('CELULAR', 'FIXO', 'COMERCIAL')
- principal, whatsapp: BOOLEAN
```

#### `core.lojas`
**Cadastro de lojas/unidades**

```sql
- id: UUID (PK)
- codigo: VARCHAR(20) UNIQUE (MAUA, SUZANO, etc)
- nome: VARCHAR(100)
- cnpj, endereco, telefone, email
- status: ENUM('ATIVA', 'INATIVA')
- data_abertura, data_fechamento
```

**Lojas Iniciais**:
- MAUA
- SUZANO  
- SUZANO2
- RIO_PEQUENO
- PERUS
- SAO_MATEUS (inativa)

#### `core.vendedores`
**Cadastro de vendedores/consultores**

```sql
- id: UUID (PK)
- codigo, nome
- loja_id: UUID (FK → core.lojas)
- email, telefone
- status, data_admissao, data_desligamento
```

### Vendas

#### `vendas.vendas`
**Vendas realizadas - 7.547 registros | R$ 6.032.727,49**

```sql
- id: UUID (PK)
- numero_venda: VARCHAR(50)
- data_venda: DATE
- loja_id: UUID (FK → core.lojas)
- cliente_id: UUID (FK → core.clientes)
- cliente_nome: VARCHAR(200) -- Denormalizado
- valor_venda: DECIMAL(10,2)
- valor_entrada: DECIMAL(10,2)
- valor_total: DECIMAL(10,2) GENERATED -- Calculado
```

#### `vendas.formas_pagamento_venda`
**Formas de pagamento das vendas (1:N)**

```sql
- id: UUID (PK)
- venda_id: UUID (FK → vendas.vendas)
- forma_pagamento: ENUM('DN', 'CTD', 'CTC', 'PIX', ...)
- valor: DECIMAL(10,2)
- parcelas: INT
```

#### `vendas.recebimentos_carne`
**Recebimentos de carnês - 3.108 registros | R$ 379.671,97**

```sql
- id: UUID (PK)
- os_id: UUID (FK → optica.ordens_servico)
- data_recebimento: DATE
- valor_parcela: DECIMAL(10,2)
- numero_parcela: VARCHAR(20) -- Ex: PARC. 5/7
- forma_pagamento
```

#### `vendas.entregas_carne`
**Entregas de carnês - 678 registros | R$ 411.087,49**

```sql
- id: UUID (PK)
- os_id: UUID (FK → optica.ordens_servico)
- data_entrega: DATE
- valor_total: DECIMAL(10,2)
- numero_parcelas: INT
```

#### `vendas.restantes_entrada`
**Restantes de entradas - 2.868 registros | R$ 929.201,55**

```sql
- id: UUID (PK)
- venda_id: UUID (FK → vendas.vendas)
- data_registro: DATE
- valor_entrada: DECIMAL(10,2)
- forma_pagamento
```

### Ótica

#### `optica.ordens_servico`
**Ordens de serviço - 5.974 entregas**

```sql
- id: UUID (PK)
- numero_os: VARCHAR(50) UNIQUE
- data_os, data_entrega: DATE
- loja_id: UUID (FK → core.lojas)
- cliente_id: UUID (FK → core.clientes)
- vendedor_id: UUID (FK → core.vendedores)
- venda_id: UUID (FK → vendas.vendas) -- Ligação!
- status: ENUM('ABERTA', 'EM_PRODUCAO', 'PRONTA', 'ENTREGUE')
- tem_carne: BOOLEAN
- valor_total: DECIMAL(10,2)
```

#### `optica.dioptrias`
**Receitas óticas (graus)**

```sql
- id: UUID (PK)
- os_id: UUID (FK → optica.ordens_servico)
- olho: ENUM('OD', 'OE', 'AO')
- esf, cil, eixo, dnp, altura, adicao: DECIMAL
- tipo_visao: ENUM('LONGE', 'PERTO', 'MULTIFOCAL')
```

### Marketing

#### `marketing.cliente_info`
**Informações de marketing/CRM**

```sql
- id: UUID (PK)
- cliente_id: UUID UNIQUE (FK → core.clientes)
- como_conheceu: VARCHAR(100)
- data_primeira_compra: DATE
- faixa_etaria: VARCHAR(30)
- ultima_compra: DATE
- total_compras: INT
- valor_total_gasto: DECIMAL(10,2)
- cliente_ativo: BOOLEAN
```

### Auditoria

#### `auditoria.log_alteracoes`
**Log de todas as alterações**

```sql
- id: UUID (PK)
- tabela: VARCHAR(100)
- registro_id: UUID
- operacao: ENUM('INSERT', 'UPDATE', 'DELETE')
- dados_antigos: JSONB
- dados_novos: JSONB
- usuario: VARCHAR(100)
- data_hora: TIMESTAMP
- ip_origem: INET
```

## 🔧 Funções Úteis

### Normalização

```sql
-- Normalizar texto (sem acentos, lowercase)
SELECT normalizar_texto('José da Silva'); -- 'jose da silva'

-- Normalizar telefone (apenas números)
SELECT normalizar_telefone('(11) 98765-4321'); -- '11987654321'
```

### Validação

```sql
-- Validar CPF
SELECT validar_cpf('123.456.789-09'); -- TRUE/FALSE

-- Formatar CPF
SELECT formatar_cpf('12345678909'); -- '123.456.789-09'
```

## 📥 Instalação

### 1. Criar Database

```bash
psql -U postgres
CREATE DATABASE oticas_db WITH ENCODING 'UTF8';
\q
```

### 2. Executar Scripts (em ordem)

```bash
cd database/

# 1. Configurações iniciais
psql -U postgres -d oticas_db -f 01_inicial_config.sql

# 2. Schema CORE
psql -U postgres -d oticas_db -f 02_schema_core.sql

# 3. Schema VENDAS (próximo)
# 4. Schema OPTICA (próximo)
# 5. Schema MARKETING (próximo)
# 6. Schema AUDITORIA (próximo)
```

## 🔍 Queries Úteis

### Buscar Cliente (Fuzzy)

```sql
SELECT * FROM core.clientes
WHERE nome_normalizado % 'jose silva'
ORDER BY similarity(nome_normalizado, 'jose silva') DESC
LIMIT 10;
```

### Total de Vendas por Loja

```sql
SELECT 
    l.nome AS loja,
    COUNT(*) AS total_vendas,
    SUM(v.valor_total) AS valor_total
FROM vendas.vendas v
JOIN core.lojas l ON v.loja_id = l.id
GROUP BY l.nome
ORDER BY valor_total DESC;
```

### Clientes com Mais Compras

```sql
SELECT 
    c.nome,
    mi.total_compras,
    mi.valor_total_gasto,
    mi.ultima_compra
FROM core.clientes c
JOIN marketing.cliente_info mi ON c.id = mi.cliente_id
WHERE mi.cliente_ativo = TRUE
ORDER BY mi.valor_total_gasto DESC
LIMIT 20;
```

### Vendas do Mês Atual

```sql
SELECT 
    COUNT(*) AS vendas,
    SUM(valor_total) AS total
FROM vendas.vendas
WHERE data_venda >= DATE_TRUNC('month', CURRENT_DATE);
```

## 🎯 Próximos Passos

- [ ] Completar schemas VENDAS, OPTICA, MARKETING, AUDITORIA
- [ ] Criar triggers de auditoria automática
- [ ] Criar views materializadas para dashboards
- [ ] Criar scripts de ETL para importar dados Excel
- [ ] Implementar Row-Level Security (RLS)
- [ ] Criar funções de relatórios
- [ ] Documentar procedures de backup

## 📚 Documentação Adicional

- [PostgreSQL 15 Documentation](https://www.postgresql.org/docs/15/)
- [UUID-OSSP Extension](https://www.postgresql.org/docs/current/uuid-ossp.html)
- [pg_trgm (Trigram)](https://www.postgresql.org/docs/current/pgtrgm.html)

## 🤝 Suporte

Para dúvidas ou melhorias no modelo de dados, consulte a equipe de desenvolvimento.