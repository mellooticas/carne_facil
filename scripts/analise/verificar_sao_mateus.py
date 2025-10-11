#!/usr/bin/env python3
"""Verificar dados de São Mateus no OneDrive"""

from pathlib import Path
import shutil

def verificar_sao_mateus():
    print("🔍 VERIFICANDO SÃO MATEUS NO ONEDRIVE")
    print("=" * 50)
    
    # Verificar se São Mateus existe no OneDrive
    base_onedrive = Path("D:/OneDrive - Óticas Taty Mello/LOJAS")
    pasta_sao_mateus = base_onedrive / "SAO_MATEUS"
    
    print(f"📁 Caminho: {pasta_sao_mateus}")
    
    if pasta_sao_mateus.exists():
        print("✅ Pasta São Mateus encontrada!")
        
        pasta_caixa = pasta_sao_mateus / "CAIXA"
        if pasta_caixa.exists():
            print("✅ Pasta CAIXA encontrada!")
            
            # Listar arquivos
            arquivos = list(pasta_caixa.glob("*.xlsx"))
            print(f"📄 Arquivos encontrados: {len(arquivos)}")
            
            for arquivo in sorted(arquivos)[:15]:  # Primeiros 15
                print(f"   📄 {arquivo.name}")
            
            if len(arquivos) > 15:
                print(f"   ... e mais {len(arquivos) - 15} arquivos")
            
            # Verificar pastas de anos
            pastas_anos = [d for d in pasta_caixa.iterdir() if d.is_dir()]
            print(f"📁 Pastas encontradas: {len(pastas_anos)}")
            for pasta in pastas_anos:
                arquivos_pasta = list(pasta.glob("*.xlsx"))
                print(f"   📁 {pasta.name}: {len(arquivos_pasta)} arquivos")
            
            return True
        else:
            print("❌ Pasta CAIXA não encontrada")
            return False
    else:
        print("❌ São Mateus não encontrado no OneDrive")
        return False

def importar_sao_mateus():
    """Importar dados de São Mateus"""
    print("\n📥 IMPORTANDO DADOS DE SÃO MATEUS")
    print("=" * 40)
    
    origem = Path("D:/OneDrive - Óticas Taty Mello/LOJAS/SAO_MATEUS/CAIXA")
    destino = Path("data/caixa_lojas/SAO_MATEUS")
    
    if not origem.exists():
        print("❌ Origem não encontrada")
        return False
    
    # Criar pasta destino
    destino.mkdir(parents=True, exist_ok=True)
    
    importados = 0
    
    # Importar arquivos da raiz
    for arquivo in origem.glob("*.xlsx"):
        try:
            arquivo_destino = destino / arquivo.name
            shutil.copy2(arquivo, arquivo_destino)
            print(f"   ✅ {arquivo.name}")
            importados += 1
        except Exception as e:
            print(f"   ❌ Erro em {arquivo.name}: {e}")
    
    # Importar pastas de anos
    for pasta in origem.iterdir():
        if pasta.is_dir():
            pasta_destino = destino / pasta.name
            if not pasta_destino.exists():
                try:
                    shutil.copytree(pasta, pasta_destino)
                    arquivos_copiados = len(list(pasta_destino.glob("*.xlsx")))
                    importados += arquivos_copiados
                    print(f"   ✅ {pasta.name}: {arquivos_copiados} arquivos")
                except Exception as e:
                    print(f"   ❌ Erro na pasta {pasta.name}: {e}")
    
    print(f"\n📊 Total importado: {importados} arquivos")
    return importados > 0

if __name__ == "__main__":
    if verificar_sao_mateus():
        resposta = input("\n❓ Importar dados de São Mateus? (s/N): ").strip().lower()
        if resposta in ['s', 'sim', 'y', 'yes']:
            importar_sao_mateus()
        else:
            print("❌ Importação cancelada")
    else:
        print("❌ Não foi possível verificar São Mateus")