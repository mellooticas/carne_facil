#!/usr/bin/env python3
"""
Extrator Completo de Dados de Dioptrías
Processa TODOS os campos de dioptrías das 14.337 OS
"""

import pandas as pd
from pathlib import Path
import re
from datetime import datetime
import logging
from collections import defaultdict

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExtratorDioptrias:
    def __init__(self):
        self.os_com_dioptrias = []
        self.campos_dioptrias_mapeados = {}
        self.estatisticas = {
            'total_os': 0,
            'com_ponte': 0,
            'com_horizontal': 0,
            'com_esf_od': 0,
            'com_esf_oe': 0,
            'com_adicao': 0,
            'arquivos_processados': 0
        }
        
        # Mapeamento dos campos de dioptrías baseado na análise
        self.campos_dioptrias = {
            # Medidas da armação
            'PONTE': 'ponte',
            'HORIZONTAL': 'horizontal', 
            'DIAG MAIOR': 'diag_maior',
            'VERTICAL': 'vertical',
            
            # Olho Direito (OD) - primeiro conjunto
            'ESF': 'esf_od',
            'CIL': 'cil_od', 
            'EIXO': 'eixo_od',
            'DNP': 'dnp_od',
            'ALTURA': 'altura_od',
            
            # Olho Esquerdo (OE) - segundo conjunto
            'ESF2': 'esf_oe',
            'CIL3': 'cil_oe',
            'EIXO4': 'eixo_oe', 
            'DNP5': 'dnp_oe',
            'ALTURA6': 'altura_oe',
            
            # Terceiro conjunto (se existir)
            'ESF7': 'esf_3',
            'CIL8': 'cil_3',
            'EIXO9': 'eixo_3',
            'DNP10': 'dnp_3',
            'ALTURA11': 'altura_3',
            
            # Quarto conjunto (se existir)
            'ESF12': 'esf_4',
            'CIL13': 'cil_4', 
            'EIXO14': 'eixo_4',
            'DNP15': 'dnp_4',
            'ALTURA16': 'altura_4',
            
            # Adição
            'ADIÇÃO': 'adicao'
        }
    
    def identificar_loja_por_arquivo(self, nome_arquivo):
        """Identifica loja pelo nome do arquivo"""
        nome_upper = nome_arquivo.upper()
        
        if 'MAUA' in nome_upper or 'MESA01' in nome_upper:
            return 'MAUA'
        elif 'SUZANO' in nome_upper and 'SUZANO2' not in nome_upper:
            return 'SUZANO'
        elif 'SUZANO2' in nome_upper:
            return 'SUZANO2'
        elif 'PERUS' in nome_upper:
            return 'PERUS'
        elif 'RIO_PEQUENO' in nome_upper or 'RP' in nome_upper:
            return 'RIO_PEQUENO'
        elif 'SAO_MATEUS' in nome_upper or 'SM' in nome_upper:
            return 'SAO_MATEUS'
        elif 'OL' in nome_upper or 'ESCRITORIO' in nome_upper:
            return 'SAO_MATEUS'
        else:
            return 'INDEFINIDA'
    
    def mapear_campos_arquivo(self, colunas):
        """Mapeia colunas do arquivo para campos de dioptrías"""
        mapeamento = {}
        
        for campo_esperado, campo_normalizado in self.campos_dioptrias.items():
            for coluna in colunas:
                coluna_str = str(coluna).strip()
                
                # Busca exata primeiro
                if coluna_str == campo_esperado:
                    mapeamento[campo_normalizado] = coluna
                    break
                # Busca contida
                elif campo_esperado in coluna_str:
                    mapeamento[campo_normalizado] = coluna
                    break
        
        return mapeamento
    
    def extrair_valor_dioptria(self, valor):
        """Extrai e normaliza valor de dioptria"""
        if pd.isna(valor) or str(valor).strip() == '':
            return None
        
        try:
            # Converter para string e limpar
            valor_str = str(valor).strip()
            
            # Remover texto comum
            valor_str = valor_str.replace('D', '').replace('°', '').strip()
            
            # Tentar converter para float
            if valor_str in ['', '-', 'nan', 'NaN']:
                return None
            
            # Substituir vírgula por ponto
            valor_str = valor_str.replace(',', '.')
            
            return float(valor_str)
        except:
            return None
    
    def processar_arquivo_dioptrias(self, arquivo_path):
        """Processa arquivo específico extraindo dioptrías"""
        logger.info(f"Processando dioptrías: {arquivo_path.name}")
        
        try:
            # Carregar arquivo
            engine = 'openpyxl' if arquivo_path.suffix.lower() in ['.xlsx', '.xlsm'] else None
            
            try:
                excel_file = pd.ExcelFile(arquivo_path, engine=engine)
            except Exception as e:
                logger.warning(f"Erro ao carregar {arquivo_path.name}: {e}")
                return 0
            
            # Encontrar sheet principal
            sheet_principal = None
            for sheet_name in ['base_clientes_OS', 'base', 'dados']:
                if sheet_name in excel_file.sheet_names:
                    sheet_principal = sheet_name
                    break
            
            if not sheet_principal:
                sheet_principal = excel_file.sheet_names[0]
            
            try:
                df = pd.read_excel(arquivo_path, sheet_name=sheet_principal, engine=engine)
            except Exception as e:
                logger.warning(f"Erro ao ler {arquivo_path.name}: {e}")
                return 0
            
            # Mapear campos de dioptrías
            mapeamento = self.mapear_campos_arquivo(df.columns)
            
            if not mapeamento:
                logger.warning(f"Nenhum campo de dioptria encontrado em {arquivo_path.name}")
                return 0
            
            # Identificar campos básicos para identificação
            campos_basicos = self.identificar_campos_basicos(df.columns)
            
            # Identificar loja
            loja = self.identificar_loja_por_arquivo(arquivo_path.name)
            
            # Processar cada linha
            os_processadas = 0
            for idx, row in df.iterrows():
                os_dioptria = self.extrair_dioptrias_linha(
                    row, mapeamento, campos_basicos, loja, arquivo_path.name, idx + 1
                )
                
                if os_dioptria:
                    self.os_com_dioptrias.append(os_dioptria)
                    os_processadas += 1
            
            self.estatisticas['arquivos_processados'] += 1
            self.estatisticas['total_os'] += os_processadas
            
            logger.info(f"✅ {arquivo_path.name}: {os_processadas} OS com dioptrías | Loja: {loja}")
            return os_processadas
            
        except Exception as e:
            logger.error(f"❌ Erro em {arquivo_path.name}: {e}")
            return 0
    
    def identificar_campos_basicos(self, colunas):
        """Identifica campos básicos para identificação"""
        campos = {}
        
        for col in colunas:
            col_str = str(col).lower().strip()
            
            if any(termo in col_str for termo in ['os n°', 'os:', 'os', 'ordem']):
                campos['numero_os'] = col
            elif any(termo in col_str for termo in ['nome:', 'nome', 'cliente']):
                campos['nome'] = col
            elif 'cpf' in col_str:
                campos['cpf'] = col
            elif any(termo in col_str for termo in ['data:', 'data']):
                campos['data'] = col
        
        return campos
    
    def extrair_dioptrias_linha(self, row, mapeamento, campos_basicos, loja, arquivo, linha):
        """Extrai dioptrías de uma linha específica"""
        # Dados básicos de identificação
        numero_os = str(row.get(campos_basicos.get('numero_os', ''))).strip() if campos_basicos.get('numero_os') else None
        nome = str(row.get(campos_basicos.get('nome', ''))).strip() if campos_basicos.get('nome') else None
        cpf = str(row.get(campos_basicos.get('cpf', ''))).strip() if campos_basicos.get('cpf') else None
        
        # Se não tem dados básicos, pular
        if not numero_os or numero_os == 'nan':
            return None
        
        # Extrair todos os campos de dioptría
        os_dioptria = {
            # Identificação
            'numero_os': numero_os,
            'nome_informado': nome if nome != 'nan' else None,
            'cpf_informado': cpf if cpf != 'nan' else None,
            'loja': loja,
            'arquivo_origem': arquivo,
            'linha_arquivo': linha,
            
            # Medidas da armação
            'ponte': self.extrair_valor_dioptria(row.get(mapeamento.get('ponte'))) if 'ponte' in mapeamento else None,
            'horizontal': self.extrair_valor_dioptria(row.get(mapeamento.get('horizontal'))) if 'horizontal' in mapeamento else None,
            'diag_maior': self.extrair_valor_dioptria(row.get(mapeamento.get('diag_maior'))) if 'diag_maior' in mapeamento else None,
            'vertical': self.extrair_valor_dioptria(row.get(mapeamento.get('vertical'))) if 'vertical' in mapeamento else None,
            
            # Olho Direito (OD)
            'esf_od': self.extrair_valor_dioptria(row.get(mapeamento.get('esf_od'))) if 'esf_od' in mapeamento else None,
            'cil_od': self.extrair_valor_dioptria(row.get(mapeamento.get('cil_od'))) if 'cil_od' in mapeamento else None,
            'eixo_od': self.extrair_valor_dioptria(row.get(mapeamento.get('eixo_od'))) if 'eixo_od' in mapeamento else None,
            'dnp_od': self.extrair_valor_dioptria(row.get(mapeamento.get('dnp_od'))) if 'dnp_od' in mapeamento else None,
            'altura_od': self.extrair_valor_dioptria(row.get(mapeamento.get('altura_od'))) if 'altura_od' in mapeamento else None,
            
            # Olho Esquerdo (OE)
            'esf_oe': self.extrair_valor_dioptria(row.get(mapeamento.get('esf_oe'))) if 'esf_oe' in mapeamento else None,
            'cil_oe': self.extrair_valor_dioptria(row.get(mapeamento.get('cil_oe'))) if 'cil_oe' in mapeamento else None,
            'eixo_oe': self.extrair_valor_dioptria(row.get(mapeamento.get('eixo_oe'))) if 'eixo_oe' in mapeamento else None,
            'dnp_oe': self.extrair_valor_dioptria(row.get(mapeamento.get('dnp_oe'))) if 'dnp_oe' in mapeamento else None,
            'altura_oe': self.extrair_valor_dioptria(row.get(mapeamento.get('altura_oe'))) if 'altura_oe' in mapeamento else None,
            
            # Terceiro conjunto (se existir)
            'esf_3': self.extrair_valor_dioptria(row.get(mapeamento.get('esf_3'))) if 'esf_3' in mapeamento else None,
            'cil_3': self.extrair_valor_dioptria(row.get(mapeamento.get('cil_3'))) if 'cil_3' in mapeamento else None,
            'eixo_3': self.extrair_valor_dioptria(row.get(mapeamento.get('eixo_3'))) if 'eixo_3' in mapeamento else None,
            'dnp_3': self.extrair_valor_dioptria(row.get(mapeamento.get('dnp_3'))) if 'dnp_3' in mapeamento else None,
            'altura_3': self.extrair_valor_dioptria(row.get(mapeamento.get('altura_3'))) if 'altura_3' in mapeamento else None,
            
            # Quarto conjunto (se existir)
            'esf_4': self.extrair_valor_dioptria(row.get(mapeamento.get('esf_4'))) if 'esf_4' in mapeamento else None,
            'cil_4': self.extrair_valor_dioptria(row.get(mapeamento.get('cil_4'))) if 'cil_4' in mapeamento else None,
            'eixo_4': self.extrair_valor_dioptria(row.get(mapeamento.get('eixo_4'))) if 'eixo_4' in mapeamento else None,
            'dnp_4': self.extrair_valor_dioptria(row.get(mapeamento.get('dnp_4'))) if 'dnp_4' in mapeamento else None,
            'altura_4': self.extrair_valor_dioptria(row.get(mapeamento.get('altura_4'))) if 'altura_4' in mapeamento else None,
            
            # Adição
            'adicao': self.extrair_valor_dioptria(row.get(mapeamento.get('adicao'))) if 'adicao' in mapeamento else None,
            
            # Metadados
            'data_processamento': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        # Contar estatísticas
        if os_dioptria['ponte'] is not None:
            self.estatisticas['com_ponte'] += 1
        if os_dioptria['horizontal'] is not None:
            self.estatisticas['com_horizontal'] += 1
        if os_dioptria['esf_od'] is not None:
            self.estatisticas['com_esf_od'] += 1
        if os_dioptria['esf_oe'] is not None:
            self.estatisticas['com_esf_oe'] += 1
        if os_dioptria['adicao'] is not None:
            self.estatisticas['com_adicao'] += 1
        
        return os_dioptria
    
    def processar_todas_dioptrias(self):
        """Processa todas as dioptrías de todos os arquivos"""
        print("👁️ EXTRATOR COMPLETO DE DIOPTRÍAS")
        print("=" * 80)
        print("🔍 Processando TODOS os campos de dioptrías")
        print("📊 25 campos: Armação + OD + OE + Conjuntos 3/4 + Adição")
        print("=" * 80)
        
        # Processar todos os arquivos
        arquivos = list(Path("data/raw").glob("OS*.xlsm")) + list(Path("data/raw").glob("OS*.xlsx"))
        logger.info(f"Encontrados {len(arquivos)} arquivos para processar")
        
        for arquivo in arquivos:
            self.processar_arquivo_dioptrias(arquivo)
        
        # Salvar resultados
        output_file = self.salvar_dioptrias()
        
        # Exibir resultados
        self.exibir_resultados(output_file)
        
        return output_file
    
    def salvar_dioptrias(self):
        """Salva dados de dioptrías em Excel"""
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"DIOPTRIAS_COMPLETAS_{timestamp}.xlsx"
        
        df_dioptrias = pd.DataFrame(self.os_com_dioptrias)
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Base principal de dioptrías
            df_dioptrias.to_excel(writer, sheet_name='Dioptrias_Completas', index=False)
            
            # Estatísticas por loja
            stats_loja = df_dioptrias.groupby('loja').agg({
                'numero_os': 'count',
                'ponte': lambda x: x.notna().sum(),
                'esf_od': lambda x: x.notna().sum(),
                'esf_oe': lambda x: x.notna().sum(),
                'adicao': lambda x: x.notna().sum()
            }).rename(columns={
                'numero_os': 'total_os',
                'ponte': 'com_ponte',
                'esf_od': 'com_esf_od',
                'esf_oe': 'com_esf_oe',
                'adicao': 'com_adicao'
            })
            stats_loja.to_excel(writer, sheet_name='Estatisticas_Por_Loja')
            
            # Análise de graus (ESF mais comuns)
            esf_od_values = df_dioptrias['esf_od'].dropna()
            esf_oe_values = df_dioptrias['esf_oe'].dropna()
            
            if not esf_od_values.empty:
                analise_graus = pd.DataFrame([
                    {'Tipo': 'ESF_OD', 'Min': esf_od_values.min(), 'Max': esf_od_values.max(), 'Media': esf_od_values.mean()},
                    {'Tipo': 'ESF_OE', 'Min': esf_oe_values.min(), 'Max': esf_oe_values.max(), 'Media': esf_oe_values.mean()}
                ])
                analise_graus.to_excel(writer, sheet_name='Analise_Graus', index=False)
        
        logger.info(f"Dioptrías salvas: {output_file}")
        return output_file
    
    def exibir_resultados(self, output_file):
        """Exibe resultados da extração"""
        print(f"\n📊 DIOPTRÍAS EXTRAÍDAS:")
        print("=" * 80)
        print(f"📁 Arquivos processados: {self.estatisticas['arquivos_processados']}")
        print(f"👁️ Total de OS: {self.estatisticas['total_os']:,}")
        print(f"🔍 Com ponte: {self.estatisticas['com_ponte']:,} ({self.estatisticas['com_ponte']/self.estatisticas['total_os']*100:.1f}%)")
        print(f"📏 Com horizontal: {self.estatisticas['com_horizontal']:,} ({self.estatisticas['com_horizontal']/self.estatisticas['total_os']*100:.1f}%)")
        print(f"👁️ Com ESF OD: {self.estatisticas['com_esf_od']:,} ({self.estatisticas['com_esf_od']/self.estatisticas['total_os']*100:.1f}%)")
        print(f"👁️ Com ESF OE: {self.estatisticas['com_esf_oe']:,} ({self.estatisticas['com_esf_oe']/self.estatisticas['total_os']*100:.1f}%)")
        print(f"➕ Com adição: {self.estatisticas['com_adicao']:,} ({self.estatisticas['com_adicao']/self.estatisticas['total_os']*100:.1f}%)")
        
        print(f"\n📁 ARQUIVO GERADO:")
        print("=" * 80)
        print(f"✅ {output_file}")
        print(f"📊 Sheets: Dioptrias_Completas, Estatisticas_Por_Loja, Analise_Graus")
        
        print(f"\n👁️ CAMPOS PROCESSADOS:")
        print("=" * 80)
        print("🔍 Medidas da armação: ponte, horizontal, diag_maior, vertical")
        print("👁️ Olho Direito (OD): esf_od, cil_od, eixo_od, dnp_od, altura_od")
        print("👁️ Olho Esquerdo (OE): esf_oe, cil_oe, eixo_oe, dnp_oe, altura_oe")
        print("👁️ Conjuntos 3 e 4: esf_3, cil_3, eixo_3, esf_4, cil_4, eixo_4")
        print("➕ Adição: adicao")

def main():
    """Função principal"""
    extrator = ExtratorDioptrias()
    output_file = extrator.processar_todas_dioptrias()
    return output_file

if __name__ == "__main__":
    main()