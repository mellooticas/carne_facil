# Sistema de Gestão de Óticas - Carne Fácil

## Visão Geral
Sistema web para gestão unificada de óticas com processamento de planilhas Excel, normalização de dados e controle de duplicações de clientes.

## Funcionalidades Implementadas
- ✅ Sistema web FastAPI operacional (localhost:8000)
- ✅ Interface de upload de arquivos Excel
- ✅ Processamento corrigido de 25,706 OS únicas
- ✅ Identificação e correção de 6 lojas (5 ativas + 1 fechada)
- ✅ Sistema de deduplicação inteligente com 1,068 correções
- ✅ Análise e consolidação de dados com agrupamento por OS única
- ✅ Correção de múltiplas formas de pagamento por OS

## Estrutura do Projeto
```
d:\projetos\carne_facil\
├── app/                    # Aplicação web FastAPI
│   ├── main.py            # Servidor principal
│   ├── models/            # Modelos de dados
│   ├── services/          # Serviços de negócio
│   └── templates/         # Templates HTML
├── scripts/               # Scripts de análise
├── data/                  # Dados das lojas
│   ├── raw/              # Dados brutos
│   └── processed/        # Dados processados
└── notebooks/            # Análises Jupyter
```

## Dados Analisados (CORRIGIDOS)
- **SUZANO**: 8,146 OS únicas (2023-2025)
- **RIO_PEQUENO**: 4,480 OS únicas (2023-2024)
- **PERUS**: 3,942 OS únicas (2023-2024)
- **MAUA**: 3,575 OS únicas (2023-2025)
- **SAO_MATEUS**: 2,811 OS únicas (2023-2024) - Loja fechada
- **SUZANO2**: 2,752 OS únicas (2023-2024)
- **Total**: 25,706 OS únicas com valor de R$ 3.971.617,86
- **Correções**: 1,068 OS duplicadas eliminadas (principalmente São Mateus)

## Tecnologias Utilizadas
- **Backend**: FastAPI + Uvicorn
- **Dados**: Pandas + Openpyxl + SQLAlchemy
- **Deduplicação**: FuzzyWuzzy + Python-Levenshtein
- **Frontend**: Jinja2 + HTML/CSS
- **Análise**: Jupyter Notebooks

## Como Executar
1. Ativar ambiente virtual: `D:/projetos/carne_facil/.venv/Scripts/activate`
2. Instalar dependências: `pip install -r requirements.txt`
3. Executar servidor: `uvicorn app.main:app --reload`
4. Acessar: http://localhost:8000

## Próximos Passos
1. **Fase 1**: ✅ Implementado ID único por OS (loja + sistema + numero)
2. **Fase 2**: ✅ Localizado e integrado dados de clientes através das planilhas
3. **Fase 3**: Expandir interface web com dashboard completo dos dados corrigidos

## Limitações Atuais
- ✅ Dados de todas as 6 lojas localizados e processados
- ✅ Sistema corrigido elimina duplicações entre LANCASTER/OTM
- ✅ Múltiplas formas de pagamento consolidadas por OS única

## Contato
Sistema desenvolvido para análise e gestão de óticas com foco em normalização de dados e eliminação de duplicações.