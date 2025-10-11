#!/usr/bin/env python3
"""
VERIFICADOR DE ARQUIVOS BASE
Verifica se todos os arquivos originais estão presentes antes de buscar dados 2025
"""

from pathlib import Path
import pandas as pd
from collections import defaultdict

class VerificadorArquivosBase:
    def __init__(self):
        self.pasta_caixa = Path("data/caixa_lojas")
        self.meses_esperados = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 
                               'jul', 'ago', 'set', 'out', 'nov', 'dez']
        self.anos_esperados = ['23', '24']  # 2023 e 2024
        
    def verificar_estrutura_lojas(self):
        """Verifica a estrutura completa de cada loja"""
        print("🔍 VERIFICAÇÃO DE ARQUIVOS BASE ORIGINAIS")
        print("=" * 70)
        
        # Listar todas as lojas encontradas
        lojas_encontradas = []
        for item in self.pasta_caixa.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                lojas_encontradas.append(item.name)
        
        lojas_encontradas.sort()
        print(f"🏪 Lojas encontradas: {lojas_encontradas}")
        print()
        
        relatorio_completo = {}
        
        for loja in lojas_encontradas:
            relatorio_loja = self.verificar_loja_individual(loja)
            relatorio_completo[loja] = relatorio_loja
        
        self.gerar_relatorio_consolidado(relatorio_completo)
        return relatorio_completo
    
    def verificar_loja_individual(self, loja):
        """Verifica arquivos de uma loja específica"""
        print(f"🏢 VERIFICANDO LOJA: {loja}")
        print("-" * 50)
        
        pasta_loja = self.pasta_caixa / loja
        relatorio = {
            'total_anos': 0,
            'anos_encontrados': [],
            'arquivos_por_ano': {},
            'arquivos_faltantes': {},
            'arquivos_extras': [],
            'total_arquivos': 0
        }
        
        # Verificar subpastas de anos
        subpastas = [d for d in pasta_loja.iterdir() if d.is_dir()]
        
        for subpasta in subpastas:
            nome_subpasta = subpasta.name
            print(f"   📁 {nome_subpasta}/")
            
            # Identificar ano
            ano = None
            if '2023' in nome_subpasta or '_23' in nome_subpasta:
                ano = '2023'
            elif '2024' in nome_subpasta or '_24' in nome_subpasta:
                ano = '2024'
            
            if ano:
                relatorio['anos_encontrados'].append(ano)
                
                # Verificar arquivos nesta pasta
                arquivos = list(subpasta.glob("*.xlsx"))
                # Filtrar apenas arquivos originais (não os que criamos)
                arquivos_originais = [arq for arq in arquivos 
                                    if not any(palavra in arq.name.upper() 
                                             for palavra in ['VENDAS_', 'TABELA_', 'ANALISE_', 'RELATORIO_'])]
                
                relatorio['arquivos_por_ano'][ano] = []
                faltantes = []
                
                # Verificar meses esperados
                for mes in self.meses_esperados:
                    ano_curto = ano[-2:]  # 23 ou 24
                    arquivo_esperado = f"{mes}_{ano_curto}.xlsx"
                    arquivo_path = subpasta / arquivo_esperado
                    
                    if arquivo_path.exists():
                        relatorio['arquivos_por_ano'][ano].append(arquivo_esperado)
                        print(f"      ✅ {arquivo_esperado}")
                    else:
                        faltantes.append(arquivo_esperado)
                        print(f"      ❌ {arquivo_esperado}")
                
                if faltantes:
                    relatorio['arquivos_faltantes'][ano] = faltantes
                
                relatorio['total_arquivos'] += len(relatorio['arquivos_por_ano'][ano])
                
                # Verificar arquivos extras (não seguem padrão)
                for arquivo in arquivos_originais:
                    if not any(arquivo.name in meses_ano 
                             for meses_ano in relatorio['arquivos_por_ano'].values()):
                        if arquivo.name not in [f"{mes}_{ano[-2:]}.xlsx" for mes in self.meses_esperados]:
                            relatorio['arquivos_extras'].append(arquivo.name)
                            print(f"      ⚠️ Extra: {arquivo.name}")
        
        relatorio['total_anos'] = len(relatorio['anos_encontrados'])
        
        # Resumo da loja
        print(f"   📊 Resumo {loja}:")
        print(f"      Anos: {relatorio['total_anos']} ({', '.join(relatorio['anos_encontrados'])})")
        print(f"      Arquivos: {relatorio['total_arquivos']} total")
        if relatorio['arquivos_faltantes']:
            total_faltantes = sum(len(f) for f in relatorio['arquivos_faltantes'].values())
            print(f"      ⚠️ Faltantes: {total_faltantes}")
        print()
        
        return relatorio
    
    def gerar_relatorio_consolidado(self, relatorio_completo):
        """Gera relatório consolidado de todas as lojas"""
        print("📊 RELATÓRIO CONSOLIDADO DOS ARQUIVOS BASE")
        print("=" * 70)
        
        # Estatísticas gerais
        total_lojas = len(relatorio_completo)
        total_arquivos_geral = sum(r['total_arquivos'] for r in relatorio_completo.values())
        
        print(f"🏪 Total de lojas: {total_lojas}")
        print(f"📄 Total de arquivos: {total_arquivos_geral}")
        print()
        
        # Análise por loja
        print("📋 ANÁLISE POR LOJA:")
        print("-" * 40)
        
        for loja, relatorio in relatorio_completo.items():
            anos = '/'.join(relatorio['anos_encontrados']) if relatorio['anos_encontrados'] else 'Nenhum'
            
            # Calcular completude
            total_esperado = len(relatorio['anos_encontrados']) * 12  # 12 meses por ano
            total_encontrado = relatorio['total_arquivos']
            percentual = (total_encontrado / total_esperado * 100) if total_esperado > 0 else 0
            
            status = "✅" if percentual >= 90 else "⚠️" if percentual >= 50 else "❌"
            
            print(f"{status} {loja:15} | Anos: {anos:10} | Arquivos: {total_encontrado:2}/{total_esperado:2} ({percentual:5.1f}%)")
            
            # Mostrar faltantes se houver
            if relatorio['arquivos_faltantes']:
                for ano, faltantes in relatorio['arquivos_faltantes'].items():
                    print(f"      ❌ {ano}: {', '.join(faltantes[:3])}{'...' if len(faltantes) > 3 else ''}")
        
        print()
        
        # Recomendações
        print("🎯 RECOMENDAÇÕES:")
        print("-" * 30)
        
        lojas_incompletas = [loja for loja, rel in relatorio_completo.items() 
                           if rel['total_arquivos'] < len(rel['anos_encontrados']) * 12]
        
        if lojas_incompletas:
            print("⚠️ Lojas com arquivos faltantes:")
            for loja in lojas_incompletas:
                print(f"   - {loja}")
            print()
        
        lojas_completas = [loja for loja, rel in relatorio_completo.items() 
                         if rel['total_arquivos'] >= len(rel['anos_encontrados']) * 12]
        
        if lojas_completas:
            print("✅ Lojas com dados completos (prontas para 2025):")
            for loja in lojas_completas:
                print(f"   - {loja}")
            print()
        
        print("🔍 PRÓXIMO PASSO: Verificar onde estão os dados 2025 na pasta origem")
        print("   → Os dados 2025 devem estar na RAIZ das pastas das lojas")
        print("   → Exemplo: pasta_origem/MAUA/jan_25.xlsx (não em subpasta)")
    
    def verificar_padroes_nomes(self):
        """Verifica padrões de nomes dos arquivos"""
        print("\n🔍 ANÁLISE DE PADRÕES DE NOMES")
        print("=" * 50)
        
        todos_arquivos = []
        for arquivo in self.pasta_caixa.rglob("*.xlsx"):
            if not any(palavra in arquivo.name.upper() 
                      for palavra in ['VENDAS_', 'TABELA_', 'ANALISE_', 'RELATORIO_']):
                todos_arquivos.append(arquivo.name)
        
        # Agrupar por padrão
        padroes = defaultdict(list)
        
        for arquivo in todos_arquivos:
            if '_' in arquivo:
                partes = arquivo.replace('.xlsx', '').split('_')
                if len(partes) == 2:
                    mes, ano = partes
                    padrao = f"mes_ano ({mes}_{ano})"
                    padroes[padrao].append(arquivo)
                else:
                    padroes['Outro formato'].append(arquivo)
            else:
                padroes['Sem underscore'].append(arquivo)
        
        print("📋 Padrões encontrados:")
        for padrao, arquivos in padroes.items():
            print(f"   {padrao}: {len(arquivos)} arquivos")
            if len(arquivos) <= 5:
                print(f"      Exemplos: {', '.join(arquivos)}")
            else:
                print(f"      Exemplos: {', '.join(arquivos[:3])}...")

def main():
    verificador = VerificadorArquivosBase()
    
    print("🔍 VERIFICADOR DE ARQUIVOS BASE ORIGINAIS")
    print("=" * 60)
    print("Este script verifica se todos os arquivos originais estão presentes")
    print("antes de procurar os dados 2025 na pasta origem.")
    print()
    
    # Executar verificação
    relatorio = verificador.verificar_estrutura_lojas()
    
    # Análise de padrões
    verificador.verificar_padroes_nomes()
    
    print(f"\n✅ VERIFICAÇÃO CONCLUÍDA!")
    print(f"📋 Relatório gerado para {len(relatorio)} lojas")

if __name__ == "__main__":
    main()