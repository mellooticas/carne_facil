#!/usr/bin/env python3
"""
Script para buscar arquivos OS_NOVA*.xlsm no OneDrive das Óticas Taty Mello
"""

import os
import shutil
from pathlib import Path
import pandas as pd

def buscar_arquivos_os_nova_onedrive():
    """Busca arquivos OS_NOVA*.xlsm no OneDrive das Óticas"""
    
    print("🔍 BUSCANDO ARQUIVOS OS_NOVA NO ONEDRIVE")
    print("=" * 60)
    
    # Caminho específico fornecido
    pasta_lojas = Path(r"D:\OneDrive - Óticas Taty Mello\LOJAS")
    
    print(f"📁 Verificando pasta: {pasta_lojas}")
    
    if not pasta_lojas.exists():
        print("❌ Pasta não encontrada!")
        print(f"   Caminho: {pasta_lojas}")
        
        # Tentar variações do caminho
        alternativas = [
            Path(r"D:\OneDrive - Óticas Taty Mello\LOJAS"),
            Path(r"D:\OneDrive - Oticas Taty Mello\LOJAS"),
            Path(r"D:\OneDrive\Óticas Taty Mello\LOJAS"),
            Path(r"D:\OneDrive\LOJAS"),
            Path(r"C:\Users\junio\OneDrive - Óticas Taty Mello\LOJAS")
        ]
        
        print(f"\n🔍 Testando caminhos alternativos:")
        for alt in alternativas:
            print(f"   • {alt}")
            if alt.exists():
                print(f"   ✅ Encontrado!")
                pasta_lojas = alt
                break
        else:
            return []
    
    print(f"✅ Pasta encontrada: {pasta_lojas}")
    
    # Buscar recursivamente por arquivos OS_NOVA*.xlsm
    arquivos_encontrados = []
    
    print(f"\n🔍 Buscando arquivos OS_NOVA*.xlsm...")
    
    try:
        for root, dirs, files in os.walk(pasta_lojas):
            nivel = str(root).count(os.sep) - str(pasta_lojas).count(os.sep)
            print(f"   📁 Pasta (nível {nivel}): {Path(root).name}")
            
            for file in files:
                print(f"      📄 {file}")
                
                if file.startswith("OS_NOVA") and file.endswith(".xlsm"):
                    caminho_completo = Path(root) / file
                    arquivos_encontrados.append(caminho_completo)
                    print(f"      ✅ ENCONTRADO: {file}")
                
                # Também verificar outros padrões similares
                elif any(pattern in file.upper() for pattern in ["OS_NOVA", "OS NOVA"]) and file.endswith((".xlsm", ".xlsx")):
                    caminho_completo = Path(root) / file
                    arquivos_encontrados.append(caminho_completo)
                    print(f"      ✅ SIMILAR: {file}")
                    
    except Exception as e:
        print(f"❌ Erro ao buscar arquivos: {e}")
        return []
    
    print(f"\n📊 RESULTADO:")
    print(f"   • Arquivos encontrados: {len(arquivos_encontrados)}")
    
    if arquivos_encontrados:
        print(f"\n📋 LISTA DE ARQUIVOS:")
        for i, arquivo in enumerate(arquivos_encontrados, 1):
            try:
                tamanho_mb = arquivo.stat().st_size / (1024 * 1024)
                print(f"   {i:2d}. {arquivo.name}")
                print(f"       📁 {arquivo.parent}")
                print(f"       📏 {tamanho_mb:.1f} MB")
            except Exception as e:
                print(f"   {i:2d}. {arquivo.name}")
                print(f"       📁 {arquivo.parent}")
                print(f"       ⚠️ Erro ao obter tamanho: {e}")
    
    return arquivos_encontrados

def copiar_arquivos_para_processamento(arquivos):
    """Copia arquivos encontrados para pasta de processamento"""
    
    if not arquivos:
        print("❌ Nenhum arquivo para copiar")
        return []
    
    print(f"\n📋 COPIANDO ARQUIVOS PARA PROCESSAMENTO")
    print("=" * 60)
    
    destino = Path("data/raw")
    destino.mkdir(parents=True, exist_ok=True)
    
    arquivos_copiados = []
    
    for arquivo in arquivos:
        try:
            # Nome do arquivo de destino (remover caracteres especiais se necessário)
            nome_original = arquivo.name
            nome_destino = nome_original
            
            # Se já existe, adicionar número
            contador = 1
            while (destino / nome_destino).exists():
                base, ext = arquivo.stem, arquivo.suffix
                nome_destino = f"{base}_{contador}{ext}"
                contador += 1
            
            caminho_destino = destino / nome_destino
            
            # Copiar arquivo
            print(f"   📋 Copiando: {nome_original}")
            shutil.copy2(arquivo, caminho_destino)
            arquivos_copiados.append(caminho_destino)
            
            tamanho_mb = caminho_destino.stat().st_size / (1024 * 1024)
            print(f"   ✅ {nome_original} → {nome_destino} ({tamanho_mb:.1f} MB)")
            
        except Exception as e:
            print(f"   ❌ Erro ao copiar {arquivo.name}: {e}")
    
    print(f"\n📊 {len(arquivos_copiados)} arquivos copiados para data/raw/")
    return arquivos_copiados

