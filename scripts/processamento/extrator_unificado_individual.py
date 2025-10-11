#!/usr/bin/env python3
"""
EXTRATOR UNIFICADO - PROCESSAMENTO INDIVIDUAL
Processa um arquivo por vez e gera documentos separados para cada tabela
Sistema modular para análise detalhada arquivo por arquivo
"""

import pandas as pd
from pathlib import Path
import openpyxl
from datetime import datetime
import re
from typing import Dict, List, Optional
import json

class ExtratorUnificadoIndividual:
    def __init__(self):
        self.pasta_caixa = Path("data/caixa_lojas")
        self.pasta_saida = Path("data/extraidos_individuais")
        self.pasta_saida.mkdir(exist_ok=True)
        
        # Estatísticas do processamento
        self.stats = {
            'arquivos_processados': 0,
            'total_vend': 0,
            'total_rest_entr': 0,
            'total_rec_carn': 0,
            'total_entr_carn': 0,
            'total_os_ent_dia': 0,
            'valor_total_vendas': 0,
            'valor_total_pendencias': 0,
            'valor_total_recebimentos': 0,
            'valor_total_entregas': 0
        }
    
    def processar_arquivo_individual(self, arquivo_path: Path):
        """Processa um único arquivo e gera todos os documentos separados"""
        print("=" * 100)
        print(f"📁 PROCESSANDO ARQUIVO: {arquivo_path.name}")
        print("=" * 100)
        
        if not arquivo_path.exists():
            print(f"❌ Arquivo não encontrado: {arquivo_path}")
            return
        
        # Identificar loja e período
        info_arquivo = self.identificar_arquivo(arquivo_path)
        print(f"🏪 Loja: {info_arquivo['loja']}")
        print(f"📅 Período: {info_arquivo['periodo']}")
        
        # Criar pasta específica para este arquivo
        pasta_arquivo = self.pasta_saida / f"{info_arquivo['loja']}_{info_arquivo['periodo']}"
        pasta_arquivo.mkdir(exist_ok=True)
        
        # Listar abas disponíveis
        abas = self.listar_abas_arquivo(arquivo_path)
        print(f"📄 Total de abas: {len(abas)}")
        
        # Processar cada aba
        resultados_arquivo = {
            'info': info_arquivo,
            'arquivo': str(arquivo_path),
            'abas_processadas': [],
            'tabelas_extraidas': {
                'VEND': [],
                'REST_ENTR': [],
                'REC_CARN': [],
                'ENTR_CARN': [],
                'OS_ENT_DIA': []
            },
            'resumo': {
                'total_abas': len(abas),
                'abas_com_dados': 0,
                'total_registros': 0
            }
        }
        
        for aba in abas:
            print(f"\n📃 Processando aba: {aba}")
            resultado_aba = self.processar_aba_completa(arquivo_path, aba, info_arquivo)
            
            if resultado_aba and any(resultado_aba.values()):
                resultados_arquivo['abas_processadas'].append(aba)
                resultados_arquivo['resumo']['abas_com_dados'] += 1
                
                # Consolidar resultados
                for tabela, dados in resultado_aba.items():
                    if dados:
                        resultados_arquivo['tabelas_extraidas'][tabela].extend(dados)
                        resultados_arquivo['resumo']['total_registros'] += len(dados)
        
        # Gerar documentos separados
        self.gerar_documentos_separados(resultados_arquivo, pasta_arquivo)
        
        # Atualizar estatísticas globais
        self.atualizar_estatisticas(resultados_arquivo)
        
        # Gerar resumo do arquivo
        self.gerar_resumo_arquivo(resultados_arquivo, pasta_arquivo)
        
        print(f"\n✅ Arquivo processado: {resultados_arquivo['resumo']['total_registros']} registros extraídos")
        self.stats['arquivos_processados'] += 1
    
    def identificar_arquivo(self, arquivo_path: Path) -> Dict:
        """Identifica loja e período do arquivo"""
        # Extrair da estrutura de pastas: MAUA/2024_MAU/abr_24.xlsx
        partes_path = arquivo_path.parts
        
        loja = "DESCONHECIDA"
        periodo = "DESCONHECIDO"
        
        # Identificar loja
        for parte in partes_path:
            if parte.upper() in ['MAUA', 'SUZANO', 'RIO_PEQUENO', 'ITAQUERA', 'GUARULHOS', 'TABOAO']:
                loja = parte.upper()
                break
        
        # Identificar período do nome do arquivo
        nome_arquivo = arquivo_path.stem  # abr_24
        if '_' in nome_arquivo:
            mes, ano = nome_arquivo.split('_')
            periodo = f"20{ano}_{mes.upper()}"
        
        return {
            'loja': loja,
            'periodo': periodo,
            'arquivo_nome': arquivo_path.name,
            'timestamp': datetime.now().isoformat()
        }
    
    def listar_abas_arquivo(self, arquivo_path: Path) -> List[str]:
        """Lista todas as abas do arquivo"""
        try:
            workbook = openpyxl.load_workbook(arquivo_path, read_only=True)
            abas = workbook.sheetnames
            workbook.close()
            return abas
        except Exception as e:
            print(f"❌ Erro ao listar abas: {e}")
            return []
    
    def processar_aba_completa(self, arquivo_path: Path, aba: str, info_arquivo: Dict) -> Dict:
        """Processa uma aba completa extraindo todas as 5 tabelas"""
        try:
            df = pd.read_excel(arquivo_path, sheet_name=aba, header=None)
            
            resultado = {
                'VEND': self.extrair_vend_aba(df, aba, info_arquivo),
                'REST_ENTR': self.extrair_rest_entr_aba(df, aba, info_arquivo),
                'REC_CARN': self.extrair_rec_carn_aba(df, aba, info_arquivo),
                'ENTR_CARN': self.extrair_entr_carn_aba(df, aba, info_arquivo),
                'OS_ENT_DIA': self.extrair_os_ent_dia_aba(df, aba, info_arquivo)
            }
            
            # Mostrar resumo da aba
            total_aba = sum(len(dados) for dados in resultado.values() if dados)
            if total_aba > 0:
                print(f"   ✅ {total_aba} registros extraídos da aba {aba}")
            
            return resultado
            
        except Exception as e:
            print(f"   ❌ Erro ao processar aba {aba}: {e}")
            return {}
    
    def extrair_vend_aba(self, df: pd.DataFrame, aba: str, info: Dict) -> List[Dict]:
        """Extrai dados de VEND da aba"""
        vendas = []
        
        # Procurar seção de vendas
        for i, row in df.iterrows():
            linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
            linha_upper = linha_texto.upper()
            
            if 'VEND' in linha_upper and any(x in linha_upper for x in ['TOTAL', 'DIA', aba]):
                # Analisar próximas linhas para vendas
                for j in range(i + 1, min(i + 10, len(df))):
                    venda = self.extrair_linha_venda(df.iloc[j], aba, info, j)
                    if venda:
                        vendas.append(venda)
        
        return vendas
    
    def extrair_rest_entr_aba(self, df: pd.DataFrame, aba: str, info: Dict) -> List[Dict]:
        """Extrai dados de REST_ENTR da aba"""
        pendencias = []
        
        for i, row in df.iterrows():
            linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
            linha_upper = linha_texto.upper()
            
            if 'RESTANTE ENTRADA' in linha_upper or 'REST_ENTR' in linha_upper:
                for j in range(i + 1, min(i + 15, len(df))):
                    pendencia = self.extrair_linha_pendencia(df.iloc[j], aba, info, j)
                    if pendencia:
                        pendencias.append(pendencia)
        
        return pendencias
    
    def extrair_rec_carn_aba(self, df: pd.DataFrame, aba: str, info: Dict) -> List[Dict]:
        """Extrai dados de REC_CARN da aba"""
        recebimentos = []
        
        for i, row in df.iterrows():
            linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
            linha_upper = linha_texto.upper()
            
            if 'RECEBIMENTO' in linha_upper and 'CARNE' in linha_upper:
                for j in range(i + 1, min(i + 10, len(df))):
                    recebimento = self.extrair_linha_recebimento(df.iloc[j], aba, info, j)
                    if recebimento:
                        recebimentos.append(recebimento)
        
        return recebimentos
    
    def extrair_entr_carn_aba(self, df: pd.DataFrame, aba: str, info: Dict) -> List[Dict]:
        """Extrai dados de ENTR_CARN da aba"""
        entregas = []
        
        for i, row in df.iterrows():
            linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
            linha_upper = linha_texto.upper()
            
            if 'ENTREGA' in linha_upper and 'CARNE' in linha_upper:
                for j in range(i + 1, min(i + 8, len(df))):
                    entrega = self.extrair_linha_entrega(df.iloc[j], aba, info, j)
                    if entrega:
                        entregas.append(entrega)
        
        return entregas
    
    def extrair_os_ent_dia_aba(self, df: pd.DataFrame, aba: str, info: Dict) -> List[Dict]:
        """Extrai dados de OS_ENT_DIA da aba"""
        os_entregues = []
        
        for i, row in df.iterrows():
            linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
            linha_upper = linha_texto.upper()
            
            if 'OS ENTREGUE NO DIA' in linha_upper:
                for j in range(i + 1, min(i + 5, len(df))):
                    os_entregue = self.extrair_linha_os_entregue(df.iloc[j], aba, info, j)
                    if os_entregue:
                        os_entregues.append(os_entregue)
        
        return os_entregues
    
    def extrair_linha_venda(self, row, aba: str, info: Dict, linha_idx: int) -> Optional[Dict]:
        """Extrai dados de uma linha de venda"""
        valores = [cell for cell in row if pd.notna(cell)]
        if len(valores) < 3:
            return None
        
        # Procurar valor monetário
        valor = None
        for val in valores:
            if isinstance(val, (int, float)) and val > 0:
                valor = float(val)
                break
        
        if valor and valor > 10:  # Filtrar valores muito pequenos
            return {
                'id_registro': f"VEND_{info['loja']}_{info['periodo']}_{aba}_{linha_idx}",
                'loja': info['loja'],
                'periodo': info['periodo'],
                'dia': aba,
                'valor': valor,
                'tipo_pagamento': self.identificar_pagamento(valores),
                'observacoes': str(valores)
            }
        return None
    
    def extrair_linha_pendencia(self, row, aba: str, info: Dict, linha_idx: int) -> Optional[Dict]:
        """Extrai dados de uma linha de pendência"""
        valores = [cell for cell in row if pd.notna(cell)]
        if len(valores) < 2:
            return None
        
        valor = None
        cliente = ""
        
        for val in valores:
            if isinstance(val, (int, float)) and val > 0:
                valor = float(val)
            elif isinstance(val, str) and len(val) > 2:
                cliente = val
        
        if valor and valor > 10:
            return {
                'id_registro': f"REST_ENTR_{info['loja']}_{info['periodo']}_{aba}_{linha_idx}",
                'loja': info['loja'],
                'periodo': info['periodo'],
                'dia': aba,
                'cliente': cliente,
                'valor_pendente': valor,
                'observacoes': str(valores)
            }
        return None
    
    def extrair_linha_recebimento(self, row, aba: str, info: Dict, linha_idx: int) -> Optional[Dict]:
        """Extrai dados de uma linha de recebimento"""
        valores = [cell for cell in row if pd.notna(cell)]
        if len(valores) < 2:
            return None
        
        # Procurar número de OS e valor
        numero_os = None
        valor = None
        
        for val in valores:
            if isinstance(val, (int, float)):
                val_int = int(val) if val == int(val) else val
                if isinstance(val_int, int) and 3000 <= val_int <= 9999:
                    numero_os = str(val_int)
                elif val > 0:
                    valor = float(val)
        
        if numero_os and valor:
            return {
                'id_registro': f"REC_CARN_{info['loja']}_{info['periodo']}_{aba}_{numero_os}",
                'loja': info['loja'],
                'periodo': info['periodo'],
                'dia': aba,
                'numero_os': numero_os,
                'valor_recebido': valor,
                'observacoes': str(valores)
            }
        return None
    
    def extrair_linha_entrega(self, row, aba: str, info: Dict, linha_idx: int) -> Optional[Dict]:
        """Extrai dados de uma linha de entrega"""
        valores = [cell for cell in row if pd.notna(cell)]
        if len(valores) < 2:
            return None
        
        numero_os = None
        valor = None
        
        for val in valores:
            if isinstance(val, (int, float)):
                val_int = int(val) if val == int(val) else val
                if isinstance(val_int, int) and 3000 <= val_int <= 9999:
                    numero_os = str(val_int)
                elif val > 0:
                    valor = float(val)
        
        if numero_os:
            return {
                'id_registro': f"ENTR_CARN_{info['loja']}_{info['periodo']}_{aba}_{numero_os}",
                'loja': info['loja'],
                'periodo': info['periodo'],
                'dia': aba,
                'numero_os': numero_os,
                'valor_entrega': valor or 0,
                'vendedor': self.identificar_vendedor(valores),
                'observacoes': str(valores)
            }
        return None
    
    def extrair_linha_os_entregue(self, row, aba: str, info: Dict, linha_idx: int) -> Optional[Dict]:
        """Extrai dados de uma linha de OS entregue"""
        valores = [cell for cell in row if pd.notna(cell)]
        if len(valores) < 2:
            return None
        
        numero_os = None
        for val in valores:
            if isinstance(val, (int, float)):
                val_int = int(val) if val == int(val) else val
                if isinstance(val_int, int) and 3000 <= val_int <= 9999:
                    numero_os = str(val_int)
                    break
        
        if numero_os:
            return {
                'id_registro': f"OS_ENT_DIA_{info['loja']}_{info['periodo']}_{aba}_{numero_os}",
                'loja': info['loja'],
                'periodo': info['periodo'],
                'dia': aba,
                'numero_os': numero_os,
                'vendedor': self.identificar_vendedor(valores),
                'status_entrega': self.identificar_status_entrega(valores),
                'observacoes': str(valores)
            }
        return None
    
    def identificar_pagamento(self, valores: List) -> str:
        """Identifica tipo de pagamento"""
        pagamentos = ['PIX', 'DINHEIRO', 'CARTAO', 'CTD', 'CTC', 'DN', 'GARANTIA', 'SS']
        
        for val in valores:
            if isinstance(val, str):
                val_upper = val.upper()
                for pag in pagamentos:
                    if pag in val_upper:
                        return pag
        return ""
    
    def identificar_vendedor(self, valores: List) -> str:
        """Identifica vendedor"""
        vendedores = ['BETH', 'CARLOS', 'MARIA', 'JOSE']
        
        for val in valores:
            if isinstance(val, str):
                val_upper = val.upper().strip()
                if val_upper in vendedores:
                    return val_upper
        return ""
    
    def identificar_status_entrega(self, valores: List) -> str:
        """Identifica status de entrega"""
        for val in valores:
            if isinstance(val, str):
                val_upper = val.upper().strip()
                if val_upper in ['SIM', 'NÃO', 'NAO']:
                    return val_upper
        return ""
    
    def gerar_documentos_separados(self, resultados: Dict, pasta_arquivo: Path):
        """Gera documentos Excel separados para cada tabela"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for tabela, dados in resultados['tabelas_extraidas'].items():
            if dados:
                arquivo_tabela = pasta_arquivo / f"{tabela}_{resultados['info']['loja']}_{resultados['info']['periodo']}_{timestamp}.xlsx"
                
                try:
                    df_tabela = pd.DataFrame(dados)
                    df_tabela.to_excel(arquivo_tabela, index=False, sheet_name=tabela)
                    print(f"   💾 {tabela}: {len(dados)} registros salvos em {arquivo_tabela.name}")
                    
                except Exception as e:
                    print(f"   ❌ Erro ao salvar {tabela}: {e}")
    
    def gerar_resumo_arquivo(self, resultados: Dict, pasta_arquivo: Path):
        """Gera resumo detalhado do arquivo processado"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_resumo = pasta_arquivo / f"RESUMO_{resultados['info']['loja']}_{resultados['info']['periodo']}_{timestamp}.json"
        
        # Calcular totais
        resumo_detalhado = {
            'info_arquivo': resultados['info'],
            'processamento': {
                'timestamp': timestamp,
                'total_abas': resultados['resumo']['total_abas'],
                'abas_processadas': len(resultados['abas_processadas']),
                'total_registros': resultados['resumo']['total_registros']
            },
            'tabelas': {}
        }
        
        for tabela, dados in resultados['tabelas_extraidas'].items():
            if dados:
                resumo_detalhado['tabelas'][tabela] = {
                    'total_registros': len(dados),
                    'primeira_entrada': dados[0] if dados else None,
                    'ultima_entrada': dados[-1] if dados else None
                }
                
                # Calcular valores se aplicável
                if tabela == 'VEND':
                    total_valor = sum(item.get('valor', 0) for item in dados)
                    resumo_detalhado['tabelas'][tabela]['valor_total'] = total_valor
                elif tabela == 'REST_ENTR':
                    total_pendente = sum(item.get('valor_pendente', 0) for item in dados)
                    resumo_detalhado['tabelas'][tabela]['valor_total_pendente'] = total_pendente
        
        # Salvar resumo
        with open(arquivo_resumo, 'w', encoding='utf-8') as f:
            json.dump(resumo_detalhado, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"   📋 Resumo salvo: {arquivo_resumo.name}")
    
    def atualizar_estatisticas(self, resultados: Dict):
        """Atualiza estatísticas globais"""
        for tabela, dados in resultados['tabelas_extraidas'].items():
            if tabela == 'VEND':
                self.stats['total_vend'] += len(dados)
                self.stats['valor_total_vendas'] += sum(item.get('valor', 0) for item in dados)
            elif tabela == 'REST_ENTR':
                self.stats['total_rest_entr'] += len(dados)
                self.stats['valor_total_pendencias'] += sum(item.get('valor_pendente', 0) for item in dados)
            elif tabela == 'REC_CARN':
                self.stats['total_rec_carn'] += len(dados)
                self.stats['valor_total_recebimentos'] += sum(item.get('valor_recebido', 0) for item in dados)
            elif tabela == 'ENTR_CARN':
                self.stats['total_entr_carn'] += len(dados)
                self.stats['valor_total_entregas'] += sum(item.get('valor_entrega', 0) for item in dados)
            elif tabela == 'OS_ENT_DIA':
                self.stats['total_os_ent_dia'] += len(dados)
    
    def processar_arquivo_especifico(self, loja: str, arquivo: str):
        """Processa um arquivo específico"""
        # Procurar arquivo na estrutura
        arquivo_path = None
        
        for pasta_loja in self.pasta_caixa.iterdir():
            if pasta_loja.is_dir() and loja.upper() in pasta_loja.name.upper():
                for subpasta in pasta_loja.iterdir():
                    if subpasta.is_dir():
                        arquivo_test = subpasta / arquivo
                        if arquivo_test.exists():
                            arquivo_path = arquivo_test
                            break
        
        if arquivo_path:
            self.processar_arquivo_individual(arquivo_path)
            self.mostrar_estatisticas_finais()
        else:
            print(f"❌ Arquivo não encontrado: {loja}/{arquivo}")
    
    def mostrar_estatisticas_finais(self):
        """Mostra estatísticas finais do processamento"""
        print("\n" + "=" * 80)
        print("📊 ESTATÍSTICAS FINAIS DO PROCESSAMENTO")
        print("=" * 80)
        
        print(f"📁 Arquivos processados: {self.stats['arquivos_processados']}")
        print(f"💰 Vendas: {self.stats['total_vend']} (R$ {self.stats['valor_total_vendas']:,.2f})")
        print(f"⏳ Pendências: {self.stats['total_rest_entr']} (R$ {self.stats['valor_total_pendencias']:,.2f})")
        print(f"💳 Recebimentos: {self.stats['total_rec_carn']} (R$ {self.stats['valor_total_recebimentos']:,.2f})")
        print(f"📦 Entregas: {self.stats['total_entr_carn']} (R$ {self.stats['valor_total_entregas']:,.2f})")
        print(f"✅ OS entregues: {self.stats['total_os_ent_dia']}")

if __name__ == "__main__":
    extrator = ExtratorUnificadoIndividual()
    
    print("🚀 EXTRATOR UNIFICADO INDIVIDUAL")
    print("Processamento arquivo por arquivo com documentos separados")
    print("\n📋 Exemplo de uso:")
    print("extrator.processar_arquivo_especifico('MAUA', 'abr_24.xlsx')")
    
    # Processar arquivo de exemplo
    extrator.processar_arquivo_especifico('MAUA', 'abr_24.xlsx')