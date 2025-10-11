#!/usr/bin/env python3
"""
SISTEMA UNIVERSAL DE EXTRAÇÃO DE VENDAS
Processa qualquer loja e gera documento único padronizado
Uso: python sistema_vendas_universal.py [loja] [arquivo]
"""

import pandas as pd
from pathlib import Path
import openpyxl
from datetime import datetime
import sys
from typing import Dict, List, Optional

class SistemaVendasUniversal:
    def __init__(self):
        self.pasta_caixa = Path("data/caixa_lojas")
        self.pasta_saida = Path("data/vendas_processadas")
        self.pasta_saida.mkdir(exist_ok=True)
        
        # Mapeamento de lojas disponíveis (múltiplos anos)
        self.lojas_disponiveis = {
            'MAUA': ['MAUA/2024_MAU', 'MAUA/2025_MAU', 'MAUA'],  # 2025 na raiz
            'SUZANO': ['SUZANO/2024_SUZ', 'SUZANO/2025_SUZ', 'SUZANO'], 
            'RIO_PEQUENO': ['RIO_PEQUENO/2024_RIO', 'RIO_PEQUENO/2025_RIO', 'RIO_PEQUENO'],
            'ITAQUERA': ['ITAQUERA/2024_ITA', 'ITAQUERA/2025_ITA', 'ITAQUERA'],
            'GUARULHOS': ['GUARULHOS/2024_GUA', 'GUARULHOS/2025_GUA', 'GUARULHOS'],
            'TABOAO': ['TABOAO/2024_TAB', 'TABOAO/2025_TAB', 'TABOAO']
        }
    
    def listar_lojas_disponiveis(self):
        """Lista lojas disponíveis no sistema"""
        print("🏪 LOJAS DISPONÍVEIS NO SISTEMA:")
        print("=" * 50)
        
        for loja, caminhos in self.lojas_disponiveis.items():
            print(f"\n🏢 {loja}:")
            total_arquivos = 0
            
            for caminho in caminhos:
                pasta_loja = self.pasta_caixa / caminho
                if pasta_loja.exists():
                    arquivos = list(pasta_loja.glob("*.xlsx"))
                    if arquivos:
                        ano = "2025" if caminho.endswith(loja) else ("2024" if "2024" in caminho else "2023")
                        print(f"   ✅ {ano}: {len(arquivos)} arquivos ({pasta_loja})")
                        total_arquivos += len(arquivos)
                        if len(arquivos) <= 3:
                            print(f"      📄 {[arq.name for arq in arquivos]}")
                else:
                    ano = "2025" if caminho.endswith(loja) else ("2024" if "2024" in caminho else "2023")
                    print(f"   ❌ {ano}: Pasta não encontrada ({pasta_loja})")
            
            if total_arquivos == 0:
                print(f"   ⚠️  Nenhum arquivo encontrado para {loja}")
        print()
    
    def processar_loja_arquivo(self, loja: str, nome_arquivo: str):
        """Processa um arquivo específico de uma loja"""
        print(f"🚀 PROCESSANDO: {loja} - {nome_arquivo}")
        print("=" * 80)
        
        # Encontrar arquivo
        arquivo_path = self.encontrar_arquivo(loja, nome_arquivo)
        if not arquivo_path:
            print(f"❌ Arquivo não encontrado: {loja}/{nome_arquivo}")
            return None
        
        print(f"📁 Arquivo encontrado: {arquivo_path}")
        
        # Identificar informações do arquivo
        info_arquivo = self.identificar_arquivo(arquivo_path, loja)
        print(f"🏪 Loja: {info_arquivo['loja']}")
        print(f"📅 Período: {info_arquivo['periodo']}")
        
        # Processar todas as vendas
        vendas = self.extrair_todas_vendas(arquivo_path, info_arquivo)
        
        if vendas:
            # Gerar documento único
            arquivo_saida = self.gerar_documento_unico(vendas, info_arquivo)
            self.gerar_relatorio_final(vendas, info_arquivo)
            return arquivo_saida
        else:
            print("❌ Nenhuma venda foi extraída")
            return None
    
    def encontrar_arquivo(self, loja: str, nome_arquivo: str) -> Optional[Path]:
        """Encontra arquivo na estrutura de pastas (múltiplos anos)"""
        if loja.upper() not in self.lojas_disponiveis:
            return None
        
        caminhos_loja = self.lojas_disponiveis[loja.upper()]
        
        # Procurar em todas as pastas da loja (2025, 2024, etc.)
        for caminho_loja in caminhos_loja:
            pasta_loja = self.pasta_caixa / caminho_loja
            
            if not pasta_loja.exists():
                continue
            
            # Procurar arquivo exato
            arquivo_path = pasta_loja / nome_arquivo
            if arquivo_path.exists():
                return arquivo_path
            
            # Procurar arquivo sem extensão
            if not nome_arquivo.endswith('.xlsx'):
                arquivo_path = pasta_loja / f"{nome_arquivo}.xlsx"
                if arquivo_path.exists():
                    return arquivo_path
        
        return None
    
    def identificar_arquivo(self, arquivo_path: Path, loja: str) -> Dict:
        """Identifica informações do arquivo"""
        nome_arquivo = arquivo_path.stem
        
        # Detectar ano baseado no caminho ou nome
        if "2025" in str(arquivo_path) or arquivo_path.parent.name == loja:
            ano_completo = "2025"
        elif "2024" in str(arquivo_path):
            ano_completo = "2024"
        elif "2023" in str(arquivo_path):
            ano_completo = "2023"
        else:
            # Se não detectou, assumir 2025 (arquivos novos na raiz)
            ano_completo = "2025"
        
        # Extrair período (ex: abr_24 -> 2024_ABR ou jan_25 -> 2025_JAN)
        if '_' in nome_arquivo:
            mes, ano_curto = nome_arquivo.split('_')
            
            # Determinar ano completo baseado no ano curto
            if ano_curto in ['25']:
                ano_completo = "2025"
                periodo = f"2025_{mes.upper()}"
            elif ano_curto in ['24']:
                ano_completo = "2024"
                periodo = f"2024_{mes.upper()}"
            elif ano_curto in ['23']:
                ano_completo = "2023"
                periodo = f"2023_{mes.upper()}"
            else:
                periodo = f"{ano_completo}_{mes.upper()}"
            
            mes = mes.upper()
        else:
            periodo = f"{ano_completo}_DESCONHECIDO"
            mes = "DESCONHECIDO"
        
        return {
            'loja': loja.upper(),
            'periodo': periodo,
            'ano': ano_completo,
            'mes': mes,
            'arquivo_nome': arquivo_path.name,
            'arquivo_path': str(arquivo_path)
        }
    
    def extrair_todas_vendas(self, arquivo_path: Path, info_arquivo: Dict) -> List[Dict]:
        """Extrai todas as vendas do arquivo"""
        print(f"\n📊 EXTRAINDO VENDAS DO ARQUIVO...")
        
        # Listar abas
        try:
            workbook = openpyxl.load_workbook(arquivo_path, read_only=True)
            todas_abas = workbook.sheetnames
            workbook.close()
        except Exception as e:
            print(f"❌ Erro ao abrir arquivo: {e}")
            return []
        
        # Filtrar abas de dias
        abas_dias = [aba for aba in todas_abas if aba.isdigit()]
        abas_dias.sort(key=int)
        
        print(f"📅 Processando {len(abas_dias)} dias: {abas_dias}")
        
        todas_vendas = []
        dias_com_vendas = 0
        
        for aba in abas_dias:
            try:
                vendas_dia = self.extrair_vendas_dia(arquivo_path, aba, info_arquivo)
                if vendas_dia:
                    todas_vendas.extend(vendas_dia)
                    dias_com_vendas += 1
                    print(f"   ✅ Dia {aba}: {len(vendas_dia)} vendas")
                else:
                    print(f"   ⚠️  Dia {aba}: sem vendas")
            except Exception as e:
                print(f"   ❌ Dia {aba}: erro - {e}")
        
        print(f"\n📊 Resumo da extração:")
        print(f"   📅 Dias processados: {len(abas_dias)}")
        print(f"   💰 Dias com vendas: {dias_com_vendas}")
        print(f"   📈 Total de vendas: {len(todas_vendas)}")
        
        return todas_vendas
    
    def extrair_vendas_dia(self, arquivo_path: Path, aba: str, info_arquivo: Dict) -> List[Dict]:
        """Extrai vendas de um dia específico"""
        try:
            df = pd.read_excel(arquivo_path, sheet_name=aba, header=None)
            
            # Encontrar tabela de vendas
            linha_cabecalho = None
            for i, row in df.iterrows():
                linha_texto = " ".join([str(cell) for cell in row if pd.notna(cell)])
                linha_upper = linha_texto.upper()
                
                if all(col in linha_upper for col in ['Nº VENDA', 'CLIENTE', 'FORMA', 'PGTO', 'VALOR']):
                    linha_cabecalho = i
                    break
            
            if linha_cabecalho is None:
                return []
            
            # Mapear colunas
            cabecalho_row = df.iloc[linha_cabecalho]
            mapeamento = self.mapear_colunas(cabecalho_row)
            
            # Extrair vendas
            vendas = []
            for i in range(linha_cabecalho + 1, len(df)):
                row = df.iloc[i]
                venda = self.extrair_venda_linha(row, mapeamento, aba, info_arquivo, i)
                
                if venda:
                    vendas.append(venda)
                elif self.e_fim_tabela(row):
                    break
            
            return vendas
            
        except Exception as e:
            print(f"      ❌ Erro detalhado no dia {aba}: {e}")
            return []
    
    def mapear_colunas(self, cabecalho_row) -> Dict:
        """Mapeia colunas do cabeçalho"""
        mapeamento = {}
        
        for i, cell in enumerate(cabecalho_row):
            if pd.notna(cell):
                cell_upper = str(cell).upper()
                
                if 'Nº VENDA' in cell_upper:
                    mapeamento['numero_venda'] = i
                elif 'CLIENTE' in cell_upper:
                    mapeamento['cliente'] = i
                elif 'FORMA' in cell_upper and 'PGTO' in cell_upper:
                    mapeamento['forma_pgto'] = i
                elif 'VALOR' in cell_upper and 'VENDA' in cell_upper:
                    mapeamento['valor_venda'] = i
                elif 'ENTRADA' in cell_upper:
                    mapeamento['entrada'] = i
        
        return mapeamento
    
    def extrair_venda_linha(self, row, mapeamento: Dict, aba: str, info_arquivo: Dict, linha_idx: int) -> Optional[Dict]:
        """Extrai dados de uma linha de venda"""
        # Extrair valores
        numero_venda = self.extrair_valor_coluna(row, mapeamento.get('numero_venda'))
        cliente = self.extrair_valor_coluna(row, mapeamento.get('cliente'))
        forma_pgto = self.extrair_valor_coluna(row, mapeamento.get('forma_pgto'))
        valor_venda = self.extrair_valor_monetario(row, mapeamento.get('valor_venda'))
        entrada = self.extrair_valor_monetario(row, mapeamento.get('entrada'))
        
        # Validar
        if not numero_venda or not str(numero_venda).isdigit():
            return None
        
        # Aplicar regras de negócio
        if forma_pgto and forma_pgto.upper() in ['SS', 'GARANTIA']:
            valor_venda = 0
            if forma_pgto.upper() == 'GARANTIA':
                entrada = 0
        
        # Construir data
        data_completa = self.construir_data(aba, info_arquivo)
        
        return {
            'loja': info_arquivo['loja'],
            'data': data_completa,
            'numero_venda': str(numero_venda),
            'cliente': cliente or '',
            'forma_pgto': forma_pgto or '',
            'valor_venda': valor_venda or 0,
            'entrada': entrada or 0
        }
    
    def extrair_valor_coluna(self, row, coluna_idx: Optional[int]) -> Optional[str]:
        """Extrai valor de uma coluna"""
        if coluna_idx is None or coluna_idx >= len(row):
            return None
        
        valor = row.iloc[coluna_idx] if hasattr(row, 'iloc') else row[coluna_idx]
        
        if pd.notna(valor):
            return str(valor).strip()
        return None
    
    def extrair_valor_monetario(self, row, coluna_idx: Optional[int]) -> Optional[float]:
        """Extrai valor monetário com formatação brasileira"""
        valor_str = self.extrair_valor_coluna(row, coluna_idx)
        
        if not valor_str:
            return 0
        
        # Limpar formato monetário
        valor_limpo = valor_str.replace('R$', '').strip()
        
        try:
            # Formatação brasileira
            if ',' in valor_limpo:
                if '.' in valor_limpo and ',' in valor_limpo:
                    valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
                else:
                    valor_limpo = valor_limpo.replace(',', '.')
            elif '.' in valor_limpo:
                partes = valor_limpo.split('.')
                if len(partes[-1]) == 2:
                    pass  # É decimal
                else:
                    valor_limpo = valor_limpo.replace('.', '')
            
            return float(valor_limpo)
            
        except ValueError:
            return 0
    
    def e_fim_tabela(self, row) -> bool:
        """Verifica se chegou ao fim da tabela"""
        valores_nao_nulos = [cell for cell in row if pd.notna(cell)]
        
        if not valores_nao_nulos:
            return True
        
        linha_texto = " ".join([str(cell) for cell in valores_nao_nulos])
        linha_upper = linha_texto.upper()
        
        return any(keyword in linha_upper for keyword in ['TOTAL', 'SOMA', 'SUBTOTAL'])
    
    def construir_data(self, aba: str, info_arquivo: Dict) -> str:
        """Constrói data completa"""
        dia = aba.zfill(2)
        
        meses = {
            'JAN': '01', 'FEV': '02', 'MAR': '03', 'ABR': '04',
            'MAI': '05', 'JUN': '06', 'JUL': '07', 'AGO': '08',
            'SET': '09', 'OUT': '10', 'NOV': '11', 'DEZ': '12'
        }
        
        mes_num = meses.get(info_arquivo['mes'], '01')
        ano = info_arquivo['ano']
        
        return f"{ano}-{mes_num}-{dia}"
    
    def gerar_documento_unico(self, vendas: List[Dict], info_arquivo: Dict) -> Path:
        """Gera documento único padronizado"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"VENDAS_{info_arquivo['loja']}_{info_arquivo['periodo']}_{timestamp}.xlsx"
        arquivo_saida = self.pasta_saida / nome_arquivo
        
        try:
            # Ordenar vendas por data e número
            df_vendas = pd.DataFrame(vendas)
            df_vendas['data'] = pd.to_datetime(df_vendas['data'])
            df_vendas = df_vendas.sort_values(['data', 'numero_venda'])
            df_vendas['data'] = df_vendas['data'].dt.strftime('%Y-%m-%d')
            
            # Garantir ordem das colunas
            colunas_ordem = ['loja', 'data', 'numero_venda', 'cliente', 'forma_pgto', 'valor_venda', 'entrada']
            df_vendas = df_vendas[colunas_ordem]
            
            # Salvar
            df_vendas.to_excel(arquivo_saida, index=False, sheet_name='VENDAS')
            
            print(f"\n💾 DOCUMENTO ÚNICO GERADO:")
            print(f"📄 Arquivo: {arquivo_saida}")
            print(f"📊 Registros: {len(vendas)} vendas")
            print(f"📋 Colunas: {list(df_vendas.columns)}")
            
            return arquivo_saida
            
        except Exception as e:
            print(f"❌ Erro ao gerar documento: {e}")
            return None
    
    def gerar_relatorio_final(self, vendas: List[Dict], info_arquivo: Dict):
        """Gera relatório final da extração"""
        print(f"\n" + "=" * 60)
        print(f"📈 RELATÓRIO FINAL - {info_arquivo['loja']}")
        print("=" * 60)
        
        # Estatísticas gerais
        total_vendas = len(vendas)
        valor_total = sum(v['valor_venda'] for v in vendas)
        entrada_total = sum(v['entrada'] for v in vendas)
        
        print(f"📊 Total de vendas: {total_vendas}")
        print(f"💰 Valor total: R$ {valor_total:,.2f}")
        print(f"💵 Entradas total: R$ {entrada_total:,.2f}")
        if total_vendas > 0:
            print(f"📉 Média por venda: R$ {valor_total/total_vendas:,.2f}")
        
        # Período
        datas = sorted(set(v['data'] for v in vendas))
        if datas:
            print(f"\n📅 Período: {datas[0]} a {datas[-1]} ({len(datas)} dias)")
        
        # Top formas de pagamento
        formas = {}
        for v in vendas:
            forma = v['forma_pgto'] or 'Não informado'
            formas[forma] = formas.get(forma, 0) + 1
        
        print(f"\n💳 Top formas de pagamento:")
        for forma, count in sorted(formas.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {forma}: {count} vendas")
        
        # Top clientes
        clientes = {}
        for v in vendas:
            cliente = v['cliente'] or 'Não informado'
            if cliente not in clientes:
                clientes[cliente] = {'count': 0, 'valor': 0}
            clientes[cliente]['count'] += 1
            clientes[cliente]['valor'] += v['valor_venda']
        
        top_clientes = sorted(clientes.items(), key=lambda x: x[1]['valor'], reverse=True)[:5]
        
        print(f"\n👥 Top 5 clientes:")
        for cliente, dados in top_clientes:
            print(f"   {cliente}: {dados['count']} vendas (R$ {dados['valor']:,.2f})")

def main():
    sistema = SistemaVendasUniversal()
    
    print("🏪 SISTEMA UNIVERSAL DE VENDAS")
    print("=" * 50)
    
    # Verificar argumentos
    if len(sys.argv) < 3:
        print("📋 Uso: python sistema_vendas_universal.py [LOJA] [ARQUIVO]")
        print("📋 Exemplo: python sistema_vendas_universal.py MAUA abr_24.xlsx")
        print()
        sistema.listar_lojas_disponiveis()
        return
    
    loja = sys.argv[1]
    arquivo = sys.argv[2]
    
    # Processar
    resultado = sistema.processar_loja_arquivo(loja, arquivo)
    
    if resultado:
        print(f"\n🎉 PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
        print(f"📄 Documento gerado: {resultado}")
    else:
        print(f"\n❌ PROCESSAMENTO FALHOU")

if __name__ == "__main__":
    main()