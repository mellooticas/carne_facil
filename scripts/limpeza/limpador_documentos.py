#!/usr/bin/env python3
"""
LIMPEZA DE DOCUMENTOS INTERMEDIÁRIOS
Remove arquivos temporários e mantém apenas os documentos finais
"""

import os
from pathlib import Path
import shutil

class LimpadorDocumentos:
    def __init__(self):
        self.pasta_projeto = Path(".")
        self.pasta_caixa = Path("data/caixa_lojas")
        self.pasta_vendas = Path("data/vendas_processadas")
        self.pasta_relatorios = Path("data/relatorios_consolidados")
        self.pasta_executivos = Path("data/relatorios_executivos")
        
        # Arquivos a manter (documentos finais importantes)
        self.manter_sempre = [
            "sistema_vendas_universal.py",
            "processar_lote.py", 
            "relatorio_executivo.py",
            "GUIA_SISTEMA_VENDAS.md"
        ]
    
    def identificar_documentos_intermediarios(self):
        """Identifica documentos intermediários para remoção"""
        print("🔍 IDENTIFICANDO DOCUMENTOS INTERMEDIÁRIOS...")
        print("=" * 60)
        
        documentos_intermediarios = []
        
        # 1. Arquivos na raiz da pasta caixa_lojas (análises temporárias)
        if self.pasta_caixa.exists():
            for arquivo in self.pasta_caixa.glob("*.xlsx"):
                nome = arquivo.name.upper()
                if any(palavra in nome for palavra in [
                    'ANALISE', 'INVESTIGACAO', 'RELATORIO_CAIXA', 'TABELA_', 
                    'VENDAS_REFINADAS', 'VENDAS_CORRETAS', 'VENDAS_ARQUIVO_COMPLETO'
                ]):
                    documentos_intermediarios.append(arquivo)
        
        # 2. Scripts temporários na raiz
        for arquivo in self.pasta_projeto.glob("*.py"):
            nome = arquivo.name.lower()
            if any(palavra in nome for palavra in [
                'extrator_', 'investigar_', 'testar_', 'debug_', 'temp_',
                'analise_', 'verificar_', 'mapear_', 'processar_arquivos'
            ]) and arquivo.name not in self.manter_sempre:
                documentos_intermediarios.append(arquivo)
        
        # 3. Documentos Excel temporários na raiz
        for arquivo in self.pasta_projeto.glob("*.xlsx"):
            documentos_intermediarios.append(arquivo)
        
        return documentos_intermediarios
    
    def analisar_pastas_finais(self):
        """Analisa o conteúdo das pastas de documentos finais"""
        print("\n📊 ANÁLISE DE DOCUMENTOS FINAIS:")
        print("=" * 50)
        
        # Pasta vendas processadas
        if self.pasta_vendas.exists():
            vendas_arquivos = list(self.pasta_vendas.glob("*.xlsx"))
            print(f"📄 Vendas Processadas: {len(vendas_arquivos)} arquivos")
            for arquivo in sorted(vendas_arquivos):
                print(f"   ✅ {arquivo.name}")
        
        # Pasta relatórios consolidados  
        if self.pasta_relatorios.exists():
            relatorio_arquivos = list(self.pasta_relatorios.glob("*.xlsx"))
            print(f"\n📊 Relatórios Consolidados: {len(relatorio_arquivos)} arquivos")
            for arquivo in sorted(relatorio_arquivos):
                print(f"   ✅ {arquivo.name}")
        
        # Pasta relatórios executivos
        if self.pasta_executivos.exists():
            executivo_arquivos = list(self.pasta_executivos.glob("*"))
            print(f"\n🎯 Relatórios Executivos: {len(executivo_arquivos)} arquivos")
            for arquivo in sorted(executivo_arquivos):
                print(f"   ✅ {arquivo.name}")
    
    def limpar_documentos_intermediarios(self, documentos: list, confirmar: bool = True):
        """Remove documentos intermediários"""
        if not documentos:
            print("✅ Nenhum documento intermediário encontrado para remoção")
            return
        
        print(f"\n🗑️ DOCUMENTOS MARCADOS PARA REMOÇÃO ({len(documentos)}):")
        print("=" * 60)
        
        total_tamanho = 0
        for arquivo in documentos:
            try:
                tamanho = arquivo.stat().st_size
                total_tamanho += tamanho
                tamanho_mb = tamanho / (1024 * 1024)
                print(f"   🗑️ {arquivo.name} ({tamanho_mb:.1f} MB)")
            except Exception:
                print(f"   🗑️ {arquivo.name}")
        
        print(f"\n💾 Espaço total a liberar: {total_tamanho / (1024 * 1024):.1f} MB")
        
        if confirmar:
            resposta = input("\n❓ Confirma a remoção? (s/N): ").strip().lower()
            if resposta not in ['s', 'sim', 'y', 'yes']:
                print("❌ Operação cancelada")
                return
        
        # Executar remoção
        removidos = 0
        erros = 0
        
        for arquivo in documentos:
            try:
                if arquivo.is_file():
                    arquivo.unlink()
                elif arquivo.is_dir():
                    shutil.rmtree(arquivo)
                removidos += 1
                print(f"   ✅ Removido: {arquivo.name}")
            except Exception as e:
                erros += 1
                print(f"   ❌ Erro ao remover {arquivo.name}: {e}")
        
        print(f"\n🎉 LIMPEZA CONCLUÍDA:")
        print(f"   ✅ Removidos: {removidos} arquivos")
        print(f"   ❌ Erros: {erros} arquivos")
        print(f"   💾 Espaço liberado: {total_tamanho / (1024 * 1024):.1f} MB")
    
    def criar_backup_documentos_finais(self):
        """Cria backup dos documentos finais importantes"""
        pasta_backup = Path("backup_documentos_finais")
        
        if pasta_backup.exists():
            shutil.rmtree(pasta_backup)
        
        pasta_backup.mkdir()
        
        print(f"💾 CRIANDO BACKUP DOS DOCUMENTOS FINAIS...")
        print("=" * 50)
        
        backup_count = 0
        
        # Backup dos sistemas principais
        for sistema in self.manter_sempre:
            arquivo = Path(sistema)
            if arquivo.exists():
                shutil.copy2(arquivo, pasta_backup / arquivo.name)
                backup_count += 1
                print(f"   ✅ {arquivo.name}")
        
        # Backup das pastas de resultados
        for pasta, nome_backup in [
            (self.pasta_vendas, "vendas_processadas"),
            (self.pasta_relatorios, "relatorios_consolidados"), 
            (self.pasta_executivos, "relatorios_executivos")
        ]:
            if pasta.exists() and any(pasta.iterdir()):
                pasta_backup_dest = pasta_backup / nome_backup
                shutil.copytree(pasta, pasta_backup_dest)
                arquivos = len(list(pasta_backup_dest.rglob("*")))
                backup_count += arquivos
                print(f"   📁 {nome_backup}/ ({arquivos} arquivos)")
        
        print(f"\n🎉 BACKUP CRIADO: {backup_count} arquivos em {pasta_backup}")
        return pasta_backup
    
    def relatorio_limpeza(self):
        """Gera relatório final da limpeza"""
        print("\n" + "=" * 80)
        print("📋 RELATÓRIO FINAL DE LIMPEZA")
        print("=" * 80)
        
        # Estrutura final
        print("🏗️ ESTRUTURA FINAL DO PROJETO:")
        print(f"   📁 Sistema Principal:")
        for sistema in self.manter_sempre:
            if Path(sistema).exists():
                print(f"      ✅ {sistema}")
        
        print(f"\n   📁 Dados das Lojas:")
        if self.pasta_caixa.exists():
            for loja in ['MAUA', 'SUZANO', 'RIO_PEQUENO']:
                pasta_loja = self.pasta_caixa / loja
                if pasta_loja.exists():
                    subpastas = [d.name for d in pasta_loja.iterdir() if d.is_dir()]
                    print(f"      🏪 {loja}: {subpastas}")
        
        print(f"\n   📁 Documentos Finais:")
        for pasta, nome in [
            (self.pasta_vendas, "Vendas Processadas"),
            (self.pasta_relatorios, "Relatórios Consolidados"),
            (self.pasta_executivos, "Relatórios Executivos")
        ]:
            if pasta.exists():
                count = len(list(pasta.glob("*")))
                print(f"      📊 {nome}: {count} arquivos")
        
        print(f"\n🎯 PRÓXIMOS PASSOS:")
        print(f"   1. Importar dados 2025 do OneDrive para as pastas das lojas")
        print(f"   2. Executar: python sistema_vendas_universal.py")
        print(f"   3. Processar dados: python processar_lote.py")
        print(f"   4. Gerar relatório: python relatorio_executivo.py")
    
    def executar_limpeza_completa(self):
        """Executa limpeza completa do projeto"""
        print("🧹 SISTEMA DE LIMPEZA DE DOCUMENTOS")
        print("=" * 60)
        
        # 1. Criar backup primeiro
        print("🔒 FASE 1: Backup de Segurança")
        pasta_backup = self.criar_backup_documentos_finais()
        
        # 2. Identificar intermediários
        print(f"\n🔍 FASE 2: Identificação de Documentos")
        documentos_intermediarios = self.identificar_documentos_intermediarios()
        
        # 3. Analisar documentos finais
        self.analisar_pastas_finais()
        
        # 4. Limpar intermediários
        print(f"\n🗑️ FASE 3: Limpeza")
        self.limpar_documentos_intermediarios(documentos_intermediarios)
        
        # 5. Relatório final
        self.relatorio_limpeza()

def main():
    limpador = LimpadorDocumentos()
    
    print("🧹 LIMPADOR DE DOCUMENTOS INTERMEDIÁRIOS")
    print("=" * 50)
    print("1. Executar limpeza completa (com backup)")
    print("2. Apenas identificar documentos intermediários")
    print("3. Apenas analisar documentos finais")
    print("4. Sair")
    
    while True:
        escolha = input("\n👉 Escolha uma opção (1-4): ").strip()
        
        if escolha == "1":
            limpador.executar_limpeza_completa()
            break
        elif escolha == "2":
            docs = limpador.identificar_documentos_intermediarios()
            print(f"\n📊 Encontrados {len(docs)} documentos intermediários")
            for doc in docs:
                print(f"   🗑️ {doc.name}")
            break
        elif escolha == "3":
            limpador.analisar_pastas_finais()
            break
        elif escolha == "4":
            print("👋 Saindo...")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()