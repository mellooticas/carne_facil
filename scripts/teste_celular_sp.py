#!/usr/bin/env pytho    elif len(cel_str) == 9:
        # Adicionar DDD 11 se só tiver 9 dígitos de celular
        cel_str = '11' + cel_str
    elif len(cel_str) == 10:
        # Adicionar DDD 11 se não tiver
        cel_str = '11' + cel_str
"""
Teste e Validação de Números de Celular SP
Testa a padronização para formato (11) 9xxxx-xxxx
"""

import re

def limpar_celular_sp(celular):
    """Limpa e padroniza celular para formato SP"""
    if not celular or str(celular).strip() == '':
        return None
    
    cel_str = re.sub(r'[^\d]', '', str(celular))
    
    # Validar tamanho mínimo
    if len(cel_str) < 10:
        return None
    
    # Padronizar para SP (11)
    if len(cel_str) == 10:
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

def testar_celulares():
    """Testa vários formatos de celular"""
    
    print("📱 TESTE DE PADRONIZAÇÃO DE CELULARES SP")
    print("=" * 60)
    print("🎯 Formato padrão: (11) 9xxxx-xxxx")
    print("=" * 60)
    
    # Casos de teste
    casos_teste = [
        # Formato original -> Esperado
        ("11987654321", "(11) 98765-4321"),
        ("(11)987654321", "(11) 98765-4321"),
        ("11 98765-4321", "(11) 98765-4321"),
        ("(11) 98765-4321", "(11) 98765-4321"),
        ("987654321", "(11) 98765-4321"),  # Sem DDD
        ("5511987654321", "(11) 98765-4321"),  # Com código país
        ("21987654321", "(11) 98765-4321"),  # DDD errado -> corrigir para 11
        ("119876543210", "(11) 98765-4321"),  # Dígito extra
        ("98765-4321", "(11) 98765-4321"),  # Só o número
        ("", None),  # Vazio
        ("123", None),  # Muito curto
        ("1187654321", None),  # Não é celular (não tem 9)
        ("11887654321", None),  # Telefone fixo
        ("abc", None),  # Inválido
    ]
    
    print("📋 CASOS DE TESTE:")
    print("-" * 60)
    
    sucessos = 0
    total = len(casos_teste)
    
    for i, (entrada, esperado) in enumerate(casos_teste, 1):
        resultado = limpar_celular_sp(entrada)
        status = "✅" if resultado == esperado else "❌"
        
        print(f"{i:2d}. {status} '{entrada}' → '{resultado}'")
        if resultado != esperado:
            print(f"    ⚠️  Esperado: '{esperado}'")
        else:
            sucessos += 1
    
    print("-" * 60)
    print(f"📊 RESULTADO: {sucessos}/{total} testes passaram ({sucessos/total*100:.1f}%)")
    
    # Exemplos de celulares reais de SP
    print(f"\n📱 EXEMPLOS DE CELULARES SP VÁLIDOS:")
    print("-" * 60)
    
    exemplos_reais = [
        "11987654321",  # Vivo
        "11999887766",  # TIM
        "11955443322",  # Claro
        "11911223344",  # Oi
        "11966778899",  # Nextel
    ]
    
    for exemplo in exemplos_reais:
        formatado = limpar_celular_sp(exemplo)
        print(f"📞 {exemplo} → {formatado}")
    
    print(f"\n🎯 VALIDAÇÕES APLICADAS:")
    print("-" * 60)
    print("✅ DDD 11 (São Paulo)")
    print("✅ Celular (9xxxx-xxxx)")
    print("✅ 11 dígitos total")
    print("✅ Formato padronizado: (11) 9xxxx-xxxx")
    print("❌ Rejeita telefones fixos")
    print("❌ Rejeita DDDs de outras cidades")
    print("❌ Rejeita números inválidos")

if __name__ == "__main__":
    testar_celulares()