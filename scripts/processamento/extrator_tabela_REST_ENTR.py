#!/usr/bin/env python3
"""
EXTRATOR ESPECÍFICO - TABELA REST_ENTR (Restantes de Entrada/Sinal)
Extrai e padroniza dados da tabela de restantes de entrada diários
"""

import pandas as pd
from pathlib import Path
import openpyxl
from datetime import datetime
import re
from typing import Dict, List, Optional

class ExtratorTabelaRESTENTR:
    def __init__(self):
        self.pasta_caixa = Path("data/caixa_lojas")
        self.arquivo_exemplo = self.pasta_caixa / "MAUA/2024_MAU/abr_24.xlsx"
        self.restantes_extraidos = []
        
        # Estrutura de colunas esperada para REST_ENTR
        self.colunas_rest_entr = [
            'id_registro',
            'loja',
            'data_restante',
            'dia',
            'mes_ano',
            'numero_venda',
            'cliente',
            'forma_pagamento',
            'valor_venda',
            'valor_entrada',
            'valor_restante',
            'observacoes',
            'linha_bruta'
        ]
    
    def extrair_rest_entr_dia_especifico(self, aba: str = "04"):
        """Extrai dados de REST_ENTR de um dia específico"""
        print("=" * 80)
        print(f"📊 EXTRAÇÃO TABELA REST_ENTR - DIA {aba}")
        print("=" * 80)
        
        if not self.arquivo_exemplo.exists():
            print(f"❌ Arquivo não encontrado: {self.arquivo_exemplo}")
            return []
        
        try:
            # Ler a aba específica
            df = pd.read_excel(self.arquivo_exemplo, sheet_name=aba, header=None)
            print(f"📏 Dimensões da página: {df.shape[0]} linhas × {df.shape[1]} colunas")
            
            # Encontrar seção de restantes de entrada
            secao_rest_entr = self.identificar_secao_rest_entr(df)
            
            if not secao_rest_entr:
                print(f"❌ Seção REST_ENTR não encontrada no dia {aba}")
                return []
            
            print(f"✅ Seção REST_ENTR encontrada: linhas {secao_rest_entr['inicio']} a {secao_rest_entr['fim']}")
            
            # Extrair dados da seção
            restantes_dia = self.extrair_dados_rest_entr(secao_rest_entr['dados'], aba)
            
            print(f"📊 Total de restantes extraídos: {len(restantes_dia)}")
            
            # Mostrar amostra
            self.mostrar_amostra_restantes(restantes_dia)
            
            return restantes_dia
            
        except Exception as e:
            print(f"❌ Erro ao extrair REST_ENTR do dia {aba}: {e}")
            return []
    
    def identificar_secao_rest_entr(self, df: pd.DataFrame) -> Optional[Dict]:
        """Identifica a seção de restantes de entrada no DataFrame"""
        for i, row in df.iterrows():
            linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
            linha_upper = linha_texto.upper()
            
            # Procurar especificamente por "Restante Entrada"
            if 'RESTANTE ENTRADA' in linha_upper:
                # Encontrou cabeçalho, agora procurar fim da seção
                fim_secao = self.encontrar_fim_secao_rest_entr(df, i)
                
                return {
                    'inicio': i,
                    'fim': fim_secao,
                    'dados': df.iloc[i:fim_secao + 1],
                    'cabecalho': linha_texto
                }
        
        return None
    
    def encontrar_fim_secao_rest_entr(self, df: pd.DataFrame, inicio: int) -> int:
        """Encontra o fim da seção de restantes de entrada"""
        for i in range(inicio + 1, len(df)):
            row = df.iloc[i]
            linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
            linha_upper = linha_texto.upper()
            
            # Parar se encontrar próxima seção
            if any(indicador in linha_upper for indicador in [
                'RECEBIMENTO DE CARNÊ', 'ENTREGA DE CARNE', 'OS ENTREGUE'
            ]):
                return i - 1
        
        # Se não encontrar fim específico, processar até 10 linhas após início
        return min(inicio + 10, len(df) - 1)
    
    def extrair_dados_rest_entr(self, dados: pd.DataFrame, dia: str) -> List[Dict]:
        """Extrai dados estruturados da seção de restantes de entrada"""
        restantes = []
        
        # Analisar cada linha procurando restantes válidos
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
                'RESTANTE ENTRADA', 'Nº VENDA', 'CLIENTE', 'FORMA DE PGTO'
            ]):
                continue
            
            # Procurar por número de venda (4 dígitos começando com 4)
            numero_venda = self.extrair_numero_venda(valores)
            
            if numero_venda:
                # Validar se é realmente uma linha de restante
                if self.e_linha_restante_valida(valores, linha_upper):
                    restante = self.criar_registro_restante(valores, numero_venda, dia, i)
                    if restante:
                        restantes.append(restante)
                        print(f"   📝 Restante extraído: {numero_venda} - {restante.get('cliente', 'N/A')}")
        
        return restantes
    
    def extrair_numero_venda(self, valores: List) -> Optional[str]:
        """Extrai número da venda da linha"""
        for val in valores:
            if isinstance(val, (int, float)) and not pd.isna(val):
                val_str = str(int(val))
                # Número de venda tem 4 dígitos e começa com 4
                if len(val_str) == 4 and val_str.startswith('4'):
                    return val_str
            elif isinstance(val, str) and val.isdigit():
                if len(val) == 4 and val.startswith('4'):
                    return val
        return None
    
    def e_linha_restante_valida(self, valores: List, linha_upper: str) -> bool:
        """Verifica se é uma linha de restante válida"""
        # Deve conter nome de cliente (string longa)
        tem_nome_cliente = any(
            isinstance(val, str) and len(val) > 5 and 
            not any(kw in val.upper() for kw in ['RESTANTE', 'ENTRADA', 'TOTAL'])
            for val in valores
        )
        
        # Pode conter forma de pagamento
        formas_conhecidas = ['DN', 'CTD', 'CTC', 'PIX', 'SS', 'GARANTIA']
        tem_forma_pagto = any(
            isinstance(val, str) and val.upper().strip() in formas_conhecidas
            for val in valores
        )
        
        return tem_nome_cliente
    
    def criar_registro_restante(self, valores: List, numero_venda: str, dia: str, linha_idx: int) -> Optional[Dict]:
        """Cria registro estruturado de um restante"""
        try:
            # Mapear valores para campos
            restante = {
                'id_registro': f"REST_ENTR_MAU_2024_04_{dia}_{numero_venda}",
                'loja': 'MAUA',
                'data_restante': f"2024-04-{dia}",
                'dia': dia,
                'mes_ano': '2024_04',
                'numero_venda': numero_venda,
                'cliente': self.extrair_cliente(valores),
                'forma_pagamento': self.extrair_forma_pagamento(valores),
                'valor_venda': self.extrair_valor_venda(valores),
                'valor_entrada': self.extrair_valor_entrada(valores),
                'valor_restante': self.extrair_valor_restante(valores),
                'observacoes': self.extrair_observacoes(valores),
                'linha_bruta': str(valores)
            }
            
            return restante
            
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
                    'RESTANTE', 'ENTRADA', 'FORMA', 'PGTO', 'VALOR', 'CTD', 'CTC', 'PIX', 'DN'
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
    
    def extrair_valor_venda(self, valores: List) -> float:
        """Extrai valor da venda"""
        valores_numericos = []
        
        for val in valores:
            if isinstance(val, (int, float)) and not pd.isna(val) and val > 0:
                # Ignorar números que parecem ser anos, dias ou códigos
                if val < 2000 and val != int(val) or val >= 100:
                    valores_numericos.append(float(val))
        
        # Geralmente o maior valor é o valor da venda
        if valores_numericos:
            return max(valores_numericos)
        return 0.0
    
    def extrair_valor_entrada(self, valores: List) -> float:
        """Extrai valor de entrada já pago"""
        valores_numericos = []
        
        for val in valores:
            if isinstance(val, (int, float)) and not pd.isna(val) and val > 0:
                if val < 2000 and val != int(val) or val >= 50:
                    valores_numericos.append(float(val))
        
        # Para restantes, pode não ter valor de entrada explícito
        if len(valores_numericos) >= 2:
            return min(valores_numericos)
        return 0.0
    
    def extrair_valor_restante(self, valores: List) -> float:
        """Extrai valor restante a ser pago"""
        # O valor restante pode ser calculado ou estar explícito
        valor_venda = self.extrair_valor_venda(valores)
        valor_entrada = self.extrair_valor_entrada(valores)
        
        if valor_venda > valor_entrada:
            return valor_venda - valor_entrada
        return valor_venda
    
    def extrair_observacoes(self, valores: List) -> str:
        """Extrai observações adicionais"""
        obs = []
        
        for val in valores:
            if isinstance(val, str) and len(val.strip()) > 0:
                val_clean = val.strip()
                # Adicionar se não for campo já extraído
                if not any(keyword in val_clean.upper() for keyword in [
                    'RESTANTE', 'ENTRADA', self.extrair_cliente(valores).upper(),
                    self.extrair_forma_pagamento(valores)
                ]):
                    obs.append(val_clean)
        
        return " | ".join(obs) if obs else ""
    
    def mostrar_amostra_restantes(self, restantes: List[Dict]):
        """Mostra amostra dos restantes extraídos"""
        if not restantes:
            print("📭 Nenhum restante encontrado")
            return
        
        print(f"\n📊 AMOSTRA DOS RESTANTES EXTRAÍDOS:")
        print("-" * 80)
        
        for i, restante in enumerate(restantes[:3], 1):
            print(f"{i}. Restante {restante['numero_venda']}")
            print(f"   👤 Cliente: {restante['cliente']}")
            print(f"   💳 Pagamento: {restante['forma_pagamento']}")
            print(f"   💰 Valor total: R$ {restante['valor_venda']:.2f}")
            print(f"   💵 Entrada: R$ {restante['valor_entrada']:.2f}")
            print(f"   🏦 Restante: R$ {restante['valor_restante']:.2f}")
            print()
    
    def testar_multiplos_dias(self, dias: List[str] = None):
        """Testa extração em múltiplos dias"""
        if dias is None:
            dias = ["01", "04", "15", "20", "30"]
        
        print("=" * 80)
        print("🧪 TESTE DE EXTRAÇÃO REST_ENTR - MÚLTIPLOS DIAS")
        print("=" * 80)
        
        todos_restantes = []
        
        for dia in dias:
            print(f"\n📅 Testando dia {dia}...")
            restantes_dia = self.extrair_rest_entr_dia_especifico(dia)
            todos_restantes.extend(restantes_dia)
            
            if restantes_dia:
                print(f"   ✅ {len(restantes_dia)} restantes extraídos")
            else:
                print(f"   ⚠️  Nenhum restante encontrado")
        
        # Relatório final
        self.gerar_relatorio_rest_entr(todos_restantes)
        
        return todos_restantes
    
    def gerar_relatorio_rest_entr(self, restantes: List[Dict]):
        """Gera relatório dos restantes extraídos"""
        if not restantes:
            print("\n❌ Nenhum restante para gerar relatório")
            return
        
        print(f"\n" + "=" * 60)
        print(f"📈 RELATÓRIO FINAL - TABELA REST_ENTR")
        print("=" * 60)
        
        print(f"📊 Total de restantes: {len(restantes)}")
        
        # Estatísticas
        valores_restante = [r['valor_restante'] for r in restantes if r['valor_restante'] > 0]
        if valores_restante:
            print(f"🏦 Total em aberto: R$ {sum(valores_restante):.2f}")
            print(f"🏦 Valor médio: R$ {sum(valores_restante) / len(valores_restante):.2f}")
            print(f"🏦 Maior restante: R$ {max(valores_restante):.2f}")
            print(f"🏦 Menor restante: R$ {min(valores_restante):.2f}")
        
        # Formas de pagamento
        formas_pagto = {}
        for restante in restantes:
            forma = restante['forma_pagamento'] or 'Não informado'
            formas_pagto[forma] = formas_pagto.get(forma, 0) + 1
        
        print(f"\n💳 Formas de pagamento:")
        for forma, count in formas_pagto.items():
            print(f"   {forma}: {count} restantes")
        
        # Salvar dados
        self.salvar_restantes_extraidos(restantes)
    
    def salvar_restantes_extraidos(self, restantes: List[Dict]):
        """Salva restantes extraídos em arquivo Excel"""
        if not restantes:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_saida = self.pasta_caixa / f"TABELA_REST_ENTR_EXTRAIDA_{timestamp}.xlsx"
        
        try:
            df_restantes = pd.DataFrame(restantes)
            df_restantes.to_excel(arquivo_saida, index=False, sheet_name='Restantes_REST_ENTR')
            
            print(f"\n💾 Dados salvos: {arquivo_saida}")
            print(f"📊 {len(restantes)} registros de restantes salvos")
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")

if __name__ == "__main__":
    extrator = ExtratorTabelaRESTENTR()
    
    print("🚀 INICIANDO EXTRAÇÃO ESPECÍFICA - TABELA REST_ENTR")
    
    # Testar em múltiplos dias
    restantes = extrator.testar_multiplos_dias()
    
    print("\n" + "=" * 80)
    print("✅ EXTRAÇÃO REST_ENTR CONCLUÍDA")
    print("=" * 80)
    print("\n🎯 PRÓXIMA TABELA: REC_CARN (Recebimento de carnê)")