# Guia de Uso - Sistema de Gestão de Óticas

## 📋 Índice
1. [Início Rápido](#início-rápido)
2. [Preparação dos Dados](#preparação-dos-dados)
3. [Processamento de Planilhas](#processamento-de-planilhas)
4. [Deduplicação de Clientes](#deduplicação-de-clientes)
5. [Interface Web](#interface-web)
6. [Análise de Dados](#análise-de-dados)
7. [Solução de Problemas](#solução-de-problemas)

## 🚀 Início Rápido

### 1. Configuração Inicial
```bash
# 1. Ativar ambiente virtual
venv\Scripts\activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Iniciar aplicação web
python -m uvicorn app.main:app --reload
```

### 2. Acessar o Sistema
- Abra o navegador em: http://localhost:8000
- Interface principal para upload e gestão de dados

## 📁 Preparação dos Dados

### Estrutura de Arquivos Esperada
```
data/
├── raw/                    # Planilhas originais
│   ├── OS_NOVA_PERUS.xlsx
│   ├── OS_NOVA_CENTRO.xlsx
│   └── ...
├── processed/              # Dados processados
└── exports/               # Relatórios gerados
```

### Formato das Planilhas
- **Extensões aceitas**: .xlsx, .xls
- **Nome do arquivo**: Deve começar com "OS_NOVA"
- **Sheet recomendado**: "base_clientes_OS"

### Colunas Esperadas
- **Cliente**: nome, cpf, telefone, endereco, email
- **OS**: numero_os, data_compra, data_entrega, valor, loja, vendedor
- **Dioptrias**: od_esferico, od_cilindrico, od_eixo, oe_esferico, oe_cilindrico, oe_eixo
- **Outros**: dp, tipo_lente, observacoes

## 🔄 Processamento de Planilhas

### Método 1: Via Interface Web
1. Acesse http://localhost:8000
2. Selecione os arquivos Excel
3. Clique em "Processar Planilhas"
4. Aguarde o processamento e visualize os resultados

### Método 2: Via Script Python
```python
from scripts.analisar_os import AnalisadorOS

# Processar todas as planilhas
analisador = AnalisadorOS()
resultados = analisador.processar_todos_arquivos()

# Ver resultados
for resultado in resultados:
    print(f"{resultado['arquivo']}: {resultado['status']}")
```

### Método 3: Jupyter Notebook
1. Abra `notebooks/analise_exploratoria.ipynb`
2. Execute as células sequencialmente
3. Análise interativa com visualizações

## 🔍 Deduplicação de Clientes

### Automática
O sistema detecta automaticamente duplicatas baseado em:
- **Nome**: Similaridade textual (60% do score)
- **CPF**: Match exato (30% do score)
- **Telefone**: Similaridade (10% do score)

### Manual
```python
from app.services.deduplicacao import DeduplicadorClientes
import pandas as pd

# Carregar dados
df = pd.read_excel("data/processed/dados_limpos.xlsx")

# Detectar duplicatas
deduplicador = DeduplicadorClientes()
duplicatas = deduplicador.encontrar_duplicatas(df)

# Gerar relatório
relatorio = deduplicador.gerar_relatorio_duplicatas(duplicatas)
print(relatorio)
```

### Interpretação dos Resultados
- **Score > 0.9**: Alta confiança - Merge automático
- **Score 0.75-0.9**: Média confiança - Revisar manualmente
- **Score < 0.75**: Baixa confiança - Provavelmente diferentes

## 🌐 Interface Web

### Funcionalidades Principais
- **Upload de arquivos**: Múltiplos arquivos Excel
- **Visualização de estatísticas**: Clientes, OS, duplicatas
- **Processamento em tempo real**: Status de progresso
- **Download de relatórios**: Dados processados

### Endpoints da API
- `GET /`: Interface principal
- `POST /upload`: Upload e processamento de arquivos
- `GET /api/analyze/{file_id}`: Análise detalhada
- `GET /api/deduplicate`: Processo de deduplicação

## 📊 Análise de Dados

### Notebook Jupyter
O arquivo `notebooks/analise_exploratoria.ipynb` contém:
- Análise exploratória completa
- Visualizações interativas
- Detecção de padrões
- Relatórios automatizados

### Métricas Importantes
1. **Taxa de Duplicação**: (Total - Únicos) / Total
2. **Completude dos Dados**: Campos preenchidos / Total
3. **Qualidade das Dioptrias**: Valores dentro dos ranges esperados
4. **Distribuição Temporal**: Padrões de vendas

### Visualizações Disponíveis
- Histogramas de dioptrias
- Gráficos de duplicatas
- Análise temporal
- Mapas de calor de correlação

## 🔧 Solução de Problemas

### Erro: "Import could not be resolved"
```bash
# Reinstalar dependências
pip install --upgrade -r requirements.txt
```

### Erro: "File not found"
```bash
# Verificar estrutura de pastas
python -c "from pathlib import Path; print([p for p in Path('data/raw').glob('*.xlsx')])"
```

### Erro: "Permission denied"
```bash
# Verificar permissões de arquivo
# Fechar Excel antes de processar
# Executar como administrador se necessário
```

### Performance Lenta
1. **Reduzir tamanho dos arquivos**: Dividir planilhas grandes
2. **Aumentar memória**: Configurar CHUNK_SIZE em config.py
3. **Usar amostragem**: Para testes, usar apenas parte dos dados

### Dados Inconsistentes
1. **Verificar mapeamento de colunas**: app/core/config.py
2. **Validar formatos**: CPF, telefone, datas
3. **Revisar duplicatas manualmente**: Score entre 0.75-0.9

## 📞 Suporte

### Logs do Sistema
- **Local**: `logs/processamento.log`
- **Formato**: Timestamp, nível, mensagem
- **Retenção**: 30 dias

### Backup dos Dados
- **Automático**: A cada 24 horas
- **Local**: `data/backups/`
- **Retenção**: 30 backups

### Contato Técnico
Para suporte adicional, consulte:
- README.md principal
- Documentação inline no código
- Issues no repositório (se aplicável)

---

## 🎯 Próximos Passos

1. **Configurar ambiente de produção**
2. **Implementar autenticação de usuários**
3. **Adicionar mais validações**
4. **Criar dashboards avançados**
5. **Integrar com sistema ERP existente**