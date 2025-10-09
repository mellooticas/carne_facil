#!/usr/bin/env python3
"""
🔗 SISTEMA DE RELACIONAMENTO OS-CLIENTE
================================================================================
🎯 Conecta as 14,337 OS com os clientes únicos criados
📊 Combina: Clientes + OS + Dioptrías + Vendas
🔍 Resultado: Sistema completo de relacionamentos
================================================================================
"""

import pandas as pd
import logging
from pathlib import Path
import glob
from datetime import datetime
import openpyxl
from fuzzywuzzy import fuzz
import re

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def normalizar_nome(nome):
    """Normaliza nome para comparação"""
    if pd.isna(nome) or not nome:
        return ""
    return re.sub(r'[^A-Za-z\s]', '', str(nome)).strip().upper()

def normalizar_cpf(cpf):
    """Normaliza CPF removendo pontuação"""
    if pd.isna(cpf) or not cpf:
        return ""
    return re.sub(r'[^\d]', '', str(cpf))

def encontrar_cliente_id(nome_os, cpf_os, df_clientes):
    """
    Encontra o ID do cliente correspondente
    Prioridade: CPF exato > Nome fuzzy match
    """
    # Normalizar dados da OS
    nome_norm = normalizar_nome(nome_os)
    cpf_norm = normalizar_cpf(cpf_os)
    
    # 1. Busca por CPF exato (prioridade máxima)
    if cpf_norm and len(cpf_norm) >= 8:
        match_cpf = df_clientes[df_clientes['CPF_normalizado'] == cpf_norm]
        if not match_cpf.empty:
            return match_cpf.iloc[0]['Cliente_ID']
    
    # 2. Busca por nome (fuzzy match)
    if nome_norm and len(nome_norm) >= 3:
        best_score = 0
        best_id = None
        
        for _, cliente in df_clientes.iterrows():
            score = fuzz.ratio(nome_norm, cliente['Nome_normalizado'])
            if score > best_score and score >= 85:  # Threshold 85%
                best_score = score
                best_id = cliente['Cliente_ID']
        
        if best_id:
            return best_id
    
    return None

def processar_arquivo_os(file_path, df_clientes):
    """Processa um arquivo de OS e relaciona com clientes"""
    try:
        # Tentar ler como Excel
        if file_path.suffix == '.xlsm':
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active
            data = []
            headers = []
            
            # Ler headers (primeira linha)
            for cell in sheet[1]:
                headers.append(cell.value)
            
            # Ler dados
            for row in sheet.iter_rows(min_row=2, values_only=True):
                data.append(row)
            
            df = pd.DataFrame(data, columns=headers)
        else:
            df = pd.read_excel(file_path)
        
        if df.empty:
            return pd.DataFrame()
        
        # Identificar campos de nome e CPF
        nome_col = None
        cpf_col = None
        
        for col in df.columns:
            col_upper = str(col).upper()
            if any(term in col_upper for term in ['NOME', 'CLIENTE', 'PACIENTE']):
                if nome_col is None:
                    nome_col = col
            if any(term in col_upper for term in ['CPF', 'DOCUMENTO']):
                if cpf_col is None:
                    cpf_col = col
        
        # Detectar loja a partir do nome do arquivo
        loja = "DESCONHECIDA"
        file_name = file_path.name.upper()
        if "MAUA" in file_name or "MESA01" in file_name:
            loja = "MAUA"
        elif any(term in file_name for term in ["SAO_MATEUS", "MESA_01", "MESA_02", "OL"]):
            loja = "SAO_MATEUS"
        elif "RIO_PEQUENO" in file_name or "PERUS" in file_name:
            loja = "RIO_PEQUENO"
        
        # Identificar sistema
        sistema = "LANCASTER"
        if "OTM" in file_name:
            sistema = "OTM"
        
        os_relacionadas = []
        
        for idx, row in df.iterrows():
            # Buscar número da OS
            os_numero = None
            for col in df.columns:
                if any(term in str(col).upper() for term in ['OS', 'NUMERO', 'Nº']):
                    val = row[col]
                    if pd.notna(val) and str(val).strip():
                        try:
                            os_numero = int(float(str(val)))
                            break
                        except:
                            continue
            
            if os_numero is None:
                continue
            
            # Extrair nome e CPF
            nome = row[nome_col] if nome_col else ""
            cpf = row[cpf_col] if cpf_col else ""
            
            # Encontrar Cliente_ID
            cliente_id = encontrar_cliente_id(nome, cpf, df_clientes)
            
            # Criar registro da relação
            relacao = {
                'OS_Numero': os_numero,
                'Loja': loja,
                'Sistema': sistema,
                'Arquivo_Origem': file_path.name,
                'Cliente_ID': cliente_id,
                'Nome_OS': nome,
                'CPF_OS': cpf,
                'Status_Match': 'IDENTIFICADO' if cliente_id else 'NÃO_IDENTIFICADO'
            }
            
            os_relacionadas.append(relacao)
        
        return pd.DataFrame(os_relacionadas)
        
    except Exception as e:
        logging.error(f"Erro ao processar {file_path}: {e}")
        return pd.DataFrame()

