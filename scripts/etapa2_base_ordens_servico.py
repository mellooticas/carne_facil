#!/usr/bin/env python3
"""
ETAPA 2: Gerador da Base de Ordens de Serviço
Consolida todas as OS relacionando com a Base de Clientes Master
"""

import pandas as pd
from pathlib import Path
import re
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeradorBaseOS:
    def __init__(self):
        self.ordens_servico = []
        self.base_clientes = None
        self.estatisticas = {
            'arquivos_processados': 0,
            'os_encontradas': 0,
            'os_com_cliente_identificado': 0,
            'os_com_data_valida': 0,
            'os_com_valor': 0,
            'lojas_processadas': set()
        }
    
    def carregar_base_clientes(self):
        """Carrega a base de clientes master"""
        logger.info("Carregando Base de Clientes Master...")
        
        # Encontrar o arquivo mais recente
        arquivo_base = None
        data_dir = Path("data/processed")
        
        for arquivo in data_dir.glob("BASE_CLIENTES_MASTER_*.xlsx"):
            if not arquivo_base or arquivo.stat().st_mtime > arquivo_base.stat().st_mtime:
                arquivo_base = arquivo
        
        if not arquivo_base:
            raise FileNotFoundError("Base de Clientes Master não encontrada! Execute primeiro a ETAPA 1.")
        
        logger.info(f"Carregando: {arquivo_base.name}")
        self.base_clientes = pd.read_excel(arquivo_base, sheet_name='Base_Clientes_Master')
        
        # Criar índices para busca rápida
        self.index_cpf = {cpf: idx for idx, cpf in enumerate(self.base_clientes['cpf']) if pd.notna(cpf)}
        self.index_nome = {nome: idx for idx, nome in enumerate(self.base_clientes['nome_completo']) if pd.notna(nome)}
        
        logger.info(f"✅ Base carregada: {len(self.base_clientes)} clientes únicos")
    
    def normalizar_nome(self, nome):
        """Normaliza nome para busca"""
        if pd.isna(nome):
            return None
        nome_str = str(nome).upper().strip()
        nome_str = re.sub(r'[^\w\s]', '', nome_str)
        nome_str = re.sub(r'\s+', ' ', nome_str)
        return nome_str if nome_str else None
    
    def limpar_cpf(self, cpf):
        """Limpa CPF para busca"""
        if pd.isna(cpf):
            return None
        cpf_str = re.sub(r'[^\d]', '', str(cpf))
        if len(cpf_str) == 11 and cpf_str.isdigit():
            return f"{cpf_str[:3]}.{cpf_str[3:6]}.{cpf_str[6:9]}-{cpf_str[9:]}"
        return None
    
    def extrair_data_os(self, data):
        """Extrai data da OS"""
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
    
    def extrair_valor(self, valor):
        """Extrai valor monetário"""
        if pd.isna(valor):
            return None
        try:
            if isinstance(valor, (int, float)):
                return float(valor)
            
            valor_str = str(valor).replace(',', '.').replace('R$', '').strip()
            valor_str = re.sub(r'[^\d\.]', '', valor_str)
            
            if valor_str:
                return float(valor_str)
            return None
        except:
            return None
    
    def identificar_cliente(self, nome, cpf):
        """Identifica cliente na base master"""
        # Primeiro, tentar por CPF
        cpf_limpo = self.limpar_cpf(cpf)
        if cpf_limpo and cpf_limpo in self.index_cpf:
            idx = self.index_cpf[cpf_limpo]
            cliente = self.base_clientes.iloc[idx]
            return {
                'cliente_id': idx,
                'metodo_identificacao': 'CPF',
                'nome_cliente': cliente['nome_completo'],
                'cpf_cliente': cliente['cpf'],
                'celular_cliente': cliente.get('celular'),
                'email_cliente': cliente.get('email'),
                'endereco_cliente': cliente.get('endereco'),
                'loja_origem_cliente': cliente.get('origem_loja')
            }
        
        # Senão, tentar por nome exato
        nome_limpo = self.normalizar_nome(nome)
        if nome_limpo and nome_limpo in self.index_nome:
            idx = self.index_nome[nome_limpo]
            cliente = self.base_clientes.iloc[idx]
            return {
                'cliente_id': idx,
                'metodo_identificacao': 'NOME_EXATO',
                'nome_cliente': cliente['nome_completo'],
                'cpf_cliente': cliente['cpf'],
                'celular_cliente': cliente.get('celular'),
                'email_cliente': cliente.get('email'),
                'endereco_cliente': cliente.get('endereco'),
                'loja_origem_cliente': cliente.get('origem_loja')
            }
        
        # Se não encontrou, busca parcial por nome
        if nome_limpo:
            for nome_base, idx in self.index_nome.items():
                if nome_limpo in nome_base or nome_base in nome_limpo:
                    cliente = self.base_clientes.iloc[idx]
                    return {
                        'cliente_id': idx,
                        'metodo_identificacao': 'NOME_PARCIAL',
                        'nome_cliente': cliente['nome_completo'],
                        'cpf_cliente': cliente['cpf'],
                        'celular_cliente': cliente.get('celular'),
                        'email_cliente': cliente.get('email'),
                        'endereco_cliente': cliente.get('endereco'),
                        'loja_origem_cliente': cliente.get('origem_loja')
                    }
        
        return None
    
    def identificar_campos_os(self, df):
        """Identifica campos da OS"""
        campos = {}
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            
            if any(termo in col_lower for termo in ['nome:', 'nome', 'cliente', 'paciente']) and 'nome' not in campos:
                campos['nome'] = col
            elif any(termo in col_lower for termo in ['cpf']) and 'cpf' not in campos:
                campos['cpf'] = col
            elif any(termo in col_lower for termo in ['os:', 'os', 'ordem', 'numero']) and 'numero_os' not in campos:
                campos['numero_os'] = col
            elif any(termo in col_lower for termo in ['data:', 'data', 'dt']) and 'data_os' not in campos:
                campos['data_os'] = col
            elif any(termo in col_lower for termo in ['valor:', 'valor', 'preco', 'total']) and 'valor' not in campos:
                campos['valor'] = col
            elif any(termo in col_lower for termo in ['descricao', 'produto', 'servico']) and 'descricao' not in campos:
                campos['descricao'] = col
            elif any(termo in col_lower for termo in ['obs', 'observacao']) and 'observacao' not in campos:
                campos['observacao'] = col
            elif any(termo in col_lower for termo in ['loja']) and 'loja' not in campos:
                campos['loja'] = col
        
        return campos
    
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
    
    def processar_arquivo_os(self, arquivo_path):
        """Processa arquivo de OS"""
        logger.info(f"Processando OS: {arquivo_path.name}")
        
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
            
            # Identificar campos
            campos = self.identificar_campos_os(df)
            
            if not campos.get('nome'):
                logger.warning(f"Campo nome não encontrado em {arquivo_path.name}")
                return 0
            
            # Identificar loja
            loja = self.identificar_loja_por_arquivo(arquivo_path.name)
            self.estatisticas['lojas_processadas'].add(loja)
            
            # Processar cada linha
            os_processadas = 0
            for idx, row in df.iterrows():
                os_data = self.extrair_os(row, campos, loja, arquivo_path.name)
                if os_data:
                    self.ordens_servico.append(os_data)
                    os_processadas += 1
            
            self.estatisticas['arquivos_processados'] += 1
            self.estatisticas['os_encontradas'] += os_processadas
            
            logger.info(f"✅ {arquivo_path.name}: {os_processadas} OS processadas")
            return os_processadas
            
        except Exception as e:
            logger.error(f"❌ Erro em {arquivo_path.name}: {e}")
            return 0
    
    def extrair_os(self, row, campos, loja, arquivo):
        """Extrai dados da OS"""
        # Dados básicos da OS
        nome = self.normalizar_nome(row.get(campos.get('nome'))) if campos.get('nome') else None
        if not nome:
            return None
        
        cpf = row.get(campos.get('cpf')) if campos.get('cpf') else None
        numero_os = str(row.get(campos.get('numero_os'))).strip() if campos.get('numero_os') and pd.notna(row.get(campos.get('numero_os'))) else None
        data_os = self.extrair_data_os(row.get(campos.get('data_os'))) if campos.get('data_os') else None
        valor = self.extrair_valor(row.get(campos.get('valor'))) if campos.get('valor') else None
        descricao = str(row.get(campos.get('descricao'))).strip() if campos.get('descricao') and pd.notna(row.get(campos.get('descricao'))) else None
        observacao = str(row.get(campos.get('observacao'))).strip() if campos.get('observacao') and pd.notna(row.get(campos.get('observacao'))) else None
        
        # Identificar cliente
        cliente_info = self.identificar_cliente(nome, cpf)
        
        # Preparar dados da OS
        os_data = {
            'numero_os': numero_os,
            'data_os': data_os,
            'valor_os': valor,
            'descricao_servico': descricao,
            'observacao': observacao,
            'loja_os': loja,
            'arquivo_origem': arquivo,
            'nome_informado': nome,
            'cpf_informado': self.limpar_cpf(cpf),
            'data_processamento': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        # Adicionar informações do cliente se identificado
        if cliente_info:
            os_data.update(cliente_info)
            self.estatisticas['os_com_cliente_identificado'] += 1
        else:
            os_data.update({
                'cliente_id': None,
                'metodo_identificacao': None,
                'nome_cliente': None,
                'cpf_cliente': None,
                'celular_cliente': None,
                'email_cliente': None,
                'endereco_cliente': None,
                'loja_origem_cliente': None
            })
        
        # Atualizar estatísticas
        if data_os:
            self.estatisticas['os_com_data_valida'] += 1
        if valor:
            self.estatisticas['os_com_valor'] += 1
        
        return os_data
    
    def gerar_base_os(self):
        """Gera a base completa de OS"""
        print("🚀 GERADOR DA BASE DE ORDENS DE SERVIÇO")
        print("=" * 80)
        print("📋 ETAPA 2: Consolidação de todas as OS com clientes")
        print("🔗 Relacionando OS com Base de Clientes Master")
        print("=" * 80)
        
        # Carregar base de clientes
        self.carregar_base_clientes()
        
        # Processar todos os arquivos de OS
        arquivos = list(Path("data/raw").glob("OS*.xlsm")) + list(Path("data/raw").glob("OS*.xlsx"))
        logger.info(f"Encontrados {len(arquivos)} arquivos de OS para processar")
        
        for arquivo in arquivos:
            self.processar_arquivo_os(arquivo)
        
        # Salvar base de OS
        output_file = self.salvar_base_os()
        
        # Exibir resultados
        self.exibir_resultados(output_file)
        
        return output_file
    
    def salvar_base_os(self):
        """Salva a base de OS em Excel"""
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"BASE_ORDENS_SERVICO_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Preparar DataFrame
        df_os = pd.DataFrame(self.ordens_servico)
        
        # Reordenar colunas
        colunas_ordenadas = [
            'numero_os', 'data_os', 'valor_os', 'loja_os',
            'nome_informado', 'cpf_informado',
            'cliente_id', 'metodo_identificacao', 
            'nome_cliente', 'cpf_cliente', 'celular_cliente', 'email_cliente',
            'endereco_cliente', 'loja_origem_cliente',
            'descricao_servico', 'observacao',
            'arquivo_origem', 'data_processamento'
        ]
        
        colunas_existentes = [col for col in colunas_ordenadas if col in df_os.columns]
        df_os = df_os[colunas_existentes]
        
        # Salvar com múltiplas sheets
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Base principal
            df_os.to_excel(writer, sheet_name='Base_OS_Completa', index=False)
            
            # OS com clientes identificados
            df_com_cliente = df_os[df_os['cliente_id'].notna()]
            df_com_cliente.to_excel(writer, sheet_name='OS_Com_Cliente', index=False)
            
            # OS sem clientes identificados
            df_sem_cliente = df_os[df_os['cliente_id'].isna()]
            df_sem_cliente.to_excel(writer, sheet_name='OS_Sem_Cliente', index=False)
            
            # Estatísticas por loja
            stats_loja = df_os.groupby('loja_os').agg({
                'numero_os': 'count',
                'cliente_id': lambda x: x.notna().sum(),
                'valor_os': lambda x: x.notna().sum(),
                'data_os': lambda x: x.notna().sum()
            }).rename(columns={
                'numero_os': 'total_os',
                'cliente_id': 'os_com_cliente',
                'valor_os': 'os_com_valor',
                'data_os': 'os_com_data'
            })
            stats_loja.to_excel(writer, sheet_name='Estatisticas_Por_Loja')
            
            # Resumo de qualidade
            total_os = len(df_os)
            qualidade = {
                'Métrica': [
                    'Total de OS',
                    'OS com Cliente Identificado', 
                    'OS com Data Válida',
                    'OS com Valor',
                    'OS por CPF',
                    'OS por Nome Exato',
                    'OS por Nome Parcial'
                ],
                'Quantidade': [
                    total_os,
                    len(df_com_cliente),
                    self.estatisticas['os_com_data_valida'],
                    self.estatisticas['os_com_valor'],
                    len(df_os[df_os['metodo_identificacao'] == 'CPF']),
                    len(df_os[df_os['metodo_identificacao'] == 'NOME_EXATO']),
                    len(df_os[df_os['metodo_identificacao'] == 'NOME_PARCIAL'])
                ],
                'Percentual': [
                    100.0,
                    (len(df_com_cliente) / total_os * 100) if total_os > 0 else 0,
                    (self.estatisticas['os_com_data_valida'] / total_os * 100) if total_os > 0 else 0,
                    (self.estatisticas['os_com_valor'] / total_os * 100) if total_os > 0 else 0,
                    (len(df_os[df_os['metodo_identificacao'] == 'CPF']) / total_os * 100) if total_os > 0 else 0,
                    (len(df_os[df_os['metodo_identificacao'] == 'NOME_EXATO']) / total_os * 100) if total_os > 0 else 0,
                    (len(df_os[df_os['metodo_identificacao'] == 'NOME_PARCIAL']) / total_os * 100) if total_os > 0 else 0
                ]
            }
            
            df_qualidade = pd.DataFrame(qualidade)
            df_qualidade.to_excel(writer, sheet_name='Relatorio_Qualidade', index=False)
        
        logger.info(f"Base de OS salva em: {output_file}")
        return output_file
    
    def exibir_resultados(self, output_file):
        """Exibe resultados finais"""
        total_os = self.estatisticas['os_encontradas']
        
        print(f"\n📊 RESULTADOS DA BASE DE ORDENS DE SERVIÇO:")
        print("=" * 80)
        print(f"📁 Arquivos processados: {self.estatisticas['arquivos_processados']}")
        print(f"🏪 Lojas processadas: {len(self.estatisticas['lojas_processadas'])}")
        print(f"📋 OS encontradas: {total_os:,}")
        print(f"🔗 OS com cliente identificado: {self.estatisticas['os_com_cliente_identificado']:,} ({self.estatisticas['os_com_cliente_identificado']/total_os*100:.1f}%)")
        print(f"📅 OS com data válida: {self.estatisticas['os_com_data_valida']:,} ({self.estatisticas['os_com_data_valida']/total_os*100:.1f}%)")
        print(f"💰 OS com valor: {self.estatisticas['os_com_valor']:,} ({self.estatisticas['os_com_valor']/total_os*100:.1f}%)")
        
        print(f"\n📁 ARQUIVO GERADO:")
        print("=" * 80)
        print(f"✅ {output_file}")
        print(f"📊 Sheets: Base_OS_Completa, OS_Com_Cliente, OS_Sem_Cliente, Estatisticas_Por_Loja, Relatorio_Qualidade")
        
        print(f"\n🎯 SISTEMA COMPLETO:")
        print("=" * 80)
        print("✅ ETAPA 1: Base de Clientes Master criada")
        print("✅ ETAPA 2: Base de Ordens de Serviço criada")
        print("🔗 RESULTADO: Sistema completo com clientes e OS relacionados")
        print("📊 PRÓXIMO: Dashboard unificado ou análises específicas")

def main():
    """Função principal"""
    gerador = GeradorBaseOS()
    output_file = gerador.gerar_base_os()
    return output_file

if __name__ == "__main__":
    main()