"""
Script para copiar arquivos OS_NOVA das lojas para o projeto
"""

import shutil
from pathlib import Path
import os
from loguru import logger

def copiar_arquivos_os():
    # Diretórios
    fonte_base = Path(r"D:\OneDrive - Óticas Taty Mello\LOJAS")
    destino = Path("data/raw")
    
    # Criar diretório de destino se não existir
    destino.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Procurando arquivos em: {fonte_base}")
    logger.info(f"Destino: {destino.absolute()}")
    
    arquivos_copiados = []
    erros = []
    
    # Verificar se diretório fonte existe
    if not fonte_base.exists():
        logger.error(f"Diretório fonte não encontrado: {fonte_base}")
        return [], [f"Diretório não encontrado: {fonte_base}"]
    
    # Procurar em todas as subpastas de lojas
    for loja_dir in fonte_base.iterdir():
        if loja_dir.is_dir():
            os_dir = loja_dir / "OSs"
            
            if os_dir.exists():
                logger.info(f"Verificando loja: {loja_dir.name}")
                
                # Procurar arquivos OS_NOVA
                for arquivo in os_dir.glob("OS_NOVA*.xlsx"):
                    try:
                        # Nome do arquivo de destino com prefixo da loja
                        nome_destino = f"{loja_dir.name}_{arquivo.name}"
                        arquivo_destino = destino / nome_destino
                        
                        # Copiar arquivo
                        shutil.copy2(arquivo, arquivo_destino)
                        arquivos_copiados.append({
                            'origem': str(arquivo),
                            'destino': str(arquivo_destino),
                            'loja': loja_dir.name,
                            'tamanho': arquivo.stat().st_size
                        })
                        
                        logger.success(f"Copiado: {arquivo.name} -> {nome_destino}")
                        
                    except Exception as e:
                        erro = f"Erro ao copiar {arquivo}: {e}"
                        erros.append(erro)
                        logger.error(erro)
            else:
                logger.warning(f"Pasta OSs não encontrada em: {loja_dir.name}")
    
    # Relatório final
    logger.info(f"\n{'='*50}")
    logger.info(f"RELATÓRIO DE CÓPIA")
    logger.info(f"{'='*50}")
    logger.info(f"Arquivos copiados: {len(arquivos_copiados)}")
    logger.info(f"Erros: {len(erros)}")
    
    if arquivos_copiados:
        logger.info(f"\nArquivos copiados:")
        for arquivo in arquivos_copiados:
            tamanho_mb = arquivo['tamanho'] / (1024*1024)
            logger.info(f"  📁 {arquivo['loja']}: {Path(arquivo['destino']).name} ({tamanho_mb:.1f} MB)")
    
    if erros:
        logger.error(f"\nErros encontrados:")
        for erro in erros:
            logger.error(f"  ❌ {erro}")
    
    return arquivos_copiados, erros

if __name__ == "__main__":
    # Configurar logging
    logger.remove()
    logger.add(
        "logs/copia_arquivos.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="INFO"
    )
    logger.add(
        lambda msg: print(msg),
        format="{time:HH:mm:ss} | {level: <8} | {message}",
        level="INFO",
        colorize=True
    )
    
    logger.info("Iniciando cópia de arquivos OS_NOVA...")
    
    try:
        arquivos, erros = copiar_arquivos_os()
        
        if arquivos:
            logger.success(f"✅ Cópia concluída! {len(arquivos)} arquivos copiados.")
        else:
            logger.warning("⚠️ Nenhum arquivo foi copiado.")
            
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")