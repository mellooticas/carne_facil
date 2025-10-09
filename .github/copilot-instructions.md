# Sistema de Gestão de Óticas - Carne Fácil

## Visão Geral
Sistema web para gestão unificada de óticas com processamento de planilhas Excel, normalização de dados e controle de duplicações de clientes.

## Funcionalidades Implementadas
- ✅ Sistema web FastAPI operacional (localhost:8000)
- ✅ Interface de upload de arquivos Excel
- ✅ Processamento de 6,892 registros de OS
- ✅ Identificação de 3 lojas operacionais ativas
- ✅ Sistema de deduplicação inteligente
- ✅ Análise e consolidação de dados

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

## Dados Analisados
- **SUZANO**: 5,252 registros (OS 8353-11408)
- **MAUA**: 1,088 registros (OS 3911-4621)  
- **RIO_PEQUENO**: 552 registros (OS 3449-4000)
- **Total**: 6,892 registros com 4,229 OS únicas
- **Duplicações**: 2,663 OS duplicadas identificadas

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
1. **Fase 1**: Implementar ID único por OS (loja + sistema + numero)
2. **Fase 2**: Localizar e integrar dados de clientes
3. **Fase 3**: Expandir interface web com dashboard completo

## Limitações Atuais
- Dados de clientes não localizados
- Apenas 3 de 6 lojas têm dados disponíveis
- Duplicações entre sistemas LANCASTER/OTM

## Contato
Sistema desenvolvido para análise e gestão de óticas com foco em normalização de dados e eliminação de duplicações.