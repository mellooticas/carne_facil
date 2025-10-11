#!/usr/bin/env python3
"""
ANALISADOR DE ESTRUTURA DOS ARQUIVOS
Lê os arquivos existentes para entender padrões e estruturas
antes de importar dados 2025
"""

import pandas as pd
from pathlib import Path
import openpyxl
from collections import defaultdict
import json

class AnalisadorEstrutura:
    def __init__(self):
        self.pasta_caixa = Path("data/caixa_lojas")
        self.relatorio = {
            'lojas_ativas': {},
            'lojas_fechadas': {},
            'padroes_estrutura': {},
            'resumo_geral': {}
        }
    
    def identificar_lojas_ativas_fechadas(self):
        """Identifica quais lojas estão ativas e quais fecharam"""
        print("🏪 IDENTIFICANDO STATUS DAS LOJAS")
        print("=" * 50)
        
        lojas_encontradas = []
        for item in self.pasta_caixa.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                lojas_encontradas.append(item.name)
        
        # Analisar cada loja
        for loja in sorted(lojas_encontradas):
            pasta_loja = self.pasta_caixa / loja
            
            # Contar arquivos 2024 (indicador de atividade recente)
            arquivos_2024 = 0
            for subpasta in pasta_loja.iterdir():
                if subpasta.is_dir() and '2024' in subpasta.name:
                    arquivos_2024 = len(list(subpasta.glob("*.xlsx")))
                    break
            
            # Classificar loja
            if arquivos_2024 >= 10:  # Mais de 10 meses = ativa
                status = "✅ ATIVA"
                self.relatorio['lojas_ativas'][loja] = arquivos_2024
            elif arquivos_2024 > 0:
                status = "⚠️ PARCIAL"
                self.relatorio['lojas_ativas'][loja] = arquivos_2024
            else:
                status = "❌ FECHADA/INATIVA"
                self.relatorio['lojas_fechadas'][loja] = 0
            
            print(f"{loja:15} | {status:15} | Arquivos 2024: {arquivos_2024:2}")
        
        print(f"\n📊 Resumo:")
        print(f"   ✅ Lojas ativas: {len(self.relatorio['lojas_ativas'])}")
        print(f"   ❌ Lojas fechadas: {len(self.relatorio['lojas_fechadas'])}")
    
    def analisar_estrutura_arquivos(self):
        """Analisa a estrutura interna dos arquivos"""
        print(f"\n📋 ANALISANDO ESTRUTURA DOS ARQUIVOS")
        print("=" * 60)
        
        # Analisar apenas lojas ativas
        for loja in self.relatorio['lojas_ativas'].keys():
            print(f"\n🏢 ANALISANDO LOJA: {loja}")
            print("-" * 40)
            
            self.relatorio['padroes_estrutura'][loja] = self.analisar_loja_especifica(loja)
    
    def analisar_loja_especifica(self, loja):
        """Analisa estrutura de arquivos de uma loja específica"""
        pasta_loja = self.pasta_caixa / loja
        padroes = {
            'abas_por_arquivo': [],
            'tipos_tabelas_encontradas': set(),
            'estrutura_abas': {},
            'amostras_dados': {},
            'total_arquivos_analisados': 0
        }
        
        # Pegar alguns arquivos para análise (2024 mais recentes)
        pasta_2024 = None
        for subpasta in pasta_loja.iterdir():
            if subpasta.is_dir() and '2024' in subpasta.name:
                pasta_2024 = subpasta
                break
        
        if not pasta_2024:
            print(f"   ❌ Pasta 2024 não encontrada")
            return padroes
        
        # Analisar alguns arquivos recentes
        arquivos = sorted(list(pasta_2024.glob("*.xlsx")))[-3:]  # Últimos 3 arquivos
        
        for arquivo in arquivos:
            try:
                print(f"   📄 Analisando: {arquivo.name}")
                estrutura_arquivo = self.analisar_arquivo_individual(arquivo)
                
                # Compilar resultados
                padroes['abas_por_arquivo'].append(len(estrutura_arquivo['abas']))
                padroes['tipos_tabelas_encontradas'].update(estrutura_arquivo['tipos_tabelas'])
                padroes['estrutura_abas'][arquivo.name] = estrutura_arquivo['estrutura_abas']
                
                # Guardar amostra de dados do primeiro arquivo
                if not padroes['amostras_dados']:
                    padroes['amostras_dados'] = estrutura_arquivo['amostra_dados']
                
                padroes['total_arquivos_analisados'] += 1
                
            except Exception as e:
                print(f"      ❌ Erro ao analisar {arquivo.name}: {e}")
        
        # Resumir padrões encontrados
        self.resumir_padroes_loja(loja, padroes)
        return padroes
    
    def analisar_arquivo_individual(self, arquivo_path):
        """Analisa um arquivo Excel individual"""
        resultado = {
            'abas': [],
            'tipos_tabelas': set(),
            'estrutura_abas': {},
            'amostra_dados': {}
        }
        
        try:
            # Listar abas
            workbook = openpyxl.load_workbook(arquivo_path, read_only=True)
            resultado['abas'] = workbook.sheetnames
            workbook.close()
            
            # Analisar algumas abas
            abas_numericas = [aba for aba in resultado['abas'] if aba.isdigit()]
            abas_para_analisar = abas_numericas[:3] if abas_numericas else resultado['abas'][:3]
            
            for aba in abas_para_analisar:
                try:
                    df = pd.read_excel(arquivo_path, sheet_name=aba, header=None)
                    estrutura_aba = self.analisar_estrutura_aba(df, aba)
                    
                    resultado['estrutura_abas'][aba] = estrutura_aba
                    resultado['tipos_tabelas'].update(estrutura_aba['tipos_tabelas'])
                    
                    # Guardar amostra de dados
                    if aba not in resultado['amostra_dados']:
                        resultado['amostra_dados'][aba] = estrutura_aba['amostra_cabecalhos']
                
                except Exception as e:
                    print(f"         ⚠️ Erro na aba {aba}: {e}")
        
        except Exception as e:
            print(f"      ❌ Erro ao abrir arquivo: {e}")
        
        return resultado
    
    def analisar_estrutura_aba(self, df, nome_aba):
        """Analisa estrutura de uma aba específica"""
        estrutura = {
            'dimensoes': df.shape,
            'tipos_tabelas': [],
            'cabecalhos_encontrados': [],
            'amostra_cabecalhos': {},
            'linhas_com_dados': 0
        }
        
        # Procurar por cabeçalhos de tabelas conhecidas
        tipos_tabelas_conhecidas = {
            'VEND': ['Nº VENDA', 'CLIENTE', 'FORMA', 'PGTO', 'VALOR'],
            'REST_ENTR': ['RESTO', 'ENTRADA', 'CLIENTE'],
            'REC_CARN': ['RECIBO', 'CARNÊ', 'VALOR'],
            'ENTR_CARN': ['ENTRADA', 'CARNÊ'],
            'OS_ENT_DIA': ['OS', 'ENTRADA', 'DIA']
        }
        
        # Procurar padrões linha por linha
        for i, row in df.iterrows():
            if i > 50:  # Limitar busca às primeiras 50 linhas
                break
                
            linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
            linha_upper = linha_texto.upper()
            
            # Verificar se contém cabeçalhos conhecidos
            for tipo_tabela, palavras_chave in tipos_tabelas_conhecidas.items():
                if all(palavra in linha_upper for palavra in palavras_chave[:3]):  # Pelo menos 3 palavras
                    estrutura['tipos_tabelas'].append(tipo_tabela)
                    estrutura['cabecalhos_encontrados'].append((i, linha_texto))
                    
                    # Guardar amostra do cabeçalho
                    estrutura['amostra_cabecalhos'][tipo_tabela] = {
                        'linha': i,
                        'conteudo': linha_texto,
                        'colunas': [str(cell) for cell in row if pd.notna(cell)]
                    }
                    break
        
        # Contar linhas com dados
        estrutura['linhas_com_dados'] = df.dropna(how='all').shape[0]
        
        return estrutura
    
    def resumir_padroes_loja(self, loja, padroes):
        """Resume os padrões encontrados para uma loja"""
        print(f"      📊 Resumo {loja}:")
        print(f"         📄 Arquivos analisados: {padroes['total_arquivos_analisados']}")
        
        if padroes['abas_por_arquivo']:
            media_abas = sum(padroes['abas_por_arquivo']) / len(padroes['abas_por_arquivo'])
            print(f"         📋 Média de abas por arquivo: {media_abas:.1f}")
        
        if padroes['tipos_tabelas_encontradas']:
            tipos_str = ', '.join(sorted(padroes['tipos_tabelas_encontradas']))
            print(f"         🔍 Tipos de tabelas: {tipos_str}")
        
        # Mostrar amostra de cabeçalhos
        if padroes['amostras_dados']:
            print(f"         💡 Amostras de cabeçalhos encontrados:")
            for aba, amostras in list(padroes['amostras_dados'].items())[:2]:  # Só 2 abas
                for tipo_tabela, info in amostras.items():
                    print(f"            {tipo_tabela}: {info['conteudo'][:80]}...")
    
    def gerar_relatorio_final(self):
        """Gera relatório final da análise"""
        print(f"\n📈 RELATÓRIO FINAL DA ANÁLISE")
        print("=" * 70)
        
        # Resumo das lojas
        print(f"🏪 STATUS DAS LOJAS:")
        print(f"   ✅ Ativas ({len(self.relatorio['lojas_ativas'])}):")
        for loja, arquivos in self.relatorio['lojas_ativas'].items():
            print(f"      - {loja}: {arquivos} arquivos 2024")
        
        if self.relatorio['lojas_fechadas']:
            print(f"   ❌ Fechadas ({len(self.relatorio['lojas_fechadas'])}):")
            for loja in self.relatorio['lojas_fechadas'].keys():
                print(f"      - {loja}")
        
        # Padrões de estrutura
        print(f"\n📋 PADRÕES DE ESTRUTURA IDENTIFICADOS:")
        
        todos_tipos_tabelas = set()
        for loja, padroes in self.relatorio['padroes_estrutura'].items():
            todos_tipos_tabelas.update(padroes['tipos_tabelas_encontradas'])
        
        print(f"   🔍 Tipos de tabelas encontradas: {', '.join(sorted(todos_tipos_tabelas))}")
        
        # Compatibilidade com sistema atual
        print(f"\n🔧 COMPATIBILIDADE COM SISTEMA ATUAL:")
        if 'VEND' in todos_tipos_tabelas:
            print(f"   ✅ Tabelas VEND encontradas - Sistema atual funcionará")
        else:
            print(f"   ⚠️ Tabelas VEND não encontradas - Pode precisar adaptação")
        
        # Recomendações
        print(f"\n🎯 RECOMENDAÇÕES:")
        lojas_recomendadas = [loja for loja, arquivos in self.relatorio['lojas_ativas'].items() 
                             if arquivos >= 10]
        
        if lojas_recomendadas:
            print(f"   ✅ Focar nestas lojas ativas (dados completos):")
            for loja in lojas_recomendadas:
                print(f"      - {loja}")
        
        if self.relatorio['lojas_fechadas']:
            print(f"   🗑️ Considerar remover lojas fechadas:")
            for loja in self.relatorio['lojas_fechadas'].keys():
                print(f"      - {loja}")
        
        print(f"\n📥 PRÓXIMO PASSO: Buscar dados 2025 para as lojas ativas")
        
    def salvar_relatorio_json(self):
        """Salva relatório detalhado em JSON"""
        # Converter sets para listas para serialização JSON
        relatorio_json = self.relatorio.copy()
        for loja, padroes in relatorio_json['padroes_estrutura'].items():
            padroes['tipos_tabelas_encontradas'] = list(padroes['tipos_tabelas_encontradas'])
        
        arquivo_json = self.pasta_caixa.parent / "analise_estrutura_arquivos.json"
        with open(arquivo_json, 'w', encoding='utf-8') as f:
            json.dump(relatorio_json, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Relatório detalhado salvo em: {arquivo_json}")
    
    def executar_analise_completa(self):
        """Executa análise completa da estrutura"""
        print("📋 ANALISADOR DE ESTRUTURA DOS ARQUIVOS")
        print("=" * 60)
        
        # 1. Identificar lojas ativas/fechadas
        self.identificar_lojas_ativas_fechadas()
        
        # 2. Analisar estrutura dos arquivos
        self.analisar_estrutura_arquivos()
        
        # 3. Gerar relatório final
        self.gerar_relatorio_final()
        
        # 4. Salvar relatório detalhado
        self.salvar_relatorio_json()

def main():
    analisador = AnalisadorEstrutura()
    
    print("📋 ANALISADOR DE ESTRUTURA - PREPARAÇÃO PARA 2025")
    print("=" * 60)
    print("Este script analisa os arquivos existentes para entender:")
    print("1. Quais lojas estão ativas e quais fecharam")
    print("2. Padrões de estrutura dos arquivos")
    print("3. Compatibilidade com o sistema atual")
    print()
    
    analisador.executar_analise_completa()
    
    print(f"\n✅ ANÁLISE CONCLUÍDA!")
    print(f"📋 Agora sabemos quais lojas focar para buscar dados 2025")

if __name__ == "__main__":
    main()