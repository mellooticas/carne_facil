#!/usr/bin/env python3
"""
LIMPEZA GERAL - Organizar e manter apenas arquivos Excel essenciais
Remove toda confusão e mantém só os dados originais das lojas
"""

import shutil
from pathlib import Path
import os

class LimpezaGeral:
    def __init__(self):
        self.pasta_projeto = Path("D:/projetos/carne_facil")
        
        # Pastas para limpar completamente
        self.pastas_limpar = [
            "data/documentos_corrigidos",
            "data/documentos_estruturados", 
            "data/vendas_estrutura_real",
            "data/vendas_vend_dia",
            "data/documentos_completos",
            "data/processed",
            "notebooks"
        ]
        
        # Scripts para remover (manter só os essenciais)
        self.scripts_remover = [
            "processador_corrigido_os.py",
            "processador_vend_dia_puro.py", 
            "processador_vendas_real.py",
            "investigar_estrutura_excel.py",
            "investigador_2025.py",
            "verificar_os_multiplas.py",
            "verificar_os_8434_corrigida.py",
            "gerador_documentos_completos.py",
            "processador_completo_vendas.py",
            "sistema_vendas_universal.py",
            "importador_direto_onedrive.py",
            "analise_sao_mateus.py",
            "limpador_documentos_intermediarios.py"
        ]
        
        # Manter apenas
        self.manter_essencial = [
            "app/",  # Sistema web
            "data/caixa_lojas/",  # Dados originais das lojas
            ".github/",  # Documentação
            "requirements.txt",
            "README.md"
        ]
    
    def fazer_backup_dados_essenciais(self):
        """Faz backup dos dados essenciais antes da limpeza"""
        print("💾 FAZENDO BACKUP DOS DADOS ESSENCIAIS...")
        
        backup_folder = self.pasta_projeto / "backup_dados_originais"
        backup_folder.mkdir(exist_ok=True)
        
        # Backup dos dados das lojas
        pasta_lojas = self.pasta_projeto / "data/caixa_lojas"
        if pasta_lojas.exists():
            backup_lojas = backup_folder / "caixa_lojas"
            if backup_lojas.exists():
                shutil.rmtree(backup_lojas)
            shutil.copytree(pasta_lojas, backup_lojas)
            print(f"   ✅ Backup criado: {backup_lojas}")
        
        return backup_folder
    
    def listar_o_que_sera_removido(self):
        """Lista tudo que será removido para confirmação"""
        print("🗑️ ITENS QUE SERÃO REMOVIDOS:")
        print("=" * 50)
        
        # Pastas
        print("📁 PASTAS:")
        for pasta in self.pastas_limpar:
            pasta_path = self.pasta_projeto / pasta
            if pasta_path.exists():
                if pasta_path.is_dir():
                    count = len(list(pasta_path.rglob("*")))
                    print(f"   📂 {pasta} ({count} itens)")
                else:
                    print(f"   📄 {pasta}")
        
        # Scripts
        print("\n🐍 SCRIPTS PYTHON:")
        for script in self.scripts_remover:
            script_path = self.pasta_projeto / script
            if script_path.exists():
                print(f"   🗑️ {script}")
        
        # Contar total
        total_pastas = sum(1 for p in self.pastas_limpar if (self.pasta_projeto / p).exists())
        total_scripts = sum(1 for s in self.scripts_remover if (self.pasta_projeto / s).exists())
        
        print(f"\n📊 TOTAL A REMOVER:")
        print(f"   📁 {total_pastas} pastas")
        print(f"   🐍 {total_scripts} scripts")
    
    def executar_limpeza(self):
        """Executa a limpeza completa"""
        print("\n🧹 EXECUTANDO LIMPEZA GERAL...")
        print("=" * 50)
        
        removidos = 0
        
        # Remover pastas
        print("🗑️ Removendo pastas desnecessárias...")
        for pasta in self.pastas_limpar:
            pasta_path = self.pasta_projeto / pasta
            if pasta_path.exists():
                try:
                    if pasta_path.is_dir():
                        shutil.rmtree(pasta_path)
                    else:
                        pasta_path.unlink()
                    print(f"   ✅ Removido: {pasta}")
                    removidos += 1
                except Exception as e:
                    print(f"   ❌ Erro ao remover {pasta}: {e}")
        
        # Remover scripts
        print("\n🗑️ Removendo scripts desnecessários...")
        for script in self.scripts_remover:
            script_path = self.pasta_projeto / script
            if script_path.exists():
                try:
                    script_path.unlink()
                    print(f"   ✅ Removido: {script}")
                    removidos += 1
                except Exception as e:
                    print(f"   ❌ Erro ao remover {script}: {e}")
        
        return removidos
    
    def verificar_estrutura_final(self):
        """Verifica a estrutura final após limpeza"""
        print("\n📋 ESTRUTURA FINAL DO PROJETO:")
        print("=" * 40)
        
        for item in sorted(self.pasta_projeto.iterdir()):
            if item.name.startswith('.'):
                continue
                
            if item.is_dir():
                if item.name == "data":
                    print(f"📁 {item.name}/")
                    data_items = list(item.iterdir())
                    for data_item in sorted(data_items):
                        if data_item.name == "caixa_lojas":
                            print(f"   📁 caixa_lojas/")
                            lojas = list(data_item.iterdir())
                            for loja in sorted(lojas):
                                if loja.is_dir():
                                    excel_count = len(list(loja.glob("**/*.xlsx")))
                                    print(f"      🏢 {loja.name}/ ({excel_count} arquivos Excel)")
                        else:
                            print(f"   📁 {data_item.name}/")
                else:
                    print(f"📁 {item.name}/")
            else:
                if item.suffix in ['.py', '.txt', '.md']:
                    print(f"📄 {item.name}")
        
        # Contar arquivos Excel por loja
        print(f"\n📊 RESUMO ARQUIVOS EXCEL POR LOJA:")
        pasta_lojas = self.pasta_projeto / "data/caixa_lojas"
        if pasta_lojas.exists():
            total_excel = 0
            for loja in sorted(pasta_lojas.iterdir()):
                if loja.is_dir():
                    excel_files = list(loja.glob("**/*.xlsx"))
                    total_excel += len(excel_files)
                    print(f"   🏢 {loja.name}: {len(excel_files)} arquivos")
            print(f"   📊 TOTAL: {total_excel} arquivos Excel")
    
    def executar_limpeza_completa(self):
        """Executa o processo completo de limpeza"""
        print("🧹 LIMPEZA GERAL - ORGANIZAÇÃO FINAL")
        print("=" * 50)
        print("🎯 Objetivo: Manter apenas dados essenciais das lojas")
        print()
        
        # 1. Fazer backup
        backup_folder = self.fazer_backup_dados_essenciais()
        
        # 2. Listar o que será removido
        self.listar_o_que_sera_removido()
        
        # 3. Confirmar
        print(f"\n⚠️ ATENÇÃO: Esta operação é IRREVERSÍVEL!")
        print(f"📦 Backup criado em: {backup_folder}")
        
        confirmacao = input("\n🤔 Confirma a limpeza? (digite 'CONFIRMO' para continuar): ").strip()
        
        if confirmacao == "CONFIRMO":
            # 4. Executar limpeza
            removidos = self.executar_limpeza()
            
            # 5. Verificar resultado
            self.verificar_estrutura_final()
            
            print(f"\n🎉 LIMPEZA CONCLUÍDA!")
            print(f"   🗑️ {removidos} itens removidos")
            print(f"   📦 Backup disponível em: {backup_folder}")
            print(f"   📊 Projeto organizado e limpo!")
            
            return True
        else:
            print("❌ Limpeza cancelada pelo usuário")
            return False

def main():
    limpeza = LimpezaGeral()
    
    print("🧹 LIMPEZA GERAL DO PROJETO")
    print("=" * 40)
    print("🎯 Remove confusão, mantém só o essencial")
    print()
    print("1. Executar limpeza completa")
    print("2. Apenas listar o que seria removido")
    print("3. Sair")
    
    while True:
        escolha = input("\n👉 Escolha uma opção (1-3): ").strip()
        
        if escolha == "1":
            limpeza.executar_limpeza_completa()
            break
        elif escolha == "2":
            limpeza.listar_o_que_sera_removido()
            limpeza.verificar_estrutura_final()
            break
        elif escolha == "3":
            print("👋 Saindo...")
            break
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    main()