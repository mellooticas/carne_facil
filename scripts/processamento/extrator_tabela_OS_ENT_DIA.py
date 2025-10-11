#!/usr/bin/env python3
"""
EXTRATOR ESPECÍFICO - TABELA OS_ENT_DIA (OS Entregues no Dia)
Extrai e padroniza dados da tabela de OS entregues diariamente
"""

import pandas as pd
from pathlib import Path
import openpyxl
from datetime import datetime
import re
from typing import Dict, List, Optional

class ExtratorTabelaOSENTDIA:
    def __init__(self):
        self.pasta_caixa = Path("data/caixa_lojas")
        self.arquivo_exemplo = self.pasta_caixa / "MAUA/2024_MAU/abr_24.xlsx"
        self.os_extraidas = []
        
        # Estrutura de colunas esperada para OS_ENT_DIA
        self.colunas_os_ent_dia = [
            'id_registro',
            'loja',
            'data_entrega',
            'dia',
            'mes_ano',
            'numero_os',
            'vendedor',
            'carne_entregue',
            'observacoes',
            'linha_bruta'
        ]
    
    def extrair_os_ent_dia_especifico(self, aba: str = "20"):
        """Extrai dados de OS_ENT_DIA de um dia específico"""
        print("=" * 80)
        print(f"📊 EXTRAÇÃO TABELA OS_ENT_DIA - DIA {aba}")
        print("=" * 80)
        
        if not self.arquivo_exemplo.exists():
            print(f"❌ Arquivo não encontrado: {self.arquivo_exemplo}")
            return []
        
        try:
            # Ler a aba específica
            df = pd.read_excel(self.arquivo_exemplo, sheet_name=aba, header=None)
            print(f"📏 Dimensões da página: {df.shape[0]} linhas × {df.shape[1]} colunas")
            
            # Encontrar seção de OS entregues no dia
            secao_os_ent_dia = self.identificar_secao_os_ent_dia(df)
            
            if not secao_os_ent_dia:
                print(f"❌ Seção OS_ENT_DIA não encontrada no dia {aba}")
                return []
            
            print(f"✅ Seção OS_ENT_DIA encontrada: linhas {secao_os_ent_dia['inicio']} a {secao_os_ent_dia['fim']}")
            
            # Extrair dados da seção
            os_dia = self.extrair_dados_os_ent_dia(secao_os_ent_dia['dados'], aba)
            
            print(f"📊 Total de OS extraídas: {len(os_dia)}")
            
            # Mostrar amostra
            self.mostrar_amostra_os(os_dia)
            
            return os_dia
            
        except Exception as e:
            print(f"❌ Erro ao extrair OS_ENT_DIA do dia {aba}: {e}")
            return []
    
    def identificar_secao_os_ent_dia(self, df: pd.DataFrame) -> Optional[Dict]:
        """Identifica a seção de OS entregues no dia no DataFrame"""
        for i, row in df.iterrows():
            linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
            linha_upper = linha_texto.upper()
            
            # Procurar por "OS Entregue no Dia"
            if 'OS ENTREGUE NO DIA' in linha_upper:
                # Encontrou cabeçalho, agora procurar fim da seção
                fim_secao = self.encontrar_fim_secao_os_ent_dia(df, i)
                
                return {
                    'inicio': i,
                    'fim': fim_secao,
                    'dados': df.iloc[i:fim_secao + 1],
                    'cabecalho': linha_texto
                }
        
        return None
    
    def encontrar_fim_secao_os_ent_dia(self, df: pd.DataFrame, inicio: int) -> int:
        """Encontra o fim da seção de OS entregues no dia"""
        # A seção de OS entregues geralmente é pequena
        for i in range(inicio + 1, len(df)):
            row = df.iloc[i]
            linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
            linha_upper = linha_texto.upper()
            
            # Parar se encontrar nova seção
            if any(indicador in linha_upper for indicador in [
                'ENTREGA DE CARNE', 'RECEBIMENTO', 'RESTANTE ENTRADA'
            ]):
                return i - 1
        
        return min(inicio + 5, len(df) - 1)
    
    def extrair_dados_os_ent_dia(self, dados: pd.DataFrame, dia: str) -> List[Dict]:
        """Extrai dados estruturados da seção de OS entregues no dia"""
        os_entregues = []
        
        # Analisar cada linha procurando OS válidas
        for i, row in dados.iterrows():
            # Converter linha para lista de valores não nulos
            valores = [cell for cell in row if pd.notna(cell)]
            
            if not valores:
                continue
            
            # Pular linha de cabeçalho
            linha_texto = " ".join([str(val) for val in valores])
            linha_upper = linha_texto.upper()
            
            # Pular cabeçalhos e totalizadores
            if any(keyword in linha_upper for keyword in [
                'OS ENTREGUE NO DIA', 'OS', 'VENDEDOR', 'CARNE', 'TOTAL'
            ]):
                continue
            
            # Procurar por número de OS (4 dígitos começando com 3 ou 4)
            numero_os = self.extrair_numero_os(valores)
            
            if numero_os:
                # Validar se é realmente uma linha de OS entregue
                if self.e_linha_os_valida(valores, linha_upper):
                    os_entregue = self.criar_registro_os(valores, numero_os, dia, i)
                    if os_entregue:
                        os_entregues.append(os_entregue)
                        print(f"   📝 OS extraída: {numero_os} - {os_entregue.get('vendedor', 'N/A')}")
        
        return os_entregues
    
    def extrair_numero_os(self, valores: List) -> Optional[str]:
        """Extrai número da OS da linha"""
        for val in valores:
            if isinstance(val, (int, float)) and not pd.isna(val):
                val_str = str(int(val))
                # Número de OS tem 4 dígitos e pode começar com 3 ou 4
                if len(val_str) == 4 and val_str[0] in ['3', '4']:
                    return val_str
            elif isinstance(val, str) and val.isdigit():
                if len(val) == 4 and val[0] in ['3', '4']:
                    return val
        return None
    
    def e_linha_os_valida(self, valores: List, linha_upper: str) -> bool:
        """Verifica se é uma linha de OS válida"""
        # Deve conter vendedor (geralmente BETH)
        tem_vendedor = any(
            isinstance(val, str) and val.upper() in ['BETH', 'CARLOS', 'MARIA']
            for val in valores
        )
        
        # Pode conter indicação de entrega (Sim/Não)
        tem_indicacao_entrega = any(
            isinstance(val, str) and val.upper() in ['SIM', 'NÃO', 'NAO']
            for val in valores
        )
        
        return tem_vendedor or tem_indicacao_entrega
    
    def criar_registro_os(self, valores: List, numero_os: str, dia: str, linha_idx: int) -> Optional[Dict]:
        """Cria registro estruturado de uma OS entregue"""
        try:
            # Mapear valores para campos
            os_entregue = {
                'id_registro': f"OS_ENT_DIA_MAU_2024_04_{dia}_{numero_os}",
                'loja': 'MAUA',
                'data_entrega': f"2024-04-{dia}",
                'dia': dia,
                'mes_ano': '2024_04',
                'numero_os': numero_os,
                'vendedor': self.extrair_vendedor(valores),
                'carne_entregue': self.extrair_status_entrega(valores),
                'observacoes': self.extrair_observacoes(valores),
                'linha_bruta': str(valores)
            }
            
            return os_entregue
            
        except Exception as e:
            print(f"   ❌ Erro ao criar registro da linha {linha_idx}: {e}")
            return None
    
    def extrair_vendedor(self, valores: List) -> str:
        """Extrai nome do vendedor"""
        vendedores_conhecidos = ['BETH', 'CARLOS', 'MARIA', 'JOSE']
        
        for val in valores:
            if isinstance(val, str):
                val_upper = val.upper().strip()
                if val_upper in vendedores_conhecidos:
                    return val_upper
        return ""
    
    def extrair_status_entrega(self, valores: List) -> str:
        """Extrai status da entrega (Sim/Não)"""
        for val in valores:
            if isinstance(val, str):
                val_upper = val.upper().strip()
                if val_upper in ['SIM', 'NÃO', 'NAO']:
                    return val_upper
        return ""
    
    def extrair_observacoes(self, valores: List) -> str:
        """Extrai observações adicionais"""
        obs = []
        
        for val in valores:
            if isinstance(val, str) and len(val.strip()) > 0:
                val_clean = val.strip()
                # Adicionar se não for campo já extraído
                if not any(keyword in val_clean.upper() for keyword in [
                    'OS', 'ENTREGUE', self.extrair_vendedor(valores),
                    'SIM', 'NAO', 'NÃO'
                ]):
                    obs.append(val_clean)
        
        return " | ".join(obs) if obs else ""
    
    def mostrar_amostra_os(self, os_entregues: List[Dict]):
        """Mostra amostra das OS extraídas"""
        if not os_entregues:
            print("📭 Nenhuma OS encontrada")
            return
        
        print(f"\n📊 AMOSTRA DAS OS EXTRAÍDAS:")
        print("-" * 80)
        
        for i, os_item in enumerate(os_entregues[:3], 1):
            print(f"{i}. OS {os_item['numero_os']}")
            print(f"   👨‍💼 Vendedor: {os_item['vendedor']}")
            print(f"   🥩 Carne entregue: {os_item['carne_entregue']}")
            if os_item['observacoes']:
                print(f"   📝 Observações: {os_item['observacoes']}")
            print()
    
    def testar_multiplos_dias(self, dias: List[str] = None):
        """Testa extração em múltiplos dias"""
        if dias is None:
            dias = ["01", "04", "15", "20", "30"]
        
        print("=" * 80)
        print("🧪 TESTE DE EXTRAÇÃO OS_ENT_DIA - MÚLTIPLOS DIAS")
        print("=" * 80)
        
        todas_os = []
        
        for dia in dias:
            print(f"\n📅 Testando dia {dia}...")
            os_dia = self.extrair_os_ent_dia_especifico(dia)
            todas_os.extend(os_dia)
            
            if os_dia:
                print(f"   ✅ {len(os_dia)} OS extraídas")
            else:
                print(f"   ⚠️  Nenhuma OS encontrada")
        
        # Relatório final
        self.gerar_relatorio_os_ent_dia(todas_os)
        
        return todas_os
    
    def gerar_relatorio_os_ent_dia(self, os_entregues: List[Dict]):
        """Gera relatório das OS extraídas"""
        if not os_entregues:
            print("\n❌ Nenhuma OS para gerar relatório")
            return
        
        print(f"\n" + "=" * 60)
        print(f"📈 RELATÓRIO FINAL - TABELA OS_ENT_DIA")
        print("=" * 60)
        
        print(f"📊 Total de OS entregues: {len(os_entregues)}")
        
        # Status de entrega
        status_entrega = {}
        for os_item in os_entregues:
            status = os_item['carne_entregue'] or 'Não informado'
            status_entrega[status] = status_entrega.get(status, 0) + 1
        
        print(f"\n🥩 Status de entrega:")
        for status, count in status_entrega.items():
            print(f"   {status}: {count} OS")
        
        # Vendedores
        vendedores = {}
        for os_item in os_entregues:
            vendedor = os_item['vendedor'] or 'Não informado'
            vendedores[vendedor] = vendedores.get(vendedor, 0) + 1
        
        print(f"\n👨‍💼 Vendedores:")
        for vendedor, count in vendedores.items():
            print(f"   {vendedor}: {count} OS")
        
        # Salvar dados
        self.salvar_os_extraidas(os_entregues)
    
    def salvar_os_extraidas(self, os_entregues: List[Dict]):
        """Salva OS extraídas em arquivo Excel"""
        if not os_entregues:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_saida = self.pasta_caixa / f"TABELA_OS_ENT_DIA_EXTRAIDA_{timestamp}.xlsx"
        
        try:
            df_os = pd.DataFrame(os_entregues)
            df_os.to_excel(arquivo_saida, index=False, sheet_name='OS_ENT_DIA')
            
            print(f"\n💾 Dados salvos: {arquivo_saida}")
            print(f"📊 {len(os_entregues)} registros de OS salvos")
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")

if __name__ == "__main__":
    extrator = ExtratorTabelaOSENTDIA()
    
    print("🚀 INICIANDO EXTRAÇÃO ESPECÍFICA - TABELA OS_ENT_DIA")
    
    # Testar em múltiplos dias
    os_entregues = extrator.testar_multiplos_dias()
    
    print("\n" + "=" * 80)
    print("✅ EXTRAÇÃO OS_ENT_DIA CONCLUÍDA")
    print("=" * 80)
    print("\n🎉 TODAS AS 5 TABELAS IMPLEMENTADAS!")
    print("🎯 PRÓXIMO PASSO: Consolidar todos os extratores")