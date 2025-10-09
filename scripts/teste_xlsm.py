#!/usr/bin/env python3
"""
Teste específico para suporte a arquivos XLSM
"""

import pandas as pd
from pathlib import Path
import numpy as np

def criar_planilha_xlsm_teste():
    """Cria uma planilha XLSM de teste"""
    
    print("📋 CRIANDO PLANILHA XLSM DE TESTE")
    print("="*50)
    
    # Dados de teste
    dados_teste = []
    
    for i in range(30):
        # OS LANCASTER
        dados_teste.append({
            'OS LANCASTER': 6000 + i,
            'já lançado': 'Usado' if i % 3 == 0 else np.nan,
            'Unnamed: 2': np.nan,
            'OS OTM': np.nan,
            'já lançado.1': np.nan
        })
        
        # OS OTM
        dados_teste.append({
            'OS LANCASTER': np.nan,
            'já lançado': np.nan,
            'Unnamed: 2': np.nan,
            'OS OTM': 6200 + i,
            'já lançado.1': 'Usado' if i % 2 == 0 else np.nan
        })
    
    df_teste = pd.DataFrame(dados_teste)
    
    # Salvar como XLSM
    pasta_teste = Path("data/teste")
    pasta_teste.mkdir(exist_ok=True)
    
    arquivo_xlsm = pasta_teste / "base_TESTE_XLSM.xlsm"
    
    try:
        # Usar engine openpyxl para criar XLSM
        with pd.ExcelWriter(arquivo_xlsm, engine='openpyxl') as writer:
            df_teste.to_excel(writer, sheet_name='Tabela1', index=False)
        
        print(f"✅ Planilha XLSM criada: {arquivo_xlsm}")
        print(f"📊 Registros: {len(df_teste)}")
        print(f"📈 OS LANCASTER: {df_teste['OS LANCASTER'].count()}")
        print(f"📈 OS OTM: {df_teste['OS OTM'].count()}")
        
        return arquivo_xlsm
        
    except Exception as e:
        print(f"❌ Erro ao criar XLSM: {e}")
        return None

def testar_leitura_xlsm(arquivo_xlsm):
    """Testa a leitura do arquivo XLSM"""
    
    print(f"\n🔬 TESTANDO LEITURA DO ARQUIVO XLSM")
    print("="*50)
    
    if not arquivo_xlsm or not arquivo_xlsm.exists():
        print("❌ Arquivo XLSM não encontrado")
        return False
    
    try:
        # Testar leitura direta
        print("📖 1. Testando leitura direta...")
        df_direto = pd.read_excel(arquivo_xlsm, engine='openpyxl')
        print(f"✅ Leitura direta: {len(df_direto)} registros")
        
        # Testar com o analisador
        print("\n📖 2. Testando com analisador...")
        
        import sys
        sys.path.append('.')
        
        from scripts.analisar_os import AnalisadorOS
        analisador = AnalisadorOS()
        
        df_analisador = analisador.carregar_planilha(arquivo_xlsm)
        print(f"✅ Analisador: {len(df_analisador)} registros")
        
        # Processar arquivo
        print("\n📊 3. Testando processamento...")
        resultado = analisador.processar_arquivo(arquivo_xlsm)
        print(f"✅ Processamento: {resultado['status']}")
        print(f"📊 Linhas processadas: {resultado['linhas_processadas']}")
        
        # Extrair OS
        print("\n🔍 4. Extraindo OS...")
        os_extraidas = []
        
        # OS LANCASTER
        os_lancaster = df_analisador[df_analisador['OS LANCASTER'].notna()]
        for _, row in os_lancaster.iterrows():
            os_extraidas.append({
                'numero_os': int(row['OS LANCASTER']),
                'tipo': 'LANCASTER'
            })
        
        # OS OTM
        os_otm = df_analisador[df_analisador['OS OTM'].notna()]
        for _, row in os_otm.iterrows():
            os_extraidas.append({
                'numero_os': int(row['OS OTM']),
                'tipo': 'OTM'
            })
        
        print(f"✅ OS LANCASTER extraídas: {len([o for o in os_extraidas if o['tipo'] == 'LANCASTER'])}")
        print(f"✅ OS OTM extraídas: {len([o for o in os_extraidas if o['tipo'] == 'OTM'])}")
        print(f"✅ Total de OS: {len(os_extraidas)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_upload_xlsm():
    """Testa se a interface web aceita XLSM"""
    
    print(f"\n🌐 TESTANDO INTERFACE WEB COM XLSM")
    print("="*45)
    
    try:
        # Verificar se o FastAPI app está configurado para XLSM
        import app.main
        
        # Ler o código fonte para verificar se aceita .xlsm
        app_code = Path("app/main.py").read_text()
        
        if '.xlsm' in app_code:
            print("✅ Interface web configurada para XLSM")
            return True
        else:
            print("❌ Interface web NÃO aceita XLSM")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar interface: {e}")
        return False

def executar_teste_xlsm():
    """Executa teste completo de suporte a XLSM"""
    
    print("🧪 TESTE DE SUPORTE A ARQUIVOS XLSM")
    print("="*60)
    
    resultados = {
        "criacao_xlsm": False,
        "leitura_xlsm": False,
        "interface_xlsm": False
    }
    
    # Passo 1: Criar arquivo XLSM
    print("📋 PASSO 1: Criar arquivo XLSM")
    try:
        arquivo_xlsm = criar_planilha_xlsm_teste()
        if arquivo_xlsm:
            resultados["criacao_xlsm"] = True
            print("✅ Arquivo XLSM criado com sucesso")
        else:
            print("❌ Falha na criação do XLSM")
            return resultados
    except Exception as e:
        print(f"❌ Erro na criação: {e}")
        return resultados
    
    # Passo 2: Testar leitura
    print(f"\n🔬 PASSO 2: Testar leitura XLSM")
    try:
        resultados["leitura_xlsm"] = testar_leitura_xlsm(arquivo_xlsm)
        if resultados["leitura_xlsm"]:
            print("✅ Leitura XLSM funcionando")
        else:
            print("❌ Falha na leitura XLSM")
    except Exception as e:
        print(f"❌ Erro na leitura: {e}")
    
    # Passo 3: Testar interface
    print(f"\n🌐 PASSO 3: Testar interface web")
    try:
        resultados["interface_xlsm"] = testar_upload_xlsm()
        if resultados["interface_xlsm"]:
            print("✅ Interface aceita XLSM")
        else:
            print("❌ Interface não aceita XLSM")
    except Exception as e:
        print(f"❌ Erro na interface: {e}")
    
    # Resumo
    print(f"\n🎯 RESUMO DO TESTE XLSM")
    print("="*35)
    
    total_testes = len(resultados)
    testes_ok = sum(resultados.values())
    
    for teste, resultado in resultados.items():
        status = "✅" if resultado else "❌"
        print(f"{status} {teste.replace('_', ' ').title()}")
    
    print(f"\n📊 Resultado: {testes_ok}/{total_testes} testes passaram")
    
    if testes_ok == total_testes:
        print("🎉 SUPORTE COMPLETO A XLSM!")
        print("🚀 Sistema pronto para arquivos Excel com macros")
    else:
        print("⚠️ Alguns testes falharam")
        print("🔧 Verifique os erros acima")
    
    return resultados

if __name__ == "__main__":
    resultados = executar_teste_xlsm()