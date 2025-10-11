#!/usr/bin/env python3
"""
EXTRATOR ESPECÍFICO - TABELA ENTR_CARN (Entrega de Carnê)
Extrai e padroniza dados da tabela de entregas de carnê
"""

import pandas as pd
from pathlib import Path
import openpyxl
from datetime import datetime
import re
from typing import Dict, List, Optional

class ExtratorTabelaENTRCARN:
    def __init__(self):
        self.pasta_caixa = Path("data/caixa_lojas")
        self.arquivo_exemplo = self.pasta_caixa / "MAUA/2024_MAU/abr_24.xlsx"
        self.entregas_extraidas = []
        
        # Estrutura de colunas esperada para ENTR_CARN
        self.colunas_entr_carn = [
            'id_registro',
            'loja',
            'data_entrega',
            'dia',
            'mes_ano',
            'numero_os',
            'vendedor',
            'carne_entregue',
            'numero_parcelas',
            'valor_total',
            'observacoes',
            'linha_bruta'
        ]
    
    def extrair_entr_carn_dia_especifico(self, aba: str = "20"):
        """Extrai dados de ENTR_CARN de um dia específico"""
        print("=" * 80)
        print(f"📊 EXTRAÇÃO TABELA ENTR_CARN - DIA {aba}")
        print("=" * 80)
        
        if not self.arquivo_exemplo.exists():
            print(f"❌ Arquivo não encontrado: {self.arquivo_exemplo}")
            return []
        
        try:
            # Ler a aba específica
            df = pd.read_excel(self.arquivo_exemplo, sheet_name=aba, header=None)
            print(f"📏 Dimensões da página: {df.shape[0]} linhas × {df.shape[1]} colunas")
            
            # Encontrar seção de entrega de carnê
            secao_entr_carn = self.identificar_secao_entr_carn(df)
            
            if not secao_entr_carn:
                print(f"❌ Seção ENTR_CARN não encontrada no dia {aba}")
                return []
            
            print(f"✅ Seção ENTR_CARN encontrada: linhas {secao_entr_carn['inicio']} a {secao_entr_carn['fim']}")
            
            # Extrair dados da seção
            entregas_dia = self.extrair_dados_entr_carn(secao_entr_carn['dados'], aba)
            
            print(f"📊 Total de entregas extraídas: {len(entregas_dia)}")
            
            # Mostrar amostra
            self.mostrar_amostra_entregas(entregas_dia)
            
            return entregas_dia
            
        except Exception as e:
            print(f"❌ Erro ao extrair ENTR_CARN do dia {aba}: {e}")
            return []
    
    def identificar_secao_entr_carn(self, df: pd.DataFrame) -> Optional[Dict]:
        """Identifica a seção de entrega de carnê no DataFrame"""
        for i, row in df.iterrows():
            linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
            linha_upper = linha_texto.upper()
            
            # Procurar por "Entrega de Carne" mas NÃO "Recebimento"
            if 'ENTREGA DE CARNE' in linha_upper and 'RECEBIMENTO' not in linha_upper:
                # Encontrou cabeçalho, agora procurar fim da seção
                fim_secao = self.encontrar_fim_secao_entr_carn(df, i)
                
                return {
                    'inicio': i,
                    'fim': fim_secao,
                    'dados': df.iloc[i:fim_secao + 1],
                    'cabecalho': linha_texto
                }
        
        return None
    
    def encontrar_fim_secao_entr_carn(self, df: pd.DataFrame, inicio: int) -> int:
        """Encontra o fim da seção de entrega de carnê"""
        # A seção de entrega geralmente vai até encontrar nova seção ou final
        for i in range(inicio + 1, len(df)):
            row = df.iloc[i]
            linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
            linha_upper = linha_texto.upper()
            
            # Parar se encontrar nova seção
            if any(indicador in linha_upper for indicador in [
                'RECEBIMENTO', 'OS ENTREGUE NO DIA', 'TOTAL DE OS'
            ]):
                return i - 1
        
        return min(inicio + 7, len(df) - 1)
    
    def extrair_dados_entr_carn(self, dados: pd.DataFrame, dia: str) -> List[Dict]:
        """Extrai dados estruturados da seção de entrega de carnê"""
        entregas = []
        
        # Analisar cada linha procurando entregas válidas
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
                'ENTREGA DE CARNE', 'OS', 'PARCELAS', 'VALOR TOTAL', 'TOTAL'
            ]):
                continue
            
            # Procurar por número de OS (4 dígitos começando com 3 ou 4)
            numero_os = self.extrair_numero_os(valores)
            
            if numero_os:
                # Validar se é realmente uma linha de entrega
                if self.e_linha_entrega_valida(valores, linha_upper):
                    entrega = self.criar_registro_entrega(valores, numero_os, dia, i)
                    if entrega:
                        entregas.append(entrega)
                        print(f"   📝 Entrega extraída: OS {numero_os} - {entrega.get('vendedor', 'N/A')}")
        
        return entregas
    
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
    
    def e_linha_entrega_valida(self, valores: List, linha_upper: str) -> bool:
        """Verifica se é uma linha de entrega válida"""
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
        
        return tem_vendedor
    
    def criar_registro_entrega(self, valores: List, numero_os: str, dia: str, linha_idx: int) -> Optional[Dict]:
        """Cria registro estruturado de uma entrega"""
        try:
            # Mapear valores para campos
            entrega = {
                'id_registro': f"ENTR_CARN_MAU_2024_04_{dia}_{numero_os}",
                'loja': 'MAUA',
                'data_entrega': f"2024-04-{dia}",
                'dia': dia,
                'mes_ano': '2024_04',
                'numero_os': numero_os,
                'vendedor': self.extrair_vendedor(valores),
                'carne_entregue': self.extrair_status_entrega(valores),
                'numero_parcelas': self.extrair_numero_parcelas(valores),
                'valor_total': self.extrair_valor_total(valores),
                'observacoes': self.extrair_observacoes(valores),
                'linha_bruta': str(valores)
            }
            
            return entrega
            
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
    
    def extrair_numero_parcelas(self, valores: List) -> int:
        """Extrai número de parcelas"""
        for val in valores:
            if isinstance(val, (int, float)) and not pd.isna(val):
                # Números pequenos podem ser parcelas
                if 1 <= int(val) <= 12:
                    return int(val)
        return 0
    
    def extrair_valor_total(self, valores: List) -> float:
        """Extrai valor total"""
        valores_numericos = []
        
        for val in valores:
            if isinstance(val, (int, float)) and not pd.isna(val) and val > 0:
                # Ignorar números que parecem ser códigos
                if val >= 100 and val < 10000:
                    valores_numericos.append(float(val))
        
        # Geralmente o maior valor é o valor total
        if valores_numericos:
            return max(valores_numericos)
        return 0.0
    
    def extrair_observacoes(self, valores: List) -> str:
        """Extrai observações adicionais"""
        obs = []
        
        for val in valores:
            if isinstance(val, str) and len(val.strip()) > 0:
                val_clean = val.strip()
                # Adicionar se não for campo já extraído
                if not any(keyword in val_clean.upper() for keyword in [
                    'ENTREGA', 'CARNE', self.extrair_vendedor(valores),
                    'SIM', 'NAO', 'NÃO'
                ]):
                    obs.append(val_clean)
        
        return " | ".join(obs) if obs else ""
    
    def mostrar_amostra_entregas(self, entregas: List[Dict]):
        """Mostra amostra das entregas extraídas"""
        if not entregas:
            print("📭 Nenhuma entrega encontrada")
            return
        
        print(f"\n📊 AMOSTRA DAS ENTREGAS EXTRAÍDAS:")
        print("-" * 80)
        
        for i, entrega in enumerate(entregas[:3], 1):
            print(f"{i}. Entrega OS {entrega['numero_os']}")
            print(f"   👨‍💼 Vendedor: {entrega['vendedor']}")
            print(f"   🥩 Carne entregue: {entrega['carne_entregue']}")
            print(f"   📋 Parcelas: {entrega['numero_parcelas']}")
            print(f"   💰 Valor total: R$ {entrega['valor_total']:.2f}")
            print()
    
    def testar_multiplos_dias(self, dias: List[str] = None):
        """Testa extração em múltiplos dias"""
        if dias is None:
            dias = ["01", "04", "15", "20", "30"]
        
        print("=" * 80)
        print("🧪 TESTE DE EXTRAÇÃO ENTR_CARN - MÚLTIPLOS DIAS")
        print("=" * 80)
        
        todas_entregas = []
        
        for dia in dias:
            print(f"\n📅 Testando dia {dia}...")
            entregas_dia = self.extrair_entr_carn_dia_especifico(dia)
            todas_entregas.extend(entregas_dia)
            
            if entregas_dia:
                print(f"   ✅ {len(entregas_dia)} entregas extraídas")
            else:
                print(f"   ⚠️  Nenhuma entrega encontrada")
        
        # Relatório final
        self.gerar_relatorio_entr_carn(todas_entregas)
        
        return todas_entregas
    
    def gerar_relatorio_entr_carn(self, entregas: List[Dict]):
        """Gera relatório das entregas extraídas"""
        if not entregas:
            print("\n❌ Nenhuma entrega para gerar relatório")
            return
        
        print(f"\n" + "=" * 60)
        print(f"📈 RELATÓRIO FINAL - TABELA ENTR_CARN")
        print("=" * 60)
        
        print(f"📊 Total de entregas: {len(entregas)}")
        
        # Estatísticas
        valores_total = [e['valor_total'] for e in entregas if e['valor_total'] > 0]
        if valores_total:
            print(f"💰 Valor total entregas: R$ {sum(valores_total):.2f}")
            print(f"💰 Valor médio: R$ {sum(valores_total) / len(valores_total):.2f}")
            print(f"💰 Maior valor: R$ {max(valores_total):.2f}")
            print(f"💰 Menor valor: R$ {min(valores_total):.2f}")
        
        # Status de entrega
        status_entrega = {}
        for entrega in entregas:
            status = entrega['carne_entregue'] or 'Não informado'
            status_entrega[status] = status_entrega.get(status, 0) + 1
        
        print(f"\n🥩 Status de entrega:")
        for status, count in status_entrega.items():
            print(f"   {status}: {count} entregas")
        
        # Vendedores
        vendedores = {}
        for entrega in entregas:
            vendedor = entrega['vendedor'] or 'Não informado'
            vendedores[vendedor] = vendedores.get(vendedor, 0) + 1
        
        print(f"\n👨‍💼 Vendedores:")
        for vendedor, count in vendedores.items():
            print(f"   {vendedor}: {count} entregas")
        
        # Salvar dados
        self.salvar_entregas_extraidas(entregas)
    
    def salvar_entregas_extraidas(self, entregas: List[Dict]):
        """Salva entregas extraídas em arquivo Excel"""
        if not entregas:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_saida = self.pasta_caixa / f"TABELA_ENTR_CARN_EXTRAIDA_{timestamp}.xlsx"
        
        try:
            df_entregas = pd.DataFrame(entregas)
            df_entregas.to_excel(arquivo_saida, index=False, sheet_name='Entregas_ENTR_CARN')
            
            print(f"\n💾 Dados salvos: {arquivo_saida}")
            print(f"📊 {len(entregas)} registros de entregas salvos")
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")

if __name__ == "__main__":
    extrator = ExtratorTabelaENTRCARN()
    
    print("🚀 INICIANDO EXTRAÇÃO ESPECÍFICA - TABELA ENTR_CARN")
    
    # Testar em múltiplos dias
    entregas = extrator.testar_multiplos_dias()
    
    print("\n" + "=" * 80)
    print("✅ EXTRAÇÃO ENTR_CARN CONCLUÍDA")
    print("=" * 80)
    print("\n🎯 ÚLTIMA TABELA: OS_ENT_DIA (OS entregues no dia)")