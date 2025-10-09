#!/usr/bin/env python3
"""
Sistema de Consolidação Inteligente de Dados das Óticas
Mescla informações de múltiplas linhas em registros únicos completos
"""

import pandas as pd
import numpy as np
from pathlib import Path
from fuzzywuzzy import fuzz
import re
from collections import defaultdict
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConsolidadorInteligente:
    def __init__(self):
        self.dados_consolidados = []
        self.mapeamento_campos = {}
        self.grupos_duplicatas = {}
        self.relatorio_mesclagens = []
        
    def limpar_cpf(self, cpf):
        """Limpa e valida CPF"""
        if pd.isna(cpf):
            return None
        cpf_str = re.sub(r'[^\d]', '', str(cpf))
        if len(cpf_str) == 11 and cpf_str.isdigit():
            return cpf_str
        return None
    
    def limpar_telefone(self, telefone):
        """Limpa telefone"""
        if pd.isna(telefone):
            return None
        tel_str = re.sub(r'[^\d]', '', str(telefone))
        if len(tel_str) >= 10:
            return tel_str
        return None
    
    def normalizar_nome(self, nome):
        """Normaliza nome para comparação"""
        if pd.isna(nome):
            return None
        nome_str = str(nome).upper().strip()
        # Remover caracteres especiais e espaços extras
        nome_str = re.sub(r'[^\w\s]', '', nome_str)
        nome_str = re.sub(r'\s+', ' ', nome_str)
        return nome_str
    
    def identificar_campos(self, df):
        """Identifica campos relevantes no DataFrame"""
        campos = {}
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            
            if any(termo in col_lower for termo in ['nome', 'cliente', 'paciente']) and 'nome' not in campos:
                campos['nome'] = col
            elif any(termo in col_lower for termo in ['cpf', 'documento']) and 'cpf' not in campos:
                campos['cpf'] = col
            elif any(termo in col_lower for termo in ['rg', 'identidade']) and 'rg' not in campos:
                campos['rg'] = col
            elif any(termo in col_lower for termo in ['telefone', 'celular', 'fone']) and 'telefone' not in campos:
                campos['telefone'] = col
            elif any(termo in col_lower for termo in ['email', 'e-mail']) and 'email' not in campos:
                campos['email'] = col
            elif any(termo in col_lower for termo in ['endereco', 'endereço', 'end']) and 'endereco' not in campos:
                campos['endereco'] = col
            elif any(termo in col_lower for termo in ['cep']) and 'cep' not in campos:
                campos['cep'] = col
            elif any(termo in col_lower for termo in ['os n', 'os', 'ordem']) and 'os' not in campos:
                campos['os'] = col
            elif any(termo in col_lower for termo in ['data', 'compra']) and 'data_compra' not in campos:
                campos['data_compra'] = col
            elif any(termo in col_lower for termo in ['loja']) and 'loja' not in campos:
                campos['loja'] = col
        
        return campos
    
    def extrair_dados_arquivo(self, arquivo_path):
        """Extrai dados padronizados de um arquivo"""
        logger.info(f"Processando arquivo: {arquivo_path.name}")
        
        try:
            # Determinar engine
            engine = 'openpyxl' if arquivo_path.suffix.lower() in ['.xlsx', '.xlsm'] else None
            
            # Carregar arquivo
            excel_file = pd.ExcelFile(arquivo_path, engine=engine)
            sheets = excel_file.sheet_names
            
            # Encontrar sheet principal
            sheet_principal = None
            for sheet_name in ['base_clientes_OS', 'base', 'dados']:
                if sheet_name in sheets:
                    sheet_principal = sheet_name
                    break
            
            if not sheet_principal and sheets:
                sheet_principal = sheets[0]
            
            if not sheet_principal:
                logger.warning(f"Nenhum sheet encontrado em {arquivo_path.name}")
                return []
            
            df = pd.read_excel(arquivo_path, sheet_name=sheet_principal, engine=engine)
            logger.info(f"Carregado sheet '{sheet_principal}': {len(df)} linhas")
            
            # Identificar campos
            campos = self.identificar_campos(df)
            
            # Extrair dados padronizados
            dados_extraidos = []
            
            for idx, row in df.iterrows():
                registro = {
                    'arquivo_origem': arquivo_path.name,
                    'linha_original': idx + 1,
                    'sheet': sheet_principal
                }
                
                # Extrair cada campo
                for campo_padrao, coluna_original in campos.items():
                    valor = row[coluna_original] if pd.notna(row[coluna_original]) else None
                    
                    # Aplicar limpeza específica
                    if campo_padrao == 'cpf':
                        valor = self.limpar_cpf(valor)
                    elif campo_padrao == 'telefone':
                        valor = self.limpar_telefone(valor)
                    elif campo_padrao == 'nome':
                        valor = self.normalizar_nome(valor)
                    elif valor is not None:
                        valor = str(valor).strip()
                    
                    registro[campo_padrao] = valor
                
                # Só incluir se tiver pelo menos nome ou CPF
                if registro.get('nome') or registro.get('cpf'):
                    dados_extraidos.append(registro)
            
            logger.info(f"Extraídos {len(dados_extraidos)} registros válidos de {arquivo_path.name}")
            return dados_extraidos
            
        except Exception as e:
            logger.error(f"Erro ao processar {arquivo_path.name}: {e}")
            return []
    
    def identificar_duplicatas(self, dados):
        """Identifica grupos de registros duplicados"""
        logger.info("Identificando duplicatas...")
        
        grupos = defaultdict(list)
        cpf_index = {}
        nome_index = defaultdict(list)
        
        # Indexar por CPF
        for i, registro in enumerate(dados):
            cpf = registro.get('cpf')
            if cpf:
                if cpf in cpf_index:
                    # CPF duplicado - agrupar
                    grupo_existente = cpf_index[cpf]
                    grupos[grupo_existente].append(i)
                else:
                    # Novo grupo
                    grupo_id = f"cpf_{cpf}"
                    cpf_index[cpf] = grupo_id
                    grupos[grupo_id].append(i)
        
        # Indexar por nome (para registros sem CPF)
        for i, registro in enumerate(dados):
            if not registro.get('cpf'):  # Só se não tem CPF
                nome = registro.get('nome')
                if nome:
                    # Buscar nomes similares
                    encontrou_similar = False
                    for nome_existente, indices in nome_index.items():
                        if fuzz.ratio(nome, nome_existente) > 90:
                            # Nome similar encontrado
                            grupos[f"nome_{nome_existente}"].append(i)
                            encontrou_similar = True
                            break
                    
                    if not encontrou_similar:
                        grupo_id = f"nome_{nome}"
                        nome_index[nome] = [i]
                        grupos[grupo_id].append(i)
        
        # Filtrar grupos com apenas 1 item (não são duplicatas)
        grupos_duplicatas = {k: v for k, v in grupos.items() if len(v) > 1}
        
        logger.info(f"Encontrados {len(grupos_duplicatas)} grupos de duplicatas")
        return grupos_duplicatas
    
    def mesclar_grupo(self, indices, dados):
        """Mescla um grupo de registros duplicados em um único registro"""
        registros = [dados[i] for i in indices]
        
        # Registro consolidado
        consolidado = {
            'arquivos_origem': [],
            'linhas_originais': [],
            'os_list': [],
            'datas_compra': []
        }
        
        # Campos para mesclar
        campos_texto = ['nome', 'endereco', 'email', 'loja']
        campos_unicos = ['cpf', 'rg', 'cep']
        campos_multiplos = ['telefone', 'email']
        
        # Coletar informações de origem
        for registro in registros:
            consolidado['arquivos_origem'].append(registro['arquivo_origem'])
            consolidado['linhas_originais'].append(registro['linha_original'])
            
            if registro.get('os'):
                consolidado['os_list'].append(str(registro['os']))
            if registro.get('data_compra'):
                consolidado['datas_compra'].append(str(registro['data_compra']))
        
        # Mesclar campos de texto (usar o mais completo)
        for campo in campos_texto:
            valores = [r.get(campo) for r in registros if r.get(campo)]
            if valores:
                # Usar o valor mais longo (mais completo)
                consolidado[campo] = max(valores, key=len)
        
        # Mesclar campos únicos (priorizar preenchidos)
        for campo in campos_unicos:
            valores = [r.get(campo) for r in registros if r.get(campo)]
            if valores:
                consolidado[campo] = valores[0]  # Usar o primeiro válido
        
        # Mesclar campos múltiplos (telefones, emails)
        telefones_unicos = []
        emails_unicos = []
        
        for registro in registros:
            tel = registro.get('telefone')
            if tel and tel not in telefones_unicos:
                telefones_unicos.append(tel)
            
            email = registro.get('email')
            if email and email not in emails_unicos:
                emails_unicos.append(email)
        
        consolidado['telefone'] = '; '.join(telefones_unicos) if telefones_unicos else None
        consolidado['email'] = '; '.join(emails_unicos) if emails_unicos else None
        
        # Estatísticas do grupo
        consolidado['total_registros_mesclados'] = len(registros)
        consolidado['total_os'] = len(consolidado['os_list'])
        consolidado['os_numeros'] = '; '.join(consolidado['os_list'])
        
        return consolidado
    
    def processar_todos_arquivos(self):
        """Processa todos os arquivos e consolida os dados"""
        logger.info("Iniciando processamento de todos os arquivos")
        
        # Buscar arquivos
        arquivos = list(Path("data/raw").glob("OS*.xlsm")) + list(Path("data/raw").glob("OS*.xlsx"))
        logger.info(f"Encontrados {len(arquivos)} arquivos para processar")
        
        # Extrair dados de todos os arquivos
        todos_dados = []
        for arquivo in arquivos:
            dados_arquivo = self.extrair_dados_arquivo(arquivo)
            todos_dados.extend(dados_arquivo)
        
        logger.info(f"Total de registros extraídos: {len(todos_dados)}")
        
        # Identificar duplicatas
        grupos_duplicatas = self.identificar_duplicatas(todos_dados)
        
        # Mesclar grupos de duplicatas
        registros_consolidados = []
        indices_processados = set()
        
        for grupo_id, indices in grupos_duplicatas.items():
            consolidado = self.mesclar_grupo(indices, todos_dados)
            consolidado['grupo_id'] = grupo_id
            registros_consolidados.append(consolidado)
            
            # Marcar índices como processados
            for idx in indices:
                indices_processados.add(idx)
            
            # Log da mesclagem
            self.relatorio_mesclagens.append({
                'grupo_id': grupo_id,
                'registros_mesclados': len(indices),
                'nome_final': consolidado.get('nome'),
                'cpf_final': consolidado.get('cpf'),
                'total_os': consolidado['total_os']
            })
        
        # Adicionar registros únicos (não duplicados)
        for i, registro in enumerate(todos_dados):
            if i not in indices_processados:
                # Converter para formato consolidado
                unico = dict(registro)
                unico['total_registros_mesclados'] = 1
                unico['total_os'] = 1 if registro.get('os') else 0
                unico['grupo_id'] = f"unico_{i}"
                registros_consolidados.append(unico)
        
        logger.info(f"Consolidação concluída: {len(registros_consolidados)} registros finais")
        return registros_consolidados, grupos_duplicatas
    
    def salvar_resultados(self, registros_consolidados, grupos_duplicatas):
        """Salva os resultados consolidados"""
        logger.info("Salvando resultados...")
        
        # Criar DataFrame consolidado
        df_consolidado = pd.DataFrame(registros_consolidados)
        
        # Salvar em Excel
        output_file = Path("data/processed/base_consolidada_inteligente.xlsx")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Base consolidada
            df_consolidado.to_excel(writer, sheet_name='base_consolidada', index=False)
            
            # Relatório de mesclagens
            df_mesclagens = pd.DataFrame(self.relatorio_mesclagens)
            df_mesclagens.to_excel(writer, sheet_name='relatorio_mesclagens', index=False)
            
            # Estatísticas
            estatisticas = {
                'Métrica': [
                    'Total de registros originais',
                    'Total de registros consolidados',
                    'Grupos de duplicatas encontrados',
                    'Registros únicos',
                    'Taxa de duplicação',
                    'Clientes com CPF',
                    'Clientes com telefone',
                    'Clientes com email'
                ],
                'Valor': [
                    len(registros_consolidados) + sum(len(indices) - 1 for indices in grupos_duplicatas.values()),
                    len(registros_consolidados),
                    len(grupos_duplicatas),
                    len(registros_consolidados) - len(grupos_duplicatas),
                    f"{(len(grupos_duplicatas) / len(registros_consolidados)) * 100:.1f}%",
                    df_consolidado['cpf'].notna().sum(),
                    df_consolidado['telefone'].notna().sum(),
                    df_consolidado['email'].notna().sum()
                ]
            }
            
            df_stats = pd.DataFrame(estatisticas)
            df_stats.to_excel(writer, sheet_name='estatisticas', index=False)
        
        logger.info(f"Resultados salvos em: {output_file}")
        return output_file

