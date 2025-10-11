#!/usr/bin/env python3
"""
EXTRATOR ESPECÍFICO - TABELA VEND (Vendas do Dia)
Extrai e padroniza dados da tabela de vendas diárias
"""

import pandas as pd
from pathlib import Path
import openpyxl
from datetime import datetime
import re
from typing import Dict, List, Optional

class ExtratorTabelaVEND:
    def __init__(self):
        self.pasta_caixa = Path("data/caixa_lojas")
        self.arquivo_exemplo = self.pasta_caixa / "MAUA/2024_MAU/abr_24.xlsx"
        self.vendas_extraidas = []
        
        # Estrutura de colunas esperada para VEND
        self.colunas_vend = [
            'id_registro',
            'loja',
            'data_venda',
            'dia',
            'mes_ano',
            'numero_venda',
            'cliente',
            'forma_pagamento',
            'valor_venda',
            'valor_entrada',
            'vendedor',
            'observacoes',
            'linha_bruta'
        ]
    
    def extrair_vend_dia_especifico(self, aba: str = "04"):
        """Extrai dados de VEND de um dia específico"""
        print("=" * 80)
        print(f"📊 EXTRAÇÃO TABELA VEND - DIA {aba}")
        print("=" * 80)
        
        if not self.arquivo_exemplo.exists():
            print(f"❌ Arquivo não encontrado: {self.arquivo_exemplo}")
            return []
        
        try:
            # Ler a aba específica
            df = pd.read_excel(self.arquivo_exemplo, sheet_name=aba, header=None)
            print(f"📏 Dimensões da página: {df.shape[0]} linhas × {df.shape[1]} colunas")
            
            # Encontrar seção de vendas
            secao_vend = self.identificar_secao_vend(df)
            
            if not secao_vend:
                print(f"❌ Seção VEND não encontrada no dia {aba}")
                return []
            
            print(f"✅ Seção VEND encontrada: linhas {secao_vend['inicio']} a {secao_vend['fim']}")
            
            # Extrair dados da seção
            vendas_dia = self.extrair_dados_vend(secao_vend['dados'], aba)
            
            print(f"📊 Total de vendas extraídas: {len(vendas_dia)}")
            
            # Mostrar amostra
            self.mostrar_amostra_vendas(vendas_dia)
            
            return vendas_dia
            
        except Exception as e:
            print(f"❌ Erro ao extrair VEND do dia {aba}: {e}")
            return []
    
    def identificar_secao_vend(self, df: pd.DataFrame) -> Optional[Dict]:
        """Identifica a seção de vendas no DataFrame"""
        for i, row in df.iterrows():
            linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
            linha_upper = linha_texto.upper()
            
            # Procurar por linha que indica vendas
            if 'VENDAS' in linha_upper and any(keyword in linha_upper for keyword in 
                ['Nº VENDA', 'CLIENTE', 'FORMA DE PGTO', 'VALOR VENDA']):
                
                # Encontrou cabeçalho, agora procurar fim da seção
                fim_secao = self.encontrar_fim_secao_vend(df, i)
                
                return {
                    'inicio': i,
                    'fim': fim_secao,
                    'dados': df.iloc[i:fim_secao + 1],
                    'cabecalho': linha_texto
                }
        
        return None
    
    def encontrar_fim_secao_vend(self, df: pd.DataFrame, inicio: int) -> int:
        """Encontra o fim da seção de vendas"""
        # A seção de vendas geralmente vai até encontrar "Tipos de Pagto" ou linhas vazias
        for i in range(inicio + 1, len(df)):
            row = df.iloc[i]
            linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
            linha_upper = linha_texto.upper()
            
            # Parar se encontrar seção de tipos de pagamento
            if 'TIPOS DE PAGTO' in linha_upper:
                return i - 1
            
            # Continuar processando até encontrar fim dos dados de vendas
            # Baseado na análise, as vendas estão nas primeiras linhas após o cabeçalho
        
        # Se não encontrar fim específico, processar até 10 linhas após início
        return min(inicio + 10, len(df) - 1)
    
    def extrair_dados_vend(self, dados: pd.DataFrame, dia: str) -> List[Dict]:
        """Extrai dados estruturados da seção de vendas"""
        vendas = []
        
        # Analisar cada linha procurando vendas válidas
        for i, row in dados.iterrows():
            # Converter linha para lista de valores não nulos
            valores = [cell for cell in row if pd.notna(cell)]
            
            if not valores:
                continue
            
            # Pular linha de cabeçalho
            linha_texto = " ".join([str(val) for val in valores])
            linha_upper = linha_texto.upper()
            
            # Pular cabeçalhos e seções
            if any(keyword in linha_upper for keyword in [
                'VENDAS', 'Nº VENDA', 'CLIENTE', 'FORMA DE PGTO',
                'TIPOS DE PAGTO', 'TOTAL', 'DESPESAS', 'ENTREGA DE CARNE'
            ]):
                continue
            
            # Procurar por número de venda (4 dígitos começando com 4)
            numero_venda = self.extrair_numero_venda(valores)
            
            if numero_venda:
                # Validar se é realmente uma linha de venda
                if self.e_linha_venda_valida(valores, linha_upper):
                    venda = self.criar_registro_venda(valores, numero_venda, dia, i)
                    if venda:
                        vendas.append(venda)
                        print(f"   📝 Venda extraída: {numero_venda} - {venda.get('cliente', 'N/A')}")
        
        return vendas
    
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
    
    def e_linha_venda_valida(self, valores: List, linha_upper: str) -> bool:
        """Verifica se é uma linha de venda válida"""
        # Deve conter nome de cliente (string longa)
        tem_nome_cliente = any(
            isinstance(val, str) and len(val) > 5 and 
            not any(kw in val.upper() for kw in ['VENDAS', 'ENTRADA', 'TOTAL', 'DESPESAS'])
            for val in valores
        )
        
        # Deve conter forma de pagamento
        formas_conhecidas = ['DN', 'CTD', 'CTC', 'PIX', 'SS', 'GARANTIA']
        tem_forma_pagto = any(
            isinstance(val, str) and val.upper().strip() in formas_conhecidas
            for val in valores
        )
        
        # Não deve ser linha de totalizadores
        e_totalizador = any(kw in linha_upper for kw in [
            'TOTAL', 'DESPESAS', 'ENTREGA', 'OS ENTREGUE'
        ])
        
        return tem_nome_cliente and tem_forma_pagto and not e_totalizador
    
    def criar_registro_venda(self, valores: List, numero_venda: str, dia: str, linha_idx: int) -> Optional[Dict]:
        """Cria registro estruturado de uma venda"""
        try:
            # Mapear valores para campos
            venda = {
                'id_registro': f"VEND_MAU_2024_04_{dia}_{numero_venda}",
                'loja': 'MAUA',
                'data_venda': f"2024-04-{dia}",
                'dia': dia,
                'mes_ano': '2024_04',
                'numero_venda': numero_venda,
                'cliente': self.extrair_cliente(valores),
                'forma_pagamento': self.extrair_forma_pagamento(valores),
                'valor_venda': self.extrair_valor_venda(valores),
                'valor_entrada': self.extrair_valor_entrada(valores),
                'vendedor': self.extrair_vendedor(valores),
                'observacoes': self.extrair_observacoes(valores),
                'linha_bruta': str(valores)
            }
            
            return venda
            
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
                    'VENDAS', 'ENTRADA', 'FORMA', 'PGTO', 'VALOR', 'CTD', 'CTC', 'PIX', 'DN'
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
        """Extrai valor de entrada"""
        valores_numericos = []
        
        for val in valores:
            if isinstance(val, (int, float)) and not pd.isna(val) and val > 0:
                if val < 2000 and val != int(val) or val >= 50:
                    valores_numericos.append(float(val))
        
        # Valor de entrada geralmente é menor ou igual ao valor da venda
        if len(valores_numericos) >= 2:
            return min(valores_numericos)
        elif len(valores_numericos) == 1:
            return valores_numericos[0]
        return 0.0
    
    def extrair_vendedor(self, valores: List) -> str:
        """Extrai nome do vendedor"""
        vendedores_conhecidos = ['BETH', 'CARLOS', 'MARIA', 'JOSE']
        
        for val in valores:
            if isinstance(val, str):
                val_upper = val.upper().strip()
                if val_upper in vendedores_conhecidos:
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
                    'VENDAS', 'ENTRADA', self.extrair_cliente(valores).upper(),
                    self.extrair_forma_pagamento(valores)
                ]):
                    obs.append(val_clean)
        
        return " | ".join(obs) if obs else ""
    
    def mostrar_amostra_vendas(self, vendas: List[Dict]):
        """Mostra amostra das vendas extraídas"""
        if not vendas:
            print("📭 Nenhuma venda encontrada")
            return
        
        print(f"\n📊 AMOSTRA DAS VENDAS EXTRAÍDAS:")
        print("-" * 80)
        
        for i, venda in enumerate(vendas[:3], 1):
            print(f"{i}. Venda {venda['numero_venda']}")
            print(f"   👤 Cliente: {venda['cliente']}")
            print(f"   💳 Pagamento: {venda['forma_pagamento']}")
            print(f"   💰 Valor: R$ {venda['valor_venda']:.2f}")
            print(f"   💵 Entrada: R$ {venda['valor_entrada']:.2f}")
            if venda['vendedor']:
                print(f"   👨‍💼 Vendedor: {venda['vendedor']}")
            print()
    
    def testar_multiplos_dias(self, dias: List[str] = None):
        """Testa extração em múltiplos dias"""
        if dias is None:
            dias = ["01", "04", "15", "20", "30"]
        
        print("=" * 80)
        print("🧪 TESTE DE EXTRAÇÃO VEND - MÚLTIPLOS DIAS")
        print("=" * 80)
        
        todas_vendas = []
        
        for dia in dias:
            print(f"\n📅 Testando dia {dia}...")
            vendas_dia = self.extrair_vend_dia_especifico(dia)
            todas_vendas.extend(vendas_dia)
            
            if vendas_dia:
                print(f"   ✅ {len(vendas_dia)} vendas extraídas")
            else:
                print(f"   ⚠️  Nenhuma venda encontrada")
        
        # Relatório final
        self.gerar_relatorio_vend(todas_vendas)
        
        return todas_vendas
    
    def gerar_relatorio_vend(self, vendas: List[Dict]):
        """Gera relatório das vendas extraídas"""
        if not vendas:
            print("\n❌ Nenhuma venda para gerar relatório")
            return
        
        print(f"\n" + "=" * 60)
        print(f"📈 RELATÓRIO FINAL - TABELA VEND")
        print("=" * 60)
        
        print(f"📊 Total de vendas: {len(vendas)}")
        
        # Estatísticas
        valores_venda = [v['valor_venda'] for v in vendas if v['valor_venda'] > 0]
        if valores_venda:
            print(f"💰 Valor total: R$ {sum(valores_venda):.2f}")
            print(f"💰 Valor médio: R$ {sum(valores_venda) / len(valores_venda):.2f}")
            print(f"💰 Maior venda: R$ {max(valores_venda):.2f}")
            print(f"💰 Menor venda: R$ {min(valores_venda):.2f}")
        
        # Formas de pagamento
        formas_pagto = {}
        for venda in vendas:
            forma = venda['forma_pagamento'] or 'Não informado'
            formas_pagto[forma] = formas_pagto.get(forma, 0) + 1
        
        print(f"\n💳 Formas de pagamento:")
        for forma, count in formas_pagto.items():
            print(f"   {forma}: {count} vendas")
        
        # Salvar dados
        self.salvar_vendas_extraidas(vendas)
    
    def salvar_vendas_extraidas(self, vendas: List[Dict]):
        """Salva vendas extraídas em arquivo Excel"""
        if not vendas:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_saida = self.pasta_caixa / f"TABELA_VEND_EXTRAIDA_{timestamp}.xlsx"
        
        try:
            df_vendas = pd.DataFrame(vendas)
            df_vendas.to_excel(arquivo_saida, index=False, sheet_name='Vendas_VEND')
            
            print(f"\n💾 Dados salvos: {arquivo_saida}")
            print(f"📊 {len(vendas)} registros de vendas salvos")
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")

if __name__ == "__main__":
    extrator = ExtratorTabelaVEND()
    
    print("🚀 INICIANDO EXTRAÇÃO ESPECÍFICA - TABELA VEND")
    
    # Testar em múltiplos dias
    vendas = extrator.testar_multiplos_dias()
    
    print("\n" + "=" * 80)
    print("✅ EXTRAÇÃO VEND CONCLUÍDA")
    print("=" * 80)
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Refinar campos extraídos conforme necessário")
    print("2. Criar extratores para as outras 4 tabelas")
    print("3. Integrar com sistema principal")