"""
Script para análise e processamento de planilhas de Ordens de Serviço
Desenvolvido para Óticas Taty Mello
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging
from fuzzywuzzy import fuzz
from unidecode import unidecode
import phonenumbers
from loguru import logger

class AnalisadorOS:
    def __init__(self, diretorio_dados: str = "data/raw"):
        self.diretorio_dados = Path(diretorio_dados)
        self.diretorio_processados = Path("data/processed")
        self.diretorio_processados.mkdir(parents=True, exist_ok=True)
        
        # Configurar logging
        logger.add("logs/processamento.log", rotation="1 day", retention="30 days")
        
    def carregar_planilha(self, arquivo: Path) -> pd.DataFrame:
        """Carrega uma planilha Excel e retorna DataFrame"""
        try:
            # Determinar engine baseado na extensão
            engine = 'openpyxl' if arquivo.suffix.lower() in ['.xlsx', '.xlsm'] else None
            
            # Primeiro tentar carregar como tabela Excel (Tabela1)
            try:
                # Ler o primeiro sheet para acessar as tabelas
                df = pd.read_excel(arquivo, sheet_name=0, engine=engine)
                logger.info(f"Carregado dados da Tabela1 do arquivo {arquivo.name}")
                
                # Se a primeira linha contém cabeçalhos da tabela, usar a partir da linha 0
                if not df.empty and len(df.columns) > 0:
                    # Verificar se há dados válidos
                    if df.iloc[0:5].count().sum() > 0:  # Verificar se há dados nas primeiras 5 linhas
                        return df
                        
            except Exception as e:
                logger.warning(f"Erro ao carregar como Tabela1: {e}")
            
            # Fallback: Tentar diferentes sheets comuns
            sheet_names = ['base_clientes_OS', 'Clientes', 'OS', 'dados', 'Tabela1']
            
            df = None
            for sheet in sheet_names:
                try:
                    df = pd.read_excel(arquivo, sheet_name=sheet, engine=engine)
                    logger.info(f"Carregado sheet '{sheet}' do arquivo {arquivo.name}")
                    break
                except:
                    continue
            
            if df is None:
                # Se não encontrou sheets específicos, carregar o primeiro
                df = pd.read_excel(arquivo, engine=engine)
                logger.info(f"Carregado primeiro sheet do arquivo {arquivo.name}")
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao carregar {arquivo}: {e}")
            return pd.DataFrame()
    
    def padronizar_colunas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Padroniza nomes das colunas"""
        # Mapeamento de possíveis nomes de colunas
        mapeamento_colunas = {
            # Cliente
            'nome': ['nome', 'cliente', 'nome_cliente', 'paciente'],
            'cpf': ['cpf', 'documento', 'cpf_cnpj'],
            'telefone': ['telefone', 'fone', 'celular', 'contato'],
            'endereco': ['endereco', 'endereço', 'rua', 'logradouro'],
            'email': ['email', 'e-mail', 'e_mail'],
            
            # OS
            'numero_os': ['numero_os', 'os', 'ordem_servico', 'n_os', 'num_os'],
            'data_compra': ['data_compra', 'data_venda', 'data_os', 'data'],
            'data_entrega': ['data_entrega', 'entrega', 'prazo_entrega'],
            'valor': ['valor', 'valor_total', 'preco', 'total'],
            'loja': ['loja', 'filial', 'unidade'],
            'vendedor': ['vendedor', 'atendente', 'funcionario'],
            
            # Dioptrias OD (Olho Direito)
            'od_esferico': ['od_esf', 'od_esferico', 'esf_od', 'esferico_od'],
            'od_cilindrico': ['od_cil', 'od_cilindrico', 'cil_od', 'cilindrico_od'],
            'od_eixo': ['od_eixo', 'eixo_od', 'grau_od'],
            'od_adicao': ['od_ad', 'od_adicao', 'adicao_od', 'ad_od'],
            
            # Dioptrias OE (Olho Esquerdo)
            'oe_esferico': ['oe_esf', 'oe_esferico', 'esf_oe', 'esferico_oe'],
            'oe_cilindrico': ['oe_cil', 'oe_cilindrico', 'cil_oe', 'cilindrico_oe'],
            'oe_eixo': ['oe_eixo', 'eixo_oe', 'grau_oe'],
            'oe_adicao': ['oe_ad', 'oe_adicao', 'adicao_oe', 'ad_oe'],
            
            # Outros
            'dp': ['dp', 'distancia_pupilar', 'dist_pupilar'],
            'tipo_lente': ['tipo_lente', 'lente', 'tipo'],
            'observacoes': ['observacoes', 'obs', 'observação', 'comentario']
        }
        
        # Normalizar nomes das colunas
        df.columns = [self.normalizar_texto(col) for col in df.columns]
        
        # Aplicar mapeamento
        colunas_padronizadas = {}
        for col_padrao, variacoes in mapeamento_colunas.items():
            variacoes_norm = [self.normalizar_texto(v) for v in variacoes]
            for col_atual in df.columns:
                if col_atual in variacoes_norm:
                    colunas_padronizadas[col_atual] = col_padrao
                    break
        
        df = df.rename(columns=colunas_padronizadas)
        logger.info(f"Colunas padronizadas: {list(colunas_padronizadas.values())}")
        
        return df
    
    def normalizar_texto(self, texto: str) -> str:
        """Normaliza texto removendo acentos e caracteres especiais"""
        if pd.isna(texto):
            return ""
        
        texto = str(texto).lower().strip()
        texto = unidecode(texto)
        texto = re.sub(r'[^\w\s]', '', texto)
        texto = re.sub(r'\s+', '_', texto)
        
        return texto
    
    def limpar_cpf(self, cpf: str) -> str:
        """Limpa e valida CPF"""
        if pd.isna(cpf):
            return ""
        
        cpf = re.sub(r'\D', '', str(cpf))
        
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        
        return ""
    
    def limpar_telefone(self, telefone: str) -> str:
        """Limpa e formata telefone"""
        if pd.isna(telefone):
            return ""
        
        try:
            # Tentar parsear como telefone brasileiro
            numero = phonenumbers.parse(str(telefone), "BR")
            if phonenumbers.is_valid_number(numero):
                return phonenumbers.format_number(numero, phonenumbers.PhoneNumberFormat.NATIONAL)
        except:
            pass
        
        # Fallback: limpar apenas números
        telefone = re.sub(r'\D', '', str(telefone))
        
        if len(telefone) >= 10:
            if len(telefone) == 11:
                return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
            elif len(telefone) == 10:
                return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
        
        return telefone
    
    def detectar_duplicatas(self, df: pd.DataFrame, threshold: float = 0.85) -> List[Dict]:
        """Detecta possíveis clientes duplicados"""
        duplicatas = []
        
        if 'nome' not in df.columns:
            return duplicatas
        
        nomes = df['nome'].dropna().unique()
        
        for i, nome1 in enumerate(nomes):
            for nome2 in nomes[i+1:]:
                # Similaridade por nome
                sim_nome = fuzz.ratio(
                    self.normalizar_texto(nome1),
                    self.normalizar_texto(nome2)
                ) / 100
                
                if sim_nome >= threshold:
                    # Verificar outros campos se disponíveis
                    registros1 = df[df['nome'] == nome1]
                    registros2 = df[df['nome'] == nome2]
                    
                    # Comparar CPF se disponível
                    sim_cpf = 0
                    if 'cpf' in df.columns:
                        cpfs1 = registros1['cpf'].dropna().unique()
                        cpfs2 = registros2['cpf'].dropna().unique()
                        
                        if len(cpfs1) > 0 and len(cpfs2) > 0:
                            if cpfs1[0] == cpfs2[0]:
                                sim_cpf = 1.0
                    
                    # Comparar telefone se disponível
                    sim_tel = 0
                    if 'telefone' in df.columns:
                        tels1 = registros1['telefone'].dropna().unique()
                        tels2 = registros2['telefone'].dropna().unique()
                        
                        if len(tels1) > 0 and len(tels2) > 0:
                            sim_tel = fuzz.ratio(
                                self.normalizar_texto(str(tels1[0])),
                                self.normalizar_texto(str(tels2[0]))
                            ) / 100
                    
                    # Score final ponderado
                    score_final = (sim_nome * 0.6 + sim_cpf * 0.3 + sim_tel * 0.1)
                    
                    if score_final >= threshold:
                        duplicatas.append({
                            'nome1': nome1,
                            'nome2': nome2,
                            'similaridade_nome': sim_nome,
                            'similaridade_cpf': sim_cpf,
                            'similaridade_telefone': sim_tel,
                            'score_final': score_final,
                            'registros1': len(registros1),
                            'registros2': len(registros2)
                        })
        
        return duplicatas
    
    def processar_arquivo(self, arquivo: Path) -> Dict:
        """Processa um arquivo específico"""
        logger.info(f"Processando arquivo: {arquivo.name}")
        
        resultado = {
            'arquivo': arquivo.name,
            'status': 'erro',
            'linhas_original': 0,
            'linhas_processadas': 0,
            'clientes_unicos': 0,
            'duplicatas_detectadas': 0,
            'colunas_encontradas': [],
            'colunas_mapeadas': [],
            'erros': []
        }
        
        try:
            # Carregar dados
            df_original = self.carregar_planilha(arquivo)
            
            if df_original.empty:
                resultado['erros'].append("Arquivo vazio ou não pôde ser lido")
                return resultado
            
            resultado['linhas_original'] = len(df_original)
            resultado['colunas_encontradas'] = list(df_original.columns)
            
            # Padronizar colunas
            df = self.padronizar_colunas(df_original.copy())
            resultado['colunas_mapeadas'] = list(df.columns)
            
            # Limpar dados
            if 'cpf' in df.columns:
                df['cpf'] = df['cpf'].apply(self.limpar_cpf)
            
            if 'telefone' in df.columns:
                df['telefone'] = df['telefone'].apply(self.limpar_telefone)
            
            # Remover linhas vazias
            df = df.dropna(how='all')
            resultado['linhas_processadas'] = len(df)
            
            # Contar clientes únicos
            if 'nome' in df.columns:
                resultado['clientes_unicos'] = df['nome'].nunique()
            
            # Detectar duplicatas
            duplicatas = self.detectar_duplicatas(df)
            resultado['duplicatas_detectadas'] = len(duplicatas)
            
            # Salvar dados processados
            arquivo_saida = self.diretorio_processados / f"processado_{arquivo.stem}.xlsx"
            
            with pd.ExcelWriter(arquivo_saida, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='dados_limpos', index=False)
                
                if duplicatas:
                    df_duplicatas = pd.DataFrame(duplicatas)
                    df_duplicatas.to_excel(writer, sheet_name='duplicatas_detectadas', index=False)
            
            resultado['status'] = 'sucesso'
            resultado['arquivo_saida'] = str(arquivo_saida)
            
            logger.info(f"Arquivo processado com sucesso: {arquivo.name}")
            
        except Exception as e:
            erro = f"Erro ao processar {arquivo.name}: {str(e)}"
            resultado['erros'].append(erro)
            logger.error(erro)
        
        return resultado
    
    def processar_todos_arquivos(self, pattern: str = "OS_NOVA*.xlsx") -> List[Dict]:
        """Processa todos os arquivos que correspondem ao padrão"""
        arquivos = list(self.diretorio_dados.glob(pattern))
        
        if not arquivos:
            logger.warning(f"Nenhum arquivo encontrado com padrão: {pattern}")
            return []
        
        logger.info(f"Encontrados {len(arquivos)} arquivos para processar")
        
        resultados = []
        for arquivo in arquivos:
            resultado = self.processar_arquivo(arquivo)
            resultados.append(resultado)
        
        # Gerar relatório consolidado
        self.gerar_relatorio_consolidado(resultados)
        
        return resultados
    
    def gerar_relatorio_consolidado(self, resultados: List[Dict]) -> None:
        """Gera relatório consolidado do processamento"""
        total_arquivos = len(resultados)
        arquivos_sucesso = len([r for r in resultados if r['status'] == 'sucesso'])
        total_linhas = sum(r['linhas_processadas'] for r in resultados)
        total_clientes = sum(r['clientes_unicos'] for r in resultados)
        total_duplicatas = sum(r['duplicatas_detectadas'] for r in resultados)
        
        relatorio = {
            'data_processamento': datetime.now().isoformat(),
            'total_arquivos': total_arquivos,
            'arquivos_sucesso': arquivos_sucesso,
            'total_linhas_processadas': total_linhas,
            'total_clientes_unicos': total_clientes,
            'total_duplicatas_detectadas': total_duplicatas,
            'detalhes_arquivos': resultados
        }
        
        # Salvar relatório
        import json
        arquivo_relatorio = self.diretorio_processados / f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Relatório consolidado salvo em: {arquivo_relatorio}")
        logger.info(f"Resumo: {arquivos_sucesso}/{total_arquivos} arquivos processados, "
                   f"{total_linhas} linhas, {total_clientes} clientes únicos, "
                   f"{total_duplicatas} duplicatas detectadas")

if __name__ == "__main__":
    analisador = AnalisadorOS()
    resultados = analisador.processar_todos_arquivos()
    
    print(f"Processamento concluído! {len(resultados)} arquivos processados.")
    for resultado in resultados:
        status = "✓" if resultado['status'] == 'sucesso' else "✗"
        print(f"{status} {resultado['arquivo']}: {resultado['linhas_processadas']} linhas, "
              f"{resultado['clientes_unicos']} clientes únicos, "
              f"{resultado['duplicatas_detectadas']} duplicatas")