def main():
    """Função principal"""
    print("🚀 SISTEMA DE CONSOLIDAÇÃO INTELIGENTE DE DADOS")
    print("=" * 80)
    
    consolidador = ConsolidadorInteligente()
    
    try:
        # Processar todos os arquivos
        registros_consolidados, grupos_duplicatas = consolidador.processar_todos_arquivos()
        
        # Salvar resultados
        arquivo_saida = consolidador.salvar_resultados(registros_consolidados, grupos_duplicatas)
        
        # Exibir resumo
        print(f"\n📊 RESUMO DA CONSOLIDAÇÃO:")
        print(f"✅ Registros consolidados: {len(registros_consolidados):,}")
        print(f"🔍 Grupos de duplicatas: {len(grupos_duplicatas):,}")
        print(f"📁 Arquivo salvo: {arquivo_saida}")
        
        # Top 5 mesclagens
        if consolidador.relatorio_mesclagens:
            print(f"\n🏆 TOP 5 MESCLAGENS:")
            top_mesclagens = sorted(consolidador.relatorio_mesclagens, 
                                  key=lambda x: x['registros_mesclados'], reverse=True)[:5]
            
            for i, mesclagem in enumerate(top_mesclagens, 1):
                print(f"   {i}. {mesclagem['nome_final']} - {mesclagem['registros_mesclados']} registros mesclados")
        
        print(f"\n🎉 CONSOLIDAÇÃO CONCLUÍDA COM SUCESSO!")
        
    except Exception as e:
        logger.error(f"Erro durante o processamento: {e}")
        raise

if __name__ == "__main__":
    main()