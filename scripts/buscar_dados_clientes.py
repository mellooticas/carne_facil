#!/usr/bin/env python3
"""
Busca ampla por dados de clientes e OSs no OneDrive das óticas
"""

import os
import shutil
from pathlib import Path
import pandas as pd

def buscar_dados_clientes():
    """Busca ampla por dados de clientes e OSs"""
    
    print("🔍 BUSCA AMPLA POR DADOS DE CLIENTES E OSs")
    print("="*70)
    
    # Pasta das Óticas Taty Mello
    oticas_path = Path(r"C:\Users\junio\OneDrive - Óticas Taty Mello")
    
    if not oticas_path.exists():
        print("❌ Pasta das Óticas Taty Mello não encontrada!")
        return []
    
    # Buscar em pastas específicas que podem conter dados
    pastas_interesse = [
        "LOJAS",
        "VENDAS",
        "FINANCEIRO", 
        "ESTOQUE",
        "TELEMARKETING"
    ]
    
    arquivos_encontrados = []
    
    for pasta_nome in pastas_interesse:
        pasta_path = oticas_path / pasta_nome
        
        if not pasta_path.exists():
            print(f"❌ Pasta {pasta_nome} não encontrada")
            continue
        
        print(f"\n📁 EXPLORANDO: {pasta_nome}")
        print("-" * 50)
        
        arquivos_pasta = []
        
        try:
            # Buscar recursivamente por arquivos Excel/CSV
            for root, dirs, files in os.walk(pasta_path):
                root_path = Path(root)
                
                # Limitar profundidade para evitar timeout
                nivel = len(root_path.relative_to(pasta_path).parts)
                if nivel > 4:  # Máximo 4 níveis de profundidade
                    continue
                
                for file in files:
                    file_path = root_path / file
                    
                    # Interessar por arquivos de dados
                    extensao = file_path.suffix.lower()
                    if extensao in ['.xlsx', '.xls', '.csv']:
                        
                        try:
                            tamanho = file_path.stat().st_size
                            
                            # Filtrar arquivos muito pequenos (provavelmente vazios)
                            if tamanho < 1024:  # Menos de 1KB
                                continue
                            
                            arquivo_info = {
                                'pasta_principal': pasta_nome,
                                'arquivo': file,
                                'caminho_completo': str(file_path),
                                'pasta_pai': root_path.name,
                                'caminho_relativo': str(file_path.relative_to(oticas_path)),
                                'extensao': extensao,
                                'tamanho_bytes': tamanho,
                                'tamanho_kb': tamanho / 1024,
                                'nivel': nivel
                            }
                            
                            arquivos_pasta.append(arquivo_info)
                            arquivos_encontrados.append(arquivo_info)
                            
                        except Exception as e:
                            continue
        
        except Exception as e:
            print(f"   ❌ Erro ao explorar {pasta_nome}: {e}")
            continue
        
        # Mostrar arquivos encontrados nesta pasta
        if arquivos_pasta:
            print(f"   📊 Arquivos Excel/CSV encontrados: {len(arquivos_pasta)}")
            
            # Ordenar por tamanho
            arquivos_pasta.sort(key=lambda x: x['tamanho_bytes'], reverse=True)
            
            # Mostrar os maiores arquivos
            for arquivo in arquivos_pasta[:5]:  # Top 5
                tamanho_str = f"{arquivo['tamanho_kb']:.1f} KB" if arquivo['tamanho_kb'] < 1024 else f"{arquivo['tamanho_kb']/1024:.1f} MB"
                print(f"      📄 {arquivo['caminho_relativo']} ({tamanho_str})")
        else:
            print(f"   📂 Nenhum arquivo Excel/CSV encontrado")
    
    # Busca específica por nomes que sugerem dados de clientes
    print(f"\n🎯 BUSCA POR PALAVRAS-CHAVE")
    print("-" * 40)
    
    palavras_chave = ['cliente', 'os', 'ordem', 'servico', 'receita', 'base', 'dados', 'planilha']
    arquivos_relevantes = []
    
    for arquivo in arquivos_encontrados:
        nome_lower = arquivo['arquivo'].lower()
        caminho_lower = arquivo['caminho_relativo'].lower()
        
        for palavra in palavras_chave:
            if palavra in nome_lower or palavra in caminho_lower:
                if arquivo not in arquivos_relevantes:
                    arquivos_relevantes.append(arquivo)
                break
    
    if arquivos_relevantes:
        print(f"📊 Arquivos com palavras-chave: {len(arquivos_relevantes)}")
        
        # Ordenar por tamanho
        arquivos_relevantes.sort(key=lambda x: x['tamanho_bytes'], reverse=True)
        
        for arquivo in arquivos_relevantes:
            tamanho_str = f"{arquivo['tamanho_kb']:.1f} KB" if arquivo['tamanho_kb'] < 1024 else f"{arquivo['tamanho_kb']/1024:.1f} MB"
            print(f"   📄 {arquivo['caminho_relativo']} ({tamanho_str})")
    else:
        print("❌ Nenhum arquivo com palavras-chave encontrado")
    
    # Resumo geral
    print(f"\n📊 RESUMO GERAL")
    print("="*50)
    
    if arquivos_encontrados:
        print(f"📈 Total de arquivos Excel/CSV: {len(arquivos_encontrados)}")
        
        # Por pasta principal
        por_pasta = {}
        for arquivo in arquivos_encontrados:
            pasta = arquivo['pasta_principal']
            if pasta not in por_pasta:
                por_pasta[pasta] = []
            por_pasta[pasta].append(arquivo)
        
        print("\n📊 Por pasta principal:")
        for pasta in sorted(por_pasta.keys()):
            arquivos_pasta = por_pasta[pasta]
            tamanho_total = sum(a['tamanho_kb'] for a in arquivos_pasta) / 1024  # MB
            print(f"   📁 {pasta}: {len(arquivos_pasta)} arquivos ({tamanho_total:.1f} MB)")
        
        # Maiores arquivos
        arquivos_ordenados = sorted(arquivos_encontrados, key=lambda x: x['tamanho_bytes'], reverse=True)
        
        print(f"\n🏆 TOP 10 MAIORES ARQUIVOS:")
        print("-" * 40)
        
        for i, arquivo in enumerate(arquivos_ordenados[:10], 1):
            tamanho_str = f"{arquivo['tamanho_kb']:.1f} KB" if arquivo['tamanho_kb'] < 1024 else f"{arquivo['tamanho_kb']/1024:.1f} MB"
            print(f"   {i:2d}. {arquivo['arquivo']} ({tamanho_str})")
            print(f"       📁 {arquivo['caminho_relativo']}")
    
    else:
        print("❌ Nenhum arquivo Excel/CSV encontrado")
    
    return arquivos_encontrados

