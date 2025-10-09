#!/usr/bin/env python3
"""
Busca específica nas pastas de OSs das lojas
"""

import os
import shutil
from pathlib import Path
import pandas as pd

def buscar_pasta_os():
    """Busca especificamente nas pastas de OSs"""
    
    print("🔍 BUSCA ESPECÍFICA NAS PASTAS DE OSs")
    print("="*60)
    
    # Pasta das Óticas Taty Mello
    oticas_path = Path(r"C:\Users\junio\OneDrive - Óticas Taty Mello")
    
    if not oticas_path.exists():
        print("❌ Pasta das Óticas Taty Mello não encontrada!")
        return []
    
    # Focar na pasta LOJAS
    lojas_path = oticas_path / "LOJAS"
    
    if not lojas_path.exists():
        print("❌ Pasta LOJAS não encontrada!")
        return []
    
    print(f"📁 Explorando: {lojas_path}")
    print()
    
    # Lojas de interesse
    lojas_operacionais = ['SUZANO', 'MAUA', 'RIO_PEQUENO', 'SAO_MATEUS', 'PERUS', 'SUZANO2']
    
    arquivos_encontrados = []
    
    for loja in lojas_operacionais:
        print(f"🏪 EXPLORANDO LOJA: {loja}")
        print("-" * 40)
        
        loja_path = lojas_path / loja
        if not loja_path.exists():
            print(f"   ❌ Pasta {loja} não encontrada")
            continue
        
        # Buscar pasta OSs
        os_path = loja_path / "OSs"
        if not os_path.exists():
            print(f"   ❌ Pasta OSs não encontrada em {loja}")
            
            # Listar o que tem na pasta da loja
            try:
                itens = list(loja_path.iterdir())
                print(f"   📂 Itens disponíveis: {[item.name for item in itens if item.is_dir()]}")
            except:
                pass
            continue
        
        print(f"   ✅ Pasta OSs encontrada!")
        
        # Explorar recursivamente a pasta OSs
        arquivos_loja = []
        
        try:
            for root, dirs, files in os.walk(os_path):
                root_path = Path(root)
                
                for file in files:
                    file_path = root_path / file
                    
                    # Interessar por arquivos potencialmente úteis
                    extensao = file_path.suffix.lower()
                    if extensao in ['.xlsx', '.xls', '.csv', '.txt', '.pdf']:
                        
                        try:
                            tamanho = file_path.stat().st_size
                            
                            arquivo_info = {
                                'loja': loja,
                                'arquivo': file,
                                'caminho_completo': str(file_path),
                                'pasta_pai': root_path.name,
                                'caminho_relativo': str(file_path.relative_to(os_path)),
                                'extensao': extensao,
                                'tamanho_bytes': tamanho,
                                'tamanho_kb': tamanho / 1024
                            }
                            
                            arquivos_loja.append(arquivo_info)
                            arquivos_encontrados.append(arquivo_info)
                            
                        except Exception as e:
                            print(f"   ❌ Erro ao processar {file}: {e}")
            
            # Mostrar arquivos encontrados nesta loja
            if arquivos_loja:
                print(f"   📊 Arquivos encontrados: {len(arquivos_loja)}")
                
                # Agrupar por extensão
                por_extensao = {}
                for arquivo in arquivos_loja:
                    ext = arquivo['extensao']
                    if ext not in por_extensao:
                        por_extensao[ext] = []
                    por_extensao[ext].append(arquivo)
                
                for ext in sorted(por_extensao.keys()):
                    arquivos_ext = por_extensao[ext]
                    print(f"   📋 {ext.upper()}: {len(arquivos_ext)} arquivos")
                    
                    # Mostrar os maiores arquivos
                    arquivos_ext.sort(key=lambda x: x['tamanho_bytes'], reverse=True)
                    for arquivo in arquivos_ext[:3]:  # Top 3
                        tamanho_str = f"{arquivo['tamanho_kb']:.1f} KB" if arquivo['tamanho_kb'] < 1024 else f"{arquivo['tamanho_kb']/1024:.1f} MB"
                        print(f"      📄 {arquivo['caminho_relativo']} ({tamanho_str})")
            else:
                print(f"   📂 Nenhum arquivo relevante encontrado")
        
        except Exception as e:
            print(f"   ❌ Erro ao explorar pasta OSs: {e}")
        
        print()
    
    # Resumo geral
    print("📊 RESUMO GERAL")
    print("="*50)
    
    if arquivos_encontrados:
        print(f"📈 Total de arquivos encontrados: {len(arquivos_encontrados)}")
        
        # Por loja
        por_loja = {}
        for arquivo in arquivos_encontrados:
            loja = arquivo['loja']
            if loja not in por_loja:
                por_loja[loja] = []
            por_loja[loja].append(arquivo)
        
        print("\n📊 Por loja:")
        for loja in sorted(por_loja.keys()):
            arquivos_loja = por_loja[loja]
            print(f"   🏪 {loja}: {len(arquivos_loja)} arquivos")
        
        # Por extensão
        por_extensao = {}
        for arquivo in arquivos_encontrados:
            ext = arquivo['extensao']
            if ext not in por_extensao:
                por_extensao[ext] = []
            por_extensao[ext].append(arquivo)
        
        print("\n📊 Por extensão:")
        for ext in sorted(por_extensao.keys()):
            arquivos_ext = por_extensao[ext]
            print(f"   📋 {ext.upper()}: {len(arquivos_ext)} arquivos")
        
        # Arquivos Excel mais promissores
        excel_files = [a for a in arquivos_encontrados if a['extensao'] in ['.xlsx', '.xls', '.csv']]
        if excel_files:
            print(f"\n🎯 ARQUIVOS EXCEL/CSV MAIS PROMISSORES:")
            print("-" * 40)
            
            excel_files.sort(key=lambda x: x['tamanho_bytes'], reverse=True)
            
            for arquivo in excel_files[:10]:  # Top 10
                tamanho_str = f"{arquivo['tamanho_kb']:.1f} KB" if arquivo['tamanho_kb'] < 1024 else f"{arquivo['tamanho_kb']/1024:.1f} MB"
                print(f"   📊 {arquivo['loja']}/{arquivo['caminho_relativo']} ({tamanho_str})")
    
    else:
        print("❌ Nenhum arquivo encontrado nas pastas de OSs")
    
    return arquivos_encontrados

