"""
Analisador específico para os dados reais das óticas
Ajustado para trabalhar com a estrutura encontrada: OS LANCASTER, OS OTM, etc.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
from datetime import datetime

def analisar_dados_reais():
    """Analisa os dados reais com a estrutura encontrada"""
    
    print("🔬 ANÁLISE DOS DADOS REAIS DAS ÓTICAS")
    print("=" * 60)
    
    arquivos = list(Path("data/raw").glob("*.xlsx"))
    
    consolidado = []
    
    for arquivo in arquivos:
        print(f"\n📁 Analisando: {arquivo.name}")
        loja = arquivo.stem.replace("base_", "")
        
        try:
            # Carregar dados do sheet 'base'
            df = pd.read_excel(arquivo, sheet_name='base')
            
            print(f"   📊 {len(df)} linhas, {len(df.columns)} colunas")
            print(f"   🏷️ Colunas: {list(df.columns)}")
            
            # Analisar estrutura dos dados
            print(f"\n   🔍 Análise detalhada:")
            
            # Verificar colunas de OS
            colunas_os = [col for col in df.columns if 'OS' in str(col).upper()]
            print(f"   📋 Colunas de OS: {colunas_os}")
            
            # Analisar dados em cada coluna de OS
            for col in colunas_os:
                valores_validos = df[col].dropna()
                valores_numericos = pd.to_numeric(valores_validos, errors='coerce').dropna()
                
                print(f"   📈 {col}:")
                print(f"      • Total de valores: {len(valores_validos)}")
                print(f"      • Valores numéricos: {len(valores_numericos)}")
                
                if len(valores_numericos) > 0:
                    print(f"      • Range: {valores_numericos.min()} - {valores_numericos.max()}")
                    print(f"      • Sample: {valores_numericos.head(3).tolist()}")
                    
                    # Extrair dados para consolidação
                    for _, valor in valores_numericos.items():
                        if pd.notna(valor) and valor > 0:
                            consolidado.append({
                                'loja': loja,
                                'numero_os': int(valor),
                                'origem_coluna': col,
                                'arquivo': arquivo.name
                            })
            
            # Verificar colunas de status
            colunas_status = [col for col in df.columns if any(termo in str(col).lower() 
                             for termo in ['lançado', 'usado', 'status'])]
            print(f"   📊 Colunas de status: {colunas_status}")
            
            for col in colunas_status:
                valores_unicos = df[col].value_counts()
                print(f"   📈 {col}: {dict(valores_unicos.head(3))}")
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    # Análise consolidada
    if consolidado:
        print(f"\n📊 ANÁLISE CONSOLIDADA")
        print("=" * 60)
        
        df_consolidado = pd.DataFrame(consolidado)
        
        print(f"✅ Total de OS encontradas: {len(df_consolidado)}")
        print(f"📁 Lojas com dados: {df_consolidado['loja'].nunique()}")
        
        # Análise por loja
        por_loja = df_consolidado.groupby('loja').agg({
            'numero_os': ['count', 'min', 'max'],
            'origem_coluna': lambda x: list(x.unique())
        }).round(0)
        
        print(f"\n📈 Resumo por loja:")
        for loja in df_consolidado['loja'].unique():
            dados_loja = df_consolidado[df_consolidado['loja'] == loja]
            print(f"   🏪 {loja}:")
            print(f"      • OS encontradas: {len(dados_loja)}")
            print(f"      • Range de OS: {dados_loja['numero_os'].min()} - {dados_loja['numero_os'].max()}")
            print(f"      • Colunas origem: {list(dados_loja['origem_coluna'].unique())}")
        
        # Verificar duplicatas entre lojas
        print(f"\n🔍 Análise de duplicatas:")
        duplicatas_entre_lojas = df_consolidado.duplicated(subset=['numero_os'], keep=False)
        
        if duplicatas_entre_lojas.any():
            os_duplicadas = df_consolidado[duplicatas_entre_lojas].groupby('numero_os')['loja'].apply(list)
            print(f"   ⚠️ OS duplicadas entre lojas: {len(os_duplicadas)}")
            
            # Mostrar alguns exemplos
            for os_num, lojas in os_duplicadas.head(3).items():
                print(f"      • OS {os_num}: {lojas}")
        else:
            print(f"   ✅ Nenhuma OS duplicada entre lojas")
        
        # Salvar dados consolidados
        output_file = Path("data/processed/os_consolidadas.xlsx")
        df_consolidado.to_excel(output_file, index=False)
        print(f"\n💾 Dados consolidados salvos em: {output_file}")
        
        return df_consolidado
    
    else:
        print(f"\n❌ Nenhum dado válido encontrado!")
        return pd.DataFrame()

def criar_base_unificada():
    """Cria uma base unificada com os dados das OS"""
    
    print(f"\n🔧 CRIANDO BASE UNIFICADA")
    print("=" * 40)
    
    try:
        # Carregar dados consolidados
        consolidado_file = Path("data/processed/os_consolidadas.xlsx")
        
        if not consolidado_file.exists():
            print("❌ Execute a análise consolidada primeiro!")
            return
        
        df_consolidado = pd.read_excel(consolidado_file)
        
        # Criar estrutura unificada
        df_unificado = df_consolidado.copy()
        
        # Adicionar campos derivados
        df_unificado['data_analise'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df_unificado['status_os'] = 'identificada'  # Todas foram identificadas nas planilhas
        
        # Tentar extrair ano da OS (assumindo padrão AANN...)
        df_unificado['ano_estimado'] = df_unificado['numero_os'].apply(
            lambda x: 2000 + int(str(x)[:2]) if len(str(x)) >= 4 else None
        )
        
        # Adicionar metadados
        metadados = {
            'total_os': len(df_unificado),
            'lojas': list(df_unificado['loja'].unique()),
            'range_os': f"{df_unificado['numero_os'].min()} - {df_unificado['numero_os'].max()}",
            'data_processamento': datetime.now().isoformat(),
            'arquivos_fonte': list(df_unificado['arquivo'].unique())
        }
        
        # Salvar base unificada
        output_file = Path("data/processed/base_unificada_os.xlsx")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df_unificado.to_excel(writer, sheet_name='os_unificadas', index=False)
            
            # Salvar metadados
            metadados_df = pd.DataFrame([metadados])
            metadados_df.to_excel(writer, sheet_name='metadados', index=False)
            
            # Resumo por loja
            resumo_loja = df_unificado.groupby('loja').agg({
                'numero_os': ['count', 'min', 'max'],
                'ano_estimado': lambda x: list(x.dropna().unique()) if x.dropna().any() else []
            })
            resumo_loja.to_excel(writer, sheet_name='resumo_por_loja')
        
        print(f"✅ Base unificada criada: {output_file}")
        print(f"   📊 {len(df_unificado)} OS de {len(metadados['lojas'])} lojas")
        
        return df_unificado, metadados
        
    except Exception as e:
        print(f"❌ Erro ao criar base unificada: {e}")
        return None, None

if __name__ == "__main__":
    # Executar análise completa
    df_consolidado = analisar_dados_reais()
    
    if not df_consolidado.empty:
        df_unificado, metadados = criar_base_unificada()
        
        if df_unificado is not None:
            print(f"\n🎉 ANÁLISE CONCLUÍDA!")
            print(f"✅ {len(df_unificado)} ordens de serviço identificadas")
            print(f"📁 {len(metadados['lojas'])} lojas processadas")
            print(f"💾 Dados salvos em data/processed/")
    else:
        print(f"\n⚠️ Nenhum dado válido foi encontrado para processar.")