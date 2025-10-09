#!/usr/bin/env python3
"""
Busca por outros arquivos nas pastas das lojas operacionais
"""

import os
from pathlib import Path
import pandas as pd

def explorar_arquivos_lojas():
    """Explora todos os arquivos nas pastas das lojas operacionais"""
    
    print("🔍 EXPLORAÇÃO DE ARQUIVOS NAS LOJAS OPERACIONAIS")
    print("="*70)
    
    # Lojas operacionais identificadas
    lojas_operacionais = ['SUZANO', 'MAUA', 'RIO_PEQUENO']
    
    # Pasta base dos dados
    data_dir = Path("data")
    
    todos_arquivos = []
    
    for loja in lojas_operacionais:
        print(f"\n🏪 EXPLORANDO LOJA: {loja}")
        print("-" * 40)
        
        loja_path = data_dir / loja
        if not loja_path.exists():
            print("❌ Pasta não encontrada")
            continue
        
        # Listar todos os arquivos na pasta
        arquivos_loja = []
        for root, dirs, files in os.walk(loja_path):
            for file in files:
                arquivo_path = Path(root) / file
                tamanho = arquivo_path.stat().st_size
                extensao = arquivo_path.suffix.lower()
                
                arquivo_info = {
                    'loja': loja,
                    'arquivo': file,
                    'caminho_completo': str(arquivo_path),
                    'caminho_relativo': str(arquivo_path.relative_to(data_dir)),
                    'extensao': extensao,
                    'tamanho_bytes': tamanho,
                    'tamanho_kb': tamanho / 1024,
                    'subpasta': str(Path(root).relative_to(loja_path)) if root != str(loja_path) else '.'
                }
                
                arquivos_loja.append(arquivo_info)
                todos_arquivos.append(arquivo_info)
        
        # Organizar por extensão
        if arquivos_loja:
            extensoes = {}
            for arquivo in arquivos_loja:
                ext = arquivo['extensao']
                if ext not in extensoes:
                    extensoes[ext] = []
                extensoes[ext].append(arquivo)
            
            print(f"📁 Total de arquivos: {len(arquivos_loja)}")
            
            for ext in sorted(extensoes.keys()):
                arquivos_ext = extensoes[ext]
                print(f"\n📋 Arquivos {ext.upper() if ext else 'SEM EXTENSÃO'} ({len(arquivos_ext)}):")
                
                for arquivo in sorted(arquivos_ext, key=lambda x: x['tamanho_bytes'], reverse=True):
                    tamanho_str = f"{arquivo['tamanho_kb']:.1f} KB" if arquivo['tamanho_kb'] < 1024 else f"{arquivo['tamanho_kb']/1024:.1f} MB"
                    subpasta_str = f" ({arquivo['subpasta']})" if arquivo['subpasta'] != '.' else ""
                    print(f"   📄 {arquivo['arquivo']} - {tamanho_str}{subpasta_str}")
        else:
            print("📂 Nenhum arquivo encontrado")
    
    # Resumo geral
    print(f"\n📊 RESUMO GERAL")
    print("="*50)
    
    if todos_arquivos:
        # Por extensão
        extensoes_resumo = {}
        for arquivo in todos_arquivos:
            ext = arquivo['extensao']
            if ext not in extensoes_resumo:
                extensoes_resumo[ext] = []
            extensoes_resumo[ext].append(arquivo)
        
        print("📈 Arquivos por extensão:")
        for ext in sorted(extensoes_resumo.keys()):
            arquivos_ext = extensoes_resumo[ext]
            tamanho_total = sum(a['tamanho_kb'] for a in arquivos_ext)
            print(f"   🏷️ {ext.upper() if ext else 'SEM EXTENSÃO'}: {len(arquivos_ext)} arquivos ({tamanho_total:.1f} KB)")
        
        # Arquivos mais relevantes (Excel, CSV, etc.)
        print(f"\n🎯 ARQUIVOS POTENCIALMENTE RELEVANTES")
        print("-" * 40)
        
        relevantes = [a for a in todos_arquivos if a['extensao'] in ['.xlsx', '.xls', '.csv', '.txt']]
        
        if relevantes:
            # Ordenar por tamanho (maior primeiro)
            relevantes.sort(key=lambda x: x['tamanho_bytes'], reverse=True)
            
            for arquivo in relevantes:
                tamanho_str = f"{arquivo['tamanho_kb']:.1f} KB" if arquivo['tamanho_kb'] < 1024 else f"{arquivo['tamanho_kb']/1024:.1f} MB"
                print(f"   📄 {arquivo['loja']}/{arquivo['caminho_relativo']} - {tamanho_str}")
        else:
            print("   ❌ Nenhum arquivo Excel/CSV encontrado além do base.xlsx")
        
        # Verificar se há padrões interessantes
        print(f"\n🔍 PADRÕES IDENTIFICADOS")
        print("-" * 30)
        
        # Arquivos com nomes sugestivos
        nomes_interesse = ['cliente', 'vendas', 'receitas', 'historico', 'backup', 'detalhes', 'completo']
        encontrados = []
        
        for arquivo in todos_arquivos:
            nome_lower = arquivo['arquivo'].lower()
            for palavra in nomes_interesse:
                if palavra in nome_lower:
                    encontrados.append((arquivo, palavra))
        
        if encontrados:
            print("📋 Arquivos com nomes interessantes:")
            for arquivo, palavra in encontrados:
                print(f"   🎯 {arquivo['loja']}/{arquivo['arquivo']} (contém '{palavra}')")
        else:
            print("   ❌ Nenhum arquivo com nome sugestivo encontrado")
    
    else:
        print("❌ Nenhum arquivo encontrado em nenhuma loja")
    
    return todos_arquivos

if __name__ == "__main__":
    arquivos = explorar_arquivos_lojas()