def analisar_arquivos_basico(arquivos):
    """Análise básica dos arquivos encontrados"""
    
    print(f"\n🔬 ANÁLISE BÁSICA DOS ARQUIVOS")
    print("=" * 60)
    
    total_os = 0
    total_clientes = 0
    
    for arquivo in arquivos:
        print(f"\n📁 {arquivo.name}")
        print("-" * 40)
        
        try:
            # Verificar se é XLSM (macro-enabled)
            engine = 'openpyxl' if arquivo.suffix.lower() in ['.xlsx', '.xlsm'] else None
            
            # Tentar diferentes sheets
            excel_file = pd.ExcelFile(arquivo, engine=engine)
            sheets = excel_file.sheet_names
            print(f"   📄 Sheets disponíveis: {sheets}")
            
            # Tentar carregar o primeiro sheet ou o mais provável
            sheet_principal = None
            for sheet_name in ['base_clientes_OS', 'dados', 'Clientes', 'OS', sheets[0] if sheets else None]:
                if sheet_name in sheets:
                    sheet_principal = sheet_name
                    break
            
            if not sheet_principal:
                sheet_principal = sheets[0] if sheets else None
            
            if sheet_principal:
                df = pd.read_excel(arquivo, sheet_name=sheet_principal, engine=engine)
                print(f"   📊 Sheet '{sheet_principal}': {len(df)} linhas, {len(df.columns)} colunas")
                print(f"   🏷️ Colunas: {list(df.columns)}")
                
                # Contar OS
                os_arquivo = 0
                colunas_os = [col for col in df.columns if 'OS' in str(col).upper()]
                for col in colunas_os:
                    valores_os = pd.to_numeric(df[col], errors='coerce').dropna()
                    os_arquivo += len(valores_os)
                    if len(valores_os) > 0:
                        print(f"      📈 {col}: {len(valores_os)} OS ({valores_os.min():.0f}-{valores_os.max():.0f})")
                
                # Contar clientes
                colunas_cliente = [col for col in df.columns if any(termo in col.lower() for termo in ['nome', 'cliente', 'paciente'])]
                clientes_arquivo = 0
                for col in colunas_cliente:
                    clientes_unicos = df[col].nunique()
                    clientes_arquivo += clientes_unicos
                    print(f"      👥 {col}: {clientes_unicos} únicos")
                
                total_os += os_arquivo
                total_clientes += clientes_arquivo
                
                print(f"   📊 Total neste arquivo: {os_arquivo} OS, {clientes_arquivo} clientes")
            
        except Exception as e:
            print(f"   ❌ Erro ao analisar: {e}")
    
    print(f"\n🎯 RESUMO GERAL:")
    print(f"   📊 Total de OS: {total_os:,}")
    print(f"   👥 Total de clientes: {total_clientes:,}")
    print(f"   📁 Arquivos processados: {len(arquivos)}")

def main():
    """Função principal"""
    
    print("🚀 BUSCA E PROCESSAMENTO DE ARQUIVOS OS_NOVA")
    print("=" * 80)
    
    # 1. Buscar arquivos no OneDrive
    arquivos_encontrados = buscar_arquivos_os_nova_onedrive()
    
    if not arquivos_encontrados:
        print("\n💡 NENHUM ARQUIVO ENCONTRADO")
        print("   1. Verifique se o caminho está correto")
        print("   2. Verifique se há arquivos OS_NOVA*.xlsm na pasta")
        print("   3. Verifique as permissões de acesso")
        return
    
    # 2. Copiar arquivos para processamento
    arquivos_copiados = copiar_arquivos_para_processamento(arquivos_encontrados)
    
    # 3. Análise básica
    if arquivos_copiados:
        analisar_arquivos_basico(arquivos_copiados)
    
    print(f"\n🎉 PROCESSAMENTO CONCLUÍDO!")
    print(f"   ✅ {len(arquivos_encontrados)} arquivos encontrados")
    print(f"   ✅ {len(arquivos_copiados)} arquivos copiados")
    print(f"   🚀 Prontos para análise completa do sistema")

if __name__ == "__main__":
    main()