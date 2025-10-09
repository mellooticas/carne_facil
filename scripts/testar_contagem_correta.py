#!/usr/bin/env python3
"""
Script para testar contagem correta de OS nos arquivos reais
"""

import pandas as pd
from pathlib import Path

def testar_contagem_os():
    """Testa a contagem correta de OS nos arquivos"""
    
    print("🔍 TESTE DE CONTAGEM CORRETA DE OS")
    print("=" * 60)
    
    arquivos = list(Path("data/raw").glob("*.xlsx"))
    
    total_os_sistema = 0
    detalhes_completos = []
    
    for arquivo in arquivos:
        print(f"\n📁 {arquivo.name}")
        print("-" * 40)
        
        try:
            df = pd.read_excel(arquivo, engine='openpyxl')
            
            print(f"📊 Linhas totais no arquivo: {len(df)}")
            print(f"📋 Colunas: {list(df.columns)}")
            
            os_count = 0
            detalhes = {
                "arquivo": arquivo.name,
                "linhas_total": len(df),
                "os_lancaster": 0,
                "os_otm": 0,
                "outras_os": 0
            }
            
            # OS LANCASTER
            if 'OS LANCASTER' in df.columns:
                os_lancaster = pd.to_numeric(df['OS LANCASTER'], errors='coerce').dropna()
                detalhes["os_lancaster"] = len(os_lancaster)
                os_count += len(os_lancaster)
                print(f"📈 OS LANCASTER: {len(os_lancaster)} registros válidos")
                if len(os_lancaster) > 0:
                    print(f"   • Range: {os_lancaster.min():.0f} - {os_lancaster.max():.0f}")
            
            # OS OTM
            if 'OS OTM' in df.columns:
                os_otm = pd.to_numeric(df['OS OTM'], errors='coerce').dropna()
                detalhes["os_otm"] = len(os_otm)
                os_count += len(os_otm)
                print(f"📈 OS OTM: {len(os_otm)} registros válidos")
                if len(os_otm) > 0:
                    print(f"   • Range: {os_otm.min():.0f} - {os_otm.max():.0f}")
            
            # Outras colunas de OS
            outras_colunas_os = [col for col in df.columns if 'OS' in str(col).upper() and col not in ['OS LANCASTER', 'OS OTM']]
            for col in outras_colunas_os:
                valores_os = pd.to_numeric(df[col], errors='coerce').dropna()
                if len(valores_os) > 0:
                    detalhes["outras_os"] += len(valores_os)
                    os_count += len(valores_os)
                    print(f"📈 {col}: {len(valores_os)} registros válidos")
            
            detalhes["total_os"] = os_count
            detalhes_completos.append(detalhes)
            total_os_sistema += os_count
            
            print(f"✅ Total de OS neste arquivo: {os_count}")
            
        except Exception as e:
            print(f"❌ Erro ao processar {arquivo.name}: {e}")
    
    print(f"\n🎯 RESUMO GERAL")
    print("=" * 60)
    print(f"📊 Total de arquivos processados: {len(detalhes_completos)}")
    print(f"📊 Total de OS no sistema: {total_os_sistema:,}")
    
    print(f"\n📋 DETALHES POR ARQUIVO:")
    print("-" * 60)
    print(f"{'Arquivo':<20} {'Linhas':<8} {'Lancaster':<10} {'OTM':<8} {'Outras':<8} {'Total OS':<10}")
    print("-" * 60)
    
    for detalhe in detalhes_completos:
        print(f"{detalhe['arquivo']:<20} {detalhe['linhas_total']:<8} {detalhe['os_lancaster']:<10} {detalhe['os_otm']:<8} {detalhe['outras_os']:<8} {detalhe['total_os']:<10}")
    
    print("-" * 60)
    total_linhas = sum(d['linhas_total'] for d in detalhes_completos)
    total_lancaster = sum(d['os_lancaster'] for d in detalhes_completos)
    total_otm = sum(d['os_otm'] for d in detalhes_completos)
    total_outras = sum(d['outras_os'] for d in detalhes_completos)
    
    print(f"{'TOTAL':<20} {total_linhas:<8} {total_lancaster:<10} {total_otm:<8} {total_outras:<8} {total_os_sistema:<10}")
    
    # Verificação
    print(f"\n🔍 VERIFICAÇÃO:")
    print(f"• Se você estava vendo apenas 43 registros, agora deveria ver {total_os_sistema:,}")
    print(f"• O problema era que o sistema contava linhas ({total_linhas}) em vez de OS válidas")
    print(f"• Agora extrai corretamente de 'OS LANCASTER' e 'OS OTM'")
    
    return detalhes_completos

if __name__ == "__main__":
    testar_contagem_os()