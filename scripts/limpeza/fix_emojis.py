import re

def remove_emojis_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove todos os emojis unicode
    content = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000026FF\U00002700-\U000027BF]', '', content)
    
    # Substitui emojis específicos por texto
    replacements = {
        '✅': 'OK',
        '❌': 'ERRO', 
        '🔍': '>',
        '📊': '*',
        '🎯': '*',
        '👤': '*',
        '👁️': '*',
        '💰': '*',
        '📋': '*',
        '📄': '*',
        '📌': '*',
        '📈': '*',
        '💾': '*',
        '⚠️': 'AVISO',
        '📁': '*',
        '🔄': '*',
        '🔗': '*',
        '🚀': '*',
        '👥': '*',
        '🏪': '*',
        '💡': '*',
        '🎉': '*'
    }
    
    for emoji, replacement in replacements.items():
        content = content.replace(emoji, replacement)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'Emojis removidos de {file_path}!')

if __name__ == "__main__":
    scripts = [
        'scripts/criar_sistema_id_cliente.py',
        'scripts/extrair_dioptrias.py', 
        'scripts/extrair_vendas.py',
        'scripts/criar_relacionamento_os_cliente.py',
        'scripts/sistema_final_integrado.py'
    ]
    
    for script in scripts:
        try:
            remove_emojis_from_file(script)
        except Exception as e:
            print(f'Erro ao processar {script}: {e}')