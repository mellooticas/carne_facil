#!/usr/bin/env python3
"""
EXTRATOR VEND CORRIGIDO - TABELA ESTRUTURADA
Procura pela tabela real de vendas com as colunas corretas:
Nº Venda | Cliente | Forma de Pgto | Valor Venda | Entrada
"""

import pandas as pd
from pathlib import Path
import openpyxl
from datetime import datetime
import re
from typing import Dict, List, Optional

class ExtratorVendCorreto:
    def __init__(self):
        self.pasta_caixa = Path("data/caixa_lojas")
        self.arquivo_exemplo = self.pasta_caixa / "MAUA/2024_MAU/abr_24.xlsx"
        self.vendas_extraidas = []
    
    def investigar_estrutura_aba(self, aba: str = "20"):
        """Investiga a estrutura da aba para encontrar a tabela correta"""
        print("=" * 80)
        print(f"🔍 INVESTIGANDO ESTRUTURA DA ABA {aba}")
        print("=" * 80)
        
        try:
            df = pd.read_excel(self.arquivo_exemplo, sheet_name=aba, header=None)
            print(f"📏 Dimensões da aba: {df.shape[0]} linhas × {df.shape[1]} colunas")
            
            # Procurar pela tabela de vendas estruturada
            for i, row in df.iterrows():
                linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
                linha_upper = linha_texto.upper()
                
                # Procurar cabeçalho da tabela de vendas
                if all(col in linha_upper for col in ['Nº VENDA', 'CLIENTE', 'FORMA', 'PGTO', 'VALOR']):
                    print(f"✅ TABELA DE VENDAS ENCONTRADA na linha {i}!")
                    print(f"📋 Cabeçalho: {linha_texto}")
                    
                    # Mostrar algumas linhas após o cabeçalho
                    print(f"\n📊 DADOS DA TABELA (próximas 10 linhas):")
                    for j in range(i + 1, min(i + 11, len(df))):
                        valores = [cell for cell in df.iloc[j] if pd.notna(cell)]
                        if valores:
                            print(f"   Linha {j}: {valores}")
                    
                    return i
            
            print("❌ Tabela de vendas não encontrada com padrão esperado")
            
            # Mostrar estrutura geral para debug
            print(f"\n🔍 ESTRUTURA GERAL DA ABA:")
            for i in range(min(30, len(df))):
                linha_texto = " ".join([str(cell) for cell in df.iloc[i] if pd.notna(cell)])
                if linha_texto.strip():
                    print(f"   Linha {i}: {linha_texto[:100]}...")
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao investigar aba {aba}: {e}")
            return None
    
    def extrair_vendas_tabela_estruturada(self, aba: str = "20"):
        """Extrai vendas da tabela estruturada correta"""
        print("=" * 80)
        print(f"💰 EXTRAINDO VENDAS DA TABELA ESTRUTURADA - ABA {aba}")
        print("=" * 80)
        
        try:
            df = pd.read_excel(self.arquivo_exemplo, sheet_name=aba, header=None)
            
            # Encontrar linha do cabeçalho
            linha_cabecalho = None
            for i, row in df.iterrows():
                linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
                linha_upper = linha_texto.upper()
                
                if all(col in linha_upper for col in ['Nº VENDA', 'CLIENTE', 'FORMA', 'PGTO', 'VALOR']):
                    linha_cabecalho = i
                    print(f"✅ Cabeçalho encontrado na linha {i}")
                    break
            
            if linha_cabecalho is None:
                print("❌ Cabeçalho da tabela não encontrado")
                return []
            
            # Identificar colunas
            cabecalho_row = df.iloc[linha_cabecalho]
            mapeamento_colunas = self.identificar_colunas(cabecalho_row)
            print(f"📋 Mapeamento de colunas: {mapeamento_colunas}")
            
            # Extrair dados da tabela
            vendas = []
            info_arquivo = self.identificar_arquivo()
            
            for i in range(linha_cabecalho + 1, len(df)):
                row = df.iloc[i]
                venda = self.extrair_linha_tabela_estruturada(row, mapeamento_colunas, aba, info_arquivo, i)
                
                if venda:
                    vendas.append(venda)
                    print(f"   💰 Venda: {venda['numero_venda']} - {venda['cliente']} - {venda['forma_pgto']} - R$ {venda['valor_venda']}")
                elif self.e_fim_tabela(row):
                    print(f"   🔚 Fim da tabela detectado na linha {i}")
                    break
            
            print(f"\n✅ Total extraído: {len(vendas)} vendas")
            return vendas
            
        except Exception as e:
            print(f"❌ Erro ao extrair vendas: {e}")
            return []
    
    def identificar_colunas(self, cabecalho_row) -> Dict:
        """Identifica posição das colunas no cabeçalho"""
        mapeamento = {}
        
        # Debug: mostrar todas as células do cabeçalho
        print(f"🔍 Células do cabeçalho:")
        for i, cell in enumerate(cabecalho_row):
            if pd.notna(cell):
                print(f"   Coluna {i}: '{cell}'")
        
        for i, cell in enumerate(cabecalho_row):
            if pd.notna(cell):
                cell_upper = str(cell).upper()
                
                if 'Nº VENDA' in cell_upper:
                    mapeamento['numero_venda'] = i
                elif 'CLIENTE' in cell_upper:
                    mapeamento['cliente'] = i
                elif 'FORMA' in cell_upper and 'PGTO' in cell_upper:
                    mapeamento['forma_pgto'] = i
                elif 'VALOR' in cell_upper and 'VENDA' in cell_upper:
                    mapeamento['valor_venda'] = i
                elif 'ENTRADA' in cell_upper:
                    mapeamento['entrada'] = i
        
        print(f"📋 Mapeamento identificado: {mapeamento}")
        return mapeamento
    
    def extrair_linha_tabela_estruturada(self, row, mapeamento: Dict, aba: str, info_arquivo: Dict, linha_idx: int) -> Optional[Dict]:
        """Extrai dados de uma linha da tabela estruturada"""
        # Verificar se linha tem dados válidos
        valores_nao_nulos = [cell for cell in row if pd.notna(cell)]
        if len(valores_nao_nulos) < 2:
            return None
        
        # Extrair dados usando mapeamento de colunas
        numero_venda = self.extrair_valor_coluna(row, mapeamento.get('numero_venda'))
        cliente = self.extrair_valor_coluna(row, mapeamento.get('cliente'))
        forma_pgto = self.extrair_valor_coluna(row, mapeamento.get('forma_pgto'))
        valor_venda = self.extrair_valor_monetario(row, mapeamento.get('valor_venda'))
        entrada = self.extrair_valor_monetario(row, mapeamento.get('entrada'))
        
        # Validar se é linha de venda válida
        if not numero_venda or not str(numero_venda).isdigit():
            return None
        
        # Aplicar regras de negócio
        # SS = sem sinal, valor = 0
        if forma_pgto and forma_pgto.upper() == 'SS':
            valor_venda = 0
        
        # GARANTIA = não gera valores
        if forma_pgto and forma_pgto.upper() == 'GARANTIA':
            valor_venda = 0
            entrada = 0
        
        # Construir data
        data_completa = self.construir_data(aba, info_arquivo)
        
        # ORDEM CORRETA: Loja, Data, Nº Venda, Cliente, Forma Pgto, Valor Venda, Entrada
        venda = {
            'loja': info_arquivo['loja'],
            'data': data_completa,
            'numero_venda': str(numero_venda),
            'cliente': cliente or '',
            'forma_pgto': forma_pgto or '',
            'valor_venda': valor_venda or 0,
            'entrada': entrada or 0
        }
        
        return venda
    
    def extrair_valor_coluna(self, row, coluna_idx: Optional[int]) -> Optional[str]:
        """Extrai valor de uma coluna específica"""
        if coluna_idx is None or coluna_idx >= len(row):
            return None
        
        valor = row.iloc[coluna_idx] if hasattr(row, 'iloc') else row[coluna_idx]
        
        if pd.notna(valor):
            return str(valor).strip()
        return None
    
    def extrair_valor_monetario(self, row, coluna_idx: Optional[int]) -> Optional[float]:
        """Extrai valor monetário de uma coluna com formatação brasileira"""
        valor_str = self.extrair_valor_coluna(row, coluna_idx)
        
        if not valor_str:
            return 0
        
        # Limpar formato monetário brasileiro
        valor_limpo = valor_str.replace('R$', '').strip()
        
        # Debug: mostrar valor original
        if valor_limpo and valor_limpo != '0':
            print(f"      🔍 Valor original: '{valor_str}' -> '{valor_limpo}'")
        
        try:
            # Se contém vírgula, tratar como formato brasileiro (999,99)
            if ',' in valor_limpo:
                # Se tem ponto E vírgula: 1.234,56 -> 1234.56
                if '.' in valor_limpo and ',' in valor_limpo:
                    valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
                # Se tem apenas vírgula: 234,56 -> 234.56
                else:
                    valor_limpo = valor_limpo.replace(',', '.')
            # Se tem apenas ponto, verificar se é milhar ou decimal
            elif '.' in valor_limpo:
                partes = valor_limpo.split('.')
                # Se a última parte tem 2 dígitos, é decimal (123.45)
                if len(partes[-1]) == 2:
                    pass  # Já está correto
                # Se tem mais de 2 dígitos, é separador de milhar (1.234)
                else:
                    valor_limpo = valor_limpo.replace('.', '')
            
            valor_float = float(valor_limpo)
            
            # Debug: mostrar conversão
            if valor_float > 0:
                print(f"         💰 Convertido para: R$ {valor_float:,.2f}")
            
            return valor_float
            
        except ValueError as e:
            print(f"         ❌ Erro ao converter '{valor_str}': {e}")
            return 0
    
    def e_fim_tabela(self, row) -> bool:
        """Verifica se chegou ao fim da tabela"""
        valores_nao_nulos = [cell for cell in row if pd.notna(cell)]
        
        if not valores_nao_nulos:
            return True
        
        # Verificar se é linha de total
        linha_texto = " ".join([str(cell) for cell in valores_nao_nulos])
        linha_upper = linha_texto.upper()
        
        if any(keyword in linha_upper for keyword in ['TOTAL', 'SOMA', 'SUBTOTAL']):
            return True
        
        return False
    
    def identificar_arquivo(self) -> Dict:
        """Identifica informações do arquivo"""
        partes_path = self.arquivo_exemplo.parts
        
        loja = "MAUA"
        for parte in partes_path:
            if parte.upper() in ['MAUA', 'SUZANO', 'RIO_PEQUENO']:
                loja = parte.upper()
                break
        
        nome_arquivo = self.arquivo_exemplo.stem
        mes, ano = nome_arquivo.split('_')
        periodo = f"20{ano}_{mes.upper()}"
        
        return {
            'loja': loja,
            'periodo': periodo,
            'ano': f"20{ano}",
            'mes': mes.upper(),
            'arquivo_nome': self.arquivo_exemplo.name
        }
    
    def construir_data(self, aba: str, info_arquivo: Dict) -> str:
        """Constrói data completa"""
        dia = aba.zfill(2)
        
        meses = {
            'JAN': '01', 'FEV': '02', 'MAR': '03', 'ABR': '04',
            'MAI': '05', 'JUN': '06', 'JUL': '07', 'AGO': '08',
            'SET': '09', 'OUT': '10', 'NOV': '11', 'DEZ': '12'
        }
        
        mes_num = meses.get(info_arquivo['mes'], '01')
        ano = info_arquivo['ano']
        
        return f"{ano}-{mes_num}-{dia}"
    
    def salvar_vendas_corretas(self, vendas: List[Dict], info_arquivo: Dict):
        """Salva vendas corretas em arquivo Excel"""
        if not vendas:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_saida = self.pasta_caixa / f"VENDAS_CORRETAS_{info_arquivo['loja']}_{info_arquivo['periodo']}_{timestamp}.xlsx"
        
        try:
            # Debug: mostrar estrutura antes de salvar
            print(f"\n🔍 DEBUG - Estrutura dos dados antes de salvar:")
            if vendas:
                print(f"📋 Primeira venda: {vendas[0]}")
                print(f"📋 Colunas: {list(vendas[0].keys())}")
            
            df_vendas = pd.DataFrame(vendas)
            
            # Garantir ordem correta das colunas
            colunas_ordem = ['loja', 'data', 'numero_venda', 'cliente', 'forma_pgto', 'valor_venda', 'entrada']
            df_vendas = df_vendas[colunas_ordem]
            
            print(f"📊 DataFrame criado:")
            print(f"   Colunas: {list(df_vendas.columns)}")
            print(f"   Shape: {df_vendas.shape}")
            
            df_vendas.to_excel(arquivo_saida, index=False, sheet_name='VENDAS_CORRETAS')
            
            print(f"\n💾 Vendas corretas salvas: {arquivo_saida}")
            print(f"📄 Arquivo contém {len(vendas)} vendas com colunas: {list(df_vendas.columns)}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            import traceback
            traceback.print_exc()
    
    def processar_arquivo_completo(self):
        """Processa todas as abas do arquivo completo"""
        print("🚀 PROCESSAMENTO COMPLETO DO ARQUIVO")
        print("=" * 80)
        
        # Identificar arquivo
        info_arquivo = self.identificar_arquivo()
        print(f"🏪 Loja: {info_arquivo['loja']}")
        print(f"📅 Período: {info_arquivo['periodo']}")
        
        # Listar todas as abas
        try:
            workbook = openpyxl.load_workbook(self.arquivo_exemplo, read_only=True)
            todas_abas = workbook.sheetnames
            workbook.close()
            
            print(f"📄 Total de abas encontradas: {len(todas_abas)}")
            print(f"📋 Abas: {todas_abas}")
            
        except Exception as e:
            print(f"❌ Erro ao listar abas: {e}")
            return []
        
        # Filtrar apenas abas de dias (números)
        abas_dias = [aba for aba in todas_abas if aba.isdigit()]
        abas_dias.sort(key=int)  # Ordenar numericamente
        
        print(f"📅 Abas de dias para processar: {len(abas_dias)}")
        print(f"📋 Dias: {abas_dias}")
        
        # Processar cada aba
        todas_vendas = []
        abas_processadas = 0
        abas_com_vendas = 0
        erros_processamento = []
        
        for aba in abas_dias:
            print(f"\n📃 Processando aba: {aba}")
            
            try:
                vendas_aba = self.extrair_vendas_tabela_estruturada(aba)
                
                if vendas_aba:
                    todas_vendas.extend(vendas_aba)
                    abas_com_vendas += 1
                    print(f"   ✅ {len(vendas_aba)} vendas extraídas")
                    
                    # Mostrar primeira venda como exemplo
                    if vendas_aba:
                        primeira = vendas_aba[0]
                        print(f"      💰 Exemplo: {primeira['numero_venda']} - {primeira['cliente']} - R$ {primeira['valor_venda']}")
                else:
                    print(f"   ⚠️  Nenhuma venda encontrada")
                
                abas_processadas += 1
                
            except Exception as e:
                erro_msg = f"Aba {aba}: {str(e)}"
                erros_processamento.append(erro_msg)
                print(f"   ❌ Erro: {e}")
        
        # Relatório final do processamento
        print(f"\n" + "=" * 80)
        print(f"� RELATÓRIO FINAL DO PROCESSAMENTO COMPLETO")
        print("=" * 80)
        
        print(f"📄 Abas processadas: {abas_processadas}/{len(abas_dias)}")
        print(f"📈 Abas com vendas: {abas_com_vendas}")
        print(f"💰 Total de vendas extraídas: {len(todas_vendas)}")
        
        if erros_processamento:
            print(f"\n❌ Erros encontrados ({len(erros_processamento)}):")
            for erro in erros_processamento[:5]:  # Mostrar apenas primeiros 5
                print(f"   - {erro}")
            if len(erros_processamento) > 5:
                print(f"   ... e mais {len(erros_processamento) - 5} erros")
        
        # Salvar todas as vendas se houver
        if todas_vendas:
            self.salvar_vendas_arquivo_completo(todas_vendas, info_arquivo)
            self.gerar_relatorio_arquivo_completo(todas_vendas)
        
        return todas_vendas
    
    def salvar_vendas_arquivo_completo(self, vendas: List[Dict], info_arquivo: Dict):
        """Salva vendas do arquivo completo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_saida = self.pasta_caixa / f"VENDAS_ARQUIVO_COMPLETO_{info_arquivo['loja']}_{info_arquivo['periodo']}_{timestamp}.xlsx"
        
        try:
            # Garantir ordem correta das colunas
            colunas_ordem = ['loja', 'data', 'numero_venda', 'cliente', 'forma_pgto', 'valor_venda', 'entrada']
            df_vendas = pd.DataFrame(vendas)
            df_vendas = df_vendas[colunas_ordem]
            
            # Ordenar por data e numero_venda
            df_vendas['data'] = pd.to_datetime(df_vendas['data'])
            df_vendas = df_vendas.sort_values(['data', 'numero_venda'])
            df_vendas['data'] = df_vendas['data'].dt.strftime('%Y-%m-%d')
            
            df_vendas.to_excel(arquivo_saida, index=False, sheet_name='VENDAS_COMPLETAS')
            
            print(f"\n💾 Arquivo completo salvo: {arquivo_saida}")
            print(f"📊 {len(vendas)} vendas do período completo")
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo completo: {e}")
            import traceback
            traceback.print_exc()
    
    def gerar_relatorio_arquivo_completo(self, vendas: List[Dict]):
        """Gera relatório detalhado do arquivo completo"""
        print(f"\n" + "=" * 60)
        print(f"📈 RELATÓRIO DETALHADO - ARQUIVO COMPLETO")
        print("=" * 60)
        
        # Estatísticas gerais
        total_vendas = len(vendas)
        valor_total = sum(venda['valor_venda'] for venda in vendas)
        entrada_total = sum(venda['entrada'] for venda in vendas)
        
        print(f"📊 Total de vendas: {total_vendas}")
        print(f"💰 Valor total: R$ {valor_total:,.2f}")
        print(f"💵 Entradas total: R$ {entrada_total:,.2f}")
        print(f"📉 Média por venda: R$ {valor_total/total_vendas:,.2f}" if total_vendas > 0 else "")
        
        # Período analisado
        datas_unicas = sorted(set(venda['data'] for venda in vendas))
        if datas_unicas:
            print(f"\n📅 Período: {datas_unicas[0]} a {datas_unicas[-1]}")
            print(f"📅 Dias com vendas: {len(datas_unicas)}")
        
        # Formas de pagamento
        formas_pgto = {}
        valores_por_forma = {}
        
        for venda in vendas:
            forma = venda['forma_pgto'] or 'Não informado'
            formas_pgto[forma] = formas_pgto.get(forma, 0) + 1
            valores_por_forma[forma] = valores_por_forma.get(forma, 0) + venda['valor_venda']
        
        print(f"\n💳 Formas de pagamento:")
        for forma, count in sorted(formas_pgto.items(), key=lambda x: x[1], reverse=True):
            valor_forma = valores_por_forma[forma]
            print(f"   {forma}: {count} vendas (R$ {valor_forma:,.2f})")
        
        # Top clientes
        vendas_por_cliente = {}
        for venda in vendas:
            cliente = venda['cliente'] or 'Não informado'
            if cliente not in vendas_por_cliente:
                vendas_por_cliente[cliente] = {'count': 0, 'valor': 0}
            vendas_por_cliente[cliente]['count'] += 1
            vendas_por_cliente[cliente]['valor'] += venda['valor_venda']
        
        top_clientes = sorted(vendas_por_cliente.items(), 
                             key=lambda x: x[1]['valor'], reverse=True)[:10]
        
        print(f"\n👥 Top 10 clientes:")
        for cliente, dados in top_clientes:
            print(f"   {cliente}: {dados['count']} vendas (R$ {dados['valor']:,.2f})")
        
        # Vendas por dia
        vendas_por_dia = {}
        for venda in vendas:
            data = venda['data']
            if data not in vendas_por_dia:
                vendas_por_dia[data] = {'count': 0, 'valor': 0}
            vendas_por_dia[data]['count'] += 1
            vendas_por_dia[data]['valor'] += venda['valor_venda']
        
        if vendas_por_dia:
            dia_mais_vendas = max(vendas_por_dia.items(), key=lambda x: x[1]['count'])
            dia_maior_valor = max(vendas_por_dia.items(), key=lambda x: x[1]['valor'])
            
            print(f"\n📈 Dia com mais vendas: {dia_mais_vendas[0]} ({dia_mais_vendas[1]['count']} vendas)")
            print(f"💰 Dia com maior valor: {dia_maior_valor[0]} (R$ {dia_maior_valor[1]['valor']:,.2f})")
    
    def gerar_relatorio_correto(self, vendas: List[Dict]):
        """Gera relatório das vendas corretas"""
        print(f"\n" + "=" * 60)
        print(f"📈 RELATÓRIO VENDAS CORRETAS")
        print("=" * 60)
        
        total_vendas = len(vendas)
        valor_total = sum(venda['valor_venda'] for venda in vendas)
        entrada_total = sum(venda['entrada'] for venda in vendas)
        
        print(f"📊 Total de vendas: {total_vendas}")
        print(f"💰 Valor total: R$ {valor_total:,.2f}")
        print(f"💵 Entradas total: R$ {entrada_total:,.2f}")
        
        # Formas de pagamento
        formas = {}
        for venda in vendas:
            forma = venda['forma_pgto'] or 'Não informado'
            formas[forma] = formas.get(forma, 0) + 1
        
        print(f"\n💳 Formas de pagamento:")
        for forma, count in formas.items():
            print(f"   {forma}: {count} vendas")

if __name__ == "__main__":
    extrator = ExtratorVendCorreto()
    
    print("🚀 TESTE COMPLETO COM FORMATAÇÃO CORRIGIDA")
    print("📁 Processando arquivo completo para verificar totais")
    
    # Processar arquivo completo com formatação corrigida
    vendas_completas = extrator.processar_arquivo_completo()
    
    print("\n" + "=" * 80)
    print("✅ PROCESSAMENTO COMPLETO CONCLUÍDO COM FORMATAÇÃO BRASILEIRA")
    print("=" * 80)
    
    if vendas_completas:
        print(f"🎉 Sucesso! {len(vendas_completas)} vendas extraídas do arquivo completo")
    else:
        print("⚠️  Nenhuma venda foi extraída")