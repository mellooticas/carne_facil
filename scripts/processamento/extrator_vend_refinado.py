#!/usr/bin/env python3
"""
EXTRATOR REFINADO - TABELA VEND (VENDAS)
Extrai dados precisos de vendas com todas as colunas necessárias
Colunas finais: Loja | Data | Nº Venda | Cliente | Forma de Pgto | Valor Venda | Entrada
"""

import pandas as pd
from pathlib import Path
import openpyxl
from datetime import datetime
import re
from typing import Dict, List, Optional

class ExtratorVendRefinado:
    def __init__(self):
        self.pasta_caixa = Path("data/caixa_lojas")
        self.arquivo_exemplo = self.pasta_caixa / "MAUA/2024_MAU/abr_24.xlsx"
        self.vendas_extraidas = []
        
        # Estrutura final desejada
        self.colunas_finais = [
            'loja',
            'data',
            'numero_venda',
            'cliente',
            'forma_pgto',
            'valor_venda',
            'entrada'
        ]
    
    def extrair_vendas_arquivo_completo(self):
        """Extrai todas as vendas do arquivo com dados precisos"""
        print("=" * 80)
        print("💰 EXTRATOR REFINADO - TABELA VEND (VENDAS)")
        print("=" * 80)
        
        if not self.arquivo_exemplo.exists():
            print(f"❌ Arquivo não encontrado: {self.arquivo_exemplo}")
            return []
        
        # Identificar informações do arquivo
        info_arquivo = self.identificar_arquivo()
        print(f"🏪 Loja: {info_arquivo['loja']}")
        print(f"📅 Período: {info_arquivo['periodo']}")
        
        # Listar abas
        abas = self.listar_abas()
        print(f"📄 Total de abas: {len(abas)}")
        
        todas_vendas = []
        
        # Processar abas que são dias (números)
        abas_dias = [aba for aba in abas if aba.isdigit()]
        print(f"📅 Abas de dias encontradas: {len(abas_dias)}")
        
        for aba in abas_dias[:5]:  # Testar primeiras 5 abas
            print(f"\n📃 Processando aba: {aba}")
            vendas_dia = self.extrair_vendas_dia(aba, info_arquivo)
            
            if vendas_dia:
                todas_vendas.extend(vendas_dia)
                print(f"   ✅ {len(vendas_dia)} vendas extraídas")
                # Mostrar primeira venda como exemplo
                if vendas_dia:
                    self.mostrar_exemplo_venda(vendas_dia[0])
            else:
                print(f"   ⚠️  Nenhuma venda encontrada")
        
        # Salvar dados
        if todas_vendas:
            self.salvar_vendas_refinadas(todas_vendas, info_arquivo)
            self.gerar_relatorio_vendas(todas_vendas)
        
        return todas_vendas
    
    def identificar_arquivo(self) -> Dict:
        """Identifica informações do arquivo"""
        partes_path = self.arquivo_exemplo.parts
        
        # Extrair loja da estrutura de pastas
        loja = "MAUA"  # padrão
        for parte in partes_path:
            if parte.upper() in ['MAUA', 'SUZANO', 'RIO_PEQUENO']:
                loja = parte.upper()
                break
        
        # Extrair período do nome do arquivo (abr_24.xlsx)
        nome_arquivo = self.arquivo_exemplo.stem  # abr_24
        mes, ano = nome_arquivo.split('_')
        periodo = f"20{ano}_{mes.upper()}"
        
        return {
            'loja': loja,
            'periodo': periodo,
            'ano': f"20{ano}",
            'mes': mes.upper(),
            'arquivo_nome': self.arquivo_exemplo.name
        }
    
    def listar_abas(self) -> List[str]:
        """Lista abas do arquivo"""
        try:
            workbook = openpyxl.load_workbook(self.arquivo_exemplo, read_only=True)
            abas = workbook.sheetnames
            workbook.close()
            return abas
        except Exception as e:
            print(f"❌ Erro ao listar abas: {e}")
            return []
    
    def extrair_vendas_dia(self, aba: str, info_arquivo: Dict) -> List[Dict]:
        """Extrai vendas de um dia específico"""
        try:
            df = pd.read_excel(self.arquivo_exemplo, sheet_name=aba, header=None)
            
            # Procurar seção de vendas
            secao_vend = self.identificar_secao_vend(df)
            
            if not secao_vend:
                return []
            
            print(f"   📊 Seção VEND encontrada: linhas {secao_vend['inicio']} a {secao_vend['fim']}")
            
            # Extrair vendas da seção
            vendas = self.extrair_vendas_secao(secao_vend['dados'], aba, info_arquivo)
            
            return vendas
            
        except Exception as e:
            print(f"   ❌ Erro ao processar aba {aba}: {e}")
            return []
    
    def identificar_secao_vend(self, df: pd.DataFrame) -> Optional[Dict]:
        """Identifica a seção de vendas no DataFrame"""
        for i, row in df.iterrows():
            linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
            linha_upper = linha_texto.upper()
            
            # Procurar por indicadores de seção de vendas
            if any(indicador in linha_upper for indicador in [
                'VEND', 'VENDA', 'Nº VENDA', 'CLIENTE', 'FORMA DE PGTO'
            ]):
                # Encontrou início, procurar fim
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
        # Procurar até encontrar nova seção ou fim dos dados
        for i in range(inicio + 1, len(df)):
            row = df.iloc[i]
            linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
            linha_upper = linha_texto.upper()
            
            # Parar se encontrar nova seção
            if any(indicador in linha_upper for indicador in [
                'RESTANTE ENTRADA', 'RECEBIMENTO', 'ENTREGA', 'OS ENTREGUE'
            ]):
                return i - 1
            
            # Parar se linha totalmente vazia por mais de 3 linhas
            if not linha_texto.strip():
                linhas_vazias = 0
                for j in range(i, min(i + 3, len(df))):
                    if not " ".join([str(cell) for cell in df.iloc[j] if pd.notna(cell)]).strip():
                        linhas_vazias += 1
                if linhas_vazias >= 3:
                    return i - 1
        
        return min(inicio + 20, len(df) - 1)  # Limite máximo
    
    def extrair_vendas_secao(self, dados: pd.DataFrame, aba: str, info_arquivo: Dict) -> List[Dict]:
        """Extrai vendas estruturadas da seção"""
        vendas = []
        
        # Analisar estrutura da seção primeiro
        print(f"   🔍 Analisando estrutura da seção VEND...")
        
        for i, row in dados.iterrows():
            valores = [cell for cell in row if pd.notna(cell)]
            
            if not valores:
                continue
            
            linha_texto = " ".join([str(val) for val in valores])
            linha_upper = linha_texto.upper()
            
            # Pular cabeçalhos
            if any(keyword in linha_upper for keyword in [
                'Nº VENDA', 'CLIENTE', 'FORMA', 'PGTO', 'VALOR', 'ENTRADA', 'TOTAL'
            ]):
                continue
            
            # Procurar por padrão de venda
            venda = self.extrair_linha_venda_refinada(valores, aba, info_arquivo, i)
            
            if venda:
                vendas.append(venda)
                print(f"      💰 Venda: {venda['numero_venda']} - {venda['cliente']} - R$ {venda['valor_venda']}")
        
        return vendas
    
    def extrair_linha_venda_refinada(self, valores: List, aba: str, info_arquivo: Dict, linha_idx: int) -> Optional[Dict]:
        """Extrai dados refinados de uma linha de venda"""
        if len(valores) < 3:
            return None
        
        # Analisar valores para identificar componentes
        numero_venda = self.extrair_numero_venda(valores)
        cliente = self.extrair_cliente(valores)
        forma_pgto = self.extrair_forma_pagamento(valores)
        valor_venda = self.extrair_valor_venda(valores)
        entrada = self.extrair_entrada(valores)
        
        # Validar se é uma venda válida
        if not numero_venda and not valor_venda:
            return None
        
        # Construir data completa
        data_completa = self.construir_data(aba, info_arquivo)
        
        venda = {
            'loja': info_arquivo['loja'],
            'data': data_completa,
            'numero_venda': numero_venda or f"AUTO_{linha_idx}",
            'cliente': cliente,
            'forma_pgto': forma_pgto,
            'valor_venda': valor_venda or 0,
            'entrada': entrada or 0,
            'dados_brutos': str(valores)  # Para debug
        }
        
        return venda
    
    def extrair_numero_venda(self, valores: List) -> Optional[str]:
        """Extrai número da venda"""
        for val in valores:
            if isinstance(val, (int, float)) and not pd.isna(val):
                val_int = int(val)
                # Número de venda pode ser sequencial ou código
                if 1 <= val_int <= 99999:
                    return str(val_int)
            elif isinstance(val, str) and val.isdigit():
                return val
        return None
    
    def extrair_cliente(self, valores: List) -> str:
        """Extrai nome do cliente"""
        for val in valores:
            if isinstance(val, str) and len(val.strip()) > 2:
                val_clean = val.strip()
                # Filtrar valores que não são nomes
                if not any(keyword in val_clean.upper() for keyword in [
                    'PIX', 'DINHEIRO', 'CARTAO', 'CTD', 'CTC', 'TOTAL', 'R$'
                ]) and not val_clean.replace('.', '').replace(',', '').isdigit():
                    return val_clean
        return ""
    
    def extrair_forma_pagamento(self, valores: List) -> str:
        """Extrai forma de pagamento"""
        formas_conhecidas = ['PIX', 'DINHEIRO', 'CARTÃO', 'CTD', 'CTC', 'DN', 'DÉBITO', 'CRÉDITO']
        
        for val in valores:
            if isinstance(val, str):
                val_upper = val.upper().strip()
                for forma in formas_conhecidas:
                    if forma in val_upper:
                        return forma
        return ""
    
    def extrair_valor_venda(self, valores: List) -> Optional[float]:
        """Extrai valor da venda"""
        valores_encontrados = []
        
        for val in valores:
            if isinstance(val, (int, float)) and not pd.isna(val) and val > 0:
                valores_encontrados.append(float(val))
        
        # Retornar o maior valor (geralmente é o valor da venda)
        if valores_encontrados:
            return max(valores_encontrados)
        return None
    
    def extrair_entrada(self, valores: List) -> Optional[float]:
        """Extrai valor da entrada"""
        valores_encontrados = []
        
        for val in valores:
            if isinstance(val, (int, float)) and not pd.isna(val) and val > 0:
                valores_encontrados.append(float(val))
        
        # Se há múltiplos valores, a entrada pode ser o menor
        if len(valores_encontrados) >= 2:
            return min(valores_encontrados)
        return None
    
    def construir_data(self, aba: str, info_arquivo: Dict) -> str:
        """Constrói data completa"""
        dia = aba.zfill(2)  # 01, 02, etc.
        
        # Mapear mês
        meses = {
            'JAN': '01', 'FEV': '02', 'MAR': '03', 'ABR': '04',
            'MAI': '05', 'JUN': '06', 'JUL': '07', 'AGO': '08',
            'SET': '09', 'OUT': '10', 'NOV': '11', 'DEZ': '12'
        }
        
        mes_num = meses.get(info_arquivo['mes'], '01')
        ano = info_arquivo['ano']
        
        return f"{ano}-{mes_num}-{dia}"
    
    def mostrar_exemplo_venda(self, venda: Dict):
        """Mostra exemplo de venda extraída"""
        print(f"      📋 Exemplo extraído:")
        print(f"         🏪 Loja: {venda['loja']}")
        print(f"         📅 Data: {venda['data']}")
        print(f"         🔢 Nº Venda: {venda['numero_venda']}")
        print(f"         👤 Cliente: {venda['cliente']}")
        print(f"         💳 Forma Pgto: {venda['forma_pgto']}")
        print(f"         💰 Valor: R$ {venda['valor_venda']}")
        print(f"         💵 Entrada: R$ {venda['entrada']}")
    
    def salvar_vendas_refinadas(self, vendas: List[Dict], info_arquivo: Dict):
        """Salva vendas em arquivo Excel refinado"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_saida = self.pasta_caixa / f"VENDAS_REFINADAS_{info_arquivo['loja']}_{info_arquivo['periodo']}_{timestamp}.xlsx"
        
        try:
            # Remover dados brutos para arquivo final
            vendas_clean = []
            for venda in vendas:
                venda_clean = {k: v for k, v in venda.items() if k != 'dados_brutos'}
                vendas_clean.append(venda_clean)
            
            df_vendas = pd.DataFrame(vendas_clean)
            df_vendas.to_excel(arquivo_saida, index=False, sheet_name='VENDAS')
            
            print(f"\n💾 Vendas salvas: {arquivo_saida}")
            print(f"📊 {len(vendas)} vendas processadas")
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
    
    def gerar_relatorio_vendas(self, vendas: List[Dict]):
        """Gera relatório das vendas"""
        print(f"\n" + "=" * 60)
        print(f"📈 RELATÓRIO DE VENDAS")
        print("=" * 60)
        
        total_vendas = len(vendas)
        valor_total = sum(venda['valor_venda'] for venda in vendas)
        entrada_total = sum(venda['entrada'] for venda in vendas if venda['entrada'])
        
        print(f"📊 Total de vendas: {total_vendas}")
        print(f"💰 Valor total: R$ {valor_total:,.2f}")
        print(f"💵 Entradas total: R$ {entrada_total:,.2f}")
        
        # Formas de pagamento
        formas_pgto = {}
        for venda in vendas:
            forma = venda['forma_pgto'] or 'Não informado'
            formas_pgto[forma] = formas_pgto.get(forma, 0) + 1
        
        print(f"\n💳 Formas de pagamento:")
        for forma, count in formas_pgto.items():
            print(f"   {forma}: {count} vendas")
        
        # Clientes
        clientes_unicos = len(set(venda['cliente'] for venda in vendas if venda['cliente']))
        print(f"\n👥 Clientes únicos: {clientes_unicos}")

if __name__ == "__main__":
    extrator = ExtratorVendRefinado()
    
    print("🚀 INICIANDO EXTRAÇÃO REFINADA - TABELA VEND")
    
    vendas = extrator.extrair_vendas_arquivo_completo()
    
    print("\n" + "=" * 80)
    print("✅ EXTRAÇÃO REFINADA CONCLUÍDA")
    print("=" * 80)