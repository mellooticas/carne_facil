#!/usr/bin/env python3
"""
Sistema de Consolidação Inteligente POR ARQUIVO/LOJA
Estratégia segura: consolida apenas dentro de cada arquivo/loja
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

class ConsolidadorPorLoja:
    def __init__(self):
        self.resultados_por_arquivo = {}
        self.dashboard_data = []
        
    def limpar_cpf(self, cpf):
        """Limpa e valida CPF"""
        if pd.isna(cpf):
            return None
        cpf_str = re.sub(r'[^\d]', '', str(cpf))
        if len(cpf_str) == 11 and cpf_str.isdigit():
            return cpf_str
        return None
    
    def limpar_celular(self, celular):
        """Limpa e padroniza celular para formato SP"""
        if pd.isna(celular):
            return None
        
        cel_str = re.sub(r'[^\d]', '', str(celular))
        
        # Validar tamanho mínimo
        if len(cel_str) < 9:
            return None
        
        # Padronizar para SP (11)
        if len(cel_str) == 9:
            # Adicionar DDD 11 se só tiver 9 dígitos de celular
            cel_str = '11' + cel_str
        elif len(cel_str) == 10:
            # Adicionar DDD 11 se não tiver
            cel_str = '11' + cel_str
        elif len(cel_str) == 11 and cel_str.startswith('1'):
            # Já tem DDD 11
            pass
        elif len(cel_str) == 11 and not cel_str.startswith('11'):
            # Corrigir DDD para 11 (SP)
            cel_str = '11' + cel_str[2:]
        elif len(cel_str) == 13 and cel_str.startswith('55'):
            # Remover código do país e usar DDD 11
            cel_str = '11' + cel_str[4:]
        elif len(cel_str) > 11:
            # Pegar os últimos 9 dígitos e adicionar DDD 11
            cel_str = '11' + cel_str[-9:]
        
        # Validar se é celular SP válido (11 9xxxx-xxxx)
        if len(cel_str) == 11 and cel_str.startswith('11') and cel_str[2] == '9':
            # Formatar: (11) 9xxxx-xxxx
            return f"(11) {cel_str[2:7]}-{cel_str[7:]}"
        
        return None
    
    def normalizar_nome(self, nome):
        """Normaliza nome para comparação"""
        if pd.isna(nome):
            return None
        nome_str = str(nome).upper().strip()
        nome_str = re.sub(r'[^\w\s]', '', nome_str)
        nome_str = re.sub(r'\s+', ' ', nome_str)
        return nome_str
    
    def extrair_data_nascimento(self, data):
        """Extrai e normaliza data de nascimento"""
        if pd.isna(data):
            return None
        try:
            if isinstance(data, str):
                # Tentar diferentes formatos
                for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']:
                    try:
                        return datetime.strptime(data.strip(), fmt).date()
                    except:
                        continue
            return None
        except:
            return None
    
    def identificar_campos(self, df):
        """Identifica campos relevantes no DataFrame"""
        campos = {}
        
        # Primeiro, buscar campos específicos com prioridade
        for col in df.columns:
            col_lower = str(col).lower().strip()
            
            # CELULAR tem prioridade absoluta sobre TELEFONE
            if any(termo in col_lower for termo in ['celular:', 'celular']) and 'celular' not in campos:
                campos['celular'] = col
        
        # Depois buscar outros campos
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
            elif any(termo in col_lower for termo in ['end:', 'endereco', 'endereço', 'endereco:', 'endereço:']) and 'endereco' not in campos:
                campos['endereco'] = col
            elif any(termo in col_lower for termo in ['cep']) and 'cep' not in campos:
                campos['cep'] = col
            elif any(termo in col_lower for termo in ['os n', 'os', 'ordem']) and 'os' not in campos:
                campos['os'] = col
            elif any(termo in col_lower for termo in ['data de compra', 'data', 'compra']) and 'data_compra' not in campos:
                campos['data_compra'] = col
            elif any(termo in col_lower for termo in ['dt nasc', 'nascimento', 'nasc']) and 'data_nascimento' not in campos:
                campos['data_nascimento'] = col
            elif any(termo in col_lower for termo in ['loja']) and 'loja' not in campos:
                campos['loja'] = col
        
        return campos
    
    def identificar_loja_por_arquivo(self, nome_arquivo):
        """Identifica a loja baseado no nome do arquivo"""
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
            return 'ESCRITORIO'
        else:
            return 'INDEFINIDA'
    
    def processar_arquivo_individual(self, arquivo_path):
        """Processa um arquivo individual com consolidação interna"""
        logger.info(f"Processando arquivo: {arquivo_path.name}")
        
        resultado = {
            'arquivo': arquivo_path.name,
            'loja': self.identificar_loja_por_arquivo(arquivo_path.name),
            'status': 'erro',
            'registros_originais': 0,
            'registros_consolidados': 0,
            'duplicatas_encontradas': 0,
            'campos_disponíveis': [],
            'qualidade_dados': {},
            'clientes_multiplas_os': 0,
            'total_os': 0,
            'erros': []
        }
        
        try:
            # Carregar arquivo
            engine = 'openpyxl' if arquivo_path.suffix.lower() in ['.xlsx', '.xlsm'] else None
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
                resultado['erros'].append("Nenhum sheet encontrado")
                return resultado
            
            df_original = pd.read_excel(arquivo_path, sheet_name=sheet_principal, engine=engine)
            resultado['registros_originais'] = len(df_original)
            
            # Identificar campos
            campos = self.identificar_campos(df_original)
            resultado['campos_disponíveis'] = list(campos.keys())
            
            if not campos.get('nome') and not campos.get('cpf'):
                resultado['erros'].append("Campos essenciais não encontrados")
                return resultado
            
            # Extrair e normalizar dados
            dados_normalizados = []
            
            for idx, row in df_original.iterrows():
                registro = {
                    'linha_original': idx + 1,
                    'loja': resultado['loja']
                }
                
                # Extrair campos normalizados
                for campo_padrao, coluna_original in campos.items():
                    valor = row[coluna_original] if pd.notna(row[coluna_original]) else None
                    
                    if campo_padrao == 'cpf':
                        valor = self.limpar_cpf(valor)
                    elif campo_padrao == 'celular':
                        valor = self.limpar_celular(valor)
                    elif campo_padrao == 'nome':
                        valor = self.normalizar_nome(valor)
                    elif campo_padrao == 'data_nascimento':
                        valor = self.extrair_data_nascimento(valor)
                    elif valor is not None:
                        valor = str(valor).strip()
                    
                    registro[campo_padrao] = valor
                
                # Só incluir se tiver dados mínimos
                if registro.get('nome') or registro.get('cpf'):
                    dados_normalizados.append(registro)
            
            # Identificar duplicatas DENTRO do arquivo
            grupos_duplicatas = self.identificar_duplicatas_seguras(dados_normalizados)
            
            # Consolidar grupos
            registros_consolidados = self.consolidar_grupos(grupos_duplicatas, dados_normalizados)
            
            # Calcular qualidade dos dados
            df_consolidado = pd.DataFrame(registros_consolidados)
            resultado['qualidade_dados'] = self.calcular_qualidade_dados(df_consolidado)
            
            # Estatísticas finais
            resultado['registros_consolidados'] = len(registros_consolidados)
            resultado['duplicatas_encontradas'] = len(grupos_duplicatas)
            resultado['clientes_multiplas_os'] = len([r for r in registros_consolidados if r.get('total_os', 0) > 1])
            resultado['total_os'] = sum(r.get('total_os', 0) for r in registros_consolidados)
            resultado['status'] = 'sucesso'
            
            # Salvar dados consolidados do arquivo
            self.salvar_arquivo_consolidado(arquivo_path, registros_consolidados)
            
            logger.info(f"Arquivo {arquivo_path.name} processado: {resultado['registros_originais']} → {resultado['registros_consolidados']} registros")
            
        except Exception as e:
            erro = f"Erro ao processar {arquivo_path.name}: {str(e)}"
            resultado['erros'].append(erro)
            logger.error(erro)
        
        return resultado
    
    def identificar_duplicatas_seguras(self, dados):
        """Identifica duplicatas com critérios seguros"""
        grupos = defaultdict(list)
        
        # Indexar por CPF (critério mais seguro)
        cpf_index = {}
        for i, registro in enumerate(dados):
            cpf = registro.get('cpf')
            if cpf:
                if cpf in cpf_index:
                    grupo_id = f"cpf_{cpf}"
                    if grupo_id not in grupos:
                        grupos[grupo_id] = [cpf_index[cpf]]
                    grupos[grupo_id].append(i)
                else:
                    cpf_index[cpf] = i
        
        # Para registros sem CPF, usar nome + data de nascimento
        nome_data_index = {}
        for i, registro in enumerate(dados):
            if not registro.get('cpf'):  # Só se não tem CPF
                nome = registro.get('nome')
                data_nasc = registro.get('data_nascimento')
                
                if nome and data_nasc:
                    chave = f"{nome}_{data_nasc}"
                    if chave in nome_data_index:
                        grupo_id = f"nome_data_{chave}"
                        if grupo_id not in grupos:
                            grupos[grupo_id] = [nome_data_index[chave]]
                        grupos[grupo_id].append(i)
                    else:
                        nome_data_index[chave] = i
        
        # Filtrar grupos com apenas 1 item
        grupos_duplicatas = {k: v for k, v in grupos.items() if len(v) > 1}
        
        return grupos_duplicatas
    
    def consolidar_grupos(self, grupos_duplicatas, dados):
        """Consolida grupos de duplicatas"""
        registros_consolidados = []
        indices_processados = set()
        
        # Processar grupos de duplicatas
        for grupo_id, indices in grupos_duplicatas.items():
            consolidado = self.mesclar_registros(indices, dados, grupo_id)
            registros_consolidados.append(consolidado)
            indices_processados.update(indices)
        
        # Adicionar registros únicos
        for i, registro in enumerate(dados):
            if i not in indices_processados:
                unico = dict(registro)
                unico['grupo_tipo'] = 'unico'
                unico['total_registros_mesclados'] = 1
                unico['total_os'] = 1 if registro.get('os') else 0
                registros_consolidados.append(unico)
        
        return registros_consolidados
    
    def mesclar_registros(self, indices, dados, grupo_id):
        """Mescla registros de um grupo"""
        registros = [dados[i] for i in indices]
        
        consolidado = {
            'grupo_tipo': 'mesclado',
            'grupo_id': grupo_id,
            'total_registros_mesclados': len(registros),
            'linhas_originais': [r['linha_original'] for r in registros],
            'os_list': [],
            'loja': registros[0].get('loja')
        }
        
        # Mesclar campos
        campos_texto = ['nome', 'endereco', 'loja']
        campos_unicos = ['cpf', 'rg', 'cep', 'data_nascimento']
        
        # Usar o valor mais completo para campos de texto
        for campo in campos_texto:
            valores = [r.get(campo) for r in registros if r.get(campo)]
            if valores:
                consolidado[campo] = max(valores, key=lambda x: len(str(x)))
        
        # Usar primeiro valor válido para campos únicos
        for campo in campos_unicos:
            valores = [r.get(campo) for r in registros if r.get(campo)]
            if valores:
                consolidado[campo] = valores[0]
        
        # Mesclar telefones e emails
        celulares = list(set([r.get('celular') for r in registros if r.get('celular')]))
        emails = list(set([r.get('email') for r in registros if r.get('email')]))
        
        consolidado['celular'] = '; '.join(celulares) if celulares else None
        consolidado['email'] = '; '.join(emails) if emails else None
        
        # Coletar todas as OS
        for registro in registros:
            if registro.get('os'):
                consolidado['os_list'].append(str(registro['os']))
        
        consolidado['total_os'] = len(consolidado['os_list'])
        consolidado['os_numeros'] = '; '.join(consolidado['os_list'])
        
        return consolidado
    
    def calcular_qualidade_dados(self, df):
        """Calcula métricas de qualidade dos dados"""
        if df.empty:
            return {}
        
        total = len(df)
        qualidade = {}
        
        campos_importantes = ['nome', 'cpf', 'celular', 'email', 'endereco']
        
        for campo in campos_importantes:
            if campo in df.columns:
                preenchidos = df[campo].notna().sum()
                qualidade[campo] = {
                    'preenchidos': int(preenchidos),
                    'total': int(total),
                    'percentual': round((preenchidos / total) * 100, 1)
                }
        
        return qualidade
    
    def salvar_arquivo_consolidado(self, arquivo_original, registros_consolidados):
        """Salva arquivo consolidado individual"""
        output_dir = Path("data/processed/por_arquivo")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        nome_base = arquivo_original.stem
        output_file = output_dir / f"{nome_base}_consolidado.xlsx"
        
        df = pd.DataFrame(registros_consolidados)
        df.to_excel(output_file, index=False, engine='openpyxl')
    
    def processar_todos_arquivos(self):
        """Processa todos os arquivos individualmente"""
        logger.info("Iniciando processamento por arquivo/loja")
        
        arquivos = list(Path("data/raw").glob("OS*.xlsm")) + list(Path("data/raw").glob("OS*.xlsx"))
        logger.info(f"Encontrados {len(arquivos)} arquivos para processar")
        
        for arquivo in arquivos:
            resultado = self.processar_arquivo_individual(arquivo)
            self.resultados_por_arquivo[arquivo.name] = resultado
            self.dashboard_data.append(resultado)
        
        return self.dashboard_data
    
    def gerar_dashboard(self):
        """Gera dashboard consolidado com todos os resultados"""
        logger.info("Gerando dashboard de resultados")
        
        dashboard_file = Path("data/processed/dashboard_consolidacao_por_loja.xlsx")
        dashboard_file.parent.mkdir(parents=True, exist_ok=True)
        
        with pd.ExcelWriter(dashboard_file, engine='openpyxl') as writer:
            # 1. Dashboard principal
            df_dashboard = pd.DataFrame(self.dashboard_data)
            df_dashboard.to_excel(writer, sheet_name='Dashboard_Principal', index=False)
            
            # 2. Resumo por loja
            resumo_loja = df_dashboard.groupby('loja').agg({
                'arquivo': 'count',
                'registros_originais': 'sum',
                'registros_consolidados': 'sum',
                'duplicatas_encontradas': 'sum',
                'total_os': 'sum'
            }).rename(columns={'arquivo': 'total_arquivos'})
            resumo_loja.to_excel(writer, sheet_name='Resumo_Por_Loja')
            
            # 3. Qualidade de dados consolidada
            qualidade_global = []
            for resultado in self.dashboard_data:
                if resultado['status'] == 'sucesso':
                    for campo, dados in resultado['qualidade_dados'].items():
                        qualidade_global.append({
                            'arquivo': resultado['arquivo'],
                            'loja': resultado['loja'],
                            'campo': campo,
                            'preenchidos': dados['preenchidos'],
                            'total': dados['total'],
                            'percentual': dados['percentual']
                        })
            
            if qualidade_global:
                df_qualidade = pd.DataFrame(qualidade_global)
                df_qualidade.to_excel(writer, sheet_name='Qualidade_Dados', index=False)
            
            # 4. Estatísticas gerais
            total_originais = sum(r['registros_originais'] for r in self.dashboard_data)
            total_consolidados = sum(r['registros_consolidados'] for r in self.dashboard_data)
            total_duplicatas = sum(r['duplicatas_encontradas'] for r in self.dashboard_data)
            total_os = sum(r['total_os'] for r in self.dashboard_data)
            
            estatisticas = {
                'Métrica': [
                    'Total de arquivos processados',
                    'Total de lojas identificadas',
                    'Registros originais (total)',
                    'Registros consolidados (total)',
                    'Duplicatas encontradas (total)',
                    'Taxa de duplicação geral',
                    'Total de OS identificadas',
                    'Arquivos com sucesso',
                    'Arquivos com erro'
                ],
                'Valor': [
                    len(self.dashboard_data),
                    df_dashboard['loja'].nunique(),
                    total_originais,
                    total_consolidados,
                    total_duplicatas,
                    f"{(total_duplicatas / total_originais * 100):.1f}%" if total_originais > 0 else "0%",
                    total_os,
                    len([r for r in self.dashboard_data if r['status'] == 'sucesso']),
                    len([r for r in self.dashboard_data if r['status'] == 'erro'])
                ]
            }
            
            df_stats = pd.DataFrame(estatisticas)
            df_stats.to_excel(writer, sheet_name='Estatisticas_Gerais', index=False)
        
        logger.info(f"Dashboard salvo em: {dashboard_file}")
        return dashboard_file

def main():
    """Função principal"""
    print("🚀 CONSOLIDAÇÃO INTELIGENTE POR ARQUIVO/LOJA")
    print("=" * 80)
    print("📋 Estratégia: Consolidar apenas dentro de cada arquivo")
    print("🏪 Preservar integridade das lojas")
    print("🎯 Critérios seguros: CPF ou Nome + Data Nascimento")
    print("=" * 80)
    
    consolidador = ConsolidadorPorLoja()
    
    try:
        # Processar todos os arquivos
        resultados = consolidador.processar_todos_arquivos()
        
        # Gerar dashboard
        dashboard_file = consolidador.gerar_dashboard()
        
        # Exibir resumo
        print(f"\n📊 RESUMO GERAL:")
        print(f"✅ Arquivos processados: {len(resultados)}")
        
        sucessos = [r for r in resultados if r['status'] == 'sucesso']
        erros = [r for r in resultados if r['status'] == 'erro']
        
        print(f"✅ Sucessos: {len(sucessos)}")
        print(f"❌ Erros: {len(erros)}")
        
        if sucessos:
            total_originais = sum(r['registros_originais'] for r in sucessos)
            total_consolidados = sum(r['registros_consolidados'] for r in sucessos)
            total_os = sum(r['total_os'] for r in sucessos)
            
            print(f"📊 {total_originais:,} → {total_consolidados:,} registros")
            print(f"📊 {total_os:,} OS identificadas")
            
            # Top 5 arquivos com mais duplicatas
            top_duplicatas = sorted(sucessos, key=lambda x: x['duplicatas_encontradas'], reverse=True)[:5]
            print(f"\n🏆 TOP 5 ARQUIVOS COM MAIS DUPLICATAS:")
            for i, resultado in enumerate(top_duplicatas, 1):
                reducao = resultado['registros_originais'] - resultado['registros_consolidados']
                print(f"   {i}. {resultado['arquivo'][:40]}... ({resultado['loja']})")
                print(f"      {resultado['registros_originais']} → {resultado['registros_consolidados']} (-{reducao} duplicatas)")
        
        print(f"\n📁 Dashboard salvo: {dashboard_file}")
        print(f"🎉 PROCESSAMENTO CONCLUÍDO!")
        
    except Exception as e:
        logger.error(f"Erro durante o processamento: {e}")
        raise

if __name__ == "__main__":
    main()