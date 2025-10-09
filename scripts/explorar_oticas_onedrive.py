#!/usr/bin/env python3
"""
Explora a pasta OneDrive das Óticas Taty Mello
"""

import os
import shutil
from pathlib import Path
import pandas as pd

def explorar_oticas_taty_mello():
    """Explora a pasta OneDrive das Óticas Taty Mello"""
    
    print("🔍 EXPLORANDO ONEDRIVE - ÓTICAS TATY MELLO")
    print("="*60)
    
    # Pasta das Óticas Taty Mello
    oticas_path = Path(r"C:\Users\junio\OneDrive - Óticas Taty Mello")
    
    if not oticas_path.exists():
        print("❌ Pasta das Óticas Taty Mello não encontrada!")
        return []
    
    print(f"📁 Explorando: {oticas_path}")
    print()
    
    # Listar pastas principais
    print("📂 PASTAS PRINCIPAIS:")
    print("-" * 30)
    
    try:
        pastas_principais = [d for d in oticas_path.iterdir() if d.is_dir()]
        for pasta in sorted(pastas_principais):
            try:
                arquivos = list(pasta.glob("*"))
                print(f"   📁 {pasta.name}/ ({len(arquivos)} itens)")
            except:
                print(f"   📁 {pasta.name}/")
    except Exception as e:
        print(f"❌ Erro ao listar pastas: {e}")
        return []
    
    print()
    
    # Buscar por pastas relacionadas a OS ou dados
    print("🔍 BUSCANDO PASTAS RELEVANTES:")
    print("-" * 40)
    
    palavras_chave = ['OS', 'ordem', 'servico', 'loja', 'cliente', 'dados', 'planilha', 'excel']
    pastas_relevantes = []
    
    for root, dirs, files in os.walk(oticas_path):
        root_path = Path(root)
        
        # Verificar se o nome da pasta contém palavras-chave
        for palavra in palavras_chave:
            if palavra.upper() in root_path.name.upper():
                pastas_relevantes.append(root_path)
                nivel = len(root_path.relative_to(oticas_path).parts)
                indent = "  " * nivel
                print(f"{indent}🎯 {root_path.relative_to(oticas_path)}")
                
                # Listar arquivos Excel nesta pasta
                try:
                    excel_files = list(root_path.glob("*.xlsx")) + list(root_path.glob("*.xls"))
                    if excel_files:
                        for excel_file in excel_files:
                            tamanho = excel_file.stat().st_size / 1024
                            tamanho_str = f"{tamanho:.1f} KB" if tamanho < 1024 else f"{tamanho/1024:.1f} MB"
                            print(f"{indent}  📊 {excel_file.name} ({tamanho_str})")
                except:
                    pass
                break
    
    if not pastas_relevantes:
        print("   ❌ Nenhuma pasta relevante encontrada com palavras-chave")
    
    print()
    
    # Buscar arquivos Excel em todo o OneDrive
    print("📊 TODOS OS ARQUIVOS EXCEL:")
    print("-" * 40)
    
    excel_files = []
    
    try:
        # Buscar recursivamente por arquivos Excel
        for root, dirs, files in os.walk(oticas_path):
            for file in files:
                if file.lower().endswith(('.xlsx', '.xls', '.csv')):
                    file_path = Path(root) / file
                    
                    try:
                        tamanho = file_path.stat().st_size
                        
                        excel_info = {
                            'arquivo': file,
                            'caminho_completo': str(file_path),
                            'pasta_pai': Path(root).name,
                            'caminho_relativo': str(file_path.relative_to(oticas_path)),
                            'tamanho_bytes': tamanho,
                            'tamanho_kb': tamanho / 1024
                        }
                        
                        excel_files.append(excel_info)
                        
                    except Exception as e:
                        print(f"   ❌ Erro ao processar {file}: {e}")
        
        # Mostrar arquivos Excel encontrados
        if excel_files:
            # Ordenar por tamanho
            excel_files.sort(key=lambda x: x['tamanho_bytes'], reverse=True)
            
            print(f"   📊 Total de arquivos Excel/CSV: {len(excel_files)}")
            print()
            
            for arquivo in excel_files:
                tamanho_str = f"{arquivo['tamanho_kb']:.1f} KB" if arquivo['tamanho_kb'] < 1024 else f"{arquivo['tamanho_kb']/1024:.1f} MB"
                print(f"   📄 {arquivo['caminho_relativo']} ({tamanho_str})")
                
                # Tentar ler preview se for pequeno
                if arquivo['tamanho_kb'] < 1000:  # Menos de 1MB
                    try:
                        df = pd.read_excel(arquivo['caminho_completo'], nrows=3)
                        if len(df.columns) > 0:
                            print(f"      Colunas: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
                    except:
                        pass
        else:
            print("   ❌ Nenhum arquivo Excel/CSV encontrado")
    
    except Exception as e:
        print(f"❌ Erro na busca de arquivos Excel: {e}")
    
    return excel_files

def copiar_arquivos_relevantes(excel_files):
    """Copia arquivos relevantes para o projeto"""
    
    if not excel_files:
        return
    
    print(f"\n📋 SELEÇÃO DE ARQUIVOS PARA CÓPIA")
    print("="*50)
    
    # Criar pasta de destino
    destino = Path("data/onedrive_backup")
    destino.mkdir(exist_ok=True)
    
    # Filtrar arquivos relevantes
    relevantes = []
    
    for arquivo in excel_files:
        nome_lower = arquivo['arquivo'].lower()
        caminho_lower = arquivo['caminho_relativo'].lower()
        
        # Critérios de relevância
        is_relevant = False
        razao = ""
        
        # Arquivos com nomes sugestivos
        if any(palavra in nome_lower for palavra in ['os', 'ordem', 'servico', 'loja', 'cliente', 'base']):
            is_relevant = True
            razao = "Nome sugestivo"
        
        # Arquivos em pastas sugestivas
        elif any(palavra in caminho_lower for palavra in ['os', 'ordem', 'servico', 'loja', 'cliente']):
            is_relevant = True
            razao = "Pasta sugestiva"
        
        # Arquivos grandes (podem conter dados importantes)
        elif arquivo['tamanho_kb'] > 50:
            is_relevant = True
            razao = "Arquivo grande"
        
        if is_relevant:
            relevantes.append((arquivo, razao))
    
    print(f"📊 Arquivos relevantes encontrados: {len(relevantes)}")
    print()
    
    arquivos_copiados = []
    
    for arquivo, razao in relevantes:
        print(f"📄 {arquivo['arquivo']} ({razao})")
        
        try:
            # Criar nome único para evitar conflitos
            nome_destino = f"{arquivo['pasta_pai']}_{arquivo['arquivo']}"
            caminho_destino = destino / nome_destino
            
            # Copiar arquivo
            shutil.copy2(arquivo['caminho_completo'], caminho_destino)
            
            tamanho_str = f"{arquivo['tamanho_kb']:.1f} KB" if arquivo['tamanho_kb'] < 1024 else f"{arquivo['tamanho_kb']/1024:.1f} MB"
            print(f"   ✅ Copiado para: {caminho_destino.name} ({tamanho_str})")
            
            arquivos_copiados.append(caminho_destino)
            
        except Exception as e:
            print(f"   ❌ Erro ao copiar: {e}")
    
    print(f"\n🎉 {len(arquivos_copiados)} arquivos copiados com sucesso!")
    print(f"📁 Destino: {destino}")
    
    return arquivos_copiados

if __name__ == "__main__":
    excel_files = explorar_oticas_taty_mello()
    if excel_files:
        copiar_arquivos_relevantes(excel_files)