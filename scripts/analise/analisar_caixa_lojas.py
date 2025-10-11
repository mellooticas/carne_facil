#!/usr/bin/env python3
"""
Analisador e Copiador de Arquivos de Caixa - Sistema Óticas
Mapeia arquivos de caixa de todas as lojas do OneDrive e copia com prefixo
"""

import os
import shutil
from pathlib import Path
import pandas as pd
from datetime import datetime
import re

class AnalisadorCaixaLojas:
    def __init__(self):
        self.base_onedrive = Path(r"D:\OneDrive - Óticas Taty Mello\LOJAS")
        self.pasta_destino = Path("data/caixa_lojas")
        self.lojas_excluidas = ['ESCRITORIO', 'TMF']
        self.relatorio = []
        
        # Criar pasta de destino
        self.pasta_destino.mkdir(exist_ok=True)
        
    def mapear_lojas_disponiveis(self):
        """Mapeia todas as lojas disponíveis no OneDrive"""
        print("=" * 80)
        print("MAPEADOR DE ARQUIVOS DE CAIXA - ÓTICAS")
        print("=" * 80)
        print(f"📂 Base OneDrive: {self.base_onedrive}")
        print()
        
        if not self.base_onedrive.exists():
            print("❌ Pasta do OneDrive não encontrada!")
            print("   Verifique se o caminho está correto")
            return []
            
        print("🔍 MAPEANDO LOJAS DISPONÍVEIS:")
        print("-" * 50)
        
        lojas_encontradas = []
        
        for item in self.base_onedrive.iterdir():
            if item.is_dir() and item.name not in self.lojas_excluidas:
                pasta_caixa = item / "CAIXA"
                tem_caixa = pasta_caixa.exists()
                
                print(f"{'✅' if tem_caixa else '❌'} {item.name:15} | {'CAIXA encontrada' if tem_caixa else 'Sem pasta CAIXA'}")
                
                if tem_caixa:
                    lojas_encontradas.append({
                        'nome': item.name,
                        'pasta': item,
                        'pasta_caixa': pasta_caixa
                    })
        
        print()
        print(f"📊 RESUMO: {len(lojas_encontradas)} lojas com pasta CAIXA encontradas")
        return lojas_encontradas
    
    def analisar_estrutura_caixa(self, loja_info):
        """Analisa estrutura de arquivos de caixa de uma loja"""
        nome_loja = loja_info['nome']
        pasta_caixa = loja_info['pasta_caixa']
        
        print(f"\n🔍 ANALISANDO: {nome_loja}")
        print("-" * 40)
        
        total_arquivos = 0
        estrutura = {
            'loja': nome_loja,
            'pasta_caixa': str(pasta_caixa),
            'subpastas': [],
            'arquivos_diretos': 0,
            'total_arquivos': 0,
            'padroes_encontrados': []
        }
        
        # Verificar arquivos diretos na pasta CAIXA
        arquivos_diretos = [f for f in pasta_caixa.iterdir() if f.is_file()]
        estrutura['arquivos_diretos'] = len(arquivos_diretos)
        total_arquivos += len(arquivos_diretos)
        
        if arquivos_diretos:
            print(f"   📄 {len(arquivos_diretos)} arquivos diretos na pasta CAIXA")
        
        # Analisar subpastas (mes/ano)
        subpastas = [d for d in pasta_caixa.iterdir() if d.is_dir()]
        
        for subpasta in subpastas:
            arquivos_subpasta = list(subpasta.rglob("*"))
            arquivos_subpasta = [f for f in arquivos_subpasta if f.is_file()]
            
            sub_info = {
                'nome': subpasta.name,
                'pasta': str(subpasta),
                'arquivos': len(arquivos_subpasta),
                'tipos_arquivo': {}
            }
            
            # Contar tipos de arquivo
            for arquivo in arquivos_subpasta:
                extensao = arquivo.suffix.lower()
                if extensao not in sub_info['tipos_arquivo']:
                    sub_info['tipos_arquivo'][extensao] = 0
                sub_info['tipos_arquivo'][extensao] += 1
            
            estrutura['subpastas'].append(sub_info)
            total_arquivos += len(arquivos_subpasta)
            
            # Identificar padrões (mes/ano)
            if re.match(r'^[a-z]{3}\d{2}$', subpasta.name.lower()):  # ex: fev22
                estrutura['padroes_encontrados'].append(subpasta.name)
            
            print(f"   📁 {subpasta.name:15} | {len(arquivos_subpasta):3} arquivos")
        
        estrutura['total_arquivos'] = total_arquivos
        print(f"   📊 TOTAL: {total_arquivos} arquivos")
        
        return estrutura
    
    def gerar_prefixo_loja(self, nome_loja):
        """Gera prefixo de 3 letras para a loja"""
        prefixos = {
            'SUZANO': 'SUZ',
            'MAUA': 'MAU', 
            'RIO_PEQUENO': 'RIO',
            'SAO_MATEUS': 'SAM',
            'PERUS': 'PER',
            'GERAL': 'GER'
        }
        
        # Se tem mapeamento específico, usa
        if nome_loja.upper() in prefixos:
            return prefixos[nome_loja.upper()]
        
        # Senão, pega as 3 primeiras letras
        return nome_loja[:3].upper()
    
    def copiar_arquivos_com_prefixo(self, estrutura, simular=True):
        """Copia arquivos adicionando prefixo da loja"""
        nome_loja = estrutura['loja']
        prefixo = self.gerar_prefixo_loja(nome_loja)
        
        print(f"\n📋 {'SIMULANDO' if simular else 'COPIANDO'} ARQUIVOS: {nome_loja} (prefixo: {prefixo})")
        print("-" * 50)
        
        pasta_loja_destino = self.pasta_destino / nome_loja
        
        if not simular:
            pasta_loja_destino.mkdir(exist_ok=True)
        
        arquivos_copiados = 0
        
        # Copiar arquivos de subpastas (mes/ano)
        for subpasta_info in estrutura['subpastas']:
            nome_subpasta = subpasta_info['nome']
            pasta_origem = Path(subpasta_info['pasta'])
            
            # Criar nome com prefixo
            if re.match(r'^[a-z]{3}\d{2}$', nome_subpasta.lower()):
                nome_com_prefixo = f"{nome_subpasta.lower()}{prefixo.lower()}"
            else:
                nome_com_prefixo = f"{nome_subpasta}_{prefixo}"
            
            pasta_destino_sub = pasta_loja_destino / nome_com_prefixo
            
            if not simular:
                pasta_destino_sub.mkdir(exist_ok=True)
            
            # Copiar arquivos
            arquivos = list(pasta_origem.rglob("*"))
            arquivos = [f for f in arquivos if f.is_file()]
            
            for arquivo in arquivos:
                if simular:
                    print(f"   📄 {arquivo.name} → {nome_com_prefixo}/")
                else:
                    try:
                        arquivo_destino = pasta_destino_sub / arquivo.name
                        shutil.copy2(arquivo, arquivo_destino)
                        print(f"   ✅ {arquivo.name} → {nome_com_prefixo}/")
                    except Exception as e:
                        print(f"   ❌ Erro ao copiar {arquivo.name}: {e}")
                
                arquivos_copiados += 1
        
        print(f"   📊 {'Simulados' if simular else 'Copiados'}: {arquivos_copiados} arquivos")
        return arquivos_copiados
    
    def gerar_relatorio_completo(self, estruturas):
        """Gera relatório completo da análise"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_relatorio = self.pasta_destino / f"RELATORIO_CAIXA_LOJAS_{timestamp}.xlsx"
        
        # Preparar dados para o relatório
        dados_resumo = []
        dados_detalhado = []
        
        total_geral_arquivos = 0
        
        for estrutura in estruturas:
            total_geral_arquivos += estrutura['total_arquivos']
            
            # Resumo por loja
            dados_resumo.append({
                'Loja': estrutura['loja'],
                'Total_Arquivos': estrutura['total_arquivos'],
                'Arquivos_Diretos': estrutura['arquivos_diretos'],
                'Subpastas': len(estrutura['subpastas']),
                'Padroes_MesAno': ', '.join(estrutura['padroes_encontrados']),
                'Prefixo_Sugerido': self.gerar_prefixo_loja(estrutura['loja'])
            })
            
            # Detalhes por subpasta
            for sub in estrutura['subpastas']:
                dados_detalhado.append({
                    'Loja': estrutura['loja'],
                    'Subpasta': sub['nome'],
                    'Arquivos': sub['arquivos'],
                    'Tipos_Arquivo': ', '.join([f"{k}({v})" for k, v in sub['tipos_arquivo'].items()]),
                    'Pasta_Completa': sub['pasta']
                })
        
        # Salvar relatório
        with pd.ExcelWriter(arquivo_relatorio, engine='openpyxl') as writer:
            # Resumo geral
            pd.DataFrame(dados_resumo).to_excel(writer, sheet_name='Resumo_Por_Loja', index=False)
            
            # Detalhes por subpasta
            pd.DataFrame(dados_detalhado).to_excel(writer, sheet_name='Detalhes_Subpastas', index=False)
            
            # Estatísticas gerais
            stats = {
                'Métrica': [
                    'Total de Lojas Analisadas',
                    'Total de Arquivos Encontrados',
                    'Data da Análise',
                    'Pasta Destino',
                    'Lojas Excluídas'
                ],
                'Valor': [
                    len(estruturas),
                    total_geral_arquivos,
                    timestamp,
                    str(self.pasta_destino),
                    ', '.join(self.lojas_excluidas)
                ]
            }
            pd.DataFrame(stats).to_excel(writer, sheet_name='Estatisticas_Gerais', index=False)
        
        print(f"\n💾 Relatório salvo: {arquivo_relatorio}")
        return arquivo_relatorio
    
    def executar_analise_completa(self, copiar_arquivos=False):
        """Executa análise completa de todas as lojas"""
        # 1. Mapear lojas
        lojas = self.mapear_lojas_disponiveis()
        
        if not lojas:
            print("❌ Nenhuma loja com pasta CAIXA encontrada!")
            return
        
        # 2. Analisar cada loja
        estruturas = []
        print("\n" + "=" * 80)
        print("ANÁLISE DETALHADA POR LOJA")
        print("=" * 80)
        
        for loja in lojas:
            estrutura = self.analisar_estrutura_caixa(loja)
            estruturas.append(estrutura)
        
        # 3. Gerar relatório
        print("\n" + "=" * 80)
        print("GERANDO RELATÓRIO")
        print("=" * 80)
        self.gerar_relatorio_completo(estruturas)
        
        # 4. Simular/Copiar arquivos
        print("\n" + "=" * 80)
        print("SIMULAÇÃO DE CÓPIA" if not copiar_arquivos else "COPIANDO ARQUIVOS")
        print("=" * 80)
        
        total_copiados = 0
        for estrutura in estruturas:
            copiados = self.copiar_arquivos_com_prefixo(estrutura, simular=not copiar_arquivos)
            total_copiados += copiados
        
        print(f"\n📊 RESUMO FINAL:")
        print(f"   • Lojas analisadas: {len(estruturas)}")
        print(f"   • Arquivos {'simulados' if not copiar_arquivos else 'copiados'}: {total_copiados:,}")
        print(f"   • Pasta destino: {self.pasta_destino}")
        
        if not copiar_arquivos:
            print(f"\n🔄 Para executar a cópia real, execute:")
            print(f"   analisador.executar_analise_completa(copiar_arquivos=True)")

def main():
    analisador = AnalisadorCaixaLojas()
    
    print("🎯 ANALISADOR DE ARQUIVOS DE CAIXA")
    print("   Mapeando lojas e estruturas de arquivos...")
    print()
    
    # Executar apenas simulação primeiro
    analisador.executar_analise_completa(copiar_arquivos=False)

if __name__ == "__main__":
    main()