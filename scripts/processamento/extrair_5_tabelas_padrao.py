#!/usr/bin/env python3
"""
EXTRATOR DAS 5 TABELAS PADRÃO POR DIA
Identifica e extrai as 5 tabelas específicas de cada dia:
- VEND(dia) - Vendas do dia
- REST_ENTR(dia) - Restantes de entrada/sinal
- REC_CARN(dia) - Recebimento de carnê
- ENTR_CARN(dia) - Entrega de carnê
- OS_ENT_DIA(dia) - OS entregues no dia
"""

import pandas as pd
from pathlib import Path
import openpyxl
from datetime import datetime
import re
from typing import Dict, List, Tuple, Optional

class ExtratorTabelasPadrao:
    def __init__(self):
        self.pasta_caixa = Path("data/caixa_lojas")
        self.arquivo_exemplo = self.pasta_caixa / "MAUA/2024_MAU/abr_24.xlsx"
        self.tabelas_extraidas = []
        
        # Padrões das 5 tabelas
        self.padroes_tabelas = {
            'VEND': {
                'keywords': ['Vendas', 'Nº Venda', 'Cliente', 'Forma de Pgto', 'Valor Venda'],
                'descricao': 'Vendas do dia'
            },
            'REST_ENTR': {
                'keywords': ['Restante Entrada', 'Nº Venda', 'Cliente', 'Valor Venda'],
                'descricao': 'Restantes de entrada/sinal'
            },
            'REC_CARN': {
                'keywords': ['Recebimento de Carnê', 'OS', 'Cliente', 'Valor Parcela'],
                'descricao': 'Recebimento de carnê'
            },
            'ENTR_CARN': {
                'keywords': ['Entrega de Carne', 'OS', 'Parcelas', 'Valor Total'],
                'descricao': 'Entrega de carnê'
            },
            'OS_ENT_DIA': {
                'keywords': ['OS Entregue no Dia', 'OS', 'Vendedor'],
                'descricao': 'OS entregues no dia'
            }
        }
    
    def analisar_dia_especifico(self, aba: str = "04"):
        """Analisa um dia específico para identificar as 5 tabelas"""
        print("=" * 80)
        print(f"🔍 ANÁLISE DAS 5 TABELAS PADRÃO - DIA {aba}")
        print("=" * 80)
        
        if not self.arquivo_exemplo.exists():
            print(f"❌ Arquivo não encontrado: {self.arquivo_exemplo}")
            return
        
        try:
            # Ler a aba específica
            df = pd.read_excel(self.arquivo_exemplo, sheet_name=aba, header=None)
            print(f"📏 Dimensões da página: {df.shape[0]} linhas × {df.shape[1]} colunas")
            
            # Identificar cada uma das 5 tabelas
            tabelas_encontradas = {}
            
            for tipo_tabela, config in self.padroes_tabelas.items():
                print(f"\n🔍 Procurando tabela: {tipo_tabela} - {config['descricao']}")
                
                tabela_info = self.identificar_tabela_especifica(df, tipo_tabela, config, aba)
                
                if tabela_info:
                    tabelas_encontradas[tipo_tabela] = tabela_info
                    print(f"   ✅ Encontrada: Linhas {tabela_info['inicio']} a {tabela_info['fim']}")
                    print(f"   📊 Dados: {tabela_info['dados'].shape[0]} registros")
                    
                    # Mostrar amostra
                    self.mostrar_amostra_tabela(tabela_info, tipo_tabela)
                else:
                    print(f"   ❌ Não encontrada")
            
            # Resumo das tabelas encontradas
            self.mostrar_resumo_tabelas(tabelas_encontradas, aba)
            
            return tabelas_encontradas
            
        except Exception as e:
            print(f"❌ Erro ao analisar dia {aba}: {e}")
            return {}
    
    def identificar_tabela_especifica(self, df: pd.DataFrame, tipo_tabela: str, 
                                    config: Dict, dia: str) -> Optional[Dict]:
        """Identifica uma tabela específica no DataFrame"""
        keywords = config['keywords']
        
        # Procurar pela linha que inicia a tabela
        inicio_tabela = None
        linha_cabecalho = None
        
        for i, row in df.iterrows():
            linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
            linha_upper = linha_texto.upper()
            
            # Verificar se contém as palavras-chave da tabela
            if tipo_tabela == 'VEND':
                # Procurar por "Vendas" seguido de valor e cabeçalhos
                if 'VENDAS' in linha_upper and any(kw.upper() in linha_upper for kw in keywords[1:]):
                    inicio_tabela = i
                    linha_cabecalho = linha_texto
                    break
                    
            elif tipo_tabela == 'REST_ENTR':
                # Procurar especificamente por "Restante Entrada"
                if 'RESTANTE ENTRADA' in linha_upper:
                    inicio_tabela = i
                    linha_cabecalho = linha_texto
                    break
                    
            elif tipo_tabela == 'REC_CARN':
                # Procurar por "Recebimento de Carnê"
                if 'RECEBIMENTO DE CARNÊ' in linha_upper or 'RECEBIMENTO DE CARNE' in linha_upper:
                    inicio_tabela = i
                    linha_cabecalho = linha_texto
                    break
                    
            elif tipo_tabela == 'ENTR_CARN':
                # Procurar por "Entrega de Carne" 
                if 'ENTREGA DE CARNE' in linha_upper and 'CARNÊ' not in linha_upper:
                    inicio_tabela = i
                    linha_cabecalho = linha_texto
                    break
                    
            elif tipo_tabela == 'OS_ENT_DIA':
                # Procurar por "OS Entregue no Dia"
                if 'OS ENTREGUE NO DIA' in linha_upper:
                    inicio_tabela = i
                    linha_cabecalho = linha_texto
                    break
        
        if inicio_tabela is None:
            return None
        
        # Determinar fim da tabela
        fim_tabela = self.encontrar_fim_tabela(df, inicio_tabela, tipo_tabela)
        
        # Extrair dados da tabela
        dados_tabela = df.iloc[inicio_tabela:fim_tabela + 1]
        
        return {
            'tipo': tipo_tabela,
            'dia': dia,
            'inicio': inicio_tabela,
            'fim': fim_tabela,
            'linha_cabecalho': linha_cabecalho,
            'dados': dados_tabela,
            'dados_limpos': self.limpar_dados_tabela(dados_tabela, tipo_tabela),
            'descricao': config['descricao']
        }
    
    def encontrar_fim_tabela(self, df: pd.DataFrame, inicio: int, tipo_tabela: str) -> int:
        """Encontra o fim de uma tabela específica"""
        # Estratégia: procurar próxima seção ou fim dos dados
        for i in range(inicio + 1, len(df)):
            row = df.iloc[i]
            linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
            linha_upper = linha_texto.upper()
            
            # Parar se encontrar início de nova seção
            indicadores_nova_secao = [
                'TIPOS DE PAGTO', 'SALDO INICIAL', 'VENDAS', 'DESPESAS',
                'RESTANTE ENTRADA', 'RECEBIMENTO', 'ENTREGA DE CARNE',
                'OS ENTREGUE NO DIA'
            ]
            
            if any(indicador in linha_upper for indicador in indicadores_nova_secao):
                # Verificar se não é a mesma seção
                if not self.e_mesma_secao(linha_upper, tipo_tabela):
                    return i - 1
            
            # Parar se linha totalmente vazia
            if linha_texto.strip() == '' or linha_texto.strip() == 'nan':
                # Verificar se há mais dados adiante
                tem_dados_adiante = False
                for j in range(i + 1, min(i + 5, len(df))):
                    if any(pd.notna(cell) and str(cell).strip() != '' for cell in df.iloc[j]):
                        tem_dados_adiante = True
                        break
                
                if not tem_dados_adiante:
                    return i - 1
        
        return len(df) - 1
    
    def e_mesma_secao(self, linha_upper: str, tipo_tabela: str) -> bool:
        """Verifica se a linha ainda pertence à mesma seção"""
        if tipo_tabela == 'VEND' and 'VENDAS' in linha_upper:
            return True
        elif tipo_tabela == 'REST_ENTR' and 'RESTANTE' in linha_upper:
            return True
        elif tipo_tabela == 'REC_CARN' and 'RECEBIMENTO' in linha_upper:
            return True
        elif tipo_tabela == 'ENTR_CARN' and 'ENTREGA' in linha_upper:
            return True
        elif tipo_tabela == 'OS_ENT_DIA' and 'OS ENTREGUE' in linha_upper:
            return True
        return False
    
    def limpar_dados_tabela(self, dados: pd.DataFrame, tipo_tabela: str) -> pd.DataFrame:
        """Limpa e estrutura os dados de uma tabela"""
        # Remover linhas totalmente vazias
        dados_limpos = dados.dropna(how='all')
        
        # Remover colunas totalmente vazias
        dados_limpos = dados_limpos.dropna(axis=1, how='all')
        
        # Filtrar apenas linhas com dados relevantes
        if tipo_tabela in ['VEND', 'REST_ENTR']:
            # Manter linhas que têm números de venda (4 dígitos)
            mask = dados_limpos.apply(lambda row: any(
                pd.notna(val) and str(val).isdigit() and len(str(val)) == 4 
                for val in row
            ), axis=1)
            dados_limpos = dados_limpos[mask]
            
        elif tipo_tabela in ['REC_CARN', 'ENTR_CARN', 'OS_ENT_DIA']:
            # Manter linhas que têm números de OS 
            mask = dados_limpos.apply(lambda row: any(
                pd.notna(val) and (str(val).isdigit() and len(str(val)) == 4)
                for val in row
            ), axis=1)
            dados_limpos = dados_limpos[mask]
        
        return dados_limpos
    
    def mostrar_amostra_tabela(self, tabela_info: Dict, tipo_tabela: str):
        """Mostra amostra dos dados de uma tabela"""
        dados_limpos = tabela_info['dados_limpos']
        
        print(f"   📋 Cabeçalho: {tabela_info['linha_cabecalho']}")
        
        if len(dados_limpos) > 0:
            print(f"   📊 Dados limpos: {len(dados_limpos)} registros válidos")
            print(f"   📝 Amostra (primeiros 3 registros):")
            
            for i, (idx, row) in enumerate(dados_limpos.head(3).iterrows()):
                valores = [str(val) for val in row if pd.notna(val) and str(val).strip() != '']
                if valores:
                    print(f"      {i+1}. {' | '.join(valores)}")
        else:
            print(f"   📭 Nenhum dado válido encontrado")
    
    def mostrar_resumo_tabelas(self, tabelas: Dict, dia: str):
        """Mostra resumo das tabelas encontradas"""
        print(f"\n" + "=" * 60)
        print(f"📊 RESUMO - DIA {dia}")
        print("=" * 60)
        
        print(f"🎯 Tabelas encontradas: {len(tabelas)}/5")
        
        for tipo, info in tabelas.items():
            dados_validos = len(info['dados_limpos']) if 'dados_limpos' in info else 0
            print(f"   ✅ {tipo:12} | {dados_validos:3d} registros | {info['descricao']}")
        
        # Mostrar tabelas não encontradas
        tabelas_faltantes = set(self.padroes_tabelas.keys()) - set(tabelas.keys())
        if tabelas_faltantes:
            print(f"\n❌ Tabelas não encontradas:")
            for tipo in tabelas_faltantes:
                print(f"   ❌ {tipo:12} | {self.padroes_tabelas[tipo]['descricao']}")
    
    def testar_multiplos_dias(self, dias: List[str] = None):
        """Testa a extração em múltiplos dias"""
        if dias is None:
            dias = ["01", "04", "15", "20", "30"]
        
        print("=" * 80)
        print("🧪 TESTE DE EXTRAÇÃO EM MÚLTIPLOS DIAS")
        print("=" * 80)
        
        resultado_geral = {}
        
        for dia in dias:
            print(f"\n📅 Testando dia {dia}...")
            try:
                tabelas = self.analisar_dia_especifico(dia)
                resultado_geral[dia] = tabelas
                
                # Resumo rápido
                encontradas = len(tabelas)
                print(f"   ✅ {encontradas}/5 tabelas encontradas")
                
            except Exception as e:
                print(f"   ❌ Erro no dia {dia}: {e}")
                resultado_geral[dia] = {}
        
        # Relatório final
        self.gerar_relatorio_teste(resultado_geral)
        
        return resultado_geral
    
    def gerar_relatorio_teste(self, resultados: Dict):
        """Gera relatório final dos testes"""
        print("\n" + "=" * 80)
        print("📈 RELATÓRIO FINAL DOS TESTES")
        print("=" * 80)
        
        # Contabilizar sucessos por tabela
        contadores = {tipo: 0 for tipo in self.padroes_tabelas.keys()}
        total_dias = len(resultados)
        
        for dia, tabelas in resultados.items():
            for tipo in tabelas.keys():
                contadores[tipo] += 1
        
        print(f"📊 TAXA DE SUCESSO POR TABELA:")
        print("-" * 50)
        for tipo, config in self.padroes_tabelas.items():
            sucesso = contadores[tipo]
            taxa = (sucesso / total_dias) * 100 if total_dias > 0 else 0
            print(f"  {tipo:12} | {sucesso:2d}/{total_dias} dias | {taxa:5.1f}% | {config['descricao']}")
        
        # Dias com melhor cobertura
        print(f"\n📅 COBERTURA POR DIA:")
        print("-" * 30)
        for dia, tabelas in resultados.items():
            cobertura = len(tabelas)
            print(f"  Dia {dia} | {cobertura}/5 tabelas")
        
        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES:")
        for tipo, count in contadores.items():
            if count < total_dias:
                print(f"  ⚠️  Melhorar detecção de {tipo} - {self.padroes_tabelas[tipo]['descricao']}")

if __name__ == "__main__":
    extrator = ExtratorTabelasPadrao()
    
    print("🚀 INICIANDO EXTRAÇÃO DAS 5 TABELAS PADRÃO")
    
    # Testar em múltiplos dias
    resultados = extrator.testar_multiplos_dias()
    
    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO")
    print("=" * 80)
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Ajustar padrões de detecção conforme necessário")
    print("2. Implementar extração para todas as lojas")
    print("3. Criar base de dados consolidada")