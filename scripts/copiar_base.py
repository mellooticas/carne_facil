"""
Script para copiar arquivos base.xlsx das lojas para o projeto
"""

import shutil
from pathlib import Path
import os

def copiar_arquivos_base():
    fonte_base = Path(r"D:\OneDrive - Óticas Taty Mello\LOJAS")
    destino = Path("data/raw")
    
    # Criar diretório de destino se não existir
    destino.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Fonte: {fonte_base}")
    print(f"📁 Destino: {destino.absolute()}")
    print("=" * 60)
    
    arquivos_copiados = []
    erros = []
    
    if not fonte_base.exists():
        print(f"❌ Diretório fonte não encontrado: {fonte_base}")
        return [], [f"Diretório não encontrado: {fonte_base}"]
    
    for loja_dir in fonte_base.iterdir():
        if loja_dir.is_dir():
            os_dir = loja_dir / "OSs"
            
            if os_dir.exists():
                print(f"\n🏪 Processando loja: {loja_dir.name}")
                
                # Procurar arquivo base.xlsx
                arquivo_base = os_dir / "base.xlsx"
                
                if arquivo_base.exists():
                    try:
                        # Nome do arquivo de destino com prefixo da loja
                        nome_destino = f"base_{loja_dir.name}.xlsx"
                        arquivo_destino = destino / nome_destino
                        
                        # Copiar arquivo
                        shutil.copy2(arquivo_base, arquivo_destino)
                        
                        tamanho_kb = arquivo_base.stat().st_size / 1024
                        arquivos_copiados.append({
                            'origem': str(arquivo_base),
                            'destino': str(arquivo_destino),
                            'loja': loja_dir.name,
                            'tamanho': arquivo_base.stat().st_size
                        })
                        
                        print(f"  ✅ Copiado: base.xlsx -> {nome_destino} ({tamanho_kb:.1f} KB)")
                        
                    except Exception as e:
                        erro = f"Erro ao copiar {arquivo_base}: {e}"
                        erros.append(erro)
                        print(f"  ❌ {erro}")
                else:
                    print(f"  ⚠️ Arquivo base.xlsx não encontrado")
            else:
                print(f"  ❌ Pasta OSs não encontrada em: {loja_dir.name}")
    
    # Relatório final
    print(f"\n{'='*60}")
    print(f"📊 RELATÓRIO DE CÓPIA")
    print(f"{'='*60}")
    print(f"✅ Arquivos copiados: {len(arquivos_copiados)}")
    print(f"❌ Erros: {len(erros)}")
    
    if arquivos_copiados:
        print(f"\n📋 Arquivos copiados com sucesso:")
        total_tamanho = 0
        for arquivo in arquivos_copiados:
            tamanho_kb = arquivo['tamanho'] / 1024
            total_tamanho += arquivo['tamanho']
            print(f"  📄 {arquivo['loja']}: {Path(arquivo['destino']).name} ({tamanho_kb:.1f} KB)")
        
        print(f"\n📈 Tamanho total: {total_tamanho/1024:.1f} KB")
    
    if erros:
        print(f"\n❌ Erros encontrados:")
        for erro in erros:
            print(f"  • {erro}")
    
    print(f"\n🎯 Próximos passos:")
    print(f"  1. Verifique os arquivos em: {destino.absolute()}")
    print(f"  2. Execute o processamento: python scripts/analisar_os.py")
    print(f"  3. Ou use o notebook: notebooks/analise_exploratoria.ipynb")
    
    return arquivos_copiados, erros

if __name__ == "__main__":
    print("🚀 Iniciando cópia de arquivos base.xlsx...")
    
    try:
        arquivos, erros = copiar_arquivos_base()
        
        if arquivos:
            print(f"\n🎉 Cópia concluída com sucesso!")
            print(f"   {len(arquivos)} arquivos prontos para análise.")
        else:
            print(f"\n⚠️ Nenhum arquivo foi copiado.")
            print(f"   Verifique se os arquivos existem nas lojas.")
            
    except Exception as e:
        print(f"\n💥 Erro geral: {e}")
        print(f"   Verifique as permissões e caminhos.")