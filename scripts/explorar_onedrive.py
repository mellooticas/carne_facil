#!/usr/bin/env python3
"""
Explora a pasta OneDrive original para encontrar mais arquivos
"""

import os
from pathlib import Path
import pandas as pd

def explorar_onedrive():
    """Explora a pasta OneDrive original"""
    
    print("🔍 EXPLORAÇÃO DA PASTA ONEDRIVE ORIGINAL")
    print("="*60)
    
    # Pasta original do OneDrive
    onedrive_path = Path(r"C:\Users\leona\OneDrive\SOMENTE PARA OS")
    
    if not onedrive_path.exists():
        print("❌ Pasta OneDrive não encontrada!")
        return []
    
    print(f"📁 Explorando: {onedrive_path}")
    print()
    
    todos_arquivos = []
    
    # Explorar recursivamente
    for root, dirs, files in os.walk(onedrive_path):
        root_path = Path(root)
        nivel = len(root_path.relative_to(onedrive_path).parts)
        
        # Mostrar estrutura de pastas
        if root != str(onedrive_path):
            pasta_rel = root_path.relative_to(onedrive_path)
            indent = "  " * (nivel - 1)
            print(f"{indent}📁 {pasta_rel}/")
        
        # Processar arquivos na pasta atual
        if files:
            for file in files:
                arquivo_path = root_path / file
                
                try:
                    tamanho = arquivo_path.stat().st_size
                    extensao = arquivo_path.suffix.lower()
                    
                    arquivo_info = {
                        'arquivo': file,
                        'caminho_completo': str(arquivo_path),
                        'pasta_pai': root_path.name,
                        'caminho_relativo': str(arquivo_path.relative_to(onedrive_path)),
                        'extensao': extensao,
                        'tamanho_bytes': tamanho,
                        'tamanho_kb': tamanho / 1024,
                        'nivel': nivel
                    }
                    
                    todos_arquivos.append(arquivo_info)
                    
                    # Mostrar arquivo
                    indent = "  " * nivel
                    tamanho_str = f"{arquivo_info['tamanho_kb']:.1f} KB" if arquivo_info['tamanho_kb'] < 1024 else f"{arquivo_info['tamanho_kb']/1024:.1f} MB"
                    
                    # Destacar arquivos importantes
                    if extensao in ['.xlsx', '.xls', '.csv']:
                        emoji = "📊"
                    elif extensao in ['.txt', '.log']:
                        emoji = "📄"
                    else:
                        emoji = "📋"
                    
                    print(f"{indent}{emoji} {file} ({tamanho_str})")
                    
                except Exception as e:
                    print(f"{indent}❌ Erro ao processar {file}: {e}")
    
    print()
    
    # Análise dos arquivos encontrados
    print("📊 ANÁLISE DOS ARQUIVOS ENCONTRADOS")
    print("="*50)
    
    if todos_arquivos:
        # Por extensão
        extensoes = {}
        for arquivo in todos_arquivos:
            ext = arquivo['extensao']
            if ext not in extensoes:
                extensoes[ext] = []
            extensoes[ext].append(arquivo)
        
        print("📈 Resumo por extensão:")
        for ext in sorted(extensoes.keys()):
            arquivos_ext = extensoes[ext]
            tamanho_total = sum(a['tamanho_kb'] for a in arquivos_ext)
            print(f"   🏷️ {ext.upper() if ext else 'SEM EXTENSÃO'}: {len(arquivos_ext)} arquivos ({tamanho_total:.1f} KB)")
        
        # Arquivos Excel/CSV mais interessantes
        print(f"\n🎯 ARQUIVOS EXCEL/CSV IMPORTANTES")
        print("-" * 40)
        
        excel_csv = [a for a in todos_arquivos if a['extensao'] in ['.xlsx', '.xls', '.csv']]
        
        if excel_csv:
            # Ordenar por tamanho
            excel_csv.sort(key=lambda x: x['tamanho_bytes'], reverse=True)
            
            for arquivo in excel_csv:
                tamanho_str = f"{arquivo['tamanho_kb']:.1f} KB" if arquivo['tamanho_kb'] < 1024 else f"{arquivo['tamanho_kb']/1024:.1f} MB"
                print(f"   📊 {arquivo['caminho_relativo']} ({tamanho_str})")
                
                # Se não for o base.xlsx, tentar analisar rapidamente
                if 'base.xlsx' not in arquivo['arquivo'].lower():
                    try:
                        df = pd.read_excel(arquivo['caminho_completo'], nrows=5)
                        print(f"      Colunas: {', '.join(df.columns)}")
                        print(f"      Registros: ~{len(df)} (preview)")
                    except Exception as e:
                        print(f"      ❌ Erro ao ler: {e}")
        else:
            print("   ❌ Nenhum arquivo Excel/CSV encontrado")
        
        # Buscar arquivos com padrões interessantes
        print(f"\n🔍 ARQUIVOS COM PADRÕES INTERESSANTES")
        print("-" * 40)
        
        padroes = ['cliente', 'vendas', 'receita', 'historico', 'backup', 'completo', 'consolidado', 'relatorio']
        interessantes = []
        
        for arquivo in todos_arquivos:
            nome_lower = arquivo['arquivo'].lower()
            for padrao in padroes:
                if padrao in nome_lower:
                    interessantes.append((arquivo, padrao))
        
        if interessantes:
            for arquivo, padrao in interessantes:
                tamanho_str = f"{arquivo['tamanho_kb']:.1f} KB" if arquivo['tamanho_kb'] < 1024 else f"{arquivo['tamanho_kb']/1024:.1f} MB"
                print(f"   🎯 {arquivo['caminho_relativo']} ('{padrao}' - {tamanho_str})")
        else:
            print("   ❌ Nenhum arquivo com padrão interessante")
        
        # Arquivos grandes que podem conter dados importantes
        print(f"\n📈 ARQUIVOS GRANDES (>50KB)")
        print("-" * 30)
        
        grandes = [a for a in todos_arquivos if a['tamanho_kb'] > 50]
        if grandes:
            grandes.sort(key=lambda x: x['tamanho_bytes'], reverse=True)
            for arquivo in grandes[:10]:  # Top 10
                tamanho_str = f"{arquivo['tamanho_kb']:.1f} KB" if arquivo['tamanho_kb'] < 1024 else f"{arquivo['tamanho_kb']/1024:.1f} MB"
                print(f"   📦 {arquivo['caminho_relativo']} ({tamanho_str})")
        else:
            print("   ❌ Nenhum arquivo grande encontrado")
    
    else:
        print("❌ Nenhum arquivo encontrado")
    
    return todos_arquivos

if __name__ == "__main__":
    arquivos = explorar_onedrive()