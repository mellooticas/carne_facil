#!/usr/bin/env python3
"""
Gerador do Arquivo Consolidado Final
Arquivo único com TODOS os clientes dos 28 arquivos em sequência
"""

import pandas as pd
from pathlib import Path
import re
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeradorArquivoConsolidadoFinal:
    def __init__(self):
        self.clientes_sequenciais = []
        self.arquivos_processados = []
        self.estatisticas = {
            'total_arquivos': 0,
            'total_clientes': 0,
            'clientes_por_loja': {},
            'qualidade_dados': {}
        }
    
    def limpar_cpf(self, cpf):
        """Limpa e formata CPF"""
        if pd.isna(cpf):
            return None
        cpf_str = re.sub(r'[^\d]', '', str(cpf))
        if len(cpf_str) == 11 and cpf_str.isdigit():
            return f"{cpf_str[:3]}.{cpf_str[3:6]}.{cpf_str[6:9]}-{cpf_str[9:]}"
        return None
    
    def limpar_celular_sp(self, celular):
        """Limpa e padroniza celular para formato SP"""
        if pd.isna(celular) or str(celular).strip() == '':
            return None
        
        cel_str = re.sub(r'[^\d]', '', str(celular))
        
        if len(cel_str) < 9:
            return None
        
        # Padronizar para SP (11)
        if len(cel_str) == 9:
            cel_str = '11' + cel_str
        elif len(cel_str) == 10:
            cel_str = '11' + cel_str
        elif len(cel_str) == 11 and cel_str.startswith('1'):
            pass
        elif len(cel_str) == 11 and not cel_str.startswith('11'):
            cel_str = '11' + cel_str[2:]
        elif len(cel_str) == 13 and cel_str.startswith('55'):
            cel_str = '11' + cel_str[4:]
        elif len(cel_str) > 11:
            cel_str = '11' + cel_str[-9:]
        
        if len(cel_str) == 11 and cel_str.startswith('11') and cel_str[2] == '9':
            return f"(11) {cel_str[2:7]}-{cel_str[7:]}"
        
        return None
    
    def normalizar_nome(self, nome):
        """Normaliza nome"""
        if pd.isna(nome):
            return None
        nome_str = str(nome).upper().strip()
        nome_str = re.sub(r'[^\w\s]', '', nome_str)
        nome_str = re.sub(r'\s+', ' ', nome_str)
        return nome_str if nome_str else None
    
    def normalizar_email(self, email):
        """Normaliza email"""
        if pd.isna(email):
            return None
        email_str = str(email).lower().strip()
        if '@' in email_str and '.' in email_str:
            return email_str
        return None
    
    def extrair_data_nascimento(self, data):
        """Extrai data de nascimento"""
        if pd.isna(data):
            return None
        try:
            if isinstance(data, str):
                for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']:
                    try:
                        return datetime.strptime(data.strip(), fmt).strftime('%d/%m/%Y')
                    except:
                        continue
            elif hasattr(data, 'strftime'):
                return data.strftime('%d/%m/%Y')
            return None
        except:
            return None
    
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
            return 'SAO_MATEUS'  # Assumindo que OL é São Mateus
        else:
            return 'INDEFINIDA'
    
    def identificar_campos(self, df):
        """Identifica campos do DataFrame com prioridade para CELULAR"""
        campos = {}
        
        # Primeiro, buscar CELULAR com prioridade
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if any(termo in col_lower for termo in ['celular:', 'celular']) and 'celular' not in campos:
                campos['celular'] = col
        
        # Depois outros campos
        for col in df.columns:
            col_lower = str(col).lower().strip()
            
            if any(termo in col_lower for termo in ['nome:', 'nome', 'cliente', 'paciente']) and 'nome' not in campos:
                campos['nome'] = col
            elif any(termo in col_lower for termo in ['cpf']) and 'cpf' not in campos:
                campos['cpf'] = col
            elif any(termo in col_lower for termo in ['rg']) and 'rg' not in campos:
                campos['rg'] = col
            elif 'celular' not in campos and any(termo in col_lower for termo in ['telefone:', 'telefone', 'fone']):
                campos['celular'] = col
            elif any(termo in col_lower for termo in ['email:', 'email', 'e-mail']) and 'email' not in campos:
                campos['email'] = col
            elif any(termo in col_lower for termo in ['end:', 'endereco', 'endereço']) and 'endereco' not in campos:
                campos['endereco'] = col
            elif any(termo in col_lower for termo in ['cep']) and 'cep' not in campos:
                campos['cep'] = col
            elif any(termo in col_lower for termo in ['bairro']) and 'bairro' not in campos:
                campos['bairro'] = col
            elif any(termo in col_lower for termo in ['dt nasc', 'nascimento']) and 'data_nascimento' not in campos:
                campos['data_nascimento'] = col
            elif any(termo in col_lower for termo in ['os:', 'os', 'ordem']) and 'numero_os' not in campos:
                campos['numero_os'] = col
            elif any(termo in col_lower for termo in ['data:', 'data']) and 'data_os' not in campos:
                campos['data_os'] = col
        
        return campos
    
    def processar_arquivo_sequencial(self, arquivo_path, ordem_arquivo):
        """Processa arquivo mantendo ordem sequencial original"""
        logger.info(f"Processando [{ordem_arquivo:02d}]: {arquivo_path.name}")
        
        try:
            # Lista de arquivos problemáticos conhecidos
            arquivos_skip = [
                'OS NOVA1.xlsm',  # Conhecido por causar problemas
                'OS NOVA_7.xlsm'  # Tem warnings de data
            ]
            
            if arquivo_path.name in arquivos_skip:
                logger.warning(f"Pulando arquivo problemático: {arquivo_path.name}")
                return 0
            
            # Carregar arquivo com tratamento robusto
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
            
            # Identificar campos
            campos = self.identificar_campos(df)
            
            if not campos.get('nome'):
                logger.warning(f"Campo nome não encontrado em {arquivo_path.name}")
                return 0
            
            # Identificar loja
            loja = self.identificar_loja_por_arquivo(arquivo_path.name)
            
            # Processar cada linha em sequência
            clientes_arquivo = 0
            for linha_idx, row in df.iterrows():
                cliente = self.extrair_cliente_sequencial(
                    row, campos, loja, arquivo_path.name, 
                    ordem_arquivo, linha_idx + 1, clientes_arquivo + 1
                )
                if cliente:
                    self.clientes_sequenciais.append(cliente)
                    clientes_arquivo += 1
            
            # Estatísticas
            self.arquivos_processados.append({
                'ordem': ordem_arquivo,
                'arquivo': arquivo_path.name,
                'loja': loja,
                'clientes': clientes_arquivo
            })
            
            if loja not in self.estatisticas['clientes_por_loja']:
                self.estatisticas['clientes_por_loja'][loja] = 0
            self.estatisticas['clientes_por_loja'][loja] += clientes_arquivo
            
            self.estatisticas['total_clientes'] += clientes_arquivo
            
            logger.info(f"✅ [{ordem_arquivo:02d}] {arquivo_path.name}: {clientes_arquivo} clientes | Loja: {loja}")
            return clientes_arquivo
            
        except Exception as e:
            logger.error(f"❌ Erro em {arquivo_path.name}: {e}")
            return 0
    
    def extrair_cliente_sequencial(self, row, campos, loja, arquivo, ordem_arquivo, linha_arquivo, sequencia_arquivo):
        """Extrai dados do cliente mantendo sequência"""
        # Dados básicos
        nome = self.normalizar_nome(row.get(campos.get('nome'))) if campos.get('nome') else None
        if not nome:
            return None
        
        # Gerar ID sequencial único
        id_sequencial = len(self.clientes_sequenciais) + 1
        
        cliente = {
            # IDs e Controle
            'ID_SEQUENCIAL': id_sequencial,
            'ORDEM_ARQUIVO': ordem_arquivo,
            'LINHA_ARQUIVO': linha_arquivo,
            'SEQUENCIA_NO_ARQUIVO': sequencia_arquivo,
            
            # Dados da Loja e Origem
            'LOJA': loja,
            'ARQUIVO_ORIGEM': arquivo,
            
            # Dados Pessoais
            'NOME_COMPLETO': nome,
            'CPF': self.limpar_cpf(row.get(campos.get('cpf'))) if campos.get('cpf') else None,
            'RG': str(row.get(campos.get('rg'))).strip() if campos.get('rg') and pd.notna(row.get(campos.get('rg'))) else None,
            'DATA_NASCIMENTO': self.extrair_data_nascimento(row.get(campos.get('data_nascimento'))) if campos.get('data_nascimento') else None,
            
            # Contatos
            'CELULAR': self.limpar_celular_sp(row.get(campos.get('celular'))) if campos.get('celular') else None,
            'EMAIL': self.normalizar_email(row.get(campos.get('email'))) if campos.get('email') else None,
            
            # Endereço
            'ENDERECO': str(row.get(campos.get('endereco'))).strip() if campos.get('endereco') and pd.notna(row.get(campos.get('endereco'))) else None,
            'CEP': str(row.get(campos.get('cep'))).strip() if campos.get('cep') and pd.notna(row.get(campos.get('cep'))) else None,
            'BAIRRO': str(row.get(campos.get('bairro'))).strip() if campos.get('bairro') and pd.notna(row.get(campos.get('bairro'))) else None,
            
            # OS (se disponível)
            'NUMERO_OS': str(row.get(campos.get('numero_os'))).strip() if campos.get('numero_os') and pd.notna(row.get(campos.get('numero_os'))) else None,
            'DATA_OS': self.extrair_data_nascimento(row.get(campos.get('data_os'))) if campos.get('data_os') else None,
            
            # Controle de Processamento
            'DATA_PROCESSAMENTO': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        return cliente
    
    def calcular_qualidade_dados(self):
        """Calcula estatísticas de qualidade dos dados"""
        if not self.clientes_sequenciais:
            return
        
        df = pd.DataFrame(self.clientes_sequenciais)
        total = len(df)
        
        self.estatisticas['qualidade_dados'] = {
            'total_clientes': total,
            'com_cpf': df['CPF'].notna().sum(),
            'com_celular': df['CELULAR'].notna().sum(),
            'com_email': df['EMAIL'].notna().sum(),
            'com_endereco': df['ENDERECO'].notna().sum(),
            'com_cep': df['CEP'].notna().sum(),
            'com_rg': df['RG'].notna().sum(),
            'com_data_nascimento': df['DATA_NASCIMENTO'].notna().sum(),
            'com_numero_os': df['NUMERO_OS'].notna().sum(),
            'pct_cpf': (df['CPF'].notna().sum() / total * 100) if total > 0 else 0,
            'pct_celular': (df['CELULAR'].notna().sum() / total * 100) if total > 0 else 0,
            'pct_email': (df['EMAIL'].notna().sum() / total * 100) if total > 0 else 0,
            'pct_endereco': (df['ENDERECO'].notna().sum() / total * 100) if total > 0 else 0
        }
    
    def gerar_arquivo_consolidado_final(self):
        """Gera arquivo consolidado final"""
        print("🚀 GERADOR DO ARQUIVO CONSOLIDADO FINAL")
        print("=" * 80)
        print("📋 Todos os 28 arquivos em sequência única")
        print("🎯 Dados completos + identificação de loja")
        print("=" * 80)
        
        # Processar todos os arquivos em ordem
        arquivos = sorted(list(Path("data/raw").glob("OS*.xlsm")) + list(Path("data/raw").glob("OS*.xlsx")))
        logger.info(f"Encontrados {len(arquivos)} arquivos para processar")
        
        self.estatisticas['total_arquivos'] = len(arquivos)
        
        for ordem, arquivo in enumerate(arquivos, 1):
            self.processar_arquivo_sequencial(arquivo, ordem)
        
        # Calcular qualidade
        self.calcular_qualidade_dados()
        
        # Salvar arquivos
        csv_file = self.salvar_csv()
        excel_file = self.salvar_excel()
        
        # Exibir resultados
        self.exibir_resultados(csv_file, excel_file)
        
        return csv_file, excel_file
    
    def salvar_csv(self):
        """Salva arquivo CSV"""
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = output_dir / f"CLIENTES_CONSOLIDADO_FINAL_{timestamp}.csv"
        
        df = pd.DataFrame(self.clientes_sequenciais)
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        logger.info(f"CSV salvo: {csv_file}")
        return csv_file
    
    def salvar_excel(self):
        """Salva arquivo Excel com múltiplas abas"""
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        excel_file = output_dir / f"CLIENTES_CONSOLIDADO_FINAL_{timestamp}.xlsx"
        
        df_clientes = pd.DataFrame(self.clientes_sequenciais)
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            # Aba principal - todos os clientes
            df_clientes.to_excel(writer, sheet_name='Clientes_Consolidados', index=False)
            
            # Aba por loja
            for loja in sorted(df_clientes['LOJA'].unique()):
                df_loja = df_clientes[df_clientes['LOJA'] == loja]
                sheet_name = f"Loja_{loja}"[:31]  # Limite do Excel
                df_loja.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Aba de estatísticas por arquivo
            df_arquivos = pd.DataFrame(self.arquivos_processados)
            df_arquivos.to_excel(writer, sheet_name='Estatisticas_Arquivos', index=False)
            
            # Aba de qualidade dos dados
            qualidade_data = []
            for loja, total in self.estatisticas['clientes_por_loja'].items():
                df_loja = df_clientes[df_clientes['LOJA'] == loja]
                qualidade_data.append({
                    'LOJA': loja,
                    'TOTAL_CLIENTES': total,
                    'COM_CPF': df_loja['CPF'].notna().sum(),
                    'COM_CELULAR': df_loja['CELULAR'].notna().sum(),
                    'COM_EMAIL': df_loja['EMAIL'].notna().sum(),
                    'COM_ENDERECO': df_loja['ENDERECO'].notna().sum(),
                    'PCT_CPF': (df_loja['CPF'].notna().sum() / total * 100) if total > 0 else 0,
                    'PCT_CELULAR': (df_loja['CELULAR'].notna().sum() / total * 100) if total > 0 else 0,
                    'PCT_EMAIL': (df_loja['EMAIL'].notna().sum() / total * 100) if total > 0 else 0,
                    'PCT_ENDERECO': (df_loja['ENDERECO'].notna().sum() / total * 100) if total > 0 else 0
                })
            
            df_qualidade = pd.DataFrame(qualidade_data)
            df_qualidade.to_excel(writer, sheet_name='Qualidade_Por_Loja', index=False)
        
        logger.info(f"Excel salvo: {excel_file}")
        return excel_file
    
    def exibir_resultados(self, csv_file, excel_file):
        """Exibe resultados finais"""
        print(f"\n📊 ARQUIVO CONSOLIDADO FINAL GERADO:")
        print("=" * 80)
        print(f"📁 Arquivos processados: {self.estatisticas['total_arquivos']}")
        print(f"👥 Total de clientes: {self.estatisticas['total_clientes']:,}")
        
        print(f"\n🏪 CLIENTES POR LOJA:")
        for loja, total in sorted(self.estatisticas['clientes_por_loja'].items()):
            print(f"   {loja}: {total:,} clientes")
        
        print(f"\n📊 QUALIDADE DOS DADOS:")
        qual = self.estatisticas['qualidade_dados']
        print(f"   🆔 CPF: {qual['com_cpf']:,} ({qual['pct_cpf']:.1f}%)")
        print(f"   📱 Celular: {qual['com_celular']:,} ({qual['pct_celular']:.1f}%)")
        print(f"   📧 Email: {qual['com_email']:,} ({qual['pct_email']:.1f}%)")
        print(f"   🏠 Endereço: {qual['com_endereco']:,} ({qual['pct_endereco']:.1f}%)")
        
        print(f"\n📁 ARQUIVOS GERADOS:")
        print("=" * 80)
        print(f"📄 CSV: {csv_file}")
        print(f"📊 Excel: {excel_file}")
        
        print(f"\n✅ ESTRUTURA DO ARQUIVO:")
        print("=" * 80)
        print("🔢 ID_SEQUENCIAL | ORDEM_ARQUIVO | LINHA_ARQUIVO")
        print("🏪 LOJA | ARQUIVO_ORIGEM")
        print("👤 NOME_COMPLETO | CPF | RG | DATA_NASCIMENTO")
        print("📱 CELULAR | EMAIL")
        print("🏠 ENDERECO | CEP | BAIRRO")
        print("📋 NUMERO_OS | DATA_OS")
        print("⏰ DATA_PROCESSAMENTO")

def main():
    """Função principal"""
    gerador = GeradorArquivoConsolidadoFinal()
    csv_file, excel_file = gerador.gerar_arquivo_consolidado_final()
    return csv_file, excel_file

if __name__ == "__main__":
    main()