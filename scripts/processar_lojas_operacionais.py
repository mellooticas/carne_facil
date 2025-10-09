"""
Processamento específico das 6 lojas operacionais
SUZANO, MAUA, RIO_PEQUENO, SAO_MATEUS, PERUS, SUZANO2
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import shutil

# Lojas operacionais para processar
LOJAS_OPERACIONAIS = ['SUZANO', 'MAUA', 'RIO_PEQUENO', 'SAO_MATEUS', 'PERUS', 'SUZANO2']
LOJAS_IGNORAR = ['TMF', 'ESCRITORIO']

def verificar_e_copiar_lojas_operacionais():
    """Verifica e copia apenas as lojas operacionais"""
    
    print("🏪 PREPARAÇÃO DAS LOJAS OPERACIONAIS")
    print("=" * 60)
    
    fonte_base = Path(r"D:\OneDrive - Óticas Taty Mello\LOJAS")
    destino = Path("data/raw")
    
    # Limpar pasta de destino (manter apenas lojas operacionais)
    print("🧹 Limpando dados antigos...")
    for arquivo in destino.glob("*.xlsx"):
        loja_arquivo = arquivo.stem.replace("base_", "")
        if loja_arquivo in LOJAS_IGNORAR:
            arquivo.unlink()
            print(f"   🗑️ Removido: {arquivo.name}")
    
    arquivos_copiados = []
    lojas_sem_dados = []
    
    print(f"\n📁 Verificando {len(LOJAS_OPERACIONAIS)} lojas operacionais:")
    
    for loja in LOJAS_OPERACIONAIS:
        print(f"\n🏪 Processando loja: {loja}")
        
        loja_dir = fonte_base / loja
        os_dir = loja_dir / "OSs"
        
        if not loja_dir.exists():
            print(f"   ❌ Diretório da loja não encontrado: {loja_dir}")
            lojas_sem_dados.append(loja)
            continue
            
        if not os_dir.exists():
            print(f"   ❌ Pasta OSs não encontrada: {os_dir}")
            lojas_sem_dados.append(loja)
            continue
        
        # Procurar arquivo base.xlsx
        arquivo_base = os_dir / "base.xlsx"
        
        if arquivo_base.exists():
            try:
                # Verificar se arquivo tem dados
                df_test = pd.read_excel(arquivo_base, sheet_name=0, nrows=5)
                
                if len(df_test) > 0:
                    # Copiar arquivo
                    nome_destino = f"base_{loja}.xlsx"
                    arquivo_destino = destino / nome_destino
                    
                    shutil.copy2(arquivo_base, arquivo_destino)
                    
                    tamanho_kb = arquivo_base.stat().st_size / 1024
                    arquivos_copiados.append({
                        'loja': loja,
                        'arquivo': nome_destino,
                        'tamanho_kb': tamanho_kb,
                        'linhas_sample': len(df_test)
                    })
                    
                    print(f"   ✅ Copiado: {nome_destino} ({tamanho_kb:.1f} KB)")
                else:
                    print(f"   ⚠️ Arquivo vazio: {arquivo_base}")
                    lojas_sem_dados.append(loja)
                    
            except Exception as e:
                print(f"   ❌ Erro ao processar {arquivo_base}: {e}")
                lojas_sem_dados.append(loja)
        else:
            print(f"   ❌ Arquivo base.xlsx não encontrado")
            lojas_sem_dados.append(loja)
    
    # Relatório
    print(f"\n📊 RESULTADO DA PREPARAÇÃO")
    print("=" * 50)
    print(f"✅ Lojas com dados: {len(arquivos_copiados)}")
    print(f"❌ Lojas sem dados: {len(lojas_sem_dados)}")
    
    if arquivos_copiados:
        print(f"\n🏪 Lojas operacionais preparadas:")
        for info in arquivos_copiados:
            print(f"   • {info['loja']}: {info['arquivo']} ({info['tamanho_kb']:.1f} KB)")
    
    if lojas_sem_dados:
        print(f"\n⚠️ Lojas sem dados disponíveis:")
        for loja in lojas_sem_dados:
            print(f"   • {loja}")
    
    return arquivos_copiados, lojas_sem_dados

def analisar_lojas_operacionais():
    """Analisa especificamente as lojas operacionais"""
    
    print(f"\n🔬 ANÁLISE DAS LOJAS OPERACIONAIS")
    print("=" * 60)
    
    destino = Path("data/raw")
    arquivos = [f for f in destino.glob("base_*.xlsx") 
                if f.stem.replace("base_", "") in LOJAS_OPERACIONAIS]
    
    if not arquivos:
        print("❌ Nenhum arquivo de loja operacional encontrado!")
        return pd.DataFrame()
    
    print(f"📁 Analisando {len(arquivos)} lojas operacionais...")
    
    dados_consolidados = []
    estatisticas_lojas = []
    
    for arquivo in arquivos:
        loja = arquivo.stem.replace("base_", "")
        print(f"\n🏪 {loja}:")
        
        try:
            # Carregar dados
            df = pd.read_excel(arquivo, sheet_name='base')
            
            print(f"   📊 {len(df)} linhas, {len(df.columns)} colunas")
            print(f"   🏷️ Colunas: {list(df.columns)}")
            
            # Extrair números de OS
            os_extraidas = 0
            
            for col in df.columns:
                if 'OS' in str(col).upper():
                    valores_os = pd.to_numeric(df[col], errors='coerce').dropna()
                    
                    if len(valores_os) > 0:
                        print(f"   📈 {col}: {len(valores_os)} OS válidas ({valores_os.min()}-{valores_os.max()})")
                        
                        # Adicionar aos dados consolidados
                        for os_num in valores_os:
                            if os_num > 0:
                                dados_consolidados.append({
                                    'loja': loja,
                                    'numero_os': int(os_num),
                                    'coluna_origem': col,
                                    'arquivo_origem': arquivo.name
                                })
                                os_extraidas += 1
            
            # Verificar status
            colunas_status = [col for col in df.columns 
                             if any(termo in str(col).lower() for termo in ['lançado', 'usado', 'status'])]
            
            status_info = {}
            for col in colunas_status:
                status_counts = df[col].value_counts()
                status_info[col] = dict(status_counts.head(3))
                print(f"   📊 {col}: {dict(status_counts.head(2))}")
            
            # Estatísticas da loja
            estatisticas_lojas.append({
                'loja': loja,
                'total_linhas': len(df),
                'total_colunas': len(df.columns),
                'os_extraidas': os_extraidas,
                'colunas_os': [col for col in df.columns if 'OS' in str(col).upper()],
                'status_info': status_info
            })
            
        except Exception as e:
            print(f"   ❌ Erro ao analisar {loja}: {e}")
            estatisticas_lojas.append({
                'loja': loja,
                'erro': str(e)
            })
    
    # Criar DataFrame consolidado
    if dados_consolidados:
        df_consolidado = pd.DataFrame(dados_consolidados)
        
        print(f"\n📊 CONSOLIDAÇÃO FINAL")
        print("=" * 50)
        print(f"✅ Total de OS extraídas: {len(df_consolidado):,}")
        print(f"🏪 Lojas processadas: {df_consolidado['loja'].nunique()}")
        
        # Resumo por loja
        resumo = df_consolidado.groupby('loja').agg({
            'numero_os': ['count', 'min', 'max'],
            'coluna_origem': lambda x: list(x.unique())
        })
        
        print(f"\n📈 Resumo por loja operacional:")
        for loja in LOJAS_OPERACIONAIS:
            if loja in df_consolidado['loja'].values:
                dados_loja = df_consolidado[df_consolidado['loja'] == loja]
                print(f"   🏪 {loja}: {len(dados_loja):,} OS ({dados_loja['numero_os'].min()}-{dados_loja['numero_os'].max()})")
            else:
                print(f"   ⚠️ {loja}: Sem dados válidos")
        
        # Verificar sobreposições
        print(f"\n🔍 Análise de sobreposições:")
        duplicatas = df_consolidado.duplicated(subset=['numero_os'], keep=False)
        
        if duplicatas.any():
            os_duplicadas = df_consolidado[duplicatas].groupby('numero_os')['loja'].apply(list)
            print(f"   ⚠️ OS compartilhadas entre lojas: {len(os_duplicadas):,}")
            
            # Analisar padrões de sobreposição
            pares_lojas = {}
            for os_num, lojas in os_duplicadas.items():
                if len(lojas) == 2:
                    par = tuple(sorted(lojas))
                    pares_lojas[par] = pares_lojas.get(par, 0) + 1
            
            print(f"   📊 Padrões de sobreposição mais comuns:")
            for par, count in sorted(pares_lojas.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"      • {par[0]} ↔ {par[1]}: {count:,} OS")
        else:
            print(f"   ✅ Cada OS é única por loja")
        
        # Salvar dados
        output_dir = Path("data/processed")
        output_dir.mkdir(exist_ok=True)
        
        # Dados consolidados
        arquivo_consolidado = output_dir / "lojas_operacionais_consolidado.xlsx"
        
        with pd.ExcelWriter(arquivo_consolidado, engine='openpyxl') as writer:
            # OS consolidadas
            df_consolidado.to_excel(writer, sheet_name='os_consolidadas', index=False)
            
            # Estatísticas por loja
            df_stats = pd.DataFrame(estatisticas_lojas)
            df_stats.to_excel(writer, sheet_name='estatisticas_lojas', index=False)
            
            # Resumo executivo
            resumo_executivo = {
                'total_os': len(df_consolidado),
                'lojas_processadas': df_consolidado['loja'].nunique(),
                'lojas_operacionais': LOJAS_OPERACIONAIS,
                'range_os_global': f"{df_consolidado['numero_os'].min()}-{df_consolidado['numero_os'].max()}",
                'os_duplicadas': duplicatas.sum() if duplicatas.any() else 0,
                'data_processamento': datetime.now().isoformat()
            }
            
            pd.DataFrame([resumo_executivo]).to_excel(writer, sheet_name='resumo_executivo', index=False)
        
        print(f"\n💾 Dados salvos em: {arquivo_consolidado}")
        
        return df_consolidado, estatisticas_lojas
    
    else:
        print(f"\n❌ Nenhum dado válido encontrado nas lojas operacionais!")
        return pd.DataFrame(), []

def main():
    """Execução principal"""
    
    print("🚀 PROCESSAMENTO DAS LOJAS OPERACIONAIS")
    print("🏪 Lojas alvo:", ", ".join(LOJAS_OPERACIONAIS))
    print("🚫 Lojas ignoradas:", ", ".join(LOJAS_IGNORAR))
    print("=" * 80)
    
    # Passo 1: Preparar dados
    arquivos_copiados, lojas_sem_dados = verificar_e_copiar_lojas_operacionais()
    
    if not arquivos_copiados:
        print("\n❌ Nenhuma loja operacional tem dados disponíveis!")
        return
    
    # Passo 2: Analisar dados
    df_consolidado, estatisticas = analisar_lojas_operacionais()
    
    if df_consolidado.empty:
        print("\n❌ Falha na consolidação dos dados!")
        return
    
    # Passo 3: Relatório final
    print(f"\n🎉 PROCESSAMENTO CONCLUÍDO!")
    print("=" * 50)
    print(f"✅ {len(arquivos_copiados)} lojas processadas com sucesso")
    print(f"📊 {len(df_consolidado):,} ordens de serviço consolidadas")
    print(f"📁 Dados salvos em: data/processed/lojas_operacionais_consolidado.xlsx")
    
    if lojas_sem_dados:
        print(f"\n⚠️ Lojas que precisam de atenção:")
        for loja in lojas_sem_dados:
            print(f"   • {loja}: Verificar se há dados disponíveis")
    
    print(f"\n🎯 Próximos passos:")
    print(f"   1. Revisar dados consolidados")
    print(f"   2. Investigar sobreposições de OS")
    print(f"   3. Procurar dados de clientes relacionados")

if __name__ == "__main__":
    main()