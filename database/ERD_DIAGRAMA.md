# 📊 Diagrama de Entidades e Relacionamentos (ERD)

## Arquitetura Completa do Banco de Dados

```mermaid
erDiagram
    %% ========================================
    %% SCHEMA: CORE (Espinha Dorsal)
    %% ========================================
    
    CLIENTES {
        uuid id PK
        varchar id_legado UK "ID antigo"
        varchar nome
        varchar nome_normalizado "gerado"
        varchar cpf UK
        varchar rg
        date data_nascimento
        char sexo
        varchar email
        enum status
        timestamp created_at
        timestamp updated_at
    }
    
    ENDERECO_CLIENTE {
        uuid id PK
        uuid cliente_id FK
        varchar cep
        varchar logradouro
        varchar numero
        varchar complemento
        varchar bairro
        varchar cidade
        char uf
        varchar pais
        enum tipo
        boolean principal
    }
    
    TELEFONES {
        uuid id PK
        uuid cliente_id FK
        varchar ddd
        varchar numero
        varchar numero_normalizado "gerado"
        enum tipo
        boolean principal
        boolean whatsapp
    }
    
    LOJAS {
        uuid id PK
        varchar codigo UK "MAUA,SUZANO..."
        varchar nome
        varchar nome_normalizado "gerado"
        varchar cnpj UK
        text endereco
        varchar telefone
        varchar email
        enum status
        date data_abertura
        date data_fechamento
    }
    
    VENDEDORES {
        uuid id PK
        varchar codigo UK
        varchar nome
        varchar nome_normalizado "gerado"
        uuid loja_id FK
        varchar email
        varchar telefone
        enum status
        date data_admissao
        date data_desligamento
    }
    
    %% ========================================
    %% SCHEMA: VENDAS
    %% ========================================
    
    VENDAS {
        uuid id PK
        varchar numero_venda
        date data_venda
        uuid loja_id FK
        uuid cliente_id FK
        varchar cliente_nome "denorm"
        decimal valor_venda
        decimal valor_entrada
        decimal valor_total "gerado"
    }
    
    FORMAS_PAGAMENTO_VENDA {
        uuid id PK
        uuid venda_id FK
        enum forma_pagamento "DN,CTD,CTC,PIX"
        decimal valor
        int parcelas
    }
    
    RECEBIMENTOS_CARNE {
        uuid id PK
        uuid os_id FK
        date data_recebimento
        decimal valor_parcela
        varchar numero_parcela "PARC. 5/7"
        enum forma_pagamento
    }
    
    ENTREGAS_CARNE {
        uuid id PK
        uuid os_id FK
        date data_entrega
        decimal valor_total
        int numero_parcelas
    }
    
    RESTANTES_ENTRADA {
        uuid id PK
        uuid venda_id FK
        date data_registro
        varchar cliente_nome
        decimal valor_entrada
        enum forma_pagamento
    }
    
    %% ========================================
    %% SCHEMA: OPTICA
    %% ========================================
    
    ORDENS_SERVICO {
        uuid id PK
        varchar numero_os UK
        date data_os
        date data_entrega
        uuid loja_id FK
        uuid cliente_id FK
        uuid vendedor_id FK
        uuid venda_id FK
        enum status "ABERTA,PRONTA,ENTREGUE"
        boolean tem_carne
        decimal valor_total
    }
    
    DIOPTRIAS {
        uuid id PK
        uuid os_id FK
        enum olho "OD,OE,AO"
        decimal esf
        decimal cil
        int eixo
        decimal dnp
        decimal altura
        decimal adicao
        enum tipo_visao
    }
    
    %% ========================================
    %% SCHEMA: MARKETING
    %% ========================================
    
    MARKETING_INFO {
        uuid id PK
        uuid cliente_id FK UK
        varchar como_conheceu
        date data_primeira_compra
        varchar faixa_etaria
        date ultima_compra
        int total_compras
        decimal valor_total_gasto
        boolean cliente_ativo
    }
    
    %% ========================================
    %% RELACIONAMENTOS
    %% ========================================
    
    %% Core
    CLIENTES ||--o{ ENDERECO_CLIENTE : "tem"
    CLIENTES ||--o{ TELEFONES : "tem"
    LOJAS ||--o{ VENDEDORES : "trabalham em"
    
    %% Vendas
    VENDAS }o--|| LOJAS : "realizada em"
    VENDAS }o--o| CLIENTES : "feita por"
    VENDAS ||--o{ FORMAS_PAGAMENTO_VENDA : "paga com"
    VENDAS ||--o{ RESTANTES_ENTRADA : "tem"
    
    %% Ótica
    ORDENS_SERVICO }o--|| LOJAS : "criada em"
    ORDENS_SERVICO }o--|| CLIENTES : "pertence a"
    ORDENS_SERVICO }o--o| VENDEDORES : "atendida por"
    ORDENS_SERVICO }o--o| VENDAS : "vinculada a"
    ORDENS_SERVICO ||--o{ DIOPTRIAS : "contém"
    ORDENS_SERVICO ||--o{ RECEBIMENTOS_CARNE : "recebe"
    ORDENS_SERVICO ||--o{ ENTREGAS_CARNE : "entrega"
    
    %% Marketing
    CLIENTES ||--o| MARKETING_INFO : "possui"
```

