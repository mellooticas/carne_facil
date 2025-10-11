#!/usr/bin/env python3
"""
IMPORTADOR DIRETO - ESTRUTURA ONEDRIVE ÓTICAS TATY MELLO
Importa dados da estrutura real: D:\OneDrive - Óticas Taty Mello\LOJAS\[LOJA]\CAIXA
"""

import shutil
from pathlib import Path
import os
from datetime import datetime

class ImportadorDiretoOneDrive:
    def __init__(self):
        # Estrutura real do OneDrive
        self.pasta_base_onedrive = Path("D:/OneDrive - Óticas Taty Mello/LOJAS")
        
        # Estrutura local de destino
        self.pasta_destino = Path("data/caixa_lojas")
        
        # Lojas conhecidas (baseado na análise anterior)
        self.lojas_ativas = {
            'MAUA': 'MAUA',
            'SUZANO': 'SUZANO', 
            'SUZANO2': 'SUZANO2',  # Se existir
            'RIO_PEQUENO': 'RIO_PEQUENO',
            'PERUS': 'PERUS'
        }
        
        # Padrões de arquivos 2025
        self.meses_2025 = ['jan_25', 'fev_25', 'mar_25', 'abr_25', 'mai_25', 'jun_25',
                          'jul_25', 'ago_25', 'set_25', 'out_25', 'nov_25', 'dez_25']
    
    def verificar_estrutura_onedrive(self):
        """Verifica se a estrutura do OneDrive existe"""
        print("🔍 VERIFICANDO ESTRUTURA DO ONEDRIVE")
        print("=" * 60)
        print(f"📁 Base: {self.pasta_base_onedrive}")
        
        if not self.pasta_base_onedrive.exists():
            print(f"❌ Pasta base não encontrada: {self.pasta_base_onedrive}")
            return False
        
        print(f"✅ Pasta base encontrada!")
        
        # Listar lojas disponíveis
        lojas_disponiveis = []
        for item in self.pasta_base_onedrive.iterdir():
            if item.is_dir():
                lojas_disponiveis.append(item.name)
        
        print(f"🏪 Lojas encontradas no OneDrive: {sorted(lojas_disponiveis)}")
        return True
    
    def analisar_loja_individual(self, loja):
        """Analisa uma loja específica"""
        pasta_loja_onedrive = self.pasta_base_onedrive / loja
        pasta_caixa = pasta_loja_onedrive / "CAIXA"
        
        print(f"\n🏢 ANALISANDO LOJA: {loja}")
        print(f"📁 Caminho: {pasta_caixa}")
        
        if not pasta_loja_onedrive.exists():
            print(f"   ❌ Loja não encontrada")
            return None
        
        if not pasta_caixa.exists():
            print(f"   ❌ Pasta CAIXA não encontrada")
            return None
        
        analise = {
            'arquivos_2025_raiz': [],
            'arquivos_outros_raiz': [],
            'pastas_anos': {},
            'total_arquivos': 0
        }
        
        # Analisar conteúdo da pasta CAIXA
        for item in pasta_caixa.iterdir():
            if item.is_file() and item.suffix.lower() == '.xlsx':
                nome = item.name.lower()
                
                # Verificar se é arquivo 2025
                if any(mes in nome for mes in self.meses_2025):
                    analise['arquivos_2025_raiz'].append(item.name)
                    print(f"   🎯 2025: {item.name}")
                else:
                    analise['arquivos_outros_raiz'].append(item.name)
                    print(f"   📄 Outro: {item.name}")
                
                analise['total_arquivos'] += 1
            
            elif item.is_dir():
                # Analisar pastas de anos
                nome_pasta = item.name
                if any(ano in nome_pasta for ano in ['2023', '2024', '2025']):
                    arquivos_pasta = list(item.glob("*.xlsx"))
                    analise['pastas_anos'][nome_pasta] = len(arquivos_pasta)
                    analise['total_arquivos'] += len(arquivos_pasta)
                    print(f"   📁 {nome_pasta}: {len(arquivos_pasta)} arquivos")
        
        print(f"   📊 Total: {analise['total_arquivos']} arquivos")
        print(f"   🎯 Arquivos 2025: {len(analise['arquivos_2025_raiz'])}")
        
        return analise
    
    def importar_dados_loja(self, loja, tipos_importacao=['2025', 'estrutura_completa']):
        """Importa dados de uma loja específica"""
        print(f"\n📥 IMPORTANDO DADOS DA LOJA: {loja}")
        print("=" * 50)
        
        pasta_origem = self.pasta_base_onedrive / loja / "CAIXA"
        pasta_destino_loja = self.pasta_destino / loja
        
        if not pasta_origem.exists():
            print(f"❌ Pasta origem não encontrada: {pasta_origem}")
            return False
        
        # Criar estrutura de destino
        pasta_destino_loja.mkdir(parents=True, exist_ok=True)
        
        importados = 0
        erros = 0
        
        # Importar arquivos da raiz (2025)
        if '2025' in tipos_importacao:
            print(f"📥 Importando arquivos 2025...")
            
            for arquivo in pasta_origem.glob("*.xlsx"):
                nome = arquivo.name.lower()
                
                # Se é arquivo 2025
                if any(mes in nome for mes in self.meses_2025):
                    try:
                        arquivo_destino = pasta_destino_loja / arquivo.name
                        
                        if arquivo_destino.exists():
                            print(f"   ⚠️ Já existe: {arquivo.name}")
                            continue
                        
                        shutil.copy2(arquivo, arquivo_destino)
                        importados += 1
                        print(f"   ✅ {arquivo.name}")
                        
                    except Exception as e:
                        erros += 1
                        print(f"   ❌ Erro em {arquivo.name}: {e}")
        
        # Importar estrutura completa (pastas de anos)
        if 'estrutura_completa' in tipos_importacao:
            print(f"📥 Importando estrutura de anos...")
            
            for item in pasta_origem.iterdir():
                if item.is_dir() and any(ano in item.name for ano in ['2023', '2024', '2025']):
                    pasta_destino_ano = pasta_destino_loja / item.name
                    
                    if pasta_destino_ano.exists():
                        print(f"   ⚠️ Pasta já existe: {item.name}")
                        continue
                    
                    try:
                        shutil.copytree(item, pasta_destino_ano)
                        arquivos_copiados = len(list(pasta_destino_ano.glob("*.xlsx")))
                        importados += arquivos_copiados
                        print(f"   ✅ {item.name}: {arquivos_copiados} arquivos")
                        
                    except Exception as e:
                        erros += 1
                        print(f"   ❌ Erro na pasta {item.name}: {e}")
        
        print(f"\n📊 Resultado da importação:")
        print(f"   ✅ Importados: {importados} arquivos")
        print(f"   ❌ Erros: {erros}")
        
        return importados > 0
    
    def executar_importacao_focalizada(self):
        """Executa importação focada em SUZANO e MAUA (prioridade 2025)"""
        print("📥 IMPORTAÇÃO FOCALIZADA - DADOS 2025")
        print("=" * 60)
        print("🎯 Foco: SUZANO e MAUA")
        print("📋 Prioridade: Dados 2025")
        print()
        
        # Verificar estrutura
        if not self.verificar_estrutura_onedrive():
            return False
        
        # Analisar lojas prioritárias
        lojas_prioritarias = ['MAUA', 'SUZANO']
        resultados = {}
        
        for loja in lojas_prioritarias:
            analise = self.analisar_loja_individual(loja)
            resultados[loja] = analise
        
        # Confirmar importação
        total_2025 = sum(len(analise['arquivos_2025_raiz']) for analise in resultados.values() if analise)
        print(f"\n📊 RESUMO DA ANÁLISE:")
        print(f"   🎯 Total arquivos 2025 encontrados: {total_2025}")
        
        if total_2025 == 0:
            print("⚠️ Nenhum arquivo 2025 encontrado")
            print("💡 Verificar se os nomes seguem padrão: jan_25.xlsx, fev_25.xlsx...")
            return False
        
        resposta = input(f"\n❓ Importar {total_2025} arquivos 2025? (s/N): ").strip().lower()
        if resposta not in ['s', 'sim', 'y', 'yes']:
            print("❌ Importação cancelada")
            return False
        
        # Executar importação
        sucessos = 0
        for loja in lojas_prioritarias:
            if resultados[loja]:
                if self.importar_dados_loja(loja, ['2025']):
                    sucessos += 1
        
        print(f"\n🎉 IMPORTAÇÃO CONCLUÍDA!")
        print(f"✅ Lojas importadas: {sucessos}/{len(lojas_prioritarias)}")
        
        return sucessos > 0
    
    def executar_importacao_completa(self):
        """Executa importação completa de todas as lojas"""
        print("📥 IMPORTAÇÃO COMPLETA - TODAS AS LOJAS")
        print("=" * 60)
        
        # Verificar estrutura
        if not self.verificar_estrutura_onedrive():
            return False
        
        # Listar lojas disponíveis
        lojas_disponiveis = [item.name for item in self.pasta_base_onedrive.iterdir() if item.is_dir()]
        
        print(f"🏪 Lojas disponíveis: {sorted(lojas_disponiveis)}")
        
        # Analisar todas
        resultados = {}
        for loja in lojas_disponiveis:
            if loja in self.lojas_ativas.values():  # Só lojas que sabemos que são ativas
                analise = self.analisar_loja_individual(loja)
                resultados[loja] = analise
        
        # Confirmar importação
        resposta = input(f"\n❓ Importar dados de {len(resultados)} lojas? (s/N): ").strip().lower()
        if resposta not in ['s', 'sim', 'y', 'yes']:
            print("❌ Importação cancelada")
            return False
        
        # Executar importação
        sucessos = 0
        for loja in resultados.keys():
            if self.importar_dados_loja(loja, ['2025', 'estrutura_completa']):
                sucessos += 1
        
        print(f"\n🎉 IMPORTAÇÃO COMPLETA CONCLUÍDA!")
        print(f"✅ Lojas importadas: {sucessos}/{len(resultados)}")
        
        return sucessos > 0
    
    def verificar_resultado_importacao(self):
        """Verifica resultado da importação"""
        print(f"\n📊 VERIFICANDO RESULTADO DA IMPORTAÇÃO")
        print("=" * 60)
        
        for loja in self.lojas_ativas.keys():
            pasta_loja = self.pasta_destino / loja
            
            if not pasta_loja.exists():
                print(f"❌ {loja}: Não importada")
                continue
            
            # Contar arquivos 2025
            arquivos_2025 = len([f for f in pasta_loja.glob("*.xlsx") 
                               if any(mes in f.name.lower() for mes in self.meses_2025)])
            
            # Contar pastas de anos
            pastas_anos = len([d for d in pasta_loja.iterdir() 
                             if d.is_dir() and any(ano in d.name for ano in ['2023', '2024', '2025'])])
            
            print(f"✅ {loja}: {arquivos_2025} arquivos 2025, {pastas_anos} pastas de anos")

def main():
    importador = ImportadorDiretoOneDrive()
    
    print("📥 IMPORTADOR DIRETO - ONEDRIVE ÓTICAS TATY MELLO")
    print("=" * 70)
    print("📁 Origem: D:/OneDrive - Óticas Taty Mello/LOJAS/[LOJA]/CAIXA")
    print("📁 Destino: data/caixa_lojas/")
    print()
    print("1. Importação focalizada (MAUA + SUZANO + dados 2025)")
    print("2. Importação completa (todas as lojas)")
    print("3. Verificar resultado da importação")
    print("4. Sair")
    
    while True:
        escolha = input("\n👉 Escolha uma opção (1-4): ").strip()
        
        if escolha == "1":
            importador.executar_importacao_focalizada()
            break
        elif escolha == "2":
            importador.executar_importacao_completa()
            break
        elif escolha == "3":
            importador.verificar_resultado_importacao()
            break
        elif escolha == "4":
            print("👋 Saindo...")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()