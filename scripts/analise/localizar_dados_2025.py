#!/usr/bin/env python3
"""
LOCALIZADOR DE DADOS 2025 NA PASTA ORIGEM
Busca dados 2025 que devem estar na raiz das pastas das lojas na origem
"""

import os
from pathlib import Path
import glob

class LocalizadorDados2025:
    def __init__(self):
        # Possíveis locais da pasta origem
        self.possiveis_origins = [
            Path("C:/Users") / os.getenv('USERNAME', 'User') / "OneDrive" / "caixa",
            Path("C:/Users") / os.getenv('USERNAME', 'User') / "OneDrive" / "CAIXA",
            Path("D:/OneDrive/caixa"),
            Path("E:/OneDrive/caixa"),
            Path("C:/Users") / os.getenv('USERNAME', 'User') / "Desktop" / "caixa",
            Path("C:/Users") / os.getenv('USERNAME', 'User') / "Documents" / "caixa",
        ]
        
        self.lojas_conhecidas = ['MAUA', 'SUZANO', 'RIO_PEQUENO', 'SAO_MATEUS', 'PERUS', 'SUZANO2']
        self.meses_2025 = ['jan_25', 'fev_25', 'mar_25', 'abr_25', 'mai_25', 'jun_25',
                          'jul_25', 'ago_25', 'set_25', 'out_25', 'nov_25', 'dez_25']
    
    def buscar_pasta_origem(self):
        """Busca a pasta origem dos dados"""
        print("🔍 PROCURANDO PASTA ORIGEM DOS DADOS...")
        print("=" * 60)
        
        for pasta in self.possiveis_origins:
            print(f"   📁 Verificando: {pasta}")
            if pasta.exists():
                print(f"      ✅ Encontrada!")
                return pasta
            else:
                print(f"      ❌ Não existe")
        
        print(f"\n⚠️ Pasta origem não encontrada automaticamente")
        print(f"💡 Vamos fazer busca manual...")
        return self.busca_manual()
    
    def busca_manual(self):
        """Busca manual pela pasta origem"""
        print(f"\n🔍 BUSCA MANUAL POR PASTAS COM DADOS DE CAIXA...")
        print("=" * 60)
        
        # Buscar em drives comuns
        drives = ['C:', 'D:', 'E:']
        pastas_suspeitas = []
        
        for drive in drives:
            drive_path = Path(drive + "/")
            if not drive_path.exists():
                continue
                
            print(f"🔍 Buscando em {drive}...")
            
            # Buscar pastas que contenham lojas conhecidas
            try:
                for pasta in drive_path.rglob("*"):
                    if pasta.is_dir():
                        nome_pasta = pasta.name.upper()
                        
                        # Se a pasta tem nome de loja conhecida
                        if nome_pasta in self.lojas_conhecidas:
                            pasta_pai = pasta.parent
                            if pasta_pai not in pastas_suspeitas:
                                pastas_suspeitas.append(pasta_pai)
                                print(f"   🏪 Encontrada loja: {pasta}")
                        
                        # Se a pasta contém palavra "caixa"
                        elif 'CAIXA' in nome_pasta:
                            if pasta not in pastas_suspeitas:
                                pastas_suspeitas.append(pasta)
                                print(f"   💰 Pasta caixa: {pasta}")
                        
                        # Limitar busca para não ser muito lenta
                        if len(pastas_suspeitas) >= 10:
                            break
                            
            except PermissionError:
                print(f"   ⚠️ Sem permissão para acessar algumas pastas em {drive}")
            except Exception as e:
                print(f"   ❌ Erro ao buscar em {drive}: {e}")
        
        print(f"\n📋 PASTAS SUSPEITAS ENCONTRADAS:")
        for i, pasta in enumerate(pastas_suspeitas, 1):
            print(f"   {i}. {pasta}")
        
        if pastas_suspeitas:
            try:
                escolha = input(f"\n👉 Escolha a pasta origem (1-{len(pastas_suspeitas)}) ou Enter para especificar manualmente: ").strip()
                
                if escolha.isdigit() and 1 <= int(escolha) <= len(pastas_suspeitas):
                    return pastas_suspeitas[int(escolha) - 1]
                
            except ValueError:
                pass
        
        # Entrada manual
        pasta_manual = input("📁 Digite o caminho completo da pasta origem: ").strip()
        if pasta_manual and Path(pasta_manual).exists():
            return Path(pasta_manual)
        
        return None
    
    def verificar_dados_2025_na_origem(self, pasta_origem):
        """Verifica dados 2025 na pasta origem"""
        print(f"\n🔍 VERIFICANDO DADOS 2025 EM: {pasta_origem}")
        print("=" * 70)
        
        dados_2025_encontrados = {}
        
        for loja in self.lojas_conhecidas:
            pasta_loja = pasta_origem / loja
            dados_2025_encontrados[loja] = {
                'pasta_existe': False,
                'arquivos_raiz': [],
                'arquivos_2025': [],
                'total_arquivos': 0
            }
            
            print(f"\n🏪 VERIFICANDO: {loja}")
            print(f"   📁 Pasta: {pasta_loja}")
            
            if not pasta_loja.exists():
                print(f"   ❌ Pasta não encontrada")
                continue
            
            dados_2025_encontrados[loja]['pasta_existe'] = True
            
            # Verificar arquivos na raiz da loja (possível localização dos dados 2025)
            arquivos_raiz = list(pasta_loja.glob("*.xlsx"))
            
            if arquivos_raiz:
                print(f"   📄 Arquivos na raiz: {len(arquivos_raiz)}")
                
                for arquivo in arquivos_raiz:
                    nome = arquivo.name.lower()
                    
                    # Verificar se é arquivo 2025
                    if any(mes in nome for mes in self.meses_2025):
                        dados_2025_encontrados[loja]['arquivos_2025'].append(arquivo.name)
                        print(f"      🎯 2025: {arquivo.name}")
                    else:
                        dados_2025_encontrados[loja]['arquivos_raiz'].append(arquivo.name)
                        print(f"      📄 Outro: {arquivo.name}")
            else:
                print(f"   ⚠️ Nenhum arquivo na raiz")
            
            # Verificar subpastas também
            subpastas = [d for d in pasta_loja.iterdir() if d.is_dir()]
            for subpasta in subpastas:
                if '2025' in subpasta.name or '25' in subpasta.name:
                    arquivos_2025_pasta = list(subpasta.glob("*.xlsx"))
                    if arquivos_2025_pasta:
                        print(f"   📁 Pasta 2025: {subpasta.name} ({len(arquivos_2025_pasta)} arquivos)")
                        for arquivo in arquivos_2025_pasta:
                            dados_2025_encontrados[loja]['arquivos_2025'].append(f"{subpasta.name}/{arquivo.name}")
            
            dados_2025_encontrados[loja]['total_arquivos'] = (
                len(dados_2025_encontrados[loja]['arquivos_raiz']) + 
                len(dados_2025_encontrados[loja]['arquivos_2025'])
            )
        
        return dados_2025_encontrados
    
    def gerar_relatorio_2025(self, dados_2025):
        """Gera relatório dos dados 2025 encontrados"""
        print(f"\n📊 RELATÓRIO DE DADOS 2025 ENCONTRADOS")
        print("=" * 70)
        
        total_lojas_com_2025 = 0
        total_arquivos_2025 = 0
        
        for loja, dados in dados_2025.items():
            if not dados['pasta_existe']:
                status = "❌ Pasta não encontrada"
            elif dados['arquivos_2025']:
                status = f"✅ {len(dados['arquivos_2025'])} arquivos 2025"
                total_lojas_com_2025 += 1
                total_arquivos_2025 += len(dados['arquivos_2025'])
            elif dados['arquivos_raiz']:
                status = f"⚠️ {len(dados['arquivos_raiz'])} arquivos (verificar se são 2025)"
            else:
                status = "❌ Sem arquivos"
            
            print(f"{loja:15} | {status}")
            
            # Mostrar arquivos 2025 encontrados
            if dados['arquivos_2025']:
                for arquivo in dados['arquivos_2025'][:3]:  # Mostrar só os primeiros 3
                    print(f"   🎯 {arquivo}")
                if len(dados['arquivos_2025']) > 3:
                    print(f"   ... e mais {len(dados['arquivos_2025']) - 3} arquivos")
        
        print(f"\n📊 RESUMO GERAL:")
        print(f"   🏪 Lojas com dados 2025: {total_lojas_com_2025}")
        print(f"   📄 Total arquivos 2025: {total_arquivos_2025}")
        
        if total_arquivos_2025 > 0:
            print(f"\n🎯 PRÓXIMO PASSO: Importar dados 2025 encontrados")
            print(f"   Comando: python importar_dados_2025.py")
        else:
            print(f"\n⚠️ NENHUM DADO 2025 ENCONTRADO")
            print(f"   Verificar se:")
            print(f"   1. Os dados 2025 estão em outra pasta")
            print(f"   2. Os arquivos têm nomes diferentes (ex: janeiro_2025.xlsx)")
            print(f"   3. Os dados ainda não foram criados")
    
    def executar_busca_completa(self):
        """Executa busca completa por dados 2025"""
        print("🔍 LOCALIZADOR DE DADOS 2025")
        print("=" * 50)
        
        # 1. Encontrar pasta origem
        pasta_origem = self.buscar_pasta_origem()
        if not pasta_origem:
            print("❌ Não foi possível localizar a pasta origem")
            return False
        
        # 2. Verificar dados 2025
        dados_2025 = self.verificar_dados_2025_na_origem(pasta_origem)
        
        # 3. Gerar relatório
        self.gerar_relatorio_2025(dados_2025)
        
        return pasta_origem, dados_2025

def main():
    localizador = LocalizadorDados2025()
    
    print("🔍 LOCALIZADOR DE DADOS 2025 NA PASTA ORIGEM")
    print("=" * 60)
    print("Este script busca os dados 2025 que devem estar na raiz")
    print("das pastas das lojas na pasta origem (não em subpastas).")
    print()
    
    resultado = localizador.executar_busca_completa()
    
    if resultado:
        print(f"\n✅ BUSCA CONCLUÍDA!")
    else:
        print(f"\n❌ BUSCA NÃO CONCLUÍDA")

if __name__ == "__main__":
    main()