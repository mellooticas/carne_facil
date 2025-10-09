#!/usr/bin/env python3
"""
Extrator Completo de Dados de Vendas e Produtos
Processa TODOS os campos de vendas, produtos, códigos e pagamentos das OS
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

class ExtratorVendas:
    def __init__(self):
        self.os_com_vendas = []
        self.produtos_identificados = set()
        self.tipos_pagamento = set()
        self.estatisticas = {
            'total_os': 0,
            'com_total': 0,
            'com_produto1': 0,
            'com_pagto1': 0,
            'com_sinal': 0,
            'com_resta': 0,
            'arquivos_processados': 0,
            'valor_total_vendas': 0
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
    
    def mapear_campos_vendas(self, colunas):
        """Mapeia colunas do arquivo para campos de vendas"""
        mapeamento = {
            'produtos': [],
            'valores': [],
            'pagamentos': [],
            'especiais': {}
        }
        
        for i, coluna in enumerate(colunas):
            coluna_str = str(coluna).strip()
            coluna_lower = coluna_str.lower()
            
            # Campos de produtos e códigos
            if any(termo in coluna_lower for termo in ['cod', 'codigo']) and 'trello' not in coluna_lower:
                mapeamento['produtos'].append({
                    'tipo': 'codigo',
                    'coluna': coluna,
                    'posicao': i,
                    'nome': coluna_str
                })
            elif any(termo in coluna_lower for termo in ['descri', 'produto']):
                mapeamento['produtos'].append({
                    'tipo': 'descricao',
                    'coluna': coluna,
                    'posicao': i,
                    'nome': coluna_str
                })
            
            # Campos de valores
            elif any(termo in coluna_lower for termo in ['valor', 'preco']) and 'total' not in coluna_lower:
                mapeamento['valores'].append({
                    'tipo': 'valor_produto',
                    'coluna': coluna,
                    'posicao': i,
                    'nome': coluna_str
                })
            
            # Campo TOTAL
            elif coluna_str == 'TOTAL' or 'total' in coluna_lower:
                mapeamento['especiais']['total'] = coluna
            
            # Campos de pagamento
            elif any(termo in coluna_lower for termo in ['pagto', 'pagamento']):
                mapeamento['pagamentos'].append({
                    'tipo': 'pagamento',
                    'coluna': coluna,
                    'posicao': i,
                    'nome': coluna_str
                })
            elif any(termo in coluna_lower for termo in ['sinal']):
                mapeamento['pagamentos'].append({
                    'tipo': 'sinal',
                    'coluna': coluna,
                    'posicao': i,
                    'nome': coluna_str
                })
            elif 'resta' in coluna_lower:
                mapeamento['especiais']['resta'] = coluna
            
            # Campos específicos da imagem
            elif 'Cod_trello' in coluna_str:
                mapeamento['especiais']['cod_trello'] = coluna
            elif coluna_str in ['Descrição', 'Descrição18', 'Descrição21', 'Descrição24', 'Descrição27']:
                numero = re.findall(r'\d+', coluna_str)
                num = numero[0] if numero else '1'
                mapeamento['produtos'].append({
                    'tipo': f'descricao_{num}',
                    'coluna': coluna,
                    'posicao': i,
                    'nome': coluna_str
                })
            elif coluna_str in ['Valor', 'Valor19', 'Valor22', 'Valor25', 'Valor28']:
                numero = re.findall(r'\d+', coluna_str)
                num = numero[0] if numero else '1'
                mapeamento['valores'].append({
                    'tipo': f'valor_{num}',
                    'coluna': coluna,
                    'posicao': i,
                    'nome': coluna_str
                })
        
        return mapeamento
    
    def extrair_valor_monetario(self, valor):
        """Extrai e normaliza valor monetário"""
        if pd.isna(valor) or str(valor).strip() == '':
            return None
        
        try:
            valor_str = str(valor).strip()
            
            # Remover símbolos e texto comum
            valor_str = valor_str.replace('R$', '').replace('R', '').replace('$', '')
            valor_str = valor_str.replace('.', '').replace(',', '.')
            valor_str = re.sub(r'[^\d\.]', '', valor_str)
            
            if valor_str and valor_str != '.':
                return float(valor_str)
            return None
        except:
            return None
    
    def extrair_codigo_produto(self, codigo):
        """Extrai código do produto"""
        if pd.isna(codigo) or str(codigo).strip() == '':
            return None
        
        codigo_str = str(codigo).strip()
        if codigo_str and codigo_str.lower() not in ['nan', '', '-']:
            return codigo_str
        return None
    
    def extrair_descricao_produto(self, descricao):
        """Extrai descrição do produto"""
        if pd.isna(descricao) or str(descricao).strip() == '':
            return None
        
        desc_str = str(descricao).strip()
        if desc_str and desc_str.lower() not in ['nan', '', '-']:
            return desc_str
        return None
    
    def processar_arquivo_vendas(self, arquivo_path):
        """Processa arquivo específico extraindo dados de vendas"""
        logger.info(f"Processando vendas: {arquivo_path.name}")
        
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
            
            # Mapear campos de vendas
            mapeamento = self.mapear_campos_vendas(df.columns)
            
            # Verificar se tem campos de vendas
            if not mapeamento['produtos'] and not mapeamento['valores'] and not mapeamento['especiais']:
                logger.warning(f"Nenhum campo de venda encontrado em {arquivo_path.name}")
                return 0
            
            # Identificar campos básicos
            campos_basicos = self.identificar_campos_basicos(df.columns)
            
            # Identificar loja
            loja = self.identificar_loja_por_arquivo(arquivo_path.name)
            
            # Processar cada linha
            os_processadas = 0
            for idx, row in df.iterrows():
                os_venda = self.extrair_vendas_linha(
                    row, mapeamento, campos_basicos, loja, arquivo_path.name, idx + 1
                )
                
                if os_venda:
                    self.os_com_vendas.append(os_venda)
                    os_processadas += 1
            
            self.estatisticas['arquivos_processados'] += 1
            self.estatisticas['total_os'] += os_processadas
            
            logger.info(f"✅ {arquivo_path.name}: {os_processadas} OS com vendas | Loja: {loja}")
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
            elif any(termo in col_str for termo in ['consultor', 'vendedor']):
                campos['consultor'] = col
        
        return campos
    
    def extrair_vendas_linha(self, row, mapeamento, campos_basicos, loja, arquivo, linha):
        """Extrai dados de vendas de uma linha específica"""
        # Dados básicos de identificação
        numero_os = str(row.get(campos_basicos.get('numero_os', ''))).strip() if campos_basicos.get('numero_os') else None
        nome = str(row.get(campos_basicos.get('nome', ''))).strip() if campos_basicos.get('nome') else None
        cpf = str(row.get(campos_basicos.get('cpf', ''))).strip() if campos_basicos.get('cpf') else None
        consultor = str(row.get(campos_basicos.get('consultor', ''))).strip() if campos_basicos.get('consultor') else None
        
        # Se não tem número da OS, pular
        if not numero_os or numero_os == 'nan':
            return None
        
        # Inicializar estrutura de venda
        os_venda = {
            # Identificação
            'numero_os': numero_os,
            'nome_informado': nome if nome != 'nan' else None,
            'cpf_informado': cpf if cpf != 'nan' else None,
            'consultor': consultor if consultor != 'nan' else None,
            'loja': loja,
            'arquivo_origem': arquivo,
            'linha_arquivo': linha,
            
            # Código especial (Trello)
            'cod_trello': self.extrair_codigo_produto(row.get(mapeamento['especiais'].get('cod_trello'))) if 'cod_trello' in mapeamento['especiais'] else None,
            
            # Produtos (até 5 produtos diferentes)
            'produto1_codigo': None,
            'produto1_descricao': None,
            'produto1_valor': None,
            'produto2_codigo': None,
            'produto2_descricao': None,
            'produto2_valor': None,
            'produto3_codigo': None,
            'produto3_descricao': None,
            'produto3_valor': None,
            'produto4_codigo': None,
            'produto4_descricao': None,
            'produto4_valor': None,
            'produto5_codigo': None,
            'produto5_descricao': None,
            'produto5_valor': None,
            
            # Valores e pagamentos
            'valor_total': self.extrair_valor_monetario(row.get(mapeamento['especiais'].get('total'))) if 'total' in mapeamento['especiais'] else None,
            'pagto_1': None,
            'sinal_1': None,
            'pagto_2': None,
            'sinal_2': None,
            'valor_resta': self.extrair_valor_monetario(row.get(mapeamento['especiais'].get('resta'))) if 'resta' in mapeamento['especiais'] else None,
            
            # Metadados
            'data_processamento': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        # Processar produtos identificados
        produto_count = 1
        
        # Primeiro, processar produtos por ordem (baseado na imagem)
        produtos_ordenados = sorted(mapeamento['produtos'], key=lambda x: x['posicao'])
        valores_ordenados = sorted(mapeamento['valores'], key=lambda x: x['posicao'])
        
        # Agrupar por posição aproximada
        i = 0
        while i < len(produtos_ordenados) and produto_count <= 5:
            produto = produtos_ordenados[i]
            
            if produto['tipo'] == 'codigo' or 'codigo' in produto['tipo']:
                codigo = self.extrair_codigo_produto(row.get(produto['coluna']))
                
                # Procurar descrição próxima
                descricao = None
                valor = None
                
                # Buscar descrição e valor nas próximas colunas
                for j in range(i+1, min(i+3, len(produtos_ordenados))):
                    if produtos_ordenados[j]['tipo'] == 'descricao' or 'descricao' in produtos_ordenados[j]['tipo']:
                        descricao = self.extrair_descricao_produto(row.get(produtos_ordenados[j]['coluna']))
                        break
                
                # Buscar valor correspondente
                for valor_item in valores_ordenados:
                    if abs(valor_item['posicao'] - produto['posicao']) <= 2:
                        valor = self.extrair_valor_monetario(row.get(valor_item['coluna']))
                        break
                
                # Adicionar produto se tem pelo menos código ou descrição
                if codigo or descricao:
                    os_venda[f'produto{produto_count}_codigo'] = codigo
                    os_venda[f'produto{produto_count}_descricao'] = descricao
                    os_venda[f'produto{produto_count}_valor'] = valor
                    
                    if codigo:
                        self.produtos_identificados.add(codigo)
                    
                    produto_count += 1
            
            i += 1
        
        # Processar pagamentos
        pagto_count = 1
        for pagamento in mapeamento['pagamentos']:
            if pagto_count > 2:
                break
            
            if 'pagamento' in pagamento['tipo']:
                pagto_valor = self.extrair_valor_monetario(row.get(pagamento['coluna']))
                os_venda[f'pagto_{pagto_count}'] = pagto_valor
            elif 'sinal' in pagamento['tipo']:
                sinal_valor = self.extrair_valor_monetario(row.get(pagamento['coluna']))
                os_venda[f'sinal_{pagto_count}'] = sinal_valor
                pagto_count += 1
        
        # Contar estatísticas
        if os_venda['valor_total'] is not None:
            self.estatisticas['com_total'] += 1
            self.estatisticas['valor_total_vendas'] += os_venda['valor_total']
        
        if os_venda['produto1_codigo'] or os_venda['produto1_descricao']:
            self.estatisticas['com_produto1'] += 1
        
        if os_venda['pagto_1'] is not None:
            self.estatisticas['com_pagto1'] += 1
        
        if os_venda['sinal_1'] is not None:
            self.estatisticas['com_sinal'] += 1
        
        if os_venda['valor_resta'] is not None:
            self.estatisticas['com_resta'] += 1
        
        return os_venda
    
    def processar_todas_vendas(self):
        """Processa todas as vendas de todos os arquivos"""
        print("💰 EXTRATOR COMPLETO DE DADOS DE VENDAS")
        print("=" * 80)
        print("🛒 Processando produtos, códigos, valores e pagamentos")
        print("💳 Códigos + Descrições + Valores + Pagamentos + Sinais")
        print("=" * 80)
        
        # Processar todos os arquivos
        arquivos = list(Path("data/raw").glob("OS*.xlsm")) + list(Path("data/raw").glob("OS*.xlsx"))
        logger.info(f"Encontrados {len(arquivos)} arquivos para processar")
        
        for arquivo in arquivos:
            self.processar_arquivo_vendas(arquivo)
        
        # Salvar resultados
        output_file = self.salvar_vendas()
        
        # Exibir resultados
        self.exibir_resultados(output_file)
        
        return output_file
    
    def salvar_vendas(self):
        """Salva dados de vendas em Excel"""
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"VENDAS_COMPLETAS_{timestamp}.xlsx"
        
        df_vendas = pd.DataFrame(self.os_com_vendas)
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Base principal de vendas
            df_vendas.to_excel(writer, sheet_name='Vendas_Completas', index=False)
            
            # Estatísticas por loja
            stats_loja = df_vendas.groupby('loja').agg({
                'numero_os': 'count',
                'valor_total': ['count', 'sum', 'mean'],
                'produto1_codigo': lambda x: x.notna().sum(),
                'pagto_1': lambda x: x.notna().sum()
            })
            stats_loja.columns = ['total_os', 'com_valor_count', 'soma_vendas', 'media_vendas', 'com_produto1', 'com_pagto1']
            stats_loja.to_excel(writer, sheet_name='Estatisticas_Por_Loja')
            
            # Produtos mais vendidos
            produtos_vendidos = []
            for _, row in df_vendas.iterrows():
                for i in range(1, 6):
                    codigo = row.get(f'produto{i}_codigo')
                    descricao = row.get(f'produto{i}_descricao')
                    valor = row.get(f'produto{i}_valor')
                    
                    if codigo or descricao:
                        produtos_vendidos.append({
                            'codigo': codigo,
                            'descricao': descricao,
                            'valor': valor,
                            'loja': row['loja']
                        })
            
            if produtos_vendidos:
                df_produtos = pd.DataFrame(produtos_vendidos)
                top_produtos = df_produtos.groupby(['codigo', 'descricao']).agg({
                    'valor': ['count', 'sum', 'mean'],
                    'loja': lambda x: ', '.join(x.unique())
                }).reset_index()
                top_produtos.columns = ['codigo', 'descricao', 'qtd_vendas', 'valor_total', 'valor_medio', 'lojas']
                top_produtos = top_produtos.sort_values('qtd_vendas', ascending=False).head(50)
                top_produtos.to_excel(writer, sheet_name='Top_Produtos', index=False)
        
        logger.info(f"Vendas salvas: {output_file}")
        return output_file
    
    def exibir_resultados(self, output_file):
        """Exibe resultados da extração de vendas"""
        print(f"\n📊 VENDAS EXTRAÍDAS:")
        print("=" * 80)
        print(f"📁 Arquivos processados: {self.estatisticas['arquivos_processados']}")
        print(f"💰 Total de OS: {self.estatisticas['total_os']:,}")
        print(f"💵 Com valor total: {self.estatisticas['com_total']:,} ({self.estatisticas['com_total']/self.estatisticas['total_os']*100:.1f}%)")
        print(f"🛒 Com produto 1: {self.estatisticas['com_produto1']:,} ({self.estatisticas['com_produto1']/self.estatisticas['total_os']*100:.1f}%)")
        print(f"💳 Com pagto 1: {self.estatisticas['com_pagto1']:,} ({self.estatisticas['com_pagto1']/self.estatisticas['total_os']*100:.1f}%)")
        print(f"💰 Com sinal: {self.estatisticas['com_sinal']:,} ({self.estatisticas['com_sinal']/self.estatisticas['total_os']*100:.1f}%)")
        print(f"💸 Valor total vendas: R$ {self.estatisticas['valor_total_vendas']:,.2f}")
        print(f"🏷️ Produtos únicos: {len(self.produtos_identificados):,}")
        
        print(f"\n📁 ARQUIVO GERADO:")
        print("=" * 80)
        print(f"✅ {output_file}")
        print(f"📊 Sheets: Vendas_Completas, Estatisticas_Por_Loja, Top_Produtos")
        
        print(f"\n💰 CAMPOS PROCESSADOS:")
        print("=" * 80)
        print("🏷️ Cod_trello: Código especial do produto")
        print("🛒 Produtos 1-5: codigo, descricao, valor de cada produto")
        print("💵 Valor_total: Total da venda")
        print("💳 Pagto 1/2: Formas de pagamento")
        print("💰 Sinal 1/2: Valores dos sinais")
        print("💸 Valor_resta: Valor restante a pagar")

def main():
    """Função principal"""
    extrator = ExtratorVendas()
    output_file = extrator.processar_todas_vendas()
    return output_file

if __name__ == "__main__":
    main()