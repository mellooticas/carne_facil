#!/usr/bin/env python3
"""
IMPORTADOR DE DADOS 2025 DO ONEDRIVE
Importa dados 2025 que estão na raiz das pastas das lojas no OneDrive
"""

import os
import shutil
from pathlib import Path
import glob

class ImportadorDados2025:
    def __init__(self):
        self.pasta_caixa_local = Path("data/caixa_lojas")
        
        # Possíveis locais do OneDrive
        self.possiveis_onedrive = [
            Path(os.path.expanduser("~/OneDrive")),
            Path(os.path.expanduser("~/OneDrive - Personal")),
            Path("C:/Users/{}/OneDrive".format(os.getenv('USERNAME', 'User'))),
            Path("D:/OneDrive"),
            Path("E:/OneDrive")
        ]
        
        self.lojas = ['MAUA', 'SUZANO', 'RIO_PEQUENO', 'ITAQUERA', 'GUARULHOS', 'TABOAO']
    
    def encontrar_onedrive(self):
        """Encontra a pasta do OneDrive"""
        print("🔍 PROCURANDO PASTA DO ONEDRIVE...")
        print("=" * 50)
        
        for pasta in self.possiveis_onedrive:
            if pasta.exists():
                print(f"   ✅ Encontrado: {pasta}")
                return pasta
            else:
                print(f"   ❌ Não encontrado: {pasta}")
        
        print(f"\n⚠️ OneDrive não encontrado automaticamente")
        pasta_manual = input("📁 Digite o caminho do OneDrive (ou Enter para pular): ").strip()
        
        if pasta_manual and Path(pasta_manual).exists():
            return Path(pasta_manual)
        
        return None
    
    def buscar_dados_caixa_onedrive(self, pasta_onedrive):
        """Busca dados de caixa no OneDrive"""
        print(f"\n🔍 BUSCANDO DADOS DE CAIXA NO ONEDRIVE...")
        print("=" * 60)
        
        # Possíveis caminhos para dados de caixa
        possiveis_caminhos = [
            pasta_onedrive / "carne_facil" / "data" / "caixa_lojas",
            pasta_onedrive / "Documents" / "carne_facil" / "caixa",
            pasta_onedrive / "Desktop" / "caixa_lojas",
            pasta_onedrive / "caixa_lojas",
            pasta_onedrive / "OPTICAS" / "CAIXA",
            pasta_onedrive / "DADOS_LOJAS"
        ]
        
        for caminho in possiveis_caminhos:
            if caminho.exists():
                print(f"   ✅ Encontrado: {caminho}")
                return caminho
            else:
                print(f"   ❌ Não encontrado: {caminho}")
        
        # Busca manual
        print(f"\n🔍 Busca manual por pastas com dados de lojas...")
        for pasta in pasta_onedrive.rglob("*"):
            if pasta.is_dir() and any(loja in pasta.name.upper() for loja in self.lojas):
                print(f"   🏪 Pasta suspeita: {pasta}")
        
        return None
    
    def identificar_arquivos_2025(self, pasta_dados):
        """Identifica arquivos 2025 nas pastas das lojas"""
        print(f"\n📊 IDENTIFICANDO ARQUIVOS 2025...")
        print("=" * 50)
        
        arquivos_2025 = {}
        
        for loja in self.lojas:
            pasta_loja = pasta_dados / loja
            arquivos_2025[loja] = []
            
            if not pasta_loja.exists():
                print(f"   ❌ {loja}: Pasta não encontrada")
                continue
            
            # Buscar arquivos .xlsx na raiz da pasta da loja (2025)
            arquivos_raiz = list(pasta_loja.glob("*.xlsx"))
            
            # Buscar arquivos em pasta 2025_XXX
            pasta_2025 = None
            for subpasta in pasta_loja.iterdir():
                if subpasta.is_dir() and "2025" in subpasta.name:
                    pasta_2025 = subpasta
                    break
            
            if pasta_2025:
                arquivos_2025_pasta = list(pasta_2025.glob("*.xlsx"))
                arquivos_2025[loja].extend(arquivos_2025_pasta)
                print(f"   ✅ {loja}: {len(arquivos_2025_pasta)} arquivos em {pasta_2025.name}")
            
            if arquivos_raiz:
                # Filtrar apenas arquivos que parecem ser de 2025
                for arquivo in arquivos_raiz:
                    nome = arquivo.stem.lower()
                    if "_25" in nome or "2025" in nome or self.detectar_arquivo_2025(arquivo):
                        arquivos_2025[loja].append(arquivo)
                
                print(f"   ✅ {loja}: {len(arquivos_raiz)} arquivos na raiz (possível 2025)")
            
            if not arquivos_2025[loja]:
                print(f"   ⚠️ {loja}: Nenhum arquivo 2025 encontrado")
        
        return arquivos_2025
    
    def detectar_arquivo_2025(self, arquivo):
        """Detecta se um arquivo é de 2025 baseado no conteúdo ou data"""
        try:
            # Verificar data de modificação (simplificado)
            stat = arquivo.stat()
            import datetime
            data_mod = datetime.datetime.fromtimestamp(stat.st_mtime)
            
            # Se foi modificado em 2025, provavelmente é arquivo 2025
            if data_mod.year >= 2025:
                return True
            
            # Verificar padrões no nome
            nome = arquivo.stem.lower()
            padroes_2025 = ["jan_25", "fev_25", "mar_25", "abr_25", "mai_25", "jun_25"]
            return any(padrao in nome for padrao in padroes_2025)
            
        except Exception:
            return False
    
    def importar_arquivos_2025(self, arquivos_2025):
        """Importa arquivos 2025 para a estrutura local"""
        print(f"\n📥 IMPORTANDO ARQUIVOS 2025...")
        print("=" * 50)
        
        total_importados = 0
        
        for loja, arquivos in arquivos_2025.items():
            if not arquivos:
                continue
            
            # Criar pasta 2025 local ou usar raiz da loja
            pasta_destino_2025 = self.pasta_caixa_local / loja / "2025_{}".format(loja[:3])
            pasta_destino_raiz = self.pasta_caixa_local / loja
            
            # Decidir estrutura baseado na quantidade de arquivos
            if len(arquivos) >= 6:  # Provavelmente dados mensais completos
                pasta_destino = pasta_destino_2025
                pasta_destino.mkdir(parents=True, exist_ok=True)
                print(f"\n🏪 {loja} → {pasta_destino}")
            else:
                pasta_destino = pasta_destino_raiz
                pasta_destino.mkdir(parents=True, exist_ok=True)
                print(f"\n🏪 {loja} → {pasta_destino} (raiz)")
            
            for arquivo in arquivos:
                try:
                    arquivo_destino = pasta_destino / arquivo.name
                    
                    # Evitar sobrescrever se já existe
                    if arquivo_destino.exists():
                        print(f"   ⚠️ Já existe: {arquivo.name}")
                        continue
                    
                    shutil.copy2(arquivo, arquivo_destino)
                    total_importados += 1
                    print(f"   ✅ Importado: {arquivo.name}")
                    
                except Exception as e:
                    print(f"   ❌ Erro ao importar {arquivo.name}: {e}")
        
        print(f"\n🎉 IMPORTAÇÃO CONCLUÍDA: {total_importados} arquivos importados")
        return total_importados
    
    def verificar_estrutura_final(self):
        """Verifica estrutura final após importação"""
        print(f"\n📊 ESTRUTURA FINAL APÓS IMPORTAÇÃO:")
        print("=" * 60)
        
        for loja in self.lojas:
            pasta_loja = self.pasta_caixa_local / loja
            
            if not pasta_loja.exists():
                print(f"❌ {loja}: Pasta não existe")
                continue
            
            print(f"\n🏪 {loja}:")
            
            # Contar arquivos por ano
            total_arquivos = 0
            
            for subpasta in pasta_loja.iterdir():
                if subpasta.is_dir():
                    arquivos = list(subpasta.glob("*.xlsx"))
                    total_arquivos += len(arquivos)
                    ano = "2025" if "2025" in subpasta.name else ("2024" if "2024" in subpasta.name else "2023")
                    print(f"   📁 {ano}: {len(arquivos)} arquivos ({subpasta.name})")
            
            # Arquivos na raiz (possível 2025)
            arquivos_raiz = list(pasta_loja.glob("*.xlsx"))
            if arquivos_raiz:
                total_arquivos += len(arquivos_raiz)
                print(f"   📄 Raiz (2025): {len(arquivos_raiz)} arquivos")
            
            print(f"   📊 Total: {total_arquivos} arquivos")
    
    def executar_importacao_completa(self):
        """Executa importação completa dos dados 2025"""
        print("📥 IMPORTADOR DE DADOS 2025 DO ONEDRIVE")
        print("=" * 70)
        
        # 1. Encontrar OneDrive
        pasta_onedrive = self.encontrar_onedrive()
        if not pasta_onedrive:
            print("❌ Não foi possível localizar o OneDrive")
            return False
        
        # 2. Buscar dados de caixa
        pasta_dados = self.buscar_dados_caixa_onedrive(pasta_onedrive)
        if not pasta_dados:
            print("❌ Não foi possível localizar dados de caixa no OneDrive")
            return False
        
        # 3. Identificar arquivos 2025
        arquivos_2025 = self.identificar_arquivos_2025(pasta_dados)
        
        total_arquivos = sum(len(arquivos) for arquivos in arquivos_2025.values())
        if total_arquivos == 0:
            print("⚠️ Nenhum arquivo 2025 foi encontrado")
            return False
        
        print(f"\n📊 RESUMO: {total_arquivos} arquivos 2025 encontrados")
        
        # 4. Confirmar importação
        resposta = input("\n❓ Confirma a importação? (s/N): ").strip().lower()
        if resposta not in ['s', 'sim', 'y', 'yes']:
            print("❌ Importação cancelada")
            return False
        
        # 5. Importar
        importados = self.importar_arquivos_2025(arquivos_2025)
        
        # 6. Verificar estrutura final
        self.verificar_estrutura_final()
        
        return importados > 0

def main():
    importador = ImportadorDados2025()
    
    print("📥 IMPORTADOR DE DADOS 2025")
    print("=" * 40)
    print("Este script importa dados 2025 do OneDrive para o sistema local")
    print()
    
    sucesso = importador.executar_importacao_completa()
    
    if sucesso:
        print(f"\n🎉 IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"📋 Próximos passos:")
        print(f"   1. python sistema_vendas_universal.py")
        print(f"   2. python processar_lote.py")
        print(f"   3. python relatorio_executivo.py")
    else:
        print(f"\n❌ IMPORTAÇÃO NÃO REALIZADA")

if __name__ == "__main__":
    main()