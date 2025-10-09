#!/usr/bin/env python3
"""
Script para localizar e processar todos os arquivos OS_NOVA*.xlsm
"""

import os
import shutil
from pathlib import Path
import pandas as pd

def localizar_arquivos_os_nova():
    """Localiza todos os arquivos OS_NOVA*.xlsm na pasta Lojas"""
    
    print("🔍 LOCALIZANDO ARQUIVOS OS_NOVA")
    print("=" * 60)
    
    # Possíveis localizações da pasta Lojas
    possiveis_pastas = [
        Path("D:/Lojas"),
        Path("D:/projetos/Lojas"), 
        Path("D:/projetos/carne_facil/Lojas"),
        Path("../Lojas"),
        Path("./Lojas"),
        Path("C:/Lojas"),
        Path("C:/Users/junio/Desktop/Lojas"),
        Path("C:/Users/junio/Documents/Lojas")
    ]
    
    arquivos_encontrados = []
    pasta_encontrada = None
    
    print("📁 Procurando pasta 'Lojas' em:")
    for pasta in possiveis_pastas:
        print(f"   • {pasta}")
        if pasta.exists():
            print(f"   ✅ Pasta encontrada: {pasta}")
            pasta_encontrada = pasta
            break
    
    if not pasta_encontrada:
        print("\n❌ Pasta 'Lojas' não encontrada nos locais verificados.")
        print("\n💡 Por favor, informe o caminho correto da pasta 'Lojas'")
        return []
    
    print(f"\n🔍 Procurando arquivos OS_NOVA*.xlsm em: {pasta_encontrada}")
    
    # Buscar recursivamente por arquivos OS_NOVA*.xlsm
    for root, dirs, files in os.walk(pasta_encontrada):
        for file in files:
            if file.startswith("OS_NOVA") and file.endswith(".xlsm"):
                caminho_completo = Path(root) / file
                arquivos_encontrados.append(caminho_completo)
                print(f"   ✅ {file} ({caminho_completo.parent.name})")
    
    print(f"\n📊 RESUMO:")
    print(f"   • Arquivos OS_NOVA*.xlsm encontrados: {len(arquivos_encontrados)}")
    
    if arquivos_encontrados:
        print(f"\n📋 LISTA COMPLETA:")
        for i, arquivo in enumerate(arquivos_encontrados, 1):
            tamanho_mb = arquivo.stat().st_size / (1024 * 1024)
            print(f"   {i:2d}. {arquivo.name}")
            print(f"       📁 {arquivo.parent}")
            print(f"       📏 {tamanho_mb:.1f} MB")
    
    return arquivos_encontrados

def copiar_arquivos_para_processamento(arquivos):
    """Copia arquivos encontrados para pasta de processamento"""
    
    if not arquivos:
        print("❌ Nenhum arquivo para copiar")
        return
    
    print(f"\n📋 COPIANDO ARQUIVOS PARA PROCESSAMENTO")
    print("=" * 60)
    
    destino = Path("data/raw")
    destino.mkdir(parents=True, exist_ok=True)
    
    arquivos_copiados = []
    
    for arquivo in arquivos:
        try:
            # Nome do arquivo de destino
            nome_destino = arquivo.name
            
            # Se já existe, adicionar número
            contador = 1
            while (destino / nome_destino).exists():
                base, ext = arquivo.stem, arquivo.suffix
                nome_destino = f"{base}_{contador}{ext}"
                contador += 1
            
            caminho_destino = destino / nome_destino
            
            # Copiar arquivo
            shutil.copy2(arquivo, caminho_destino)
            arquivos_copiados.append(caminho_destino)
            
            print(f"   ✅ {arquivo.name} → {nome_destino}")
            
        except Exception as e:
            print(f"   ❌ Erro ao copiar {arquivo.name}: {e}")
    
    print(f"\n📊 {len(arquivos_copiados)} arquivos copiados para data/raw/")
    return arquivos_copiados

def analisar_estrutura_arquivos(arquivos):
    """Analisa a estrutura dos arquivos OS_NOVA"""
    
    print(f"\n🔬 ANALISANDO ESTRUTURA DOS ARQUIVOS")
    print("=" * 60)
    
    for arquivo in arquivos:
        print(f"\n📁 {arquivo.name}")
        print("-" * 40)
        
        try:
            # Tentar ler o arquivo
            df = pd.read_excel(arquivo, engine='openpyxl')
            
            print(f"   📊 {len(df)} linhas, {len(df.columns)} colunas")
            print(f"   🏷️ Colunas: {list(df.columns)}")
            
            # Verificar colunas de OS
            colunas_os = [col for col in df.columns if 'OS' in str(col).upper()]
            if colunas_os:
                print(f"   📈 Colunas de OS: {colunas_os}")
                
                for col in colunas_os:
                    valores_validos = pd.to_numeric(df[col], errors='coerce').dropna()
                    if len(valores_validos) > 0:
                        print(f"      • {col}: {len(valores_validos)} OS válidas ({valores_validos.min():.0f}-{valores_validos.max():.0f})")
            
            # Verificar colunas de clientes
            colunas_cliente = [col for col in df.columns if any(termo in col.lower() for termo in ['nome', 'cliente', 'paciente'])]
            if colunas_cliente:
                print(f"   👥 Colunas de cliente: {colunas_cliente}")
                
                for col in colunas_cliente:
                    clientes_unicos = df[col].nunique()
                    total_nomes = len(df[col].dropna())
                    print(f"      • {col}: {total_nomes} nomes, {clientes_unicos} únicos")
            
            # Amostra dos dados
            print(f"   🔍 Primeiras 3 linhas:")
            print(df.head(3).to_string().replace('\n', '\n      '))
            
        except Exception as e:
            print(f"   ❌ Erro ao analisar: {e}")

def main():
    """Função principal"""
    
    print("🚀 PROCESSAMENTO COMPLETO DE ARQUIVOS OS_NOVA")
    print("=" * 80)
    
    # 1. Localizar arquivos
    arquivos = localizar_arquivos_os_nova()
    
    if not arquivos:
        print("\n💡 AJUDA:")
        print("   1. Verifique se a pasta 'Lojas' existe")
        print("   2. Verifique se há arquivos que começam com 'OS_NOVA' e terminam com '.xlsm'")
        print("   3. Informe o caminho correto da pasta se necessário")
        return
    
    # 2. Copiar para processamento
    arquivos_copiados = copiar_arquivos_para_processamento(arquivos)
    
    # 3. Analisar estrutura
    if arquivos_copiados:
        analisar_estrutura_arquivos(arquivos_copiados)
    
    print(f"\n🎉 PROCESSAMENTO CONCLUÍDO!")
    print(f"   • {len(arquivos)} arquivos encontrados")
    print(f"   • {len(arquivos_copiados)} arquivos copiados")
    print(f"   • Prontos para análise completa do sistema")

if __name__ == "__main__":
    main()