#!/usr/bin/env python3
"""
LIMPEZA ARQUIVOS EXCEL TEMPORÁRIOS - Só os intermediários!
Remove apenas os arquivos Excel criados durante processamento
MANTÉM: dados originais + resultado final
"""

from pathlib import Path
import os

class LimpezaExcelTemporarios:
    def __init__(self):
        self.pasta_projeto = Path("D:/projetos/carne_facil")
        
        # Pastas com arquivos Excel temporários para limpar
        self.pastas_excel_temp = [
            "data/documentos_corrigidos",
            "data/documentos_estruturados", 
            "data/vendas_estrutura_real",
            "data/vendas_vend_dia",
            "data/documentos_completos"
        ]
        
        # MANTER INTOCADOS:
        # - data/caixa_lojas/ (dados originais)
        # - Qualquer arquivo final que você queira manter
    
    def listar_arquivos_excel_temporarios(self):
        """Lista apenas os arquivos Excel temporários que serão removidos"""
        print("📋 ARQUIVOS EXCEL TEMPORÁRIOS A REMOVER:")
        print("=" * 60)
        
        total_arquivos = 0
        total_tamanho = 0
        
        for pasta in self.pastas_excel_temp:
            pasta_path = self.pasta_projeto / pasta
            if pasta_path.exists():
                print(f"\n📁 {pasta}:")
                
                arquivos_excel = list(pasta_path.glob("**/*.xlsx"))
                if arquivos_excel:
                    for arquivo in arquivos_excel:
                        try:
                            tamanho = arquivo.stat().st_size / (1024*1024)  # MB
                            print(f"   🗑️ {arquivo.name} ({tamanho:.2f} MB)")
                            total_arquivos += 1
                            total_tamanho += tamanho
                        except:
                            print(f"   🗑️ {arquivo.name}")
                            total_arquivos += 1
                else:
                    print(f"   ✅ Nenhum arquivo Excel encontrado")
        
        print(f"\n📊 RESUMO:")
        print(f"   📄 Total arquivos Excel temporários: {total_arquivos}")
        print(f"   💾 Total tamanho: {total_tamanho:.2f} MB")
        
        return total_arquivos
    
    def verificar_dados_originais_seguros(self):
        """Verifica que os dados originais estão seguros"""
        print("\n🔒 VERIFICANDO SEGURANÇA DOS DADOS ORIGINAIS:")
        print("=" * 50)
        
        pasta_lojas = self.pasta_projeto / "data/caixa_lojas"
        if pasta_lojas.exists():
            print("✅ Pasta data/caixa_lojas/ - SERÁ MANTIDA")
            
            for loja in sorted(pasta_lojas.iterdir()):
                if loja.is_dir():
                    excel_originais = len(list(loja.glob("**/*.xlsx")))
                    print(f"   🏢 {loja.name}: {excel_originais} arquivos originais - SEGUROS")
        else:
            print("❌ ATENÇÃO: Pasta data/caixa_lojas/ não encontrada!")
    
    def executar_limpeza_excel_temp(self):
        """Remove apenas os arquivos Excel temporários"""
        print("\n🧹 REMOVENDO ARQUIVOS EXCEL TEMPORÁRIOS...")
        print("=" * 50)
        
        arquivos_removidos = 0
        mb_liberados = 0
        
        for pasta in self.pastas_excel_temp:
            pasta_path = self.pasta_projeto / pasta
            if pasta_path.exists():
                arquivos_excel = list(pasta_path.glob("**/*.xlsx"))
                
                for arquivo in arquivos_excel:
                    try:
                        tamanho = arquivo.stat().st_size / (1024*1024)  # MB
                        arquivo.unlink()
                        print(f"   ✅ Removido: {arquivo.name}")
                        arquivos_removidos += 1
                        mb_liberados += tamanho
                    except Exception as e:
                        print(f"   ❌ Erro ao remover {arquivo.name}: {e}")
        
        print(f"\n🎉 LIMPEZA CONCLUÍDA!")
        print(f"   🗑️ {arquivos_removidos} arquivos Excel temporários removidos")
        print(f"   💾 {mb_liberados:.2f} MB liberados")
        
        return arquivos_removidos
    
    def mostrar_estrutura_final(self):
        """Mostra estrutura final mantendo só o essencial"""
        print("\n📁 ESTRUTURA FINAL - SÓ O ESSENCIAL:")
        print("=" * 40)
        
        # Mostrar dados originais preservados
        pasta_lojas = self.pasta_projeto / "data/caixa_lojas"
        if pasta_lojas.exists():
            print("📁 data/")
            print("   📁 caixa_lojas/ (DADOS ORIGINAIS PRESERVADOS)")
            
            total_originais = 0
            for loja in sorted(pasta_lojas.iterdir()):
                if loja.is_dir():
                    excel_count = len(list(loja.glob("**/*.xlsx")))
                    total_originais += excel_count
                    print(f"      🏢 {loja.name}/ ({excel_count} arquivos originais)")
            
            print(f"   📊 Total: {total_originais} arquivos Excel originais preservados")
        
        # Verificar se sobrou algum temporário
        print(f"\n🔍 VERIFICAÇÃO PÓS-LIMPEZA:")
        temp_restantes = 0
        for pasta in self.pastas_excel_temp:
            pasta_path = self.pasta_projeto / pasta
            if pasta_path.exists():
                temp_files = list(pasta_path.glob("**/*.xlsx"))
                if temp_files:
                    temp_restantes += len(temp_files)
                    print(f"   ⚠️ {pasta}: {len(temp_files)} arquivos restantes")
        
        if temp_restantes == 0:
            print("   ✅ Nenhum arquivo temporário restante - LIMPEZA PERFEITA!")

def main():
    limpeza = LimpezaExcelTemporarios()
    
    print("🧹 LIMPEZA ARQUIVOS EXCEL TEMPORÁRIOS")
    print("=" * 50)
    print("🎯 Remove APENAS arquivos Excel criados durante processamento")
    print("🔒 MANTÉM dados originais dos caixas INTOCADOS")
    print()
    
    # Verificar segurança primeiro
    limpeza.verificar_dados_originais_seguros()
    
    # Listar o que será removido
    total = limpeza.listar_arquivos_excel_temporarios()
    
    if total > 0:
        print(f"\n⚠️ Serão removidos {total} arquivos Excel TEMPORÁRIOS")
        print("🔒 Dados originais em data/caixa_lojas/ ficam SEGUROS")
        
        confirmacao = input("\n🤔 Confirma a remoção dos temporários? (s/n): ").strip().lower()
        
        if confirmacao in ['s', 'sim', 'y', 'yes']:
            removidos = limpeza.executar_limpeza_excel_temp()
            limpeza.mostrar_estrutura_final()
        else:
            print("❌ Limpeza cancelada")
    else:
        print("\n✅ Nenhum arquivo Excel temporário encontrado!")
        limpeza.mostrar_estrutura_final()

if __name__ == "__main__":
    main()