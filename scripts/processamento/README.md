# ⚙️ Scripts de Processamento

Scripts para extração e processamento de dados das planilhas Excel.

## 📂 Total: 17 scripts

### 🔄 Processadores

- processador_completo_vendas.py
- processador_corrigido_os.py
- processador_rest_entr.py
- processador_rest_entr_final.py
- processador_vendas_real.py
- processador_vend_dia_puro.py
- processar_lote.py

### 📤 Extratores

#### Extrator Unificado
- extrair_5_tabelas_padrao.py
- extrator_unificado_individual.py

#### Extratores por Tabela
- extrator_tabela_VEND.py
- extrator_tabela_REC_CARN.py
- extrator_tabela_OS_ENT_DIA.py
- extrator_tabela_ENTR_CARN.py
- extrator_tabela_REST_ENTR.py

#### Versões Específicas
- extrator_vend_correto.py
- extrator_vend_refinado.py
- extrair_dados_caixa.py

## 🎯 Como Usar

### Extrair todas as 5 tabelas padrão
```bash
python scripts/processamento/extrair_5_tabelas_padrao.py
```

### Processar vendas completas
```bash
python scripts/processamento/processador_completo_vendas.py
```

### Extrair tabela específica
```bash
python scripts/processamento/extrator_tabela_VEND.py
```

## 📊 Tabelas Processadas

1. **VEND** - Vendas diárias
2. **REC_CARN** - Recebimentos carnê
3. **OS_ENTR_DIA** - Entregas do dia
4. **ENTR_CARN** - Entregas carnê
5. **REST_ENTR** - Restantes entrada

## 🔄 Fluxo de Processamento

```
Excel Bruto → Extrator → Normalização → Validação → Dados Limpos
```

## ⚠️ Diferença para /etl/

- **Aqui (/scripts/processamento/)**: Scripts de processamento intermediário, extrações específicas
- **/etl/**: Scripts finais de importação para o banco de dados
