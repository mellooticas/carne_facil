"""
Processamento incremental de planilhas - Um arquivo por vez
"""

import sys
from pathlib import Path
import pandas as pd
import time
import json
from datetime import datetime

sys.path.append(str(Path(__file__).parent))
from analisar_os import AnalisadorOS

def processar_incremental():
    print("🚀 Processamento Incremental de Planilhas")
    print("=" * 60)
    
    analisador = AnalisadorOS()
    
    # Verificar arquivos disponíveis
    arquivos = list(analisador.diretorio_dados.glob("*.xlsx"))
    
    if not arquivos:
        print("❌ Nenhum arquivo encontrado em data/raw/")
        return
    
    print(f"📁 Arquivos encontrados: {len(arquivos)}")
    for i, arquivo in enumerate(arquivos, 1):
        tamanho_kb = arquivo.stat().st_size / 1024
        print(f"  {i}. {arquivo.name} ({tamanho_kb:.1f} KB)")
    
    # Verificar arquivos já processados
    processados_dir = Path("data/processed")
    arquivos_processados = []
    if processados_dir.exists():
        arquivos_processados = [f.stem.replace("processado_", "") for f in processados_dir.glob("processado_*.xlsx")]
    
    print(f"\n📊 Status do processamento:")
    print(f"  ✅ Já processados: {len(arquivos_processados)}")
    print(f"  ⏳ Pendentes: {len(arquivos) - len(arquivos_processados)}")
    
    # Menu de opções
    print(f"\n🎯 Opções:")
    print(f"  1. Processar próximo arquivo pendente")
    print(f"  2. Escolher arquivo específico")
    print(f"  3. Ver resumo de arquivo já processado")
    print(f"  4. Processar todos (com confirmação)")
    print(f"  0. Sair")
    
    while True:
        try:
            opcao = input(f"\n➤ Escolha uma opção (0-4): ").strip()
            
            if opcao == "0":
                print("👋 Saindo...")
                break
                
            elif opcao == "1":
                # Processar próximo pendente
                pendentes = [a for a in arquivos if a.stem not in arquivos_processados]
                if pendentes:
                    processar_arquivo_individual(analisador, pendentes[0])
                    arquivos_processados.append(pendentes[0].stem)
                else:
                    print("✅ Todos os arquivos já foram processados!")
                    
            elif opcao == "2":
                # Escolher arquivo específico
                print(f"\n📋 Escolha um arquivo:")
                for i, arquivo in enumerate(arquivos, 1):
                    status = "✅" if arquivo.stem in arquivos_processados else "⏳"
                    print(f"  {i}. {status} {arquivo.name}")
                
                try:
                    escolha = int(input(f"➤ Número do arquivo (1-{len(arquivos)}): ")) - 1
                    if 0 <= escolha < len(arquivos):
                        processar_arquivo_individual(analisador, arquivos[escolha])
                        if arquivos[escolha].stem not in arquivos_processados:
                            arquivos_processados.append(arquivos[escolha].stem)
                    else:
                        print("❌ Número inválido!")
                except ValueError:
                    print("❌ Digite um número válido!")
                    
            elif opcao == "3":
                # Ver resumo
                mostrar_resumo_processados()
                
            elif opcao == "4":
                # Processar todos
                pendentes = [a for a in arquivos if a.stem not in arquivos_processados]
                if pendentes:
                    print(f"\n⚠️ Isso processará {len(pendentes)} arquivos.")
                    confirma = input(f"Continuar? (s/N): ").strip().lower()
                    if confirma in ['s', 'sim', 'y', 'yes']:
                        for arquivo in pendentes:
                            print(f"\n" + "="*40)
                            processar_arquivo_individual(analisador, arquivo)
                            arquivos_processados.append(arquivo.stem)
                            time.sleep(1)  # Pequena pausa entre arquivos
                        print(f"\n🎉 Todos os arquivos processados!")
                    else:
                        print("❌ Processamento cancelado.")
                else:
                    print("✅ Todos os arquivos já foram processados!")
                    
            else:
                print("❌ Opção inválida! Use 0-4.")
                
        except KeyboardInterrupt:
            print(f"\n\n⚠️ Processamento interrompido pelo usuário.")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

