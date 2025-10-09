#!/usr/bin/env python3
"""
Busca pela pasta do OneDrive no sistema
"""

import os
from pathlib import Path
import subprocess

def encontrar_onedrive():
    """Encontra a pasta do OneDrive no sistema"""
    
    print("🔍 BUSCANDO PASTA DO ONEDRIVE")
    print("="*50)
    
    # Possíveis localizações do OneDrive
    possiveis_caminhos = [
        Path.home() / "OneDrive",
        Path.home() / "OneDrive - Personal",
        Path("C:/Users") / os.getenv('USERNAME', 'user') / "OneDrive",
        Path("C:/Users") / os.getenv('USERNAME', 'user') / "OneDrive - Personal",
        Path("D:/OneDrive"),
        Path("E:/OneDrive"),
    ]
    
    # Também verificar via registro do Windows
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\OneDrive\Accounts\Personal")
        onedrive_path = winreg.QueryValueEx(key, "UserFolder")[0]
        possiveis_caminhos.insert(0, Path(onedrive_path))
        winreg.CloseKey(key)
        print(f"📍 Caminho do registro: {onedrive_path}")
    except Exception as e:
        print(f"⚠️ Não foi possível ler o registro: {e}")
    
    print("\n🔍 Verificando possíveis localizações...")
    
    for caminho in possiveis_caminhos:
        print(f"   📁 Verificando: {caminho}")
        if caminho.exists():
            print(f"   ✅ Encontrado!")
            
            # Procurar pela pasta específica
            pasta_os = caminho / "SOMENTE PARA OS"
            if pasta_os.exists():
                print(f"   🎯 Pasta SOMENTE PARA OS encontrada!")
                return pasta_os
            else:
                # Listar subpastas para ajudar
                try:
                    subpastas = [d for d in caminho.iterdir() if d.is_dir()]
                    print(f"   📂 Subpastas encontradas: {len(subpastas)}")
                    for subpasta in subpastas[:10]:  # Primeiras 10
                        print(f"      • {subpasta.name}")
                    if len(subpastas) > 10:
                        print(f"      ... e mais {len(subpastas) - 10}")
                except Exception as e:
                    print(f"   ❌ Erro ao listar: {e}")
        else:
            print(f"   ❌ Não existe")
    
    print("\n🔍 BUSCA ALTERNATIVA")
    print("-" * 30)
    
    # Buscar em todo o sistema por pastas com "OS" no nome
    print("Buscando pastas com 'OS' no nome...")
    
    # Verificar drives disponíveis
    drives = ['C:', 'D:', 'E:']
    for drive in drives:
        if Path(drive).exists():
            print(f"\n📁 Buscando em {drive}")
            try:
                # Buscar apenas em Users e raiz
                for pasta_base in [Path(drive) / "Users", Path(drive)]:
                    if pasta_base.exists():
                        for root, dirs, files in os.walk(pasta_base):
                            # Limitar profundidade
                            if len(Path(root).parts) > 6:
                                continue
                            
                            for d in dirs:
                                if "OS" in d.upper() and ("SOMENTE" in d.upper() or "PARA" in d.upper()):
                                    pasta_encontrada = Path(root) / d
                                    print(f"   🎯 Possível: {pasta_encontrada}")
                                    
                                    # Verificar se tem arquivos Excel
                                    try:
                                        excel_files = list(pasta_encontrada.glob("*.xlsx"))
                                        if excel_files:
                                            print(f"      ✅ Contém {len(excel_files)} arquivos Excel")
                                            return pasta_encontrada
                                    except:
                                        pass
            except Exception as e:
                print(f"   ❌ Erro na busca: {e}")
    
    print("\n❌ Pasta OneDrive não encontrada automaticamente")
    print("\n💡 SUGESTÕES:")
    print("1. Verifique se o OneDrive está sincronizado")
    print("2. Procure manualmente pela pasta 'SOMENTE PARA OS'")
    print("3. Copie os arquivos para uma pasta local")
    
    return None

def listar_conteudo_pasta(pasta_path):
    """Lista o conteúdo de uma pasta encontrada"""
    
    if not pasta_path or not pasta_path.exists():
        return
    
    print(f"\n📁 CONTEÚDO DE: {pasta_path}")
    print("="*60)
    
    try:
        for item in pasta_path.iterdir():
            if item.is_file():
                tamanho = item.stat().st_size / 1024  # KB
                tamanho_str = f"{tamanho:.1f} KB" if tamanho < 1024 else f"{tamanho/1024:.1f} MB"
                print(f"   📄 {item.name} ({tamanho_str})")
            elif item.is_dir():
                try:
                    arquivos = list(item.glob("*"))
                    print(f"   📁 {item.name}/ ({len(arquivos)} itens)")
                except:
                    print(f"   📁 {item.name}/")
    except Exception as e:
        print(f"❌ Erro ao listar: {e}")

if __name__ == "__main__":
    pasta_os = encontrar_onedrive()
    if pasta_os:
        listar_conteudo_pasta(pasta_os)