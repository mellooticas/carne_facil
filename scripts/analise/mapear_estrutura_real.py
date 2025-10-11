#!/usr/bin/env python3
"""
MAPEADOR DA ESTRUTURA REAL DE DADOS
Mapeia a estrutura real: lojas/loja_individual/cxs/
e identifica dados 2025 disponíveis
"""

import os
from pathlib import Path
import glob

class MapeadorEstruturaReal:
    def __init__(self):
        # Possíveis locais da estrutura real
        self.possiveis_origens = [
            Path("C:/Users") / os.getenv('USERNAME', 'User') / "OneDrive" / "lojas",
            Path("D:/OneDrive/lojas"),
            Path("E:/OneDrive/lojas"),
            Path("C:/Users") / os.getenv('USERNAME', 'User') / "Desktop" / "lojas",
            Path("C:/Users") / os.getenv('USERNAME', 'User') / "Documents" / "lojas",
            # Estrutura alternativa
            Path("C:/Users") / os.getenv('USERNAME', 'User') / "OneDrive" / "LOJAS",
            Path("D:/LOJAS"),
            Path("E:/LOJAS")
        ]
        
        # Lojas que sabemos que existem
        self.lojas_conhecidas = {
            'MAUA': ['MAUA', 'maua', 'Maua'],
            'SUZANO': ['SUZANO', 'suzano', 'Suzano'], 
            'SUZANO2': ['SUZANO2', 'suzano2', 'Suzano2'],
            'RIO_PEQUENO': ['RIO_PEQUENO', 'rio_pequeno', 'Rio_Pequeno', 'RIO PEQUENO'],
            'PERUS': ['PERUS', 'perus', 'Perus'],
            'SAO_MATEUS': ['SAO_MATEUS', 'sao_mateus', 'Sao_Mateus', 'SAO MATEUS']
        }
        
        self.meses_2025 = ['jan_25', 'fev_25', 'mar_25', 'abr_25', 'mai_25', 'jun_25',
                          'jul_25', 'ago_25', 'set_25', 'out_25', 'nov_25', 'dez_25']
    
    def encontrar_pasta_lojas(self):
        """Encontra a pasta principal 'lojas'"""
        print("🔍 PROCURANDO PASTA 'lojas' NA ESTRUTURA REAL...")
        print("=" * 60)
        
        for pasta in self.possiveis_origens:
            print(f"   📁 Verificando: {pasta}")
            if pasta.exists():
                print(f"      ✅ Encontrada!")
                return pasta
            else:
                print(f"      ❌ Não existe")
        
        print(f"\n⚠️ Pasta 'lojas' não encontrada automaticamente")
        return self.busca_manual_lojas()
    
    def busca_manual_lojas(self):
        """Busca manual pela pasta lojas"""
        print(f"\n🔍 BUSCA MANUAL POR PASTA 'lojas'...")
        print("=" * 50)
        
        # Buscar em drives comuns
        drives = ['C:', 'D:', 'E:']
        pastas_suspeitas = []
        
        for drive in drives:
            drive_path = Path(drive + "/")
            if not drive_path.exists():
                continue
                
            print(f"🔍 Buscando 'lojas' em {drive}...")
            
            try:
                # Buscar pasta com nome "lojas" ou "LOJAS"
                for pasta in drive_path.rglob("*"):
                    if pasta.is_dir():
                        nome_pasta = pasta.name.upper()
                        
                        if nome_pasta in ['LOJAS', 'LOJA']:
                            pastas_suspeitas.append(pasta)
                            print(f"   🏪 Encontrada: {pasta}")
                        
                        # Limitar busca
                        if len(pastas_suspeitas) >= 5:
                            break
                            
            except PermissionError:
                print(f"   ⚠️ Sem permissão para acessar {drive}")
            except Exception as e:
                print(f"   ❌ Erro ao buscar em {drive}: {e}")
        
        if pastas_suspeitas:
            print(f"\n📋 PASTAS 'lojas' ENCONTRADAS:")
            for i, pasta in enumerate(pastas_suspeitas, 1):
                print(f"   {i}. {pasta}")
            
            try:
                escolha = input(f"\n👉 Escolha a pasta (1-{len(pastas_suspeitas)}) ou Enter para especificar: ").strip()
                
                if escolha.isdigit() and 1 <= int(escolha) <= len(pastas_suspeitas):
                    return pastas_suspeitas[int(escolha) - 1]
                
            except ValueError:
                pass
        
        # Entrada manual
        pasta_manual = input("📁 Digite o caminho da pasta 'lojas': ").strip()
        if pasta_manual and Path(pasta_manual).exists():
            return Path(pasta_manual)
        
        return None
    
    def mapear_estrutura_lojas(self, pasta_lojas):
        """Mapeia a estrutura: lojas/loja_individual/cxs/"""
        print(f"\n🗺️ MAPEANDO ESTRUTURA EM: {pasta_lojas}")
        print("=" * 70)
        
        estrutura_mapeada = {}
        
        # Listar todas as subpastas (lojas individuais)
        subpastas = [d for d in pasta_lojas.iterdir() if d.is_dir()]
        
        print(f"📁 Subpastas encontradas: {len(subpastas)}")
        for subpasta in subpastas:
            print(f"   📂 {subpasta.name}")
        print()
        
        # Mapear cada loja conhecida
        for loja_padrao, variantes in self.lojas_conhecidas.items():
            print(f"🏪 MAPEANDO LOJA: {loja_padrao}")
            
            loja_encontrada = None
            
            # Procurar por variantes do nome
            for subpasta in subpastas:
                if subpasta.name in variantes:
                    loja_encontrada = subpasta
                    break
            
            if not loja_encontrada:
                print(f"   ❌ Loja não encontrada")
                estrutura_mapeada[loja_padrao] = None
                continue
            
            print(f"   ✅ Encontrada: {loja_encontrada}")
            
            # Verificar estrutura: loja_individual/cxs/
            pasta_cxs = loja_encontrada / "cxs"
            if not pasta_cxs.exists():
                # Procurar variantes da pasta cxs
                possiveis_cxs = ['cxs', 'CXS', 'caixa', 'CAIXA', 'Caixa']
                for variante in possiveis_cxs:
                    pasta_teste = loja_encontrada / variante
                    if pasta_teste.exists():
                        pasta_cxs = pasta_teste
                        break
            
            if pasta_cxs.exists():
                print(f"   📁 Pasta cxs: {pasta_cxs}")
                estrutura_loja = self.analisar_pasta_cxs(pasta_cxs, loja_padrao)
                estrutura_mapeada[loja_padrao] = {
                    'pasta_loja': loja_encontrada,
                    'pasta_cxs': pasta_cxs,
                    'estrutura': estrutura_loja
                }
            else:
                print(f"   ❌ Pasta 'cxs' não encontrada em {loja_encontrada}")
                estrutura_mapeada[loja_padrao] = None
        
        return estrutura_mapeada
    
    def analisar_pasta_cxs(self, pasta_cxs, loja):
        """Analisa conteúdo da pasta cxs"""
        print(f"      🔍 Analisando conteúdo...")
        
        analise = {
            'arquivos_2025': [],
            'pastas_anos': [],
            'arquivos_raiz': [],
            'total_arquivos': 0
        }
        
        # Listar tudo na pasta cxs
        for item in pasta_cxs.iterdir():
            if item.is_file() and item.suffix == '.xlsx':
                nome = item.name.lower()
                
                # Verificar se é arquivo 2025
                if any(mes in nome for mes in self.meses_2025):
                    analise['arquivos_2025'].append(item.name)
                    print(f"         🎯 2025: {item.name}")
                else:
                    analise['arquivos_raiz'].append(item.name)
                    print(f"         📄 Arquivo: {item.name}")
                
                analise['total_arquivos'] += 1
            
            elif item.is_dir():
                # Verificar se é pasta de ano
                nome_pasta = item.name
                if any(ano in nome_pasta for ano in ['2023', '2024', '2025']):
                    analise['pastas_anos'].append(nome_pasta)
                    
                    # Contar arquivos na pasta do ano
                    arquivos_ano = list(item.glob("*.xlsx"))
                    print(f"         📁 {nome_pasta}: {len(arquivos_ano)} arquivos")
                    analise['total_arquivos'] += len(arquivos_ano)
                else:
                    print(f"         📂 Pasta: {nome_pasta}")
        
        return analise
    
    def gerar_relatorio_mapeamento(self, estrutura_mapeada):
        """Gera relatório do mapeamento"""
        print(f"\n📊 RELATÓRIO DO MAPEAMENTO DA ESTRUTURA REAL")
        print("=" * 70)
        
        lojas_com_dados = 0
        lojas_com_2025 = 0
        total_arquivos_2025 = 0
        
        for loja, dados in estrutura_mapeada.items():
            if dados is None:
                status = "❌ Não encontrada"
            else:
                analise = dados['estrutura']
                total_arq = analise['total_arquivos']
                arquivos_2025 = len(analise['arquivos_2025'])
                
                if arquivos_2025 > 0:
                    status = f"🎯 {arquivos_2025} arquivos 2025 + {total_arq - arquivos_2025} outros"
                    lojas_com_2025 += 1
                    total_arquivos_2025 += arquivos_2025
                elif total_arq > 0:
                    status = f"✅ {total_arq} arquivos (verificar 2025)"
                else:
                    status = "⚠️ Sem arquivos"
                
                if total_arq > 0:
                    lojas_com_dados += 1
            
            print(f"{loja:15} | {status}")
            
            # Mostrar detalhes dos arquivos 2025
            if dados and dados['estrutura']['arquivos_2025']:
                for arquivo in dados['estrutura']['arquivos_2025'][:3]:
                    print(f"   🎯 {arquivo}")
                if len(dados['estrutura']['arquivos_2025']) > 3:
                    print(f"   ... e mais {len(dados['estrutura']['arquivos_2025']) - 3}")
        
        print(f"\n📊 RESUMO GERAL:")
        print(f"   🏪 Lojas mapeadas: {len(estrutura_mapeada)}")
        print(f"   ✅ Lojas com dados: {lojas_com_dados}")
        print(f"   🎯 Lojas com dados 2025: {lojas_com_2025}")
        print(f"   📄 Total arquivos 2025: {total_arquivos_2025}")
        
        # Próximos passos
        if lojas_com_2025 > 0:
            print(f"\n🚀 PRÓXIMOS PASSOS:")
            print(f"   1. Importar dados 2025 das {lojas_com_2025} lojas")
            print(f"   2. Integrar com estrutura local")
            print(f"   3. Processar sistema completo")
        else:
            print(f"\n⚠️ NENHUM ARQUIVO 2025 ENCONTRADO")
            print(f"   Verificar se os nomes seguem padrão: jan_25.xlsx, fev_25.xlsx...")
        
        return estrutura_mapeada
    
    def executar_mapeamento_completo(self):
        """Executa mapeamento completo da estrutura real"""
        print("🗺️ MAPEADOR DA ESTRUTURA REAL")
        print("=" * 50)
        print("Mapeando: lojas/loja_individual/cxs/")
        print("Foco: SUZANO e MAUA com dados 2025")
        print()
        
        # 1. Encontrar pasta lojas
        pasta_lojas = self.encontrar_pasta_lojas()
        if not pasta_lojas:
            print("❌ Não foi possível localizar a pasta 'lojas'")
            return None
        
        # 2. Mapear estrutura
        estrutura_mapeada = self.mapear_estrutura_lojas(pasta_lojas)
        
        # 3. Gerar relatório
        resultado = self.gerar_relatorio_mapeamento(estrutura_mapeada)
        
        return pasta_lojas, resultado

def main():
    mapeador = MapeadorEstruturaReal()
    
    print("🗺️ MAPEADOR DA ESTRUTURA REAL DE DADOS")
    print("=" * 60)
    print("Este script mapeia a estrutura real:")
    print("📁 lojas/loja_individual/cxs/")
    print("🎯 Foco: Identificar dados 2025 em SUZANO e MAUA")
    print()
    
    resultado = mapeador.executar_mapeamento_completo()
    
    if resultado:
        print(f"\n✅ MAPEAMENTO CONCLUÍDO!")
        print(f"📋 Estrutura real identificada e mapeada")
    else:
        print(f"\n❌ MAPEAMENTO NÃO CONCLUÍDO")

if __name__ == "__main__":
    main()