def analisar_arquivos_promissores(arquivos_encontrados):
    """Analisa os arquivos mais promissores"""
    
    if not arquivos_encontrados:
        return
    
    print(f"\n🔬 ANÁLISE DE ARQUIVOS PROMISSORES")
    print("="*60)
    
    # Selecionar arquivos mais promissores (maiores e com nomes sugestivos)
    promissores = []
    
    for arquivo in arquivos_encontrados:
        is_promissor = False
        razao = []
        
        # Critério 1: Tamanho > 10KB
        if arquivo['tamanho_kb'] > 10:
            is_promissor = True
            razao.append("grande")
        
        # Critério 2: Nome sugestivo
        nome_lower = arquivo['arquivo'].lower()
        palavras_importantes = ['cliente', 'os', 'base', 'dados', 'planilha', 'receita']
        for palavra in palavras_importantes:
            if palavra in nome_lower:
                is_promissor = True
                razao.append(f"'{palavra}'")
                break
        
        # Critério 3: Pasta sugestiva
        caminho_lower = arquivo['caminho_relativo'].lower()
        pastas_importantes = ['cliente', 'vendas', 'telemarketing', 'financeiro']
        for pasta in pastas_importantes:
            if pasta in caminho_lower:
                is_promissor = True
                razao.append(f"pasta '{pasta}'")
                break
        
        if is_promissor:
            arquivo['razao'] = ', '.join(razao)
            promissores.append(arquivo)
    
    if not promissores:
        print("❌ Nenhum arquivo promissor identificado")
        return
    
    # Ordenar por tamanho
    promissores.sort(key=lambda x: x['tamanho_bytes'], reverse=True)
    
    print(f"📊 Arquivos promissores encontrados: {len(promissores)}")
    print()
    
    # Analisar cada arquivo promissor
    destino = Path("data/arquivos_promissores")
    destino.mkdir(exist_ok=True)
    
    for i, arquivo in enumerate(promissores[:5], 1):  # Top 5
        print(f"📄 {i}. {arquivo['arquivo']}")
        print(f"   📁 {arquivo['caminho_relativo']}")
        
        tamanho_str = f"{arquivo['tamanho_kb']:.1f} KB" if arquivo['tamanho_kb'] < 1024 else f"{arquivo['tamanho_kb']/1024:.1f} MB"
        print(f"   📊 Tamanho: {tamanho_str}")
        print(f"   🎯 Razão: {arquivo['razao']}")
        
        # Tentar copiar e analisar
        try:
            nome_destino = f"promissor_{i}_{arquivo['arquivo']}"
            caminho_destino = destino / nome_destino
            
            shutil.copy2(arquivo['caminho_completo'], caminho_destino)
            print(f"   ✅ Copiado para: {nome_destino}")
            
            # Tentar ler preview
            try:
                if arquivo['extensao'] in ['.xlsx', '.xls']:
                    df = pd.read_excel(caminho_destino, nrows=5)
                else:  # CSV
                    df = pd.read_csv(caminho_destino, nrows=5)
                
                print(f"   📋 Colunas ({len(df.columns)}): {', '.join(df.columns[:10])}{'...' if len(df.columns) > 10 else ''}")
                print(f"   📈 Preview (primeiras linhas):")
                print(f"       {df.head(2).to_string().replace(chr(10), chr(10) + '       ')}")
                
            except Exception as e:
                print(f"   ⚠️ Erro ao ler preview: {e}")
        
        except Exception as e:
            print(f"   ❌ Erro ao copiar: {e}")
        
        print()
    
    print(f"🎉 Análise concluída! Arquivos salvos em: {destino}")

if __name__ == "__main__":
    arquivos = buscar_dados_clientes()
    if arquivos:
        analisar_arquivos_promissores(arquivos)