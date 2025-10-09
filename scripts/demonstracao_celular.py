#!/usr/bin/env python3
"""
Demonstração da Validação de Celulares SP
Mostra exemplos de como os celulares são padronizados
"""

import pandas as pd
from pathlib import Path
import re

def limpar_celular_sp(celular):
    """Limpa e padroniza celular para formato SP"""
    if not celular or str(celular).strip() == '':
        return None
    
    cel_str = re.sub(r'[^\d]', '', str(celular))
    
    # Validar tamanho mínimo
    if len(cel_str) < 9:
        return None
    
    # Padronizar para SP (11)
    if len(cel_str) == 9:
        # Adicionar DDD 11 se só tiver 9 dígitos de celular
        cel_str = '11' + cel_str
    elif len(cel_str) == 10:
        # Adicionar DDD 11 se não tiver
        cel_str = '11' + cel_str
    elif len(cel_str) == 11 and cel_str.startswith('1'):
        # Já tem DDD 11
        pass
    elif len(cel_str) == 11 and not cel_str.startswith('11'):
        # Corrigir DDD para 11 (SP)
        cel_str = '11' + cel_str[2:]
    elif len(cel_str) == 13 and cel_str.startswith('55'):
        # Remover código do país e usar DDD 11
        cel_str = '11' + cel_str[4:]
    elif len(cel_str) > 11:
        # Pegar os últimos 9 dígitos e adicionar DDD 11
        cel_str = '11' + cel_str[-9:]
    
    # Validar se é celular SP válido (11 9xxxx-xxxx)
    if len(cel_str) == 11 and cel_str.startswith('11') and cel_str[2] == '9':
        # Formatar: (11) 9xxxx-xxxx
        return f"(11) {cel_str[2:7]}-{cel_str[7:]}"
    
    return None

def demonstrar_validacao():
    """Demonstra a validação com exemplos práticos"""
    
    print("📱 DEMONSTRAÇÃO - VALIDAÇÃO DE CELULARES SP")
    print("=" * 70)
    print("🎯 Objetivo: Padronizar todos os celulares para formato (11) 9xxxx-xxxx")
    print("📍 Região: São Paulo (DDD 11)")
    print("=" * 70)
    
    # Exemplos comuns encontrados nos dados
    exemplos_comuns = [
        "11987654321",          # Formato completo
        "(11) 98765-4321",      # Já formatado
        "11 98765-4321",        # Com espaço
        "987654321",            # Sem DDD
        "98765-4321",           # Com hífen, sem DDD
        "(11)98765-4321",       # Sem espaço após DDD
        "5511987654321",        # Com código do país
        "21987654321",          # DDD errado (RJ) → corrigir para SP
        "47987654321",          # DDD errado (SC) → corrigir para SP
        "11 9 8765-4321",       # Com espaços extras
        "+55 11 98765-4321",    # Formato internacional
        "119876543210",         # Dígito extra
        "1187654321",           # Telefone fixo → rejeitar
        "11887654321",          # Telefone fixo → rejeitar
        "",                     # Vazio
        "abc123",              # Inválido
    ]
    
    print("📋 EXEMPLOS DE CONVERSÃO:")
    print("-" * 70)
    
    for i, exemplo in enumerate(exemplos_comuns, 1):
        resultado = limpar_celular_sp(exemplo)
        status = "✅" if resultado else "❌"
        
        if resultado:
            print(f"{i:2d}. {status} '{exemplo:<20}' → '{resultado}'")
        else:
            print(f"{i:2d}. {status} '{exemplo:<20}' → REJEITADO")
    
    print("\n🎯 REGRAS DE VALIDAÇÃO:")
    print("-" * 70)
    print("✅ Aceita apenas celulares (9xxxx-xxxx)")
    print("✅ Força DDD 11 (São Paulo)")
    print("✅ Formata como (11) 9xxxx-xxxx")
    print("❌ Rejeita telefones fixos (8xxxx-xxxx, 7xxxx-xxxx, etc)")
    print("❌ Rejeita números muito curtos ou inválidos")
    print("❌ Ignora DDDs de outras cidades (converte para 11)")
    
    # Verificar dados reais se existir
    dashboard_file = Path("data/processed/dashboard_consolidacao_por_loja.xlsx")
    
    if dashboard_file.exists():
        print(f"\n📊 ESTATÍSTICAS DOS DADOS REAIS:")
        print("-" * 70)
        
        try:
            df_qualidade = pd.read_excel(dashboard_file, sheet_name='Qualidade_Dados')
            celular_data = df_qualidade[df_qualidade['campo'] == 'celular']
            
            if not celular_data.empty:
                total_preenchidos = celular_data['preenchidos'].sum()
                total_registros = celular_data['total'].sum()
                percentual = (total_preenchidos / total_registros * 100) if total_registros > 0 else 0
                
                print(f"📱 Celulares válidos encontrados: {total_preenchidos:,}")
                print(f"📊 Total de registros: {total_registros:,}")
                print(f"📈 Taxa de preenchimento: {percentual:.1f}%")
                print(f"🎯 Todos no formato: (11) 9xxxx-xxxx")
            else:
                print("📊 Dados de celular não encontrados no dashboard")
                
        except Exception as e:
            print(f"❌ Erro ao ler dados: {e}")
    
    print(f"\n🏆 BENEFÍCIOS DA PADRONIZAÇÃO:")
    print("-" * 70)
    print("✅ Formato único e consistente")
    print("✅ Facilita buscas e comparações")
    print("✅ Elimina duplicações por formato diferente")
    print("✅ Padrão brasileiro de telecomunicações")
    print("✅ Compatível com sistemas de CRM")
    
    print(f"\n📱 EXEMPLOS FINAIS VÁLIDOS:")
    print("-" * 70)
    
    exemplos_finais = [
        "(11) 99999-9999",  # Vivo
        "(11) 98888-8888",  # TIM  
        "(11) 97777-7777",  # Claro
        "(11) 96666-6666",  # Oi
        "(11) 95555-5555",  # Nextel
    ]
    
    for exemplo in exemplos_finais:
        print(f"📞 {exemplo}")

if __name__ == "__main__":
    demonstrar_validacao()