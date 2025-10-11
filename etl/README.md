# 📦 ETL - Extract, Transform, Load

Scripts para importação e transformação de dados das planilhas Excel para o banco PostgreSQL.

## 📋 Scripts Principais

### ⭐ importador_caixas_completo.py
**Propósito**: Importador principal dos dados de caixas  
**Fonte**: `data/todos_os_caixas_original.xlsx`  
**Saída**: Dados processados das 5 abas (vend, rec_carn, os_entr_dia, entr_carn, rest_entr)  
**Status**: ✅ Funcional  

### importar_dados_2025.py
**Propósito**: Importação específica de dados de 2025  
**Status**: 🔄 Em uso

### importar_2025_agora.py
**Propósito**: Importação imediata dados 2025  
**Status**: 🔄 Em uso

### padronizar_clientes_vixen.py
**Propósito**: Normalização dados de clientes do sistema Vixen  
**Status**: ✅ Funcional

### importador_direto_onedrive.py
**Propósito**: Importação direta do OneDrive  
**Status**: ⚠️ Experimental

## 🎯 Como Usar

### Importar dados de caixas (principal)
```bash
python etl/importador_caixas_completo.py
```

### Importar clientes Vixen
```bash
python etl/padronizar_clientes_vixen.py
```

## 📊 Dados Processados

- **VEND**: 7.547 vendas | R$ 6.032.727,49
- **REC_CARN**: 3.108 recebimentos | R$ 379.671,97
- **OS_ENTR_DIA**: 5.974 entregas
- **ENTR_CARN**: 678 entregas carnê | R$ 411.087,49
- **REST_ENTR**: 2.868 restantes | R$ 929.201,55
- **TOTAL**: 20.175 registros | R$ 7.752.688,50

## 🔄 Fluxo ETL

```
Excel Planilhas → ETL Scripts → Dados Normalizados → PostgreSQL
     ↓                ↓                  ↓                ↓
  Raw Data      Transform         Validate         Database
```

## 📁 Estrutura de Utilidades

- `utils/` - Funções auxiliares
  - `normalizar.py` - Normalização de textos
  - `validar.py` - Validação CPF, telefones, etc

## ⚠️ Requisitos

- pandas
- openpyxl
- sqlalchemy (para banco)
- psycopg2 (PostgreSQL)

## 📝 Próximos Desenvolvimentos

- [ ] ETL unificado único
- [ ] Validações automáticas
- [ ] Relatórios de importação
- [ ] Retry automático em caso de erro
- [ ] Log detalhado de operações
