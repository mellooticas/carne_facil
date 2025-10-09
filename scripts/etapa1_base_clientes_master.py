#!/usr/bin/env python3
"""
ETAPA 1: Gerador da Base de Clientes Master
Consolida TODOS os clientes únicos com dados completos
"""

import pandas as pd
from pathlib import Path
import re
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeradorBaseClientes:
    def __init__(self):
        self.clientes_master = []
        self.estatisticas = {
            'arquivos_processados': 0,
            'clientes_encontrados': 0,
            'clientes_unicos': 0,
            'com_cpf': 0,
            'com_celular': 0,
            'com_email': 0,
            'com_endereco_completo': 0
        }
    
    def limpar_cpf(self, cpf):
        """Limpa e valida CPF"""
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
        # Validação básica de email
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
            return None
        except:
            return None
    
    def identificar_campos(self, df):
        """Identifica campos do DataFrame"""
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
            elif any(termo in col_lower for termo in ['loja']) and 'loja' not in campos:
                campos['loja'] = col
        
        return campos
    
    def processar_arquivo(self, arquivo_path):
        """Processa um arquivo e extrai clientes"""
        logger.info(f"Processando: {arquivo_path.name}")
        
        try:
            # Carregar arquivo com tratamento de erro robusto
            engine = 'openpyxl' if arquivo_path.suffix.lower() in ['.xlsx', '.xlsm'] else None
            
            # Primeiro, tentar carregar o arquivo
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
            
            # Tentar ler o DataFrame
            try:
                df = pd.read_excel(arquivo_path, sheet_name=sheet_principal, engine=engine)
            except Exception as e:
                logger.warning(f"Erro ao ler sheet {sheet_principal} de {arquivo_path.name}: {e}")
                return 0
            
            # Identificar campos
            campos = self.identificar_campos(df)
            
            if not campos.get('nome'):
                logger.warning(f"Campo nome não encontrado em {arquivo_path.name}")
                return 0
            
            # Extrair clientes
            clientes_arquivo = 0
            loja = self.identificar_loja_por_arquivo(arquivo_path.name)
            
            for idx, row in df.iterrows():
                cliente = self.extrair_cliente(row, campos, loja, arquivo_path.name)
                if cliente:
                    self.clientes_master.append(cliente)
                    clientes_arquivo += 1
            
            self.estatisticas['arquivos_processados'] += 1
            self.estatisticas['clientes_encontrados'] += clientes_arquivo
            
            logger.info(f"✅ {arquivo_path.name}: {clientes_arquivo} clientes extraídos")
            return clientes_arquivo
            
        except Exception as e:
            logger.error(f"❌ Erro em {arquivo_path.name}: {e}")
            return 0
    
    def extrair_cliente(self, row, campos, loja, arquivo):
        """Extrai dados do cliente de uma linha"""
        cliente = {
            'origem_loja': loja,
            'origem_arquivo': arquivo,
            'data_extracao': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        # Extrair dados básicos
        nome = self.normalizar_nome(row.get(campos.get('nome'))) if campos.get('nome') else None
        if not nome:
            return None  # Cliente deve ter nome
        
        cliente['nome_completo'] = nome
        
        # Dados pessoais
        cliente['cpf'] = self.limpar_cpf(row.get(campos.get('cpf'))) if campos.get('cpf') else None
        cliente['rg'] = str(row.get(campos.get('rg'))).strip() if campos.get('rg') and pd.notna(row.get(campos.get('rg'))) else None
        cliente['data_nascimento'] = self.extrair_data_nascimento(row.get(campos.get('data_nascimento'))) if campos.get('data_nascimento') else None
        
        # Contatos
        cliente['celular'] = self.limpar_celular_sp(row.get(campos.get('celular'))) if campos.get('celular') else None
        cliente['email'] = self.normalizar_email(row.get(campos.get('email'))) if campos.get('email') else None
        
        # Endereço
        cliente['endereco'] = str(row.get(campos.get('endereco'))).strip() if campos.get('endereco') and pd.notna(row.get(campos.get('endereco'))) else None
        cliente['cep'] = str(row.get(campos.get('cep'))).strip() if campos.get('cep') and pd.notna(row.get(campos.get('cep'))) else None
        cliente['bairro'] = str(row.get(campos.get('bairro'))).strip() if campos.get('bairro') and pd.notna(row.get(campos.get('bairro'))) else None
        
        return cliente
    
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
    
    def consolidar_clientes_duplicados(self):
        """Consolida clientes duplicados usando CPF como chave principal"""
        logger.info("Consolidando clientes duplicados...")
        
        # Agrupar por CPF primeiro (mais confiável)
        clientes_por_cpf = {}
        clientes_sem_cpf = []
        
        for cliente in self.clientes_master:
            cpf = cliente.get('cpf')
            if cpf:
                if cpf not in clientes_por_cpf:
                    clientes_por_cpf[cpf] = []
                clientes_por_cpf[cpf].append(cliente)
            else:
                clientes_sem_cpf.append(cliente)
        
        # Consolidar grupos por CPF
        clientes_consolidados = []
        
        for cpf, grupo in clientes_por_cpf.items():
            if len(grupo) == 1:
                clientes_consolidados.append(grupo[0])
            else:
                cliente_consolidado = self.mesclar_clientes(grupo)
                clientes_consolidados.append(cliente_consolidado)
        
        # Para clientes sem CPF, agrupar por nome + data nascimento
        clientes_sem_cpf_agrupados = {}
        
        for cliente in clientes_sem_cpf:
            chave = f"{cliente['nome_completo']}_{cliente.get('data_nascimento', 'SEM_DATA')}"
            if chave not in clientes_sem_cpf_agrupados:
                clientes_sem_cpf_agrupados[chave] = []
            clientes_sem_cpf_agrupados[chave].append(cliente)
        
        for grupo in clientes_sem_cpf_agrupados.values():
            if len(grupo) == 1:
                clientes_consolidados.append(grupo[0])
            else:
                cliente_consolidado = self.mesclar_clientes(grupo)
                clientes_consolidados.append(cliente_consolidado)
        
        self.estatisticas['clientes_unicos'] = len(clientes_consolidados)
        return clientes_consolidados
    
    def mesclar_clientes(self, grupo):
        """Mescla dados de clientes duplicados"""
        cliente_master = dict(grupo[0])  # Base no primeiro
        
        # Consolidar lojas de origem
        lojas = list(set([c['origem_loja'] for c in grupo]))
        arquivos = list(set([c['origem_arquivo'] for c in grupo]))
        
        cliente_master['origem_loja'] = '; '.join(lojas)
        cliente_master['origem_arquivo'] = f"{len(arquivos)} arquivos"
        cliente_master['total_registros_mesclados'] = len(grupo)
        
        # Usar dados mais completos de cada campo
        for cliente in grupo[1:]:
            for campo in ['rg', 'data_nascimento', 'celular', 'email', 'endereco', 'cep', 'bairro']:
                if not cliente_master.get(campo) and cliente.get(campo):
                    cliente_master[campo] = cliente[campo]
        
        return cliente_master
    
    def calcular_estatisticas_finais(self, clientes_consolidados):
        """Calcula estatísticas finais"""
        for cliente in clientes_consolidados:
            if cliente.get('cpf'):
                self.estatisticas['com_cpf'] += 1
            if cliente.get('celular'):
                self.estatisticas['com_celular'] += 1
            if cliente.get('email'):
                self.estatisticas['com_email'] += 1
            if cliente.get('endereco') and cliente.get('cep'):
                self.estatisticas['com_endereco_completo'] += 1
    
    def gerar_base_master(self):
        """Gera a base master de clientes"""
        print("🚀 GERADOR DA BASE DE CLIENTES MASTER")
        print("=" * 80)
        print("📋 ETAPA 1: Consolidação completa de todos os clientes")
        print("🎯 Objetivo: Base única com dados pessoais + endereço + contatos")
        print("=" * 80)
        
        # Processar todos os arquivos
        arquivos = list(Path("data/raw").glob("OS*.xlsm")) + list(Path("data/raw").glob("OS*.xlsx"))
        logger.info(f"Encontrados {len(arquivos)} arquivos para processar")
        
        for arquivo in arquivos:
            self.processar_arquivo(arquivo)
        
        # Consolidar duplicados
        clientes_consolidados = self.consolidar_clientes_duplicados()
        
        # Calcular estatísticas
        self.calcular_estatisticas_finais(clientes_consolidados)
        
        # Salvar base master
        output_file = self.salvar_base_master(clientes_consolidados)
        
        # Exibir resultados
        self.exibir_resultados(output_file)
        
        return output_file
    
    def salvar_base_master(self, clientes_consolidados):
        """Salva a base master em Excel"""
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"BASE_CLIENTES_MASTER_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Preparar DataFrame
        df_clientes = pd.DataFrame(clientes_consolidados)
        
        # Reordenar colunas para melhor visualização
        colunas_ordenadas = [
            'nome_completo', 'cpf', 'rg', 'data_nascimento',
            'celular', 'email',
            'endereco', 'cep', 'bairro',
            'origem_loja', 'origem_arquivo', 'total_registros_mesclados',
            'data_extracao'
        ]
        
        # Apenas colunas que existem
        colunas_existentes = [col for col in colunas_ordenadas if col in df_clientes.columns]
        df_clientes = df_clientes[colunas_existentes]
        
        # Salvar com múltiplas sheets
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Base principal
            df_clientes.to_excel(writer, sheet_name='Base_Clientes_Master', index=False)
            
            # Estatísticas por loja
            stats_loja = df_clientes.groupby('origem_loja').agg({
                'nome_completo': 'count',
                'cpf': lambda x: x.notna().sum(),
                'celular': lambda x: x.notna().sum(),
                'email': lambda x: x.notna().sum(),
                'endereco': lambda x: x.notna().sum()
            }).rename(columns={
                'nome_completo': 'total_clientes',
                'cpf': 'com_cpf',
                'celular': 'com_celular', 
                'email': 'com_email',
                'endereco': 'com_endereco'
            })
            stats_loja.to_excel(writer, sheet_name='Estatisticas_Por_Loja')
            
            # Relatório de qualidade
            qualidade = {
                'Campo': ['Total de Clientes', 'Com CPF', 'Com Celular', 'Com Email', 'Com Endereço Completo'],
                'Quantidade': [
                    len(df_clientes),
                    df_clientes['cpf'].notna().sum(),
                    df_clientes['celular'].notna().sum(),
                    df_clientes['email'].notna().sum(),
                    (df_clientes['endereco'].notna() & df_clientes['cep'].notna()).sum()
                ],
                'Percentual': [
                    100.0,
                    (df_clientes['cpf'].notna().sum() / len(df_clientes) * 100),
                    (df_clientes['celular'].notna().sum() / len(df_clientes) * 100),
                    (df_clientes['email'].notna().sum() / len(df_clientes) * 100),
                    ((df_clientes['endereco'].notna() & df_clientes['cep'].notna()).sum() / len(df_clientes) * 100)
                ]
            }
            
            df_qualidade = pd.DataFrame(qualidade)
            df_qualidade.to_excel(writer, sheet_name='Relatorio_Qualidade', index=False)
        
        logger.info(f"Base master salva em: {output_file}")
        return output_file
    
    def exibir_resultados(self, output_file):
        """Exibe resultados finais"""
        print(f"\n📊 RESULTADOS DA BASE MASTER:")
        print("=" * 80)
        print(f"📁 Arquivos processados: {self.estatisticas['arquivos_processados']}")
        print(f"📋 Clientes encontrados: {self.estatisticas['clientes_encontrados']:,}")
        print(f"👤 Clientes únicos: {self.estatisticas['clientes_unicos']:,}")
        print(f"🆔 Com CPF: {self.estatisticas['com_cpf']:,} ({self.estatisticas['com_cpf']/self.estatisticas['clientes_unicos']*100:.1f}%)")
        print(f"📱 Com celular: {self.estatisticas['com_celular']:,} ({self.estatisticas['com_celular']/self.estatisticas['clientes_unicos']*100:.1f}%)")
        print(f"📧 Com email: {self.estatisticas['com_email']:,} ({self.estatisticas['com_email']/self.estatisticas['clientes_unicos']*100:.1f}%)")
        print(f"🏠 Com endereço completo: {self.estatisticas['com_endereco_completo']:,} ({self.estatisticas['com_endereco_completo']/self.estatisticas['clientes_unicos']*100:.1f}%)")
        
        print(f"\n📁 ARQUIVO GERADO:")
        print("=" * 80)
        print(f"✅ {output_file}")
        print(f"📊 Sheets: Base_Clientes_Master, Estatisticas_Por_Loja, Relatorio_Qualidade")
        
        print(f"\n🎯 PRÓXIMA ETAPA:")
        print("=" * 80)
        print("📋 ETAPA 2: Criar documento de Ordens de Serviço")
        print("🔗 Relacionar OS com clientes da base master")
        print("📊 Dashboard unificado de clientes + OS")

def main():
    """Função principal"""
    gerador = GeradorBaseClientes()
    output_file = gerador.gerar_base_master()
    return output_file

if __name__ == "__main__":
    main()