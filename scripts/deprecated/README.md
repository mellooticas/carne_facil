# 📦 Scripts Deprecated (Legado)

Scripts antigos mantidos como referência. **Não usar em produção.**

## 📂 Total: 2 scripts

### ⚠️ Sistema Antigo

- **sistema_vendas_universal.py** - Sistema antigo de vendas (substituído pelo app web)
- **gerador_documentos_completos.py** - Gerador antigo (substituído pelos relatórios)

## ❌ Por que estão aqui?

Estes scripts foram **substituídos** por versões melhores:

- `sistema_vendas_universal.py` → Substituído por `/app/` (FastAPI)
- `gerador_documentos_completos.py` → Substituído por `/scripts/relatorios/`

## 🔒 Política

- ❌ **NÃO USAR** em produção
- 📖 **APENAS REFERÊNCIA** histórica
- 🗑️ **DELETAR** após 6 meses sem uso
- 📝 **DOCUMENTAR** o motivo da depreciação

## ✅ Usar ao invés

| Deprecated | Use agora |
|-----------|-----------|
| sistema_vendas_universal.py | `python app/main.py` |
| gerador_documentos_completos.py | `python scripts/relatorios/relatorio_executivo_final.py` |

## 📅 Histórico

- **2025-10-10**: Movidos para deprecated após reorganização do projeto