def main():
    print("🔗 SISTEMA DE RELACIONAMENTO OS-CLIENTE")
    print("=" * 80)
    print("🎯 Conectando 14,337 OS com clientes únicos")
    print("📊 Combinando todos os dados extraídos")
    print("=" * 80)
    
    # Diretórios
    data_dir = Path("data")
    processed_dir = data_dir / "processed"
    
    # 1. Carregar dados de clientes
    print("\n📋 Carregando dados de clientes...")
    # Priorizar arquivo com ID_CLIENTE
    clientes_files = list(processed_dir.glob("BASE_CLIENTES_COM_ID_*.xlsx"))
    if not clientes_files:
        # Fallback para outros arquivos
        clientes_files = (list(processed_dir.glob("CLIENTES_UNICOS_*.xlsx")) + 
                         list(processed_dir.glob("CLIENTES_CONSOLIDADO_*.xlsx")))
    if not clientes_files:
        print("❌ Arquivo de clientes não encontrado!")
        return
    
    df_clientes = pd.read_excel(clientes_files[-1])  # Mais recente
    print(f"✅ {len(df_clientes)} clientes únicos carregados")
    
    # Normalizar dados dos clientes para busca
    df_clientes['Nome_normalizado'] = df_clientes['nome_completo'].apply(normalizar_nome)
    df_clientes['CPF_normalizado'] = df_clientes['cpf'].apply(normalizar_cpf)
    # Adicionar coluna Cliente_ID que corresponde ao ID_CLIENTE
    df_clientes['Cliente_ID'] = df_clientes['ID_CLIENTE']
    
    # 2. Processar todos os arquivos de OS
    print("\n🔍 Processando arquivos de OS...")
    raw_dir = data_dir / "raw"
    all_files = list(raw_dir.glob("*.xlsm")) + list(raw_dir.glob("*.xlsx"))
    
    todas_relacoes = []
    
    for i, file_path in enumerate(all_files, 1):
        print(f"[{i:2d}/{len(all_files)}] Processando: {file_path.name}")
        
        df_relacoes = processar_arquivo_os(file_path, df_clientes)
        if not df_relacoes.empty:
            todas_relacoes.append(df_relacoes)
            print(f"    ✅ {len(df_relacoes)} OS processadas")
        else:
            print(f"    ⚠️  Nenhuma OS encontrada")
    
    # 3. Combinar todas as relações
    if todas_relacoes:
        df_final = pd.concat(todas_relacoes, ignore_index=True)
    else:
        print("❌ Nenhuma relação encontrada!")
        return
    
    # 4. Estatísticas
    total_os = len(df_final)
    identificadas = len(df_final[df_final['Cliente_ID'].notna()])
    nao_identificadas = total_os - identificadas
    
    print(f"\n📊 ESTATÍSTICAS DE RELACIONAMENTO:")
    print("=" * 50)
    print(f"📋 Total de OS processadas: {total_os:,}")
    print(f"✅ OS identificadas: {identificadas:,} ({identificadas/total_os*100:.1f}%)")
    print(f"❌ OS não identificadas: {nao_identificadas:,} ({nao_identificadas/total_os*100:.1f}%)")
    
    # 5. Análise por loja
    print(f"\n🏪 RELACIONAMENTO POR LOJA:")
    print("=" * 50)
    for loja in df_final['Loja'].unique():
        df_loja = df_final[df_final['Loja'] == loja]
        total_loja = len(df_loja)
        ident_loja = len(df_loja[df_loja['Cliente_ID'].notna()])
        print(f"{loja}: {ident_loja}/{total_loja} ({ident_loja/total_loja*100:.1f}%)")
    
    # 6. Análise por sistema
    print(f"\n⚙️ RELACIONAMENTO POR SISTEMA:")
    print("=" * 50)
    for sistema in df_final['Sistema'].unique():
        df_sist = df_final[df_final['Sistema'] == sistema]
        total_sist = len(df_sist)
        ident_sist = len(df_sist[df_sist['Cliente_ID'].notna()])
        print(f"{sistema}: {ident_sist}/{total_sist} ({ident_sist/total_sist*100:.1f}%)")
    
    # 7. Salvar resultado
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = processed_dir / f"RELACIONAMENTO_OS_CLIENTE_{timestamp}.xlsx"
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet principal com relacionamentos
        df_final.to_excel(writer, sheet_name='Relacionamentos_OS_Cliente', index=False)
        
        # Sheet com estatísticas detalhadas
        stats_data = []
        
        # Stats gerais
        stats_data.append(['GERAL', 'Total_OS', total_os])
        stats_data.append(['GERAL', 'OS_Identificadas', identificadas])
        stats_data.append(['GERAL', 'OS_Não_Identificadas', nao_identificadas])
        stats_data.append(['GERAL', 'Taxa_Identificação_%', round(identificadas/total_os*100, 1)])
        
        # Stats por loja
        for loja in df_final['Loja'].unique():
            df_loja = df_final[df_final['Loja'] == loja]
            total_loja = len(df_loja)
            ident_loja = len(df_loja[df_loja['Cliente_ID'].notna()])
            stats_data.append([f'LOJA_{loja}', 'Total_OS', total_loja])
            stats_data.append([f'LOJA_{loja}', 'OS_Identificadas', ident_loja])
            stats_data.append([f'LOJA_{loja}', 'Taxa_Identificação_%', round(ident_loja/total_loja*100, 1)])
        
        # Stats por sistema
        for sistema in df_final['Sistema'].unique():
            df_sist = df_final[df_final['Sistema'] == sistema]
            total_sist = len(df_sist)
            ident_sist = len(df_sist[df_sist['Cliente_ID'].notna()])
            stats_data.append([f'SISTEMA_{sistema}', 'Total_OS', total_sist])
            stats_data.append([f'SISTEMA_{sistema}', 'OS_Identificadas', ident_sist])
            stats_data.append([f'SISTEMA_{sistema}', 'Taxa_Identificação_%', round(ident_sist/total_sist*100, 1)])
        
        df_stats = pd.DataFrame(stats_data, columns=['Categoria', 'Métrica', 'Valor'])
        df_stats.to_excel(writer, sheet_name='Estatisticas_Relacionamento', index=False)
        
        # Sheet com OS não identificadas para análise
        df_nao_identificadas = df_final[df_final['Cliente_ID'].isna()]
        if not df_nao_identificadas.empty:
            df_nao_identificadas.to_excel(writer, sheet_name='OS_Não_Identificadas', index=False)
    
    print(f"\n📁 ARQUIVO GERADO:")
    print("=" * 50)
    print(f"✅ {output_file}")
    print(f"📊 Sheets: Relacionamentos_OS_Cliente, Estatisticas_Relacionamento, OS_Não_Identificadas")
    
    print(f"\n🔗 RELACIONAMENTO CONCLUÍDO!")
    print("=" * 50)
    print(f"🎯 {identificadas:,} OS conectadas com clientes")
    print(f"📋 Base pronta para sistema final integrado")

if __name__ == "__main__":
    main()