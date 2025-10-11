#!/usr/bin/env python3
"""
EXTRATOR DE DADOS DE CAIXA
Extrai e padroniza dados de todas as planilhas de caixa das 6 lojas
"""

import pandas as pd
from pathlib import Path
import openpyxl
from datetime import datetime, timedelta
import re
from typing import Dict, List, Tuple

class ExtratorDadosCaixa:
    def __init__(self):
        self.pasta_caixa = Path("data/caixa_lojas")
        self.dados_extraidos = []
        self.resumo_extraido = []
        self.prefixos_lojas = {
            'MAUA': 'MAU',
            'PERUS': 'PER', 
            'RIO_PEQUENO': 'RIO',
            'SAO_MATEUS': 'SAM',
            'SUZANO': 'SUZ',
            'SUZANO2': 'SU2'
        }
        
    def processar_todas_lojas(self):
        """Processa dados de caixa de todas as lojas"""
        print("=" * 80)
        print("🏪 EXTRAÇÃO DE DADOS DE CAIXA - TODAS AS LOJAS")
        print("=" * 80)
        
        total_arquivos = 0
        total_transacoes = 0
        
        for loja_dir in self.pasta_caixa.iterdir():
            if loja_dir.is_dir() and loja_dir.name in self.prefixos_lojas:
                print(f"\n🏪 Processando loja: {loja_dir.name}")
                
                arquivos_processados, transacoes_loja = self.processar_loja(loja_dir)
                total_arquivos += arquivos_processados
                total_transacoes += transacoes_loja
                
        print(f"\n📊 RESUMO GERAL:")
        print(f"  🏪 Lojas processadas: {len([d for d in self.pasta_caixa.iterdir() if d.is_dir() and d.name in self.prefixos_lojas])}")
        print(f"  📄 Arquivos processados: {total_arquivos}")
        print(f"  💰 Total de transações: {total_transacoes}")
        
        return self.salvar_dados_consolidados()
    
    def processar_loja(self, loja_dir: Path) -> Tuple[int, int]:
        """Processa todos os arquivos de uma loja"""
        prefixo = self.prefixos_lojas[loja_dir.name]
        arquivos_processados = 0
        transacoes_loja = 0
        
        # Procurar pastas por ano
        for ano_dir in loja_dir.iterdir():
            if ano_dir.is_dir() and ano_dir.name.startswith(("2024", "2023")):
                print(f"  📅 Processando: {ano_dir.name}")
                
                for arquivo in ano_dir.glob("*.xlsx"):
                    print(f"    📄 {arquivo.name}")
                    
                    try:
                        transacoes = self.extrair_dados_arquivo(arquivo, loja_dir.name, prefixo)
                        transacoes_loja += len(transacoes)
                        arquivos_processados += 1
                        
                    except Exception as e:
                        print(f"    ❌ Erro: {e}")
        
        print(f"  ✅ {arquivos_processados} arquivos | {transacoes_loja} transações")
        return arquivos_processados, transacoes_loja
    
    def extrair_dados_arquivo(self, arquivo: Path, loja: str, prefixo: str) -> List[Dict]:
        """Extrai dados de um arquivo de caixa"""
        transacoes = []
        
        # Determinar mês/ano do arquivo
        nome_arquivo = arquivo.stem
        mes_ano = self.parse_mes_ano(nome_arquivo)
        
        try:
            # Ler todas as abas
            xl_file = pd.ExcelFile(arquivo)
            
            # Processar resumo
            if "resumo_cx" in xl_file.sheet_names:
                self.extrair_resumo_mensal(arquivo, loja, prefixo, mes_ano)
            
            # Processar abas diárias (01 a 31)
            for sheet_name in xl_file.sheet_names:
                if re.match(r'^\d{1,2}$', sheet_name):  # Abas numéricas (dias)
                    dia = int(sheet_name)
                    transacoes_dia = self.extrair_transacoes_dia(
                        arquivo, sheet_name, loja, prefixo, mes_ano, dia
                    )
                    transacoes.extend(transacoes_dia)
            
        except Exception as e:
            print(f"      ❌ Erro ao processar {arquivo.name}: {e}")
            
        return transacoes
    
    def extrair_transacoes_dia(self, arquivo: Path, aba: str, loja: str, 
                              prefixo: str, mes_ano: str, dia: int) -> List[Dict]:
        """Extrai transações de uma aba diária"""
        transacoes = []
        
        try:
            df = pd.read_excel(arquivo, sheet_name=aba, header=None)
            
            # Procurar seção de vendas
            vendas_inicio = None
            for i, row in df.iterrows():
                if any("Nº Venda" in str(cell) for cell in row if pd.notna(cell)):
                    vendas_inicio = i
                    break
            
            if vendas_inicio is not None:
                # Extrair vendas
                for i in range(vendas_inicio + 1, len(df)):
                    row = df.iloc[i]
                    
                    # Parar se encontrar nova seção
                    if any("Despesas" in str(cell) or "Tipos de Pagtos" in str(cell) 
                          for cell in row if pd.notna(cell)):
                        break
                    
                    # Verificar se é uma venda válida
                    num_venda = row.iloc[2] if len(row) > 2 else None
                    if pd.notna(num_venda) and str(num_venda).isdigit():
                        transacao = self.criar_transacao(
                            row, loja, prefixo, mes_ano, dia, "VENDA"
                        )
                        if transacao:
                            transacoes.append(transacao)
            
            # Extrair outros tipos (despesas, entradas, etc.)
            transacoes.extend(self.extrair_outros_tipos(df, loja, prefixo, mes_ano, dia))
            
        except Exception as e:
            print(f"        ❌ Erro na aba {aba}: {e}")
            
        return transacoes
    
    def criar_transacao(self, row: pd.Series, loja: str, prefixo: str, 
                       mes_ano: str, dia: int, tipo: str) -> Dict:
        """Cria registro de transação padronizado"""
        try:
            data_transacao = self.criar_data(mes_ano, dia)
            
            transacao = {
                'id_transacao': f"{prefixo}_{mes_ano}_{dia:02d}_{len(self.dados_extraidos) + 1}",
                'loja': loja,
                'prefixo_loja': prefixo,
                'data_transacao': data_transacao,
                'mes_ano': mes_ano,
                'dia': dia,
                'tipo_transacao': tipo,
                'numero_venda': self.extrair_numero_venda(row),
                'cliente': self.extrair_cliente(row),
                'forma_pagamento': self.extrair_forma_pagamento(row),
                'valor_total': self.extrair_valor_total(row),
                'valor_entrada': self.extrair_valor_entrada(row),
                'os_relacionada': self.extrair_os(row),
                'observacoes': self.extrair_observacoes(row),
                'dados_brutos': str(row.to_dict())
            }
            
            return transacao
            
        except Exception as e:
            return None
    
    def extrair_numero_venda(self, row: pd.Series) -> str:
        """Extrai número da venda"""
        for val in row:
            if pd.notna(val) and str(val).isdigit() and len(str(val)) >= 4:
                return str(val)
        return ""
    
    def extrair_cliente(self, row: pd.Series) -> str:
        """Extrai nome do cliente"""
        for val in row:
            if pd.notna(val) and isinstance(val, str) and len(val) > 5:
                if not any(x in val.upper() for x in ['VENDA', 'PAGTO', 'ENTRADA', 'TOTAL']):
                    return val.strip()
        return ""
    
    def extrair_forma_pagamento(self, row: pd.Series) -> str:
        """Extrai forma de pagamento"""
        formas_conhecidas = ['DN', 'CTD', 'CTC', 'PIX', 'SS', 'GARANTIA']
        for val in row:
            if pd.notna(val) and str(val).upper() in formas_conhecidas:
                return str(val).upper()
        return ""
    
    def extrair_valor_total(self, row: pd.Series) -> float:
        """Extrai valor total"""
        for val in row:
            if pd.notna(val) and isinstance(val, (int, float)) and val > 0:
                return float(val)
        return 0.0
    
    def extrair_valor_entrada(self, row: pd.Series) -> float:
        """Extrai valor de entrada"""
        # Lógica similar ao valor total, mas pode ser em coluna específica
        return self.extrair_valor_total(row)
    
    def extrair_os(self, row: pd.Series) -> str:
        """Extrai número da OS relacionada"""
        for val in row:
            if pd.notna(val) and "OS" in str(val).upper():
                return str(val)
        return ""
    
    def extrair_observacoes(self, row: pd.Series) -> str:
        """Extrai observações adicionais"""
        obs = []
        for val in row:
            if pd.notna(val) and isinstance(val, str) and len(val.strip()) > 0:
                if not any(x in val.upper() for x in ['UNNAMED', 'VENDA', 'CLIENTE']):
                    obs.append(val.strip())
        return " | ".join(obs) if obs else ""
    
    def extrair_outros_tipos(self, df: pd.DataFrame, loja: str, prefixo: str, 
                           mes_ano: str, dia: int) -> List[Dict]:
        """Extrai despesas e outros tipos de transação"""
        outros = []
        
        # Procurar seção de despesas
        for i, row in df.iterrows():
            if any("Despesas" in str(cell) for cell in row if pd.notna(cell)):
                # Processar próximas linhas como despesas
                for j in range(i + 1, min(i + 10, len(df))):
                    despesa_row = df.iloc[j]
                    if any(pd.notna(cell) and str(cell).replace('.', '').replace(',', '').isdigit() 
                          for cell in despesa_row):
                        transacao = self.criar_transacao(
                            despesa_row, loja, prefixo, mes_ano, dia, "DESPESA"
                        )
                        if transacao:
                            outros.append(transacao)
                break
        
        return outros
    
    def extrair_resumo_mensal(self, arquivo: Path, loja: str, prefixo: str, mes_ano: str):
        """Extrai resumo mensal"""
        try:
            df = pd.read_excel(arquivo, sheet_name="resumo_cx", header=None)
            
            resumo = {
                'id_resumo': f"{prefixo}_{mes_ano}_RESUMO",
                'loja': loja,
                'prefixo_loja': prefixo,
                'mes_ano': mes_ano,
                'saldo_inicial': self.extrair_valor_resumo(df, "Saldo Inicial"),
                'total_vendas': self.extrair_valor_resumo(df, "Vendas"),
                'total_entradas': self.extrair_valor_resumo(df, "Entrada"),
                'total_despesas': self.extrair_valor_resumo(df, "Despesas"),
                'total_dn': self.extrair_valor_resumo(df, "DN"),
                'total_ctd': self.extrair_valor_resumo(df, "CTD"),
                'total_ctc': self.extrair_valor_resumo(df, "CTC"),
                'total_pix': self.extrair_valor_resumo(df, "PIX"),
                'dados_brutos': str(df.to_dict())
            }
            
            self.resumo_extraido.append(resumo)
            
        except Exception as e:
            print(f"      ❌ Erro no resumo: {e}")
    
    def extrair_valor_resumo(self, df: pd.DataFrame, campo: str) -> float:
        """Extrai valor específico do resumo"""
        for i, row in df.iterrows():
            if any(campo in str(cell) for cell in row if pd.notna(cell)):
                for val in row:
                    if pd.notna(val) and isinstance(val, (int, float)) and val != 0:
                        return float(val)
        return 0.0
    
    def parse_mes_ano(self, nome_arquivo: str) -> str:
        """Converte nome do arquivo para formato mes_ano"""
        meses = {
            'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04',
            'mai': '05', 'jun': '06', 'jul': '07', 'ago': '08',
            'set': '09', 'out': '10', 'nov': '11', 'dez': '12'
        }
        
        for mes_nome, mes_num in meses.items():
            if mes_nome in nome_arquivo.lower():
                if '24' in nome_arquivo:
                    return f"2024_{mes_num}"
                elif '23' in nome_arquivo:
                    return f"2023_{mes_num}"
        
        return "2024_01"  # Default
    
    def criar_data(self, mes_ano: str, dia: int) -> str:
        """Cria data formatada"""
        try:
            ano, mes = mes_ano.split('_')
            return f"{ano}-{mes}-{dia:02d}"
        except:
            return f"2024-01-{dia:02d}"
    
    def salvar_dados_consolidados(self) -> str:
        """Salva todos os dados extraídos"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_saida = self.pasta_caixa / f"DADOS_CAIXA_CONSOLIDADOS_{timestamp}.xlsx"
        
        try:
            with pd.ExcelWriter(arquivo_saida, engine='openpyxl') as writer:
                # Transações
                if self.dados_extraidos:
                    df_transacoes = pd.DataFrame(self.dados_extraidos)
                    df_transacoes.to_excel(writer, sheet_name='Transacoes', index=False)
                
                # Resumos
                if self.resumo_extraido:
                    df_resumos = pd.DataFrame(self.resumo_extraido)
                    df_resumos.to_excel(writer, sheet_name='Resumos_Mensais', index=False)
                
                # Relatório de extração
                self.criar_relatorio_extracao(writer, timestamp)
            
            print(f"\n💾 Dados salvos: {arquivo_saida}")
            return str(arquivo_saida)
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            return ""
    
    def criar_relatorio_extracao(self, writer, timestamp: str):
        """Cria relatório da extração"""
        relatorio = {
            'Data_Extracao': [timestamp],
            'Total_Transacoes': [len(self.dados_extraidos)],
            'Total_Resumos': [len(self.resumo_extraido)],
            'Lojas_Processadas': [len(set(t['loja'] for t in self.dados_extraidos))],
            'Periodo_Dados': [f"{min(t['data_transacao'] for t in self.dados_extraidos)} a {max(t['data_transacao'] for t in self.dados_extraidos)}" if self.dados_extraidos else "N/A"]
        }
        
        df_relatorio = pd.DataFrame(relatorio)
        df_relatorio.to_excel(writer, sheet_name='Relatorio_Extracao', index=False)

if __name__ == "__main__":
    extrator = ExtratorDadosCaixa()
    extrator.processar_todas_lojas()