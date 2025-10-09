#!/usr/bin/env python3
"""
Script para buscar arquivos OS_NOVA*.xlsm em todo o sistema
"""

import os
from pathlib import Path

def buscar_arquivos_os_nova_sistema():
    """Busca arquivos OS_NOVA*.xlsm em drives principais"""
    
    print("🔍 BUSCA COMPLETA POR ARQUIVOS OS_NOVA*.xlsm")
    print("=" * 60)
    
    arquivos_encontrados = []
    
    # Drives para verificar
    drives = ['C:', 'D:', 'E:', 'F:']
    
    for drive in drives:
        drive_path = Path(f"{drive}/")
        if not drive_path.exists():
            continue
            
        print(f"\n📁 Verificando drive {drive}")
        
        try:
            # Buscar diretamente na raiz do drive
            for item in drive_path.iterdir():
                if item.is_file() and item.name.startswith("OS_NOVA") and item.name.endswith(".xlsm"):
                    arquivos_encontrados.append(item)
                    print(f"   ✅ {item}")
                
                # Buscar em subpastas principais
                elif item.is_dir() and item.name in ['Lojas', 'Users', 'projetos', 'Desktop', 'Documents', 'Downloads']:
                    print(f"   🔍 Verificando pasta: {item.name}")
                    
                    try:
                        for root, dirs, files in os.walk(item):
                            # Limitar profundidade para evitar busca muito lenta
                            level = str(root).count(os.sep) - str(item).count(os.sep)
                            if level > 3:  # Máximo 3 níveis de profundidade
                                continue
                                
                            for file in files:
                                if file.startswith("OS_NOVA") and file.endswith(".xlsm"):
                                    arquivo_path = Path(root) / file
                                    arquivos_encontrados.append(arquivo_path)
                                    print(f"      ✅ {file} em {root}")
                    except (PermissionError, OSError):
                        continue
                        
        except (PermissionError, OSError):
            print(f"   ⚠️ Sem permissão para acessar {drive}")
            continue
    
    # Buscar também em locais específicos do usuário
    usuario_paths = [
        Path.home() / "Desktop",
        Path.home() / "Documents", 
        Path.home() / "Downloads",
        Path.home() / "OneDrive"
    ]
    
    print(f"\n📁 Verificando pastas do usuário:")
    for pasta in usuario_paths:
        if pasta.exists():
            print(f"   🔍 {pasta}")
            try:
                for root, dirs, files in os.walk(pasta):
                    for file in files:
                        if file.startswith("OS_NOVA") and file.endswith(".xlsm"):
                            arquivo_path = Path(root) / file
                            if arquivo_path not in arquivos_encontrados:
                                arquivos_encontrados.append(arquivo_path)
                                print(f"      ✅ {file} em {root}")
            except (PermissionError, OSError):
                continue
    
    print(f"\n📊 RESULTADO DA BUSCA:")
    print(f"   • Total de arquivos OS_NOVA*.xlsm encontrados: {len(arquivos_encontrados)}")
    
    if arquivos_encontrados:
        print(f"\n📋 ARQUIVOS ENCONTRADOS:")
        for i, arquivo in enumerate(arquivos_encontrados, 1):
            try:
                tamanho_mb = arquivo.stat().st_size / (1024 * 1024)
                print(f"   {i:2d}. {arquivo.name}")
                print(f"       📁 {arquivo.parent}")
                print(f"       📏 {tamanho_mb:.1f} MB")
            except:
                print(f"   {i:2d}. {arquivo.name}")
                print(f"       📁 {arquivo.parent}")
    else:
        print("\n❌ Nenhum arquivo OS_NOVA*.xlsm encontrado")
        print("\n💡 SUGESTÕES:")
        print("   1. Verifique se os arquivos existem")
        print("   2. Confirme se começam com 'OS_NOVA'")
        print("   3. Confirme se têm extensão '.xlsm'")
        print("   4. Verifique se estão em pastas acessíveis")
    
    return arquivos_encontrados

def buscar_arquivos_similares():
    """Busca arquivos similares (OS*.xlsm, *NOVA*.xlsm, etc)"""
    
    print(f"\n🔍 BUSCA POR ARQUIVOS SIMILARES")
    print("=" * 60)
    
    padroes = ["OS*.xlsm", "*NOVA*.xlsm", "*OS_*.xlsm"]
    drives = ['C:', 'D:']
    
    for drive in drives:
        if not Path(f"{drive}/").exists():
            continue
            
        print(f"\n📁 Drive {drive} - buscando padrões similares:")
        
        for pasta in [Path(f"{drive}/"), Path.home()]:
            if not pasta.exists():
                continue
                
            try:
                for item in pasta.iterdir():
                    if item.is_file():
                        nome = item.name.upper()
                        if (nome.endswith('.XLSM') and 
                            ('OS' in nome or 'NOVA' in nome)):
                            print(f"   📄 {item.name} em {item.parent}")
            except (PermissionError, OSError):
                continue

if __name__ == "__main__":
    arquivos = buscar_arquivos_os_nova_sistema()
    
    if not arquivos:
        buscar_arquivos_similares()