#!/usr/bin/env python3
"""Importação direta dos dados 2025 - MAUA e SUZANO"""

import shutil
from pathlib import Path

def importar_dados_2025():
    # Pastas origem (OneDrive)
    base_onedrive = Path("D:/OneDrive - Óticas Taty Mello/LOJAS")
    
    # Pasta destino
    destino = Path("data/caixa_lojas")
    destino.mkdir(parents=True, exist_ok=True)
    
    # Meses 2025
    meses_2025 = ['jan_25', 'fev_25', 'mar_25', 'abr_25', 'mai_25', 'jun_25',
                  'jul_25', 'ago_25', 'set_25', 'out_25', 'nov_25', 'dez_25']
    
    # Lojas para importar
    lojas = ['MAUA', 'SUZANO']
    
    total_importados = 0
    
    for loja in lojas:
        print(f"\n📥 IMPORTANDO {loja}...")
        
        pasta_origem = base_onedrive / loja / "CAIXA"
        pasta_destino = destino / loja
        pasta_destino.mkdir(exist_ok=True)
        
        if not pasta_origem.exists():
            print(f"❌ Pasta não encontrada: {pasta_origem}")
            continue
        
        # Importar arquivos 2025
        importados_loja = 0
        for arquivo in pasta_origem.glob("*.xlsx"):
            nome = arquivo.name.lower()
            
            # Verificar se é arquivo 2025
            if any(mes in nome for mes in meses_2025):
                arquivo_destino = pasta_destino / arquivo.name
                
                try:
                    shutil.copy2(arquivo, arquivo_destino)
                    print(f"✅ {arquivo.name}")
                    importados_loja += 1
                    total_importados += 1
                except Exception as e:
                    print(f"❌ Erro em {arquivo.name}: {e}")
        
        print(f"📊 {loja}: {importados_loja} arquivos importados")
    
    print(f"\n🎉 TOTAL IMPORTADO: {total_importados} arquivos 2025")
    return total_importados

if __name__ == "__main__":
    print("📥 IMPORTADOR DIRETO - DADOS 2025")
    print("=" * 40)
    importar_dados_2025()