def copiar_arquivos_os(arquivos_encontrados):
    """Copia arquivos de OSs relevantes"""
    
    if not arquivos_encontrados:
        return []
    
    print(f"\n📋 CÓPIA DE ARQUIVOS DE OSs")
    print("="*50)
    
    # Criar pasta de destino
    destino = Path("data/lojas_os")
    destino.mkdir(exist_ok=True)
    
    # Filtrar apenas Excel/CSV
    excel_files = [a for a in arquivos_encontrados if a['extensao'] in ['.xlsx', '.xls', '.csv']]
    
    if not excel_files:
        print("❌ Nenhum arquivo Excel/CSV encontrado")
        return []
    
    print(f"📊 Arquivos Excel/CSV encontrados: {len(excel_files)}")
    
    arquivos_copiados = []
    
    for arquivo in excel_files:
        print(f"📄 {arquivo['loja']}/{arquivo['caminho_relativo']}")
        
        try:
            # Criar nome único
            nome_destino = f"{arquivo['loja']}_{arquivo['arquivo']}"
            caminho_destino = destino / nome_destino
            
            # Copiar arquivo
            shutil.copy2(arquivo['caminho_completo'], caminho_destino)
            
            tamanho_str = f"{arquivo['tamanho_kb']:.1f} KB" if arquivo['tamanho_kb'] < 1024 else f"{arquivo['tamanho_kb']/1024:.1f} MB"
            print(f"   ✅ Copiado: {nome_destino} ({tamanho_str})")
            
            arquivos_copiados.append(caminho_destino)
            
        except Exception as e:
            print(f"   ❌ Erro ao copiar: {e}")
    
    print(f"\n🎉 {len(arquivos_copiados)} arquivos copiados!")
    print(f"📁 Destino: {destino}")
    
    return arquivos_copiados

if __name__ == "__main__":
    arquivos = buscar_pasta_os()
    if arquivos:
        copiar_arquivos_os(arquivos)