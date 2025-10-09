"""
Teste rápido do sistema de análise
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from analisar_os import AnalisadorOS

def teste_rapido():
    print("🔍 Testando sistema de análise...")
    
    # Inicializar analisador
    analisador = AnalisadorOS()
    
    # Verificar arquivos disponíveis
    arquivos = list(analisador.diretorio_dados.glob("*.xlsx"))
    print(f"📁 Arquivos encontrados: {len(arquivos)}")
    
    for arquivo in arquivos:
        print(f"  • {arquivo.name}")
    
    if arquivos:
        # Processar o primeiro arquivo
        arquivo_teste = arquivos[0]
        print(f"\n🔬 Analisando: {arquivo_teste.name}")
        
        resultado = analisador.processar_arquivo(arquivo_teste)
        
        print(f"\n📊 RESULTADO:")
        print(f"  Status: {resultado['status']}")
        print(f"  Linhas originais: {resultado['linhas_original']}")
        print(f"  Linhas processadas: {resultado['linhas_processadas']}")
        print(f"  Clientes únicos: {resultado['clientes_unicos']}")
        print(f"  Duplicatas detectadas: {resultado['duplicatas_detectadas']}")
        print(f"  Colunas encontradas: {len(resultado['colunas_encontradas'])}")
        
        if resultado['colunas_encontradas']:
            print(f"\n📋 Primeiras 5 colunas:")
            for i, col in enumerate(resultado['colunas_encontradas'][:5]):
                print(f"    {i+1}. {col}")
        
        if resultado['status'] == 'sucesso':
            print(f"\n✅ SUCESSO! Arquivo processado.")
            if 'arquivo_saida' in resultado:
                print(f"   Salvo em: {resultado['arquivo_saida']}")
        else:
            print(f"\n❌ ERRO:")
            for erro in resultado.get('erros', []):
                print(f"   • {erro}")
    
    else:
        print("\n⚠️ Nenhum arquivo encontrado para processar")

if __name__ == "__main__":
    teste_rapido()