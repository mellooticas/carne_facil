#!/usr/bin/env python3
"""
Criar planilha de teste para validar o sistema
"""

import pandas as pd
from pathlib import Path
import random
import numpy as np

def criar_planilha_teste():
    """Cria uma planilha de teste com dados fictícios"""
    
    print("📋 CRIANDO PLANILHA DE TESTE")
    print("="*50)
    
    # Dados fictícios para teste
    dados_teste = []
    
    # Simular 50 OS para teste
    base_os_lancaster = 5000
    base_os_otm = 5500
    
    for i in range(50):
        # Algumas OS terão duplicações intencionais
        os_lancaster = base_os_lancaster + i
        os_otm = base_os_otm + i
        
        # Adicionar linha com OS LANCASTER
        dados_teste.append({
            'OS LANCASTER': os_lancaster,
            'já lançado': 'Usado' if random.random() > 0.3 else np.nan,
            'Unnamed: 2': np.nan,
            'OS OTM': np.nan,
            'já lançado.1': np.nan
        })
        
        # Adicionar linha com OS OTM (simula duplicação)
        dados_teste.append({
            'OS LANCASTER': np.nan,
            'já lançado': np.nan,
            'Unnamed: 2': np.nan,
            'OS OTM': os_otm,
            'já lançado.1': 'Usado' if random.random() > 0.3 else np.nan
        })
    
    # Criar DataFrame
    df_teste = pd.DataFrame(dados_teste)
    
    # Embaralhar linhas para simular dados reais
    df_teste = df_teste.sample(frac=1).reset_index(drop=True)
    
    # Salvar planilha de teste
    pasta_teste = Path("data/teste")
    pasta_teste.mkdir(exist_ok=True)
    
    arquivo_teste = pasta_teste / "base_TESTE.xlsx"
    df_teste.to_excel(arquivo_teste, index=False, sheet_name='Tabela1')
    
    print(f"✅ Planilha criada: {arquivo_teste}")
    print(f"📊 Registros: {len(df_teste)}")
    print(f"📈 OS LANCASTER: {df_teste['OS LANCASTER'].count()}")
    print(f"📈 OS OTM: {df_teste['OS OTM'].count()}")
    
    # Mostrar preview
    print(f"\n👀 PREVIEW DOS DADOS:")
    print("-" * 30)
    print(df_teste.head(10).to_string())
    
    return arquivo_teste

