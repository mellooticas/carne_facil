# 🧹 PLANO DE LIMPEZA E ORGANIZAÇÃO DO APP

## 📊 SITUAÇÃO ATUAL
- ✅ **Banco de dados**: Profissional, enterprise-ready (OK!)
- ❌ **App Python**: 60+ scripts desorganizados na raiz (PROBLEMA!)

## 🎯 NOVA ESTRUTURA PROPOSTA

```
D:/projetos/carne_facil/
├── 📂 app/                    # Aplicação Web (FastAPI)
│   ├── main.py               # ✅ JÁ EXISTE
│   ├── models/               # ✅ JÁ EXISTE
│   ├── services/             # ✅ JÁ EXISTE
│   └── templates/            # ✅ JÁ EXISTE
│
├── 📂 database/               # Scripts SQL
│   ├── 01_inicial_config.sql        # ✅ CRIADO
│   ├── 02_schema_core.sql           # ✅ CRIADO
│   ├── 03_schema_vendas.sql         # TODO
│   ├── 04_schema_optica.sql         # TODO
│   ├── 05_schema_marketing.sql      # TODO
│   ├── 06_schema_auditoria.sql      # TODO
│   ├── README.md                    # ✅ CRIADO
│   └── ERD_DIAGRAMA.md              # ✅ CRIADO
│
├── 📂 etl/                    # Scripts de Importação/ETL
│   ├── __init__.py
│   ├── importar_clientes.py         # MOVER: importador_caixas_completo.py
│   ├── importar_vendas.py           # CRIAR
│   ├── importar_os.py               # CRIAR
│   └── utils/
│       ├── normalizar.py
│       └── validar.py
│
├── 📂 scripts/                # Utilitários/Análises
│   ├── analise/              # Scripts de análise (MOVER 20+ scripts)
│   │   ├── analisar_dados_reais.py
│   │   ├── analisar_modelo_banco_correto.py
│   │   └── ...
│   │
│   ├── relatorios/           # Geradores de relatórios
│   │   ├── relatorio_executivo.py
│   │   ├── relatorio_comparativo_dados.py
│   │   └── ...
│   │
│   ├── limpeza/              # Scripts de manutenção
│   │   ├── limpeza_excel_temporarios.py
│   │   ├── limpeza_geral.py
│   │   └── ...
│   │
│   └── deprecated/           # Scripts antigos (não deletar ainda)
│       └── ...
│
├── 📂 data/                   # Dados (OK)
│   ├── raw/                  # Excel originais
│   ├── processed/            # Dados processados
│   └── exports/              # Relatórios gerados
│
├── 📂 docs/                   # Documentação
│   ├── RESUMO_EXECUTIVO.md
│   ├── GUIA_SISTEMA_VENDAS.md
│   └── arquitetura/
│
├── 📂 tests/                  # Testes (OK)
│
├── 📂 logs/                   # Logs (OK)
│
└── 📄 Arquivos raiz (manter apenas essenciais)
    ├── README.md
    ├── requirements.txt
    ├── .gitignore
    └── setup.py              # CRIAR (configuração do projeto)
```

## 🔍 CLASSIFICAÇÃO DOS SCRIPTS ATUAIS

### Categoria A: MOVER para /etl/
- `importador_caixas_completo.py` ⭐ (principal)
- `importador_direto_onedrive.py`
- `importar_2025_agora.py`
- `importar_dados_2025.py`
- `padronizar_clientes_vixen.py`

### Categoria B: MOVER para /scripts/analise/
- `analisar_*.py` (15 arquivos)
- `investigar_*.py` (6 arquivos)
- `verificar_*.py` (8 arquivos)
- `mapear_*.py` (3 arquivos)

### Categoria C: MOVER para /scripts/relatorios/
- `relatorio_*.py` (5 arquivos)
- `dashboard_*.py` (2 arquivos)

### Categoria D: MOVER para /scripts/processamento/
- `processador_*.py` (7 arquivos)
- `extrator_*.py` (10 arquivos)

### Categoria E: MOVER para /scripts/limpeza/
- `limpeza_*.py` (3 arquivos)
- `limpador_*.py` (1 arquivo)
- `fix_emojis.py`

### Categoria F: MOVER para /scripts/deprecated/
- Scripts duplicados ou supersedidos
- Scripts de teste antigos
- Versões antigas (_correto, _refinado, _final)

### Categoria G: DELETAR (após backup)
- `__pycache__/` (cache Python)
- Arquivos .pyc
- Temporários

## 📋 CHECKLIST DE AÇÕES

### Fase 1: Backup (5 min)
- [ ] Criar backup completo antes de qualquer mudança
- [ ] Commitar estado atual no Git

### Fase 2: Criar estrutura (10 min)
- [ ] Criar pastas: etl/, scripts/{analise,relatorios,processamento,limpeza,deprecated}
- [ ] Criar __init__.py onde necessário

### Fase 3: Mover scripts (30 min)
- [ ] Mover scripts categoria A → /etl/
- [ ] Mover scripts categoria B → /scripts/analise/
- [ ] Mover scripts categoria C → /scripts/relatorios/
- [ ] Mover scripts categoria D → /scripts/processamento/
- [ ] Mover scripts categoria E → /scripts/limpeza/
- [ ] Mover scripts categoria F → /scripts/deprecated/

### Fase 4: Limpar (10 min)
- [ ] Deletar __pycache__/
- [ ] Limpar imports quebrados
- [ ] Atualizar paths relativos

### Fase 5: Documentar (15 min)
- [ ] Criar README.md em cada pasta
- [ ] Documentar propósito de cada diretório
- [ ] Listar scripts principais

### Fase 6: Testar (20 min)
- [ ] Testar app web (python app/main.py)
- [ ] Testar script ETL principal
- [ ] Verificar imports

## 🎯 RESULTADO ESPERADO

### ANTES (Caótico)
```
carne_facil/
├── 60+ scripts .py misturados
├── app/
├── data/
└── database/
```

### DEPOIS (Organizado)
```
carne_facil/
├── app/              # Web app limpo
├── database/         # SQL enterprise
├── etl/              # 5 scripts ETL principais
├── scripts/          # Organizados por categoria
│   ├── analise/     # 15 scripts
│   ├── relatorios/  # 7 scripts
│   ├── processamento/ # 17 scripts
│   ├── limpeza/     # 5 scripts
│   └── deprecated/  # Scripts antigos (referência)
├── data/            # Dados
├── docs/            # Documentação
└── README.md        # Limpo e objetivo
```

## ⚠️ REGRAS IMPORTANTES

1. **NÃO DELETAR NADA** ainda - apenas mover
2. **FAZER BACKUP** antes de começar
3. **COMMITAR NO GIT** cada fase
4. **TESTAR** após cada movimentação grande
5. **DOCUMENTAR** o que cada pasta contém

## 📝 SCRIPTS ESSENCIAIS (Top 5)

Estes são os únicos que realmente precisamos usar:

1. **app/main.py** - Servidor web
2. **etl/importar_clientes.py** - Importar clientes
3. **etl/importar_vendas.py** - Importar vendas
4. **database/*.sql** - Criar banco
5. **scripts/relatorios/relatorio_executivo.py** - Relatórios

---

**Tempo estimado**: 1h30min  
**Dificuldade**: Baixa (apenas organização)  
**Benefício**: App limpo, profissional, manutenível
