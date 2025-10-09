#!/usr/bin/env python3
"""
Analisador Avançado de Estrutura das OS
Mapeia TODOS os campos disponíveis nas 14.337 OS
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

class AnalisadorEstruturaOS:
    def __init__(self):
        self.campos_encontrados = defaultdict(int)
        self.estrutura_por_arquivo = {}
        self.padroes_dioptrias = []
        self.padroes_vendas = []
        self.campos_especiais = {}
        
        # Padrões esperados baseados na imagem
        self.campos_dioptrias_esperados = [
            'PONTE', 'HORIZONTAL', 'DIAG MAIOR', 'VERTICAL', 
            'ESF', 'CIL', 'EIXO', 'DNP', 'ALTURA',
            'ESF2', 'CIL3', 'EIXO4', 'DNP5', 'ALTURA6',
            'ESF7', 'CIL8', 'EIXO9', 'DNP10', 'ALTURA11',
            'ESF12', 'CIL13', 'EIXO14', 'DNP15', 'ALTURA16',
            'ADIÇÃO'
        ]
        
        self.campos_vendas_esperados = [
            'Cod_trello', 'Descrição', 'Valor',
            'Cod17', 'Descrição18', 'Valor19',
            'Cod20', 'Descrição21', 'Valor22',
            'Cod23', 'Descrição24', 'Valor25',
            'Cod26', 'Descrição27', 'Valor28',
            'TOTAL', 'PAGTO 1', 'SINAL 1:', 'PAGTO 2', 'SINAL 2:', 'RESTA'
        ]
    
    def analisar_arquivo(self, arquivo_path):
        """Analisa um arquivo específico"""
        logger.info(f"Analisando: {arquivo_path.name}")
        
        try:
            # Carregar arquivo
            engine = 'openpyxl' if arquivo_path.suffix.lower() in ['.xlsx', '.xlsm'] else None
            
            try:
                excel_file = pd.ExcelFile(arquivo_path, engine=engine)
            except Exception as e:
                logger.warning(f"Erro ao carregar {arquivo_path.name}: {e}")
                return None
            
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
                return None
            
            # Analisar colunas
            colunas = list(df.columns)
            estrutura = {
                'arquivo': arquivo_path.name,
                'total_colunas': len(colunas),
                'total_linhas': len(df),
                'colunas': colunas,
                'campos_basicos': self.identificar_campos_basicos(colunas),
                'campos_dioptrias': self.identificar_campos_dioptrias(colunas),
                'campos_vendas': self.identificar_campos_vendas(colunas),
                'campos_especiais': self.identificar_campos_especiais(colunas)
            }
            
            # Contar ocorrências de cada campo
            for coluna in colunas:
                self.campos_encontrados[str(coluna)] += 1
            
            self.estrutura_por_arquivo[arquivo_path.name] = estrutura
            
            logger.info(f"✅ {arquivo_path.name}: {len(colunas)} colunas, {len(df)} linhas")
            return estrutura
            
        except Exception as e:
            logger.error(f"❌ Erro em {arquivo_path.name}: {e}")
            return None
    
    def identificar_campos_basicos(self, colunas):
        """Identifica campos básicos da OS"""
        campos = {}
        
        for col in colunas:
            col_str = str(col).lower().strip()
            
            # Campos básicos
            if any(termo in col_str for termo in ['os:', 'os', 'ordem', 'numero']):
                campos['numero_os'] = col
            elif any(termo in col_str for termo in ['nome:', 'nome', 'cliente', 'paciente']):
                campos['nome_cliente'] = col
            elif any(termo in col_str for termo in ['cpf']):
                campos['cpf'] = col
            elif any(termo in col_str for termo in ['data:', 'data']):
                campos['data_os'] = col
            elif any(termo in col_str for termo in ['loja']):
                campos['loja'] = col
            elif any(termo in col_str for termo in ['consultor', 'vendedor']):
                campos['consultor'] = col
            elif any(termo in col_str for termo in ['entrega', 'prev', 'previsao']):
                campos['prev_entrega'] = col
            elif any(termo in col_str for termo in ['como conheceu', 'conheceu', 'marketing']):
                campos['como_conheceu'] = col
        
        return campos
    
    def identificar_campos_dioptrias(self, colunas):
        """Identifica campos de dioptrías"""
        campos_dioptrias = {}
        
        for col in colunas:
            col_str = str(col).upper().strip()
            
            # Buscar padrões exatos da imagem
            for campo_esperado in self.campos_dioptrias_esperados:
                if campo_esperado in col_str or col_str == campo_esperado:
                    campos_dioptrias[campo_esperado] = col
        
        return campos_dioptrias
    
    def identificar_campos_vendas(self, colunas):
        """Identifica campos de vendas e produtos"""
        campos_vendas = {}
        
        for col in colunas:
            col_str = str(col).strip()
            
            # Buscar padrões exatos da imagem
            for campo_esperado in self.campos_vendas_esperados:
                if campo_esperado in col_str or col_str == campo_esperado:
                    campos_vendas[campo_esperado] = col
            
            # Buscar padrões genéricos
            col_lower = col_str.lower()
            if any(termo in col_lower for termo in ['cod', 'codigo']):
                if 'codigos' not in campos_vendas:
                    campos_vendas['codigos'] = []
                campos_vendas['codigos'].append(col)
            elif any(termo in col_lower for termo in ['descri', 'produto']):
                if 'descricoes' not in campos_vendas:
                    campos_vendas['descricoes'] = []
                campos_vendas['descricoes'].append(col)
            elif any(termo in col_lower for termo in ['valor', 'preco', 'total']):
                if 'valores' not in campos_vendas:
                    campos_vendas['valores'] = []
                campos_vendas['valores'].append(col)
            elif any(termo in col_lower for termo in ['pagto', 'pagamento', 'sinal']):
                if 'pagamentos' not in campos_vendas:
                    campos_vendas['pagamentos'] = []
                campos_vendas['pagamentos'].append(col)
        
        return campos_vendas
    
    def identificar_campos_especiais(self, colunas):
        """Identifica campos especiais e únicos"""
        especiais = {}
        
        for col in colunas:
            col_str = str(col).lower().strip()
            
            # Campos únicos que podem existir
            if any(termo in col_str for termo in ['obs', 'observacao']):
                especiais['observacoes'] = col
            elif any(termo in col_str for termo in ['desconto']):
                especiais['desconto'] = col
            elif any(termo in col_str for termo in ['promocao']):
                especiais['promocao'] = col
            elif any(termo in col_str for termo in ['garantia']):
                especiais['garantia'] = col
        
        return especiais
    
    def analisar_todos_arquivos(self):
        """Analisa todos os arquivos disponíveis"""
        print("🔍 ANALISADOR AVANÇADO DE ESTRUTURA DAS OS")
        print("=" * 80)
        print("📊 Mapeando TODOS os campos das 14.337 OS")
        print("🎯 Identificando padrões de dioptrías e vendas")
        print("=" * 80)
        
        # Processar todos os arquivos
        arquivos = list(Path("data/raw").glob("OS*.xlsm")) + list(Path("data/raw").glob("OS*.xlsx"))
        logger.info(f"Encontrados {len(arquivos)} arquivos para analisar")
        
        arquivos_processados = 0
        
        for arquivo in arquivos:
            estrutura = self.analisar_arquivo(arquivo)
            if estrutura:
                arquivos_processados += 1
        
        # Gerar relatório
        self.gerar_relatorio_completo()
        
        print(f"\n✅ ANÁLISE CONCLUÍDA:")
        print(f"📁 Arquivos analisados: {arquivos_processados}/{len(arquivos)}")
        print(f"🔍 Campos únicos encontrados: {len(self.campos_encontrados)}")
        
        return self.estrutura_por_arquivo
    
    def gerar_relatorio_completo(self):
        """Gera relatório detalhado da análise"""
        output_dir = Path("data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        relatorio_file = output_dir / f"ANALISE_ESTRUTURA_OS_{timestamp}.xlsx"
        
        with pd.ExcelWriter(relatorio_file, engine='openpyxl') as writer:
            # 1. Resumo geral de campos
            campos_df = pd.DataFrame([
                {'Campo': campo, 'Frequencia': freq, 'Porcentagem': freq/len(self.estrutura_por_arquivo)*100}
                for campo, freq in sorted(self.campos_encontrados.items(), key=lambda x: x[1], reverse=True)
            ])
            campos_df.to_excel(writer, sheet_name='Campos_Encontrados', index=False)
            
            # 2. Estrutura por arquivo
            estruturas = []
            for arquivo, dados in self.estrutura_por_arquivo.items():
                estruturas.append({
                    'Arquivo': arquivo,
                    'Total_Colunas': dados['total_colunas'],
                    'Total_Linhas': dados['total_linhas'],
                    'Campos_Basicos': len(dados['campos_basicos']),
                    'Campos_Dioptrias': len(dados['campos_dioptrias']),
                    'Campos_Vendas': len(dados['campos_vendas']),
                    'Campos_Especiais': len(dados['campos_especiais'])
                })
            
            estruturas_df = pd.DataFrame(estruturas)
            estruturas_df.to_excel(writer, sheet_name='Estrutura_Por_Arquivo', index=False)
            
            # 3. Mapeamento de campos básicos
            basicos_mapeamento = []
            for arquivo, dados in self.estrutura_por_arquivo.items():
                for tipo_campo, coluna in dados['campos_basicos'].items():
                    basicos_mapeamento.append({
                        'Arquivo': arquivo,
                        'Tipo_Campo': tipo_campo,
                        'Coluna_Encontrada': coluna
                    })
            
            if basicos_mapeamento:
                basicos_df = pd.DataFrame(basicos_mapeamento)
                basicos_df.to_excel(writer, sheet_name='Campos_Basicos', index=False)
            
            # 4. Mapeamento de dioptrías
            dioptrias_mapeamento = []
            for arquivo, dados in self.estrutura_por_arquivo.items():
                for tipo_campo, coluna in dados['campos_dioptrias'].items():
                    dioptrias_mapeamento.append({
                        'Arquivo': arquivo,
                        'Campo_Dioptria': tipo_campo,
                        'Coluna_Encontrada': coluna
                    })
            
            if dioptrias_mapeamento:
                dioptrias_df = pd.DataFrame(dioptrias_mapeamento)
                dioptrias_df.to_excel(writer, sheet_name='Campos_Dioptrias', index=False)
            
            # 5. Campos de vendas
            vendas_mapeamento = []
            for arquivo, dados in self.estrutura_por_arquivo.items():
                campos_vendas = dados['campos_vendas']
                for tipo_campo, colunas in campos_vendas.items():
                    if isinstance(colunas, list):
                        for coluna in colunas:
                            vendas_mapeamento.append({
                                'Arquivo': arquivo,
                                'Tipo_Campo': tipo_campo,
                                'Coluna_Encontrada': coluna
                            })
                    else:
                        vendas_mapeamento.append({
                            'Arquivo': arquivo,
                            'Tipo_Campo': tipo_campo,
                            'Coluna_Encontrada': colunas
                        })
            
            if vendas_mapeamento:
                vendas_df = pd.DataFrame(vendas_mapeamento)
                vendas_df.to_excel(writer, sheet_name='Campos_Vendas', index=False)
        
        logger.info(f"Relatório salvo: {relatorio_file}")
        
        # Exibir resumo na tela
        self.exibir_resumo_analise()
    
    def exibir_resumo_analise(self):
        """Exibe resumo da análise na tela"""
        print(f"\n📊 RESUMO DA ANÁLISE:")
        print("=" * 80)
        
        # Campos mais comuns
        print("🔍 TOP 10 CAMPOS MAIS COMUNS:")
        for campo, freq in sorted(self.campos_encontrados.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {campo}: {freq} arquivos ({freq/len(self.estrutura_por_arquivo)*100:.1f}%)")
        
        # Estatísticas por categoria
        total_basicos = sum(len(dados['campos_basicos']) for dados in self.estrutura_por_arquivo.values())
        total_dioptrias = sum(len(dados['campos_dioptrias']) for dados in self.estrutura_por_arquivo.values())
        total_vendas = sum(len(dados['campos_vendas']) for dados in self.estrutura_por_arquivo.values())
        
        print(f"\n📋 CAMPOS POR CATEGORIA:")
        print(f"   👤 Básicos: {total_basicos} ocorrências")
        print(f"   👁️ Dioptrías: {total_dioptrias} ocorrências")
        print(f"   💰 Vendas: {total_vendas} ocorrências")
        
        # Campos de dioptrías encontrados
        dioptrias_encontradas = set()
        for dados in self.estrutura_por_arquivo.values():
            dioptrias_encontradas.update(dados['campos_dioptrias'].keys())
        
        print(f"\n👁️ CAMPOS DE DIOPTRÍAS IDENTIFICADOS ({len(dioptrias_encontradas)}):")
        for campo in sorted(dioptrias_encontradas):
            print(f"   ✅ {campo}")
        
        # Campos de dioptrías faltantes
        faltantes = set(self.campos_dioptrias_esperados) - dioptrias_encontradas
        if faltantes:
            print(f"\n❓ CAMPOS DE DIOPTRÍAS NÃO ENCONTRADOS ({len(faltantes)}):")
            for campo in sorted(faltantes):
                print(f"   ❌ {campo}")

def main():
    """Função principal"""
    analisador = AnalisadorEstruturaOS()
    estruturas = analisador.analisar_todos_arquivos()
    return estruturas

if __name__ == "__main__":
    main()