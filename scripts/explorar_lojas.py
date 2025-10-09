"""
Script para explorar a estrutura das lojas e encontrar arquivos Excel
"""

from pathlib import Path
import os

def explorar_lojas():
    fonte_base = Path(r"D:\OneDrive - Óticas Taty Mello\LOJAS")
    
    print(f"🔍 Explorando: {fonte_base}")
    print("=" * 60)
    
    if not fonte_base.exists():
        print(f"❌ Diretório não encontrado: {fonte_base}")
        return
    
    total_arquivos = 0
    
    for loja_dir in fonte_base.iterdir():
        if loja_dir.is_dir():
            print(f"\n📁 LOJA: {loja_dir.name}")
            print("-" * 40)
            
            # Verificar se tem pasta OSs
            os_dir = loja_dir / "OSs"
            if os_dir.exists():
                print(f"  ✅ Pasta OSs encontrada")
                
                # Listar todos os arquivos Excel
                arquivos_excel = list(os_dir.glob("*.xlsx")) + list(os_dir.glob("*.xls"))
                
                if arquivos_excel:
                    print(f"  📊 Arquivos Excel encontrados: {len(arquivos_excel)}")
                    for arquivo in arquivos_excel:
                        tamanho_mb = arquivo.stat().st_size / (1024*1024)
                        print(f"    • {arquivo.name} ({tamanho_mb:.1f} MB)")
                        total_arquivos += 1
                else:
                    print(f"  ⚠️ Nenhum arquivo Excel encontrado")
                
                # Verificar especificamente OS_NOVA
                os_nova = list(os_dir.glob("OS_NOVA*"))
                if os_nova:
                    print(f"  🎯 Arquivos OS_NOVA: {len(os_nova)}")
                    for arquivo in os_nova:
                        print(f"    → {arquivo.name}")
                else:
                    print(f"  ❌ Nenhum arquivo OS_NOVA encontrado")
                    
            else:
                print(f"  ❌ Pasta OSs não encontrada")
                
                # Listar subpastas disponíveis
                subpastas = [d.name for d in loja_dir.iterdir() if d.is_dir()]
                if subpastas:
                    print(f"  📂 Subpastas disponíveis: {', '.join(subpastas)}")
    
    print(f"\n{'='*60}")
    print(f"📈 RESUMO TOTAL: {total_arquivos} arquivos Excel encontrados")
    print(f"{'='*60}")

if __name__ == "__main__":
    explorar_lojas()