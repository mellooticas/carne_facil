#!/usr/bin/env python3
"""
INVESTIGADOR DE TABELAS POR PÁGINA
Analisa cada aba diária para identificar as diferentes tabelas/seções
"""

import pandas as pd
from pathlib import Path
import openpyxl
from datetime import datetime
import re
from typing import Dict, List, Tuple

class InvestigadorTabelasPagina:
    def __init__(self):
        self.pasta_caixa = Path("data/caixa_lojas")
        self.arquivo_exemplo = self.pasta_caixa / "MAUA/2024_MAU/abr_24.xlsx"
        self.tabelas_identificadas = {}
        
    def analisar_estrutura_pagina(self, aba: str = "04"):
        """Analisa a estrutura de uma página específica (ex: dia 4)"""
        print("=" * 80)
        print(f"🔍 INVESTIGAÇÃO DA PÁGINA: DIA {aba}")
        print("=" * 80)
        
        if not self.arquivo_exemplo.exists():
            print(f"❌ Arquivo não encontrado: {self.arquivo_exemplo}")
            return
        
        try:
            # Ler a aba específica
            df = pd.read_excel(self.arquivo_exemplo, sheet_name=aba, header=None)
            print(f"📏 Dimensões da página: {df.shape[0]} linhas × {df.shape[1]} colunas")
            
            # Identificar seções/tabelas
            secoes = self.identificar_secoes(df)
            
            # Analisar cada seção
            for i, secao in enumerate(secoes, 1):
                print(f"\n📋 SEÇÃO {i}: {secao['nome']}")
                print(f"   📍 Localização: Linhas {secao['inicio']} a {secao['fim']}")
                print(f"   📊 Dados: {secao['dados'].shape[0]} linhas × {secao['dados'].shape[1]} colunas")
                
                # Mostrar amostra dos dados
                self.mostrar_amostra_secao(secao)
                
                # Salvar para análise posterior
                self.tabelas_identificadas[f"dia_{aba}_{secao['nome']}"] = secao
            
            return secoes
            
        except Exception as e:
            print(f"❌ Erro ao analisar página: {e}")
            return []
    
    def identificar_secoes(self, df: pd.DataFrame) -> List[Dict]:
        """Identifica seções/tabelas na página"""
        secoes = []
        secao_atual = None
        
        for i, row in df.iterrows():
            # Procurar por cabeçalhos/títulos de seção
            linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
            linha_texto_upper = linha_texto.upper()
            
            # Identificar início de novas seções
            if any(keyword in linha_texto_upper for keyword in [
                'FECHAMENTO DIÁRIO', 'SALDO INICIAL', 'VENDAS', 'ENTRADA', 
                'DESPESAS', 'TIPOS DE PAGTO', 'RESTANTE', 'RECEBIMENTO'
            ]):
                # Finalizar seção anterior
                if secao_atual:
                    secao_atual['fim'] = i - 1
                    secao_atual['dados'] = df.iloc[secao_atual['inicio']:i]
                    secoes.append(secao_atual)
                
                # Iniciar nova seção
                secao_atual = {
                    'nome': self.classificar_secao(linha_texto),
                    'inicio': i,
                    'fim': None,
                    'dados': None,
                    'linha_titulo': linha_texto
                }
        
        # Finalizar última seção
        if secao_atual:
            secao_atual['fim'] = len(df) - 1
            secao_atual['dados'] = df.iloc[secao_atual['inicio']:]
            secoes.append(secao_atual)
        
        return secoes
    
    def classificar_secao(self, linha_texto: str) -> str:
        """Classifica o tipo de seção baseado no texto"""
        linha_upper = linha_texto.upper()
        
        if 'FECHAMENTO DIÁRIO' in linha_upper:
            return 'CABECALHO'
        elif 'SALDO INICIAL' in linha_upper:
            return 'SALDO_INICIAL'
        elif 'VENDAS' in linha_upper and 'Nº VENDA' in linha_upper:
            return 'VENDAS_DIA'
        elif 'ENTRADA' in linha_upper or 'TOTAL' in linha_upper:
            return 'ENTRADAS_TOTAIS'
        elif 'DESPESAS' in linha_upper:
            return 'DESPESAS_DIA'
        elif 'TIPOS DE PAGTO' in linha_upper:
            return 'TIPOS_PAGAMENTO'
        elif 'RESTANTE' in linha_upper or 'REST' in linha_upper:
            return 'RESTANTES_ENTRADA'
        elif 'RECEBIMENTO' in linha_upper or 'CARNÊ' in linha_upper:
            return 'RECEBIMENTO_CARNE'
        elif 'OS' in linha_upper and 'ENTREGUE' in linha_upper:
            return 'OS_ENTREGUES'
        else:
            return 'OUTRAS'
    
    def mostrar_amostra_secao(self, secao: Dict):
        """Mostra amostra dos dados de uma seção"""
        dados = secao['dados']
        
        # Filtrar linhas com dados
        dados_filtrados = dados.dropna(how='all')
        
        if len(dados_filtrados) > 0:
            print(f"   📋 Linha de título: {secao['linha_titulo']}")
            
            # Mostrar algumas linhas de dados
            print(f"   📊 Amostra (primeiras 3 linhas com dados):")
            for idx, (i, row) in enumerate(dados_filtrados.head(3).iterrows()):
                valores = [str(val) for val in row if pd.notna(val)]
                if valores:
                    print(f"      {idx+1}. {' | '.join(valores)}")
        else:
            print(f"   📭 Seção sem dados visíveis")
    
    def analisar_multiplas_paginas(self, dias: List[str] = None):
        """Analisa múltiplas páginas para identificar padrões"""
        if dias is None:
            dias = ["01", "04", "15", "30"]  # Amostra de dias
        
        print("=" * 80)
        print("🔍 ANÁLISE COMPARATIVA DE MÚLTIPLAS PÁGINAS")
        print("=" * 80)
        
        padroes_encontrados = {}
        
        for dia in dias:
            print(f"\n📅 Analisando dia {dia}...")
            try:
                secoes = self.analisar_estrutura_pagina(dia)
                
                # Catalogar tipos de seções encontradas
                for secao in secoes:
                    tipo = secao['nome']
                    if tipo not in padroes_encontrados:
                        padroes_encontrados[tipo] = []
                    padroes_encontrados[tipo].append({
                        'dia': dia,
                        'linhas': secao['dados'].shape[0] if secao['dados'] is not None else 0,
                        'exemplo': secao['linha_titulo']
                    })
                    
            except Exception as e:
                print(f"   ❌ Erro no dia {dia}: {e}")
        
        # Mostrar padrões identificados
        self.mostrar_padroes_identificados(padroes_encontrados)
        
        return padroes_encontrados
    
    def mostrar_padroes_identificados(self, padroes: Dict):
        """Mostra os padrões identificados em todas as páginas"""
        print("\n" + "=" * 80)
        print("📊 PADRÕES IDENTIFICADOS EM TODAS AS PÁGINAS")
        print("=" * 80)
        
        print("\n🎯 TIPOS DE TABELAS ENCONTRADAS:")
        print("-" * 50)
        
        for tipo, ocorrencias in padroes.items():
            print(f"\n📋 {tipo}:")
            print(f"   🔢 Ocorrências: {len(ocorrencias)} páginas")
            print(f"   📏 Média de linhas: {sum(o['linhas'] for o in ocorrencias) / len(ocorrencias):.1f}")
            print(f"   📝 Exemplo: {ocorrencias[0]['exemplo']}")
            
            # Mostrar em quais dias aparece
            dias_com_tipo = [o['dia'] for o in ocorrencias]
            print(f"   📅 Dias: {', '.join(dias_com_tipo)}")
    
    def investigar_tabela_especifica(self, dia: str, nome_tabela: str):
        """Investiga uma tabela específica em detalhes"""
        print("=" * 80)
        print(f"🔬 INVESTIGAÇÃO DETALHADA: {nome_tabela.upper()} - DIA {dia}")
        print("=" * 80)
        
        chave_tabela = f"dia_{dia}_{nome_tabela}"
        if chave_tabela not in self.tabelas_identificadas:
            print(f"❌ Tabela não encontrada. Execute analisar_estrutura_pagina('{dia}') primeiro")
            return
        
        secao = self.tabelas_identificadas[chave_tabela]
        dados = secao['dados']
        
        print(f"📍 Localização: Linhas {secao['inicio']} a {secao['fim']}")
        print(f"📏 Dimensões: {dados.shape[0]} linhas × {dados.shape[1]} colunas")
        
        # Analisar estrutura de colunas
        print(f"\n📋 ESTRUTURA DE COLUNAS:")
        print("-" * 50)
        
        for i, col in enumerate(dados.columns):
            valores_nao_nulos = dados[col].dropna()
            if len(valores_nao_nulos) > 0:
                tipos_encontrados = set(type(val).__name__ for val in valores_nao_nulos)
                print(f"  {i+1:2d}. Coluna {col}: {len(valores_nao_nulos)} valores | Tipos: {', '.join(tipos_encontrados)}")
                
                # Mostrar alguns valores de exemplo
                exemplos = valores_nao_nulos.head(3).tolist()
                print(f"      Exemplos: {exemplos}")
        
        # Mostrar dados completos (limitado)
        print(f"\n📊 DADOS COMPLETOS:")
        print("-" * 50)
        dados_limpos = dados.dropna(how='all')
        if len(dados_limpos) > 0:
            print(dados_limpos.head(10).to_string())
        else:
            print("Nenhum dado encontrado")
    
    def salvar_investigacao(self):
        """Salva os resultados da investigação"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_saida = self.pasta_caixa / f"INVESTIGACAO_TABELAS_PAGINA_{timestamp}.xlsx"
        
        try:
            with pd.ExcelWriter(arquivo_saida, engine='openpyxl') as writer:
                for nome_tabela, secao in self.tabelas_identificadas.items():
                    if secao['dados'] is not None and not secao['dados'].empty:
                        secao['dados'].to_excel(writer, sheet_name=nome_tabela[:31], index=False)
            
            print(f"\n💾 Investigação salva: {arquivo_saida}")
            return str(arquivo_saida)
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            return ""

if __name__ == "__main__":
    investigador = InvestigadorTabelasPagina()
    
    print("🚀 INICIANDO INVESTIGAÇÃO DE TABELAS POR PÁGINA")
    
    # Analisar padrões em múltiplas páginas
    padroes = investigador.analisar_multiplas_paginas(["01", "04", "15", "20", "30"])
    
    # Salvar resultados
    investigador.salvar_investigacao()
    
    print("\n" + "=" * 80)
    print("✅ INVESTIGAÇÃO CONCLUÍDA")
    print("=" * 80)
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Identificar as 5 tabelas principais (vendas, restantes, recebimentos, etc.)")
    print("2. Criar extrator específico para cada tipo de tabela")
    print("3. Padronizar dados de todas as lojas")