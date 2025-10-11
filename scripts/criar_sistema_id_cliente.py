#!/usr/bin/env python3
"""
Sistema de ID Cliente nico
Cria numerao nica para relacionamento Cliente  OS
"""

import pandas as pd
from pathlib import Path
import re
from datetime import datetime
import logging
import hashlib

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SistemaIDCliente:
    def __init__(self):
        self.base_clientes = None
        self.mapeamento_ids = {}
        self.clientes_com_id = []
        self.estatisticas = {
            'total_clientes': 0,
            'com_cpf': 0,
            'sem_cpf': 0,
            'duplicados_resolvidos': 0
        }
    
    def carregar_base_clientes(self):
        """Carrega a base de clientes master"""
        logger.info("Carregando Base de Clientes Master...")
        
        data_dir = Path("data/processed")
        arquivo_base = None
        
        for arquivo in data_dir.glob("BASE_CLIENTES_MASTER_*.xlsx"):
            if not arquivo_base or arquivo.stat().st_mtime > arquivo_base.stat().st_mtime:
                arquivo_base = arquivo
        
        if not arquivo_base:
            raise FileNotFoundError("Base de Clientes Master no encontrada!")
        
        logger.info(f"Carregando: {arquivo_base.name}")
        self.base_clientes = pd.read_excel(arquivo_base, sheet_name='Base_Clientes_Master')
        
        logger.info(f" {len(self.base_clientes)} clientes carregados")
    
    def limpar_cpf(self, cpf):
        """Limpa CPF para chave"""
        if pd.isna(cpf):
            return None
        cpf_str = re.sub(r'[^\d]', '', str(cpf))
        if len(cpf_str) == 11 and cpf_str.isdigit():
            return cpf_str
        return None
    
    def normalizar_nome(self, nome):
        """Normaliza nome para chave"""
        if pd.isna(nome):
            return None
        nome_str = str(nome).upper().strip()
        nome_str = re.sub(r'[^\w\s]', '', nome_str)
        nome_str = re.sub(r'\s+', ' ', nome_str)
        return nome_str if nome_str else None
    
    def gerar_chave_cliente(self, nome, cpf, data_nascimento=None):
        """Gera chave nica para o cliente"""
        # Prioridade 1: CPF limpo
        cpf_limpo = self.limpar_cpf(cpf)
        if cpf_limpo:
            return f"CPF_{cpf_limpo}"
        
        # Prioridade 2: Nome + Data Nascimento
        nome_limpo = self.normalizar_nome(nome)
        if nome_limpo and pd.notna(data_nascimento):
            data_str = str(data_nascimento).replace('/', '').replace('-', '')[:8]
            return f"NOME_DATA_{nome_limpo}_{data_str}"
        
        # Prioridade 3: Apenas Nome
        if nome_limpo:
            return f"NOME_{nome_limpo}"
        
        # ltimo recurso: Hash baseado nos dados disponveis
        dados_hash = str(nome or '') + str(cpf or '') + str(data_nascimento or '')
        hash_obj = hashlib.md5(dados_hash.encode())
        return f"HASH_{hash_obj.hexdigest()[:8]}"
    
    def criar_sistema_ids(self):
        """Cria sistema de IDs nicos para todos os clientes"""
        print(" SISTEMA DE ID CLIENTE NICO")
        print("=" * 80)
        print(" Criando numerao nica para relacionamento")
        print(" Base: CPF > Nome+Data > Nome > Hash")
        print("=" * 80)
        
        # Carregar base
        self.carregar_base_clientes()
        
        # Processar cada cliente
        id_contador = 1
        chaves_processadas = set()
        
        for idx, cliente in self.base_clientes.iterrows():
            # Gerar chave nica
            chave = self.gerar_chave_cliente(
                cliente.get('nome_completo'),
                cliente.get('cpf'),
                cliente.get('data_nascimento')
            )
            
            # Verificar se j foi processada (duplicado)
            if chave in chaves_processadas:
                # Encontrar ID existente
                id_cliente = self.mapeamento_ids[chave]
                self.estatisticas['duplicados_resolvidos'] += 1
            else:
                # Criar novo ID
                id_cliente = f"CLI_{id_contador:06d}"
                self.mapeamento_ids[chave] = id_cliente
                chaves_processadas.add(chave)
                id_contador += 1
            
            # Adicionar  lista com ID
            cliente_com_id = dict(cliente)
            cliente_com_id['ID_CLIENTE'] = id_cliente
            cliente_com_id['CHAVE_CLIENTE'] = chave
            cliente_com_id['METODO_ID'] = chave.split('_')[0]
            
            self.clientes_com_id.append(cliente_com_id)
            
            # Estatsticas
            if cliente.get('cpf'):
                self.estatisticas['com_cpf'] += 1
            else:
                self.estatisticas['sem_cpf'] += 1
        
        self.estatisticas['total_clientes'] = len(self.clientes_com_id)
        
        # Salvar base com IDs
        output_file = self.salvar_base_com_ids()
        
        # Exibir resultados
        self.exibir_resultados(output_file)
        
        return output_file, self.mapeamento_ids
    
    def salvar_base_com_ids(self):
        """Salva base de clientes com IDs nicos"""
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"BASE_CLIENTES_COM_ID_{timestamp}.xlsx"
        
        df_clientes = pd.DataFrame(self.clientes_com_id)
        
        # Reordenar colunas para colocar ID no incio
        colunas = ['ID_CLIENTE', 'CHAVE_CLIENTE', 'METODO_ID'] + [col for col in df_clientes.columns if col not in ['ID_CLIENTE', 'CHAVE_CLIENTE', 'METODO_ID']]
        df_clientes = df_clientes[colunas]
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Base principal com IDs
            df_clientes.to_excel(writer, sheet_name='Clientes_Com_ID', index=False)
            
            # Estatsticas de IDs
            stats_metodos = df_clientes['METODO_ID'].value_counts().reset_index()
            stats_metodos.columns = ['Metodo_ID', 'Quantidade']
            stats_metodos['Percentual'] = (stats_metodos['Quantidade'] / len(df_clientes) * 100).round(1)
            stats_metodos.to_excel(writer, sheet_name='Estatisticas_Metodos', index=False)
            
            # Mapeamento de chaves para IDs
            mapeamento_df = pd.DataFrame([
                {'Chave_Cliente': chave, 'ID_Cliente': id_cliente}
                for chave, id_cliente in self.mapeamento_ids.items()
            ])
            mapeamento_df.to_excel(writer, sheet_name='Mapeamento_Chaves', index=False)
            
            # Duplicados identificados
            clientes_duplicados = df_clientes[df_clientes.duplicated(subset=['ID_CLIENTE'], keep=False)]
            if not clientes_duplicados.empty:
                clientes_duplicados.to_excel(writer, sheet_name='Duplicados_Resolvidos', index=False)
        
        logger.info(f"Base com IDs salva: {output_file}")
        return output_file
    
    def exibir_resultados(self, output_file):
        """Exibe resultados do sistema de IDs"""
        print(f"\n SISTEMA DE IDs CRIADO:")
        print("=" * 80)
        print(f" Total de clientes: {self.estatisticas['total_clientes']:,}")
        print(f" IDs nicos gerados: {len(self.mapeamento_ids):,}")
        print(f" Com CPF: {self.estatisticas['com_cpf']:,} ({self.estatisticas['com_cpf']/self.estatisticas['total_clientes']*100:.1f}%)")
        print(f" Sem CPF: {self.estatisticas['sem_cpf']:,} ({self.estatisticas['sem_cpf']/self.estatisticas['total_clientes']*100:.1f}%)")
        print(f" Duplicados resolvidos: {self.estatisticas['duplicados_resolvidos']:,}")
        
        # Estatsticas por mtodo
        df_clientes = pd.DataFrame(self.clientes_com_id)
        metodos = df_clientes['METODO_ID'].value_counts()
        
        print(f"\n MTODOS DE IDENTIFICAO:")
        for metodo, count in metodos.items():
            print(f"   {metodo}: {count:,} clientes ({count/len(df_clientes)*100:.1f}%)")
        
        print(f"\n ARQUIVO GERADO:")
        print("=" * 80)
        print(f" {output_file}")
        print(f" Sheets: Clientes_Com_ID, Estatisticas_Metodos, Mapeamento_Chaves")
        
        print(f"\n ESTRUTURA DO ID:")
        print("=" * 80)
        print(" ID_CLIENTE: CLI_000001, CLI_000002, ...")
        print(" CHAVE_CLIENTE: CPF_12345678901, NOME_JOAO_SILVA_01011980, ...")
        print(" METODO_ID: CPF, NOME, HASH")
        
        print(f"\n PRONTO PARA RELACIONAMENTO:")
        print("=" * 80)
        print(" Cada cliente tem ID nico")
        print(" Base preparada para relacionar com OS")
        print(" Prximo: Extrair dados completos das OS")

def main():
    """Funo principal"""
    sistema = SistemaIDCliente()
    output_file, mapeamento = sistema.criar_sistema_ids()
    return output_file, mapeamento

if __name__ == "__main__":
    main()