def testar_processamento(arquivo_teste):
    """Testa o processamento da planilha criada"""
    
    print(f"\n🔬 TESTANDO PROCESSAMENTO")
    print("="*40)
    
    # Importar o sistema de análise
    import sys
    sys.path.append('.')
    
    try:
        from scripts.analisar_os import AnalisadorOS
        
        print("✅ Módulo de análise importado")
        
        # Processar arquivo de teste
        analisador = AnalisadorOS()
        
        print(f"📁 Processando: {arquivo_teste}")
        
        # Carregar planilha
        df = analisador.carregar_planilha(arquivo_teste)
        print(f"✅ Planilha carregada: {len(df)} registros")
        
        # Processar dados
        resultado = analisador.processar_arquivo(arquivo_teste)
        print(f"✅ Processamento concluído: {resultado['status']}")
        
        # Mostrar detalhes do resultado
        print(f"📊 Linhas originais: {resultado['linhas_original']}")
        print(f"📊 Linhas processadas: {resultado['linhas_processadas']}")
        
        # Extrair dados das OS
        dados_processados = []
        if resultado['status'] == 'sucesso':
            # Reprocessar para extrair OS
            df = analisador.carregar_planilha(arquivo_teste)
            
            # Extrair OS LANCASTER
            if 'OS LANCASTER' in df.columns:
                os_lancaster = df[df['OS LANCASTER'].notna()]
                for _, row in os_lancaster.iterrows():
                    dados_processados.append({
                        'numero_os': int(row['OS LANCASTER']),
                        'coluna_origem': 'OS LANCASTER',
                        'loja': 'TESTE'
                    })
            
            # Extrair OS OTM
            if 'OS OTM' in df.columns:
                os_otm = df[df['OS OTM'].notna()]
                for _, row in os_otm.iterrows():
                    dados_processados.append({
                        'numero_os': int(row['OS OTM']),
                        'coluna_origem': 'OS OTM',
                        'loja': 'TESTE'
                    })
            
            print(f"✅ OS extraídas: {len(dados_processados)}")
        else:
            print("⚠️ Processamento falhou")
        
        # Mostrar resultados
        print(f"\n📊 RESULTADOS DO PROCESSAMENTO:")
        print("-" * 40)
        
        if dados_processados:
            # Contar por tipo de OS
            lancaster = [d for d in dados_processados if d['coluna_origem'] == 'OS LANCASTER']
            otm = [d for d in dados_processados if d['coluna_origem'] == 'OS OTM']
            
            print(f"📈 OS LANCASTER processadas: {len(lancaster)}")
            print(f"📈 OS OTM processadas: {len(otm)}")
            
            # Verificar faixas
            if lancaster:
                nums_lancaster = [d['numero_os'] for d in lancaster]
                print(f"📈 Faixa LANCASTER: {min(nums_lancaster)} - {max(nums_lancaster)}")
            
            if otm:
                nums_otm = [d['numero_os'] for d in otm]
                print(f"📈 Faixa OTM: {min(nums_otm)} - {max(nums_otm)}")
            
            # Mostrar alguns exemplos
            print(f"\n👀 EXEMPLOS PROCESSADOS:")
            print("-" * 30)
            for i, dado in enumerate(dados_processados[:5]):
                print(f"  {i+1}. OS {dado['numero_os']} ({dado['coluna_origem']}) - Loja: {dado['loja']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        return False

def testar_servidor_web():
    """Testa se o servidor web está funcionando"""
    
    print(f"\n🌐 TESTANDO SERVIDOR WEB")
    print("="*40)
    
    try:
        import requests
        
        # Testar se o servidor está rodando
        try:
            response = requests.get("http://localhost:8000", timeout=3)
            if response.status_code == 200:
                print("✅ Servidor web funcionando")
                print(f"📊 Status: {response.status_code}")
                return True
            else:
                print(f"⚠️ Servidor respondeu com status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Servidor não está rodando")
            print("💡 Execute: uvicorn app.main:app --reload")
            return False
        except requests.exceptions.Timeout:
            print("⚠️ Timeout na conexão com servidor")
            return False
        except Exception as e:
            print(f"❌ Erro ao testar servidor: {e}")
            return False
            
    except ImportError:
        print("⚠️ Biblioteca requests não instalada")
        print("💡 Execute: pip install requests")
        return False

def executar_teste_completo():
    """Executa teste completo do sistema"""
    
    print("🧪 TESTE COMPLETO DO SISTEMA")
    print("="*60)
    
    resultados = {
        "planilha_criada": False,
        "processamento_ok": False,
        "servidor_ok": False
    }
    
    # Passo 1: Criar planilha de teste
    print("📋 PASSO 1: Criar planilha de teste")
    try:
        arquivo_teste = criar_planilha_teste()
        resultados["planilha_criada"] = True
        print("✅ Planilha de teste criada com sucesso")
    except Exception as e:
        print(f"❌ Erro ao criar planilha: {e}")
        return resultados
    
    # Passo 2: Testar processamento
    print(f"\n📊 PASSO 2: Testar processamento")
    try:
        resultados["processamento_ok"] = testar_processamento(arquivo_teste)
        if resultados["processamento_ok"]:
            print("✅ Processamento funcionando")
        else:
            print("❌ Falha no processamento")
    except Exception as e:
        print(f"❌ Erro no teste de processamento: {e}")
    
    # Passo 3: Testar servidor web
    print(f"\n🌐 PASSO 3: Testar servidor web")
    try:
        resultados["servidor_ok"] = testar_servidor_web()
        if resultados["servidor_ok"]:
            print("✅ Servidor web funcionando")
        else:
            print("❌ Servidor não está acessível")
    except Exception as e:
        print(f"❌ Erro no teste do servidor: {e}")
    
    # Resumo final
    print(f"\n🎯 RESUMO DO TESTE")
    print("="*30)
    
    total_testes = len(resultados)
    testes_ok = sum(resultados.values())
    
    for teste, resultado in resultados.items():
        status = "✅" if resultado else "❌"
        print(f"{status} {teste.replace('_', ' ').title()}")
    
    print(f"\n📊 Resultado: {testes_ok}/{total_testes} testes passaram")
    
    if testes_ok == total_testes:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("🚀 Sistema funcionando perfeitamente")
    else:
        print("⚠️ Alguns testes falharam")
        print("🔧 Verifique os erros acima")
    
    return resultados

if __name__ == "__main__":
    resultados = executar_teste_completo()