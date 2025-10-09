#!/usr/bin/env python3
"""
Gerador Simplificado - Arquivo Consolidado Final
Usa apenas os arquivos que funcionaram na análise anterior
"""

import pandas as pd
from pathlib import Path
import re
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("🚀 GERADOR SIMPLIFICADO - ARQUIVO CONSOLIDADO FINAL")
    print("=" * 80)
    print("📋 Usando dados já processados da Base Master")
    print("🎯 Arquivo único com sequência e identificação de loja")
    print("=" * 80)
    
    # Carregar base master já processada
    data_dir = Path("data/processed")
    arquivo_base = None
    
    for arquivo in data_dir.glob("BASE_CLIENTES_MASTER_*.xlsx"):
        if not arquivo_base or arquivo.stat().st_mtime > arquivo_base.stat().st_mtime:
            arquivo_base = arquivo
    
    if not arquivo_base:
        print("❌ Base de Clientes Master não encontrada!")
        return
    
    print(f"📂 Carregando: {arquivo_base.name}")
    
    # Carregar dados
    df_clientes = pd.read_excel(arquivo_base, sheet_name='Base_Clientes_Master')
    
    print(f"✅ {len(df_clientes):,} clientes carregados")
    
    # Reorganizar colunas para arquivo final
    colunas_finais = [
        'ID_SEQUENCIAL',
        'LOJA',
        'ORIGEM_ARQUIVO',
        'NOME_COMPLETO',
        'CPF',
        'RG',
        'DATA_NASCIMENTO',
        'CELULAR',
        'EMAIL',
        'ENDERECO',
        'CEP',
        'BAIRRO',
        'TOTAL_REGISTROS_MESCLADOS',
        'DATA_EXTRACAO'
    ]
    
    # Preparar DataFrame final
    df_final = df_clientes.copy()
    
    # Renomear colunas para padrão final
    df_final = df_final.rename(columns={
        'nome_completo': 'NOME_COMPLETO',
        'cpf': 'CPF',
        'rg': 'RG',
        'data_nascimento': 'DATA_NASCIMENTO',
        'celular': 'CELULAR',
        'email': 'EMAIL',
        'endereco': 'ENDERECO',
        'cep': 'CEP',
        'bairro': 'BAIRRO',
        'origem_loja': 'LOJA',
        'origem_arquivo': 'ORIGEM_ARQUIVO',
        'total_registros_mesclados': 'TOTAL_REGISTROS_MESCLADOS',
        'data_extracao': 'DATA_EXTRACAO'
    })
    
    # Adicionar ID sequencial
    df_final['ID_SEQUENCIAL'] = range(1, len(df_final) + 1)
    
    # Tratar dados ausentes
    df_final['TOTAL_REGISTROS_MESCLADOS'] = df_final.get('TOTAL_REGISTROS_MESCLADOS', 1)
    df_final['DATA_EXTRACAO'] = df_final.get('DATA_EXTRACAO', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    
    # Selecionar apenas colunas que existem
    colunas_existentes = [col for col in colunas_finais if col in df_final.columns]
    df_final = df_final[colunas_existentes]
    
    # Estatísticas
    total_clientes = len(df_final)
    lojas = df_final['LOJA'].value_counts()
    
    print(f"\n📊 ESTATÍSTICAS:")
    print("=" * 50)
    print(f"👥 Total de clientes: {total_clientes:,}")
    print(f"🏪 Lojas identificadas: {len(lojas)}")
    
    for loja, count in lojas.items():
        print(f"   {loja}: {count:,} clientes ({count/total_clientes*100:.1f}%)")
    
    # Qualidade dos dados
    print(f"\n📊 QUALIDADE DOS DADOS:")
    print("=" * 50)
    print(f"🆔 CPF: {df_final['CPF'].notna().sum():,} ({df_final['CPF'].notna().sum()/total_clientes*100:.1f}%)")
    print(f"📱 Celular: {df_final['CELULAR'].notna().sum():,} ({df_final['CELULAR'].notna().sum()/total_clientes*100:.1f}%)")
    print(f"📧 Email: {df_final['EMAIL'].notna().sum():,} ({df_final['EMAIL'].notna().sum()/total_clientes*100:.1f}%)")
    print(f"🏠 Endereço: {df_final['ENDERECO'].notna().sum():,} ({df_final['ENDERECO'].notna().sum()/total_clientes*100:.1f}%)")
    
    # Salvar arquivos
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # CSV
    csv_file = data_dir / f"CLIENTES_CONSOLIDADO_FINAL_{timestamp}.csv"
    df_final.to_csv(csv_file, index=False, encoding='utf-8-sig')
    
    # Excel com múltiplas abas
    excel_file = data_dir / f"CLIENTES_CONSOLIDADO_FINAL_{timestamp}.xlsx"
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Aba principal
        df_final.to_excel(writer, sheet_name='Clientes_Consolidados', index=False)
        
        # Aba por loja
        for loja in sorted(df_final['LOJA'].unique()):
            if pd.notna(loja):
                df_loja = df_final[df_final['LOJA'] == loja]
                sheet_name = f"Loja_{loja}"[:31]
                df_loja.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Estatísticas
        stats_data = []
        for loja in sorted(df_final['LOJA'].unique()):
            if pd.notna(loja):
                df_loja = df_final[df_final['LOJA'] == loja]
                stats_data.append({
                    'LOJA': loja,
                    'TOTAL_CLIENTES': len(df_loja),
                    'COM_CPF': df_loja['CPF'].notna().sum(),
                    'COM_CELULAR': df_loja['CELULAR'].notna().sum(),
                    'COM_EMAIL': df_loja['EMAIL'].notna().sum(),
                    'COM_ENDERECO': df_loja['ENDERECO'].notna().sum(),
                    'PCT_CPF': (df_loja['CPF'].notna().sum() / len(df_loja) * 100),
                    'PCT_CELULAR': (df_loja['CELULAR'].notna().sum() / len(df_loja) * 100),
                    'PCT_EMAIL': (df_loja['EMAIL'].notna().sum() / len(df_loja) * 100),
                    'PCT_ENDERECO': (df_loja['ENDERECO'].notna().sum() / len(df_loja) * 100)
                })
        
        df_stats = pd.DataFrame(stats_data)
        df_stats.to_excel(writer, sheet_name='Estatisticas_Por_Loja', index=False)
    
    print(f"\n📁 ARQUIVOS GERADOS:")
    print("=" * 80)
    print(f"📄 CSV: {csv_file}")
    print(f"📊 Excel: {excel_file}")
    
    print(f"\n✅ ESTRUTURA DO ARQUIVO:")
    print("=" * 80)
    print("🔢 ID_SEQUENCIAL - Numeração única sequencial")
    print("🏪 LOJA - Identificação da loja de origem")
    print("📁 ORIGEM_ARQUIVO - Arquivo de origem dos dados")
    print("👤 NOME_COMPLETO - Nome completo do cliente")
    print("🆔 CPF - CPF formatado (xxx.xxx.xxx-xx)")
    print("🆔 RG - Registro Geral")
    print("📅 DATA_NASCIMENTO - Data de nascimento (dd/mm/aaaa)")
    print("📱 CELULAR - Celular formatado SP (11) 9xxxx-xxxx")
    print("📧 EMAIL - Email do cliente")
    print("🏠 ENDERECO - Endereço completo")
    print("📮 CEP - Código postal")
    print("🏘️ BAIRRO - Bairro de residência")
    print("🔢 TOTAL_REGISTROS_MESCLADOS - Quantos registros foram consolidados")
    print("⏰ DATA_EXTRACAO - Data/hora do processamento")
    
    print(f"\n🎯 PRONTO PARA USO:")
    print("=" * 80)
    print("✅ Arquivo único com todos os clientes")
    print("✅ Dados normalizados e limpos")
    print("✅ Identificação clara da loja")
    print("✅ Formato Excel + CSV para máxima compatibilidade")
    print("✅ Abas separadas por loja para análise específica")
    
    return csv_file, excel_file

if __name__ == "__main__":
    main()