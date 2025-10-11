#!/usr/bin/env python3
"""
🔄 SCRIPT DE RECÁLCULO COMPLETO
================================================================================
🎯 Processa todos os dados novos automaticamente
📊 Executa pipeline completo: Clientes → OS → Dioptrías → Vendas → Dashboard
🚀 Basta trocar os arquivos em data/raw/ e executar este script
================================================================================
"""

import subprocess
import sys
from pathlib import Path
import time

def executar_script(script_path, descricao):
    """Executa um script e monitora o resultado"""
    print(f"\n🔄 {descricao}")
    print("=" * 80)
    
    try:
        # Usa o Python do ambiente virtual
        python_exe = Path("D:/projetos/carne_facil/.venv/Scripts/python.exe")
        if not python_exe.exists():
            python_exe = sys.executable
            
        result = subprocess.run([
            str(python_exe), script_path
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            print(f"✅ {descricao} - CONCLUÍDO")
            if result.stdout:
                # Mostrar apenas últimas linhas importantes
                linhas = result.stdout.strip().split('\n')
                for linha in linhas[-5:]:
                    if any(key in linha.lower() for key in ['✅', '📊', '💰', '👥', 'processado', 'gerado']):
                        print(f"   {linha}")
        else:
            print(f"❌ {descricao} - ERRO")
            print(f"   {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ {descricao} - ERRO: {e}")
        return False
    
    return True

def main():
    print("🚀 RECÁLCULO COMPLETO DO SISTEMA")
    print("=" * 80)
    print("🔄 Processando todos os arquivos da pasta data/raw/")
    print("📊 Pipeline: Estrutura → Clientes → Dioptrías → Vendas → Relacionamentos → Dashboard")
    print("=" * 80)
    
    # Verificar se existem arquivos na pasta raw
    raw_dir = Path("data/raw")
    if not raw_dir.exists():
        print("❌ Pasta data/raw não encontrada!")
        return
    
    arquivos = list(raw_dir.glob("*.xlsx")) + list(raw_dir.glob("*.xlsm"))
    if not arquivos:
        print("❌ Nenhum arquivo Excel encontrado em data/raw/")
        print("   Coloque os arquivos .xlsx ou .xlsm na pasta e execute novamente.")
        return
    
    print(f"📁 Encontrados {len(arquivos)} arquivos para processar:")
    for arquivo in arquivos:
        print(f"   📄 {arquivo.name}")
    
    input("\n⏳ Pressione ENTER para iniciar o processamento...")
    
    # Pipeline de processamento
    scripts = [
        ("scripts/analisar_estrutura_os.py", "1. Analisando estrutura das OS"),
        ("scripts/criar_sistema_id_cliente.py", "2. Criando sistema de ID único para clientes"),
        ("scripts/extrair_dioptrias.py", "3. Extraindo dados de dioptrías"),
        ("scripts/extrair_vendas.py", "4. Extraindo dados de vendas"),
        ("scripts/criar_relacionamento_os_cliente.py", "5. Criando relacionamentos OS-Cliente"),
        ("scripts/sistema_final_integrado.py", "6. Gerando sistema final integrado")
    ]
    
    sucesso_total = True
    inicio = time.time()
    
    for script_path, descricao in scripts:
        if not executar_script(script_path, descricao):
            sucesso_total = False
            break
        time.sleep(1)  # Pausa entre scripts
    
    fim = time.time()
    tempo_total = fim - inicio
    
    print("\n" + "=" * 80)
    if sucesso_total:
        print("🎉 RECÁLCULO COMPLETO CONCLUÍDO COM SUCESSO!")
        print("=" * 80)
        print(f"⏱️  Tempo total: {tempo_total:.1f} segundos")
        print(f"📁 Resultados salvos em: data/processed/")
        print(f"📊 Dashboard atualizado automaticamente")
        print(f"🌐 Acesse: http://localhost:8000 e http://localhost:8002")
    else:
        print("❌ ERRO NO PROCESSAMENTO!")
        print("=" * 80)
        print("   Verifique os logs acima e corrija os problemas.")
    
    print("\n🔄 Para executar novamente:")
    print("   python recalcular_tudo.py")

if __name__ == "__main__":
    main()