def processar_arquivo_individual(analisador, arquivo):
    """Processa um arquivo individual com feedback detalhado"""
    
    print(f"\n🔬 PROCESSANDO: {arquivo.name}")
    print(f"📁 Tamanho: {arquivo.stat().st_size / 1024:.1f} KB")
    print("-" * 50)
    
    inicio = time.time()
    
    try:
        # Carregar e analisar básico
        print("📋 1/4 Carregando planilha...")
        df_original = analisador.carregar_planilha(arquivo)
        
        if df_original.empty:
            print("❌ Arquivo vazio ou não pôde ser lido!")
            return
        
        print(f"   ✅ {len(df_original)} linhas, {len(df_original.columns)} colunas")
        
        # Mostrar primeiras colunas
        print(f"   📋 Colunas: {', '.join(df_original.columns[:3])}...")
        
        # Processar
        print("🔧 2/4 Processando dados...")
        resultado = analisador.processar_arquivo(arquivo)
        
        # Mostrar resultado
        print("📊 3/4 Analisando resultados...")
        if resultado['status'] == 'sucesso':
            print(f"   ✅ Status: {resultado['status']}")
            print(f"   📈 Linhas processadas: {resultado['linhas_processadas']}")
            print(f"   👥 Clientes únicos: {resultado['clientes_unicos']}")
            print(f"   🔍 Duplicatas detectadas: {resultado['duplicatas_detectadas']}")
            
            # Mostrar colunas mapeadas
            if resultado['colunas_mapeadas']:
                print(f"   🗂️ Colunas mapeadas: {len(resultado['colunas_mapeadas'])}")
                mapeadas = [col for col in resultado['colunas_mapeadas'] 
                           if col in ['nome', 'cpf', 'telefone', 'numero_os', 'data_compra']]
                if mapeadas:
                    print(f"   🎯 Campos identificados: {', '.join(mapeadas)}")
            
            print("💾 4/4 Salvando resultados...")
            if 'arquivo_saida' in resultado:
                print(f"   💾 Salvo em: {resultado['arquivo_saida']}")
        else:
            print(f"   ❌ Status: {resultado['status']}")
            for erro in resultado.get('erros', []):
                print(f"   ❌ Erro: {erro}")
        
        tempo_total = time.time() - inicio
        print(f"\n⏱️ Tempo de processamento: {tempo_total:.1f}s")
        
        # Perguntar se quer ver detalhes
        if resultado['status'] == 'sucesso':
            detalhes = input(f"\n🔍 Ver detalhes do arquivo processado? (s/N): ").strip().lower()
            if detalhes in ['s', 'sim', 'y', 'yes']:
                mostrar_detalhes_arquivo(resultado)
        
    except Exception as e:
        print(f"❌ Erro durante processamento: {e}")
        tempo_total = time.time() - inicio
        print(f"⏱️ Tempo até erro: {tempo_total:.1f}s")

def mostrar_detalhes_arquivo(resultado):
    """Mostra detalhes de um arquivo processado"""
    
    print(f"\n📋 DETALHES DO PROCESSAMENTO")
    print("=" * 40)
    
    try:
        # Carregar arquivo processado
        arquivo_saida = Path(resultado['arquivo_saida'])
        if arquivo_saida.exists():
            df = pd.read_excel(arquivo_saida, sheet_name='dados_limpos')
            
            print(f"📊 Dados processados:")
            print(f"   📈 Total de registros: {len(df)}")
            print(f"   📋 Total de colunas: {len(df.columns)}")
            
            # Mostrar info das colunas principais
            colunas_principais = ['nome', 'cpf', 'telefone', 'numero_os', 'data_compra']
            for col in colunas_principais:
                if col in df.columns:
                    nao_nulos = df[col].count()
                    percentual = (nao_nulos / len(df)) * 100
                    print(f"   📋 {col}: {nao_nulos} valores ({percentual:.1f}% preenchido)")
            
            # Mostrar sample dos dados
            print(f"\n🔍 Amostra dos dados (primeiras 3 linhas):")
            colunas_mostrar = [col for col in ['nome', 'cpf', 'telefone'] if col in df.columns][:3]
            if colunas_mostrar:
                sample = df[colunas_mostrar].head(3)
                for i, (_, row) in enumerate(sample.iterrows(), 1):
                    print(f"   {i}. ", end="")
                    for col in colunas_mostrar:
                        valor = str(row[col])[:20]
                        print(f"{col}: {valor}, ", end="")
                    print()
            
        else:
            print("❌ Arquivo processado não encontrado!")
            
    except Exception as e:
        print(f"❌ Erro ao mostrar detalhes: {e}")

def mostrar_resumo_processados():
    """Mostra resumo de todos os arquivos processados"""
    
    processados_dir = Path("data/processed")
    
    if not processados_dir.exists():
        print("❌ Nenhum arquivo processado encontrado!")
        return
    
    arquivos_processados = list(processados_dir.glob("processado_*.xlsx"))
    
    if not arquivos_processados:
        print("❌ Nenhum arquivo processado encontrado!")
        return
    
    print(f"\n📊 RESUMO DOS ARQUIVOS PROCESSADOS")
    print("=" * 60)
    
    total_registros = 0
    total_clientes = 0
    total_duplicatas = 0
    
    for arquivo in arquivos_processados:
        try:
            df = pd.read_excel(arquivo, sheet_name='dados_limpos')
            
            # Tentar carregar estatísticas se existir
            stats = {}
            try:
                stats_df = pd.read_excel(arquivo, sheet_name='estatisticas')
                for _, row in stats_df.iterrows():
                    stats[row['Metrica']] = row['Valor']
            except:
                pass
            
            nome_loja = arquivo.stem.replace("processado_base_", "")
            registros = len(df)
            clientes = df['nome'].nunique() if 'nome' in df.columns else 0
            
            total_registros += registros
            total_clientes += clientes
            
            print(f"📁 {nome_loja}:")
            print(f"   📈 {registros} registros")
            print(f"   👥 {clientes} clientes únicos")
            
            # Mostrar duplicatas se disponível
            try:
                dup_df = pd.read_excel(arquivo, sheet_name='duplicatas_detectadas')
                duplicatas = len(dup_df)
                total_duplicatas += duplicatas
                print(f"   🔍 {duplicatas} duplicatas detectadas")
            except:
                print(f"   🔍 0 duplicatas detectadas")
            
        except Exception as e:
            print(f"❌ Erro ao ler {arquivo.name}: {e}")
    
    print(f"\n📈 TOTAL GERAL:")
    print(f"   📁 {len(arquivos_processados)} arquivos processados")
    print(f"   📈 {total_registros} registros totais")
    print(f"   👥 {total_clientes} clientes únicos")
    print(f"   🔍 {total_duplicatas} duplicatas detectadas")

if __name__ == "__main__":
    processar_incremental()