## 🔑 Legenda

- **PK**: Primary Key (UUID)
- **FK**: Foreign Key (UUID)
- **UK**: Unique Key
- **gerado**: Campo calculado automaticamente
- **denorm**: Campo denormalizado para performance
- **||--o{**: Um para muitos
- **}o--||**: Muitos para um
- **}o--o|**: Muitos para zero ou um

## 📊 Estatísticas de Dados

### Dados Reais Disponíveis

| Tabela | Registros | Valor Total |
|--------|-----------|-------------|
| **VENDAS** | 7.547 | R$ 6.032.727,49 |
| **RECEBIMENTOS_CARNE** | 3.108 | R$ 379.671,97 |
| **ENTREGAS_CARNE** | 678 | R$ 411.087,49 |
| **RESTANTES_ENTRADA** | 2.868 | R$ 929.201,55 |
| **ORDENS_SERVICO** | 5.974 entregas | - |
| **LOJAS** | 6 (5 ativas + 1 fechada) | - |

### Total Geral
**20.175 registros** processados dos arquivos Excel  
**R$ 7.752.688,50** em valores financeiros

## 🎯 Pontos Importantes

### 1. Chave Primária: UUID
Todas as tabelas usam UUID como chave primária:
```sql
id UUID PRIMARY KEY DEFAULT uuid_generate_v4()
```

### 2. Migração: id_legado
Campo especial para preservar IDs antigos:
```sql
id_legado VARCHAR(50) UNIQUE  -- ID do sistema antigo
```

### 3. Soft Delete
Todas as tabelas suportam exclusão lógica:
```sql
deleted_at TIMESTAMP NULL
```

### 4. Auditoria Automática
Campos padrão em todas as tabelas:
```sql
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Atualizado via trigger
created_by VARCHAR(100)
updated_by VARCHAR(100)
version INT DEFAULT 1  -- Controle de versão otimista
```

### 5. Normalização Automática
Campos gerados para busca eficiente:
```sql
nome_normalizado VARCHAR(200) GENERATED ALWAYS AS (normalizar_texto(nome)) STORED
```

### 6. Relacionamento Venda ↔ OS
Ligação crucial entre vendas e ordens de serviço:
```sql
ORDENS_SERVICO.venda_id → VENDAS.id
```

## 📋 Schemas e Responsabilidades

### 🗂️ CORE
**Responsabilidade**: Dados centrais e mestres
- Clientes (espinha dorsal)
- Endereços e telefones
- Lojas e vendedores

### 💰 VENDAS
**Responsabilidade**: Transações financeiras
- Vendas completas (valor + entrada)
- Formas de pagamento
- Recebimentos e entregas de carnês
- Restantes de entrada

### 👓 OPTICA
**Responsabilidade**: Operação ótica
- Ordens de serviço
- Receitas (dioptrias)
- Produtos óticos

### 📢 MARKETING
**Responsabilidade**: CRM e relacionamento
- Informações de marketing
- Histórico de compras
- Campanhas e aniversários

### 📝 AUDITORIA
**Responsabilidade**: Rastreabilidade
- Log de alterações
- Histórico de valores
- Snapshots para backup

## 🔗 Integridade Referencial

Todas as Foreign Keys são protegidas com:
```sql
REFERENCES schema.tabela(id) ON DELETE CASCADE
REFERENCES schema.tabela(id) ON DELETE RESTRICT
```

Escolha baseada em:
- **CASCADE**: Dependências diretas (telefones, endereços)
- **RESTRICT**: Dados críticos (vendas, OSs)

## 🚀 Performance

### Índices Criados

1. **GIN (Fuzzy Search)**:
   - `nome_normalizado` em clientes, lojas, vendedores
   
2. **B-Tree (Busca Exata)**:
   - Todas as FKs
   - Campos únicos (CPF, CNPJ, código)
   - Campos de filtro (status, data)

3. **Parciais (Condicionais)**:
   ```sql
   WHERE deleted_at IS NULL
   WHERE principal = TRUE
   WHERE whatsapp = TRUE
   ```

### Triggers Automáticos

1. **updated_at**: Atualização automática do timestamp
2. **Auditoria**: Log de todas as mudanças (futuro)
3. **Validações**: Constraints complexas (futuro)

---

**Última atualização**: 10/10/2025  
**Versão do modelo**: 1.0.0