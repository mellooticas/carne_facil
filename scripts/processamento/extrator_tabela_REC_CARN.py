#!/usr/bin/env python3
"""
EXTRATOR ESPECÍFICO - TABELA REC_CARN (Recebimento de Carnê)
Extrai e padroniza dados da tabela de recebimentos de carnê
"""

import pandas as pd
from pathlib import Path
import openpyxl
from datetime import datetime
import re
from typing import Dict, List, Optional

class ExtratorTabelaRECCARN:
    def __init__(self):
        self.pasta_caixa = Path("data/caixa_lojas")
        self.arquivo_exemplo = self.pasta_caixa / "MAUA/2024_MAU/abr_24.xlsx"
        self.recebimentos_extraidos = []
        
        # Estrutura de colunas esperada para REC_CARN
        self.colunas_rec_carn = [
            'id_registro',
            'loja',
            'data_recebimento',
            'dia',
            'mes_ano',
            'numero_os',
            'cliente',
            'forma_pagamento',
            'valor_parcela',
            'numero_parcela',
            'descricao_parcela',
            'observacoes',
            'linha_bruta'
        ]
    
    def extrair_rec_carn_dia_especifico(self, aba: str = "15"):
        """Extrai dados de REC_CARN de um dia específico"""
        print("=" * 80)
        print(f"📊 EXTRAÇÃO TABELA REC_CARN - DIA {aba}")
        print("=" * 80)
        
        if not self.arquivo_exemplo.exists():
            print(f"❌ Arquivo não encontrado: {self.arquivo_exemplo}")
            return []
        
        try:
            # Ler a aba específica
            df = pd.read_excel(self.arquivo_exemplo, sheet_name=aba, header=None)
            print(f"📏 Dimensões da página: {df.shape[0]} linhas × {df.shape[1]} colunas")
            
            # Encontrar seção de recebimento de carnê
            secao_rec_carn = self.identificar_secao_rec_carn(df)
            
            if not secao_rec_carn:
                print(f"❌ Seção REC_CARN não encontrada no dia {aba}")
                return []
            
            print(f"✅ Seção REC_CARN encontrada: linhas {secao_rec_carn['inicio']} a {secao_rec_carn['fim']}")
            
            # Extrair dados da seção
            recebimentos_dia = self.extrair_dados_rec_carn(secao_rec_carn['dados'], aba)
            
            print(f"📊 Total de recebimentos extraídos: {len(recebimentos_dia)}")
            
            # Mostrar amostra
            self.mostrar_amostra_recebimentos(recebimentos_dia)
            
            return recebimentos_dia
            
        except Exception as e:
            print(f"❌ Erro ao extrair REC_CARN do dia {aba}: {e}")
            return []
    
    def identificar_secao_rec_carn(self, df: pd.DataFrame) -> Optional[Dict]:
        """Identifica a seção de recebimento de carnê no DataFrame"""
        for i, row in df.iterrows():
            linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
            linha_upper = linha_texto.upper()
            
            # Procurar por "Recebimento de Carnê"
            if 'RECEBIMENTO DE CARNÊ' in linha_upper or 'RECEBIMENTO DE CARNE' in linha_upper:
                # Encontrou cabeçalho, agora procurar fim da seção
                fim_secao = self.encontrar_fim_secao_rec_carn(df, i)
                
                return {
                    'inicio': i,
                    'fim': fim_secao,
                    'dados': df.iloc[i:fim_secao + 1],
                    'cabecalho': linha_texto
                }
        
        return None
    
    def encontrar_fim_secao_rec_carn(self, df: pd.DataFrame, inicio: int) -> int:
        """Encontra o fim da seção de recebimento de carnê"""
        # A seção de recebimento geralmente vai até o final dos dados ou próxima seção
        return min(inicio + 8, len(df) - 1)
    
    def extrair_dados_rec_carn(self, dados: pd.DataFrame, dia: str) -> List[Dict]:
        """Extrai dados estruturados da seção de recebimento de carnê"""
        recebimentos = []
        
        # Analisar cada linha procurando recebimentos válidos
        for i, row in dados.iterrows():
            # Converter linha para lista de valores não nulos
            valores = [cell for cell in row if pd.notna(cell)]
            
            if not valores:
                continue
            
            # Pular linha de cabeçalho
            linha_texto = " ".join([str(val) for val in valores])
            linha_upper = linha_texto.upper()
            
            # Pular cabeçalhos
            if any(keyword in linha_upper for keyword in [
                'RECEBIMENTO DE CARNÊ', 'ENTREGA DE CARNE', 'OS', 'CLIENTE', 
                'FORMA DE PGTO', 'VALOR PARCELA', 'TOTAL DE OS'
            ]):
                continue
            
            # Procurar por número de OS (4 dígitos começando com 3 ou 4)
            numero_os = self.extrair_numero_os(valores)
            
            if numero_os:
                # Validar se é realmente uma linha de recebimento
                if self.e_linha_recebimento_valida(valores, linha_upper):
                    recebimento = self.criar_registro_recebimento(valores, numero_os, dia, i)
                    if recebimento:
                        recebimentos.append(recebimento)
                        print(f"   📝 Recebimento extraído: OS {numero_os} - {recebimento.get('cliente', 'N/A')}")
        
        return recebimentos
    
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
    
    def e_linha_recebimento_valida(self, valores: List, linha_upper: str) -> bool:
        """Verifica se é uma linha de recebimento válida"""
        # Deve conter nome de cliente (string longa)
        tem_nome_cliente = any(
            isinstance(val, str) and len(val) > 5 and 
            not any(kw in val.upper() for kw in ['RECEBIMENTO', 'OS', 'PARCELA', 'TOTAL'])
            for val in valores
        )
        
        # Pode conter indicação de parcela
        tem_parcela = any(
            isinstance(val, str) and 'PARC' in val.upper()
            for val in valores
        )
        
        return tem_nome_cliente
    
    def criar_registro_recebimento(self, valores: List, numero_os: str, dia: str, linha_idx: int) -> Optional[Dict]:
        """Cria registro estruturado de um recebimento"""
        try:
            # Mapear valores para campos
            recebimento = {
                'id_registro': f"REC_CARN_MAU_2024_04_{dia}_{numero_os}",
                'loja': 'MAUA',
                'data_recebimento': f"2024-04-{dia}",
                'dia': dia,
                'mes_ano': '2024_04',
                'numero_os': numero_os,
                'cliente': self.extrair_cliente(valores),
                'forma_pagamento': self.extrair_forma_pagamento(valores),
                'valor_parcela': self.extrair_valor_parcela(valores),
                'numero_parcela': self.extrair_numero_parcela(valores),
                'descricao_parcela': self.extrair_descricao_parcela(valores),
                'observacoes': self.extrair_observacoes(valores),
                'linha_bruta': str(valores)
            }
            
            return recebimento
            
        except Exception as e:
            print(f"   ❌ Erro ao criar registro da linha {linha_idx}: {e}")
            return None
    
    def extrair_cliente(self, valores: List) -> str:
        """Extrai nome do cliente"""
        for val in valores:
            if isinstance(val, str) and len(val) > 5:
                # Nome de cliente geralmente é texto longo sem palavras-chave
                val_upper = val.upper()
                if not any(keyword in val_upper for keyword in [
                    'RECEBIMENTO', 'OS', 'FORMA', 'PGTO', 'VALOR', 'PARC', 'CTD', 'CTC', 'PIX', 'DN'
                ]):
                    return val.strip()
        return ""
    
    def extrair_forma_pagamento(self, valores: List) -> str:
        """Extrai forma de pagamento"""
        formas_conhecidas = ['DN', 'CTD', 'CTC', 'PIX', 'SS', 'GARANTIA']
        
        for val in valores:
            if isinstance(val, str):
                val_upper = val.upper().strip()
                if val_upper in formas_conhecidas:
                    return val_upper
        return ""
    
    def extrair_valor_parcela(self, valores: List) -> float:
        """Extrai valor da parcela"""
        valores_numericos = []
        
        for val in valores:
            if isinstance(val, (int, float)) and not pd.isna(val) and val > 0:
                # Ignorar números que parecem ser códigos ou anos
                if val < 2000 and val != int(val) or (val >= 50 and val < 5000):
                    valores_numericos.append(float(val))
        
        # Geralmente há um valor claro da parcela
        if valores_numericos:
            # Pegar um valor que não seja número de OS
            for val in valores_numericos:
                if not (len(str(int(val))) == 4 and str(int(val))[0] in ['3', '4']):
                    return val
            return valores_numericos[0]
        return 0.0
    
    def extrair_numero_parcela(self, valores: List) -> str:
        """Extrai número/descrição da parcela"""
        for val in valores:
            if isinstance(val, str) and 'PARC' in val.upper():
                return val.strip()
        return ""
    
    def extrair_descricao_parcela(self, valores: List) -> str:
        """Extrai descrição da parcela"""
        return self.extrair_numero_parcela(valores)
    
    def extrair_observacoes(self, valores: List) -> str:
        """Extrai observações adicionais"""
        obs = []
        
        for val in valores:
            if isinstance(val, str) and len(val.strip()) > 0:
                val_clean = val.strip()
                # Adicionar se não for campo já extraído
                if not any(keyword in val_clean.upper() for keyword in [
                    'RECEBIMENTO', 'OS', self.extrair_cliente(valores).upper(),
                    self.extrair_forma_pagamento(valores), 'PARC'
                ]):
                    obs.append(val_clean)
        
        return " | ".join(obs) if obs else ""
    
    def mostrar_amostra_recebimentos(self, recebimentos: List[Dict]):
        """Mostra amostra dos recebimentos extraídos"""
        if not recebimentos:
            print("📭 Nenhum recebimento encontrado")
            return
        
        print(f"\n📊 AMOSTRA DOS RECEBIMENTOS EXTRAÍDOS:")
        print("-" * 80)
        
        for i, recebimento in enumerate(recebimentos[:3], 1):
            print(f"{i}. Recebimento OS {recebimento['numero_os']}")
            print(f"   👤 Cliente: {recebimento['cliente']}")
            print(f"   💳 Pagamento: {recebimento['forma_pagamento']}")
            print(f"   💰 Valor parcela: R$ {recebimento['valor_parcela']:.2f}")
            print(f"   📋 Parcela: {recebimento['descricao_parcela']}")
            print()
    
    def testar_multiplos_dias(self, dias: List[str] = None):
        """Testa extração em múltiplos dias"""
        if dias is None:
            dias = ["01", "04", "15", "20", "30"]
        
        print("=" * 80)
        print("🧪 TESTE DE EXTRAÇÃO REC_CARN - MÚLTIPLOS DIAS")
        print("=" * 80)
        
        todos_recebimentos = []
        
        for dia in dias:
            print(f"\n📅 Testando dia {dia}...")
            recebimentos_dia = self.extrair_rec_carn_dia_especifico(dia)
            todos_recebimentos.extend(recebimentos_dia)
            
            if recebimentos_dia:
                print(f"   ✅ {len(recebimentos_dia)} recebimentos extraídos")
            else:
                print(f"   ⚠️  Nenhum recebimento encontrado")
        
        # Relatório final
        self.gerar_relatorio_rec_carn(todos_recebimentos)
        
        return todos_recebimentos
    
    def gerar_relatorio_rec_carn(self, recebimentos: List[Dict]):
        """Gera relatório dos recebimentos extraídos"""
        if not recebimentos:
            print("\n❌ Nenhum recebimento para gerar relatório")
            return
        
        print(f"\n" + "=" * 60)
        print(f"📈 RELATÓRIO FINAL - TABELA REC_CARN")
        print("=" * 60)
        
        print(f"📊 Total de recebimentos: {len(recebimentos)}")
        
        # Estatísticas
        valores_parcela = [r['valor_parcela'] for r in recebimentos if r['valor_parcela'] > 0]
        if valores_parcela:
            print(f"💰 Total recebido: R$ {sum(valores_parcela):.2f}")
            print(f"💰 Valor médio: R$ {sum(valores_parcela) / len(valores_parcela):.2f}")
            print(f"💰 Maior parcela: R$ {max(valores_parcela):.2f}")
            print(f"💰 Menor parcela: R$ {min(valores_parcela):.2f}")
        
        # Formas de pagamento
        formas_pagto = {}
        for recebimento in recebimentos:
            forma = recebimento['forma_pagamento'] or 'Não informado'
            formas_pagto[forma] = formas_pagto.get(forma, 0) + 1
        
        print(f"\n💳 Formas de pagamento:")
        for forma, count in formas_pagto.items():
            print(f"   {forma}: {count} recebimentos")
        
        # Salvar dados
        self.salvar_recebimentos_extraidos(recebimentos)
    
    def salvar_recebimentos_extraidos(self, recebimentos: List[Dict]):
        """Salva recebimentos extraídos em arquivo Excel"""
        if not recebimentos:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_saida = self.pasta_caixa / f"TABELA_REC_CARN_EXTRAIDA_{timestamp}.xlsx"
        
        try:
            df_recebimentos = pd.DataFrame(recebimentos)
            df_recebimentos.to_excel(arquivo_saida, index=False, sheet_name='Recebimentos_REC_CARN')
            
            print(f"\n💾 Dados salvos: {arquivo_saida}")
            print(f"📊 {len(recebimentos)} registros de recebimentos salvos")
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")

if __name__ == "__main__":
    extrator = ExtratorTabelaRECCARN()
    
    print("🚀 INICIANDO EXTRAÇÃO ESPECÍFICA - TABELA REC_CARN")
    
    # Testar em múltiplos dias
    recebimentos = extrator.testar_multiplos_dias()
    
    print("\n" + "=" * 80)
    print("✅ EXTRAÇÃO REC_CARN CONCLUÍDA")
    print("=" * 80)
    print("\n🎯 PRÓXIMA TABELA: ENTR_CARN (Entrega de carnê)")