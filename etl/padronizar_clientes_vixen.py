#!/usr/bin/env python3
"""
Padronizador de Clientes Vixen para o Modelo Padrão
Converte clientes_completos_vixen.XLSX para o formato BASE_CLIENTES_COM_ID
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import re

class PadronizadorClientesVixen:
    def __init__(self):
        self.arquivo_vixen = Path("data/analise_especial/clientes_completos_vixen.XLSX")
        # Usar ID original do Vixen em vez de gerar novo
        
    def limpar_cpf(self, cpf_str):
        """Limpa e valida CPF"""
        if pd.isna(cpf_str):
            return None
        cpf_limpo = re.sub(r'[^\d]', '', str(cpf_str))
        if len(cpf_limpo) == 11:
            return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        return None
    
    def limpar_telefone(self, fone_str):
        """Limpa e padroniza telefone"""
        if pd.isna(fone_str):
            return None
        # Remove caracteres especiais e extrai números
        fone_limpo = re.sub(r'[^\d]', '', str(fone_str))
        if len(fone_limpo) >= 10:
            # Formato (11) 94240-5279
            if len(fone_limpo) == 11:  # Com DDD
                return f"({fone_limpo[:2]}) {fone_limpo[2:7]}-{fone_limpo[7:]}"
            elif len(fone_limpo) == 10:  # Sem 9 inicial
                return f"({fone_limpo[:2]}) {fone_limpo[2:6]}-{fone_limpo[6:]}"
        return str(fone_str)  # Retorna original se não conseguir formatar
    
    def limpar_cep(self, cep_str):
        """Limpa e padroniza CEP"""
        if pd.isna(cep_str):
            return None
        cep_limpo = re.sub(r'[^\d]', '', str(cep_str))
        if len(cep_limpo) >= 5:
            return cep_limpo[:8]  # Máximo 8 dígitos
        return None
    
    def processar_data_nascimento(self, data_str):
        """Processa data de aniversário"""
        if pd.isna(data_str):
            return None
        try:
            # Tenta diferentes formatos
            data_str = str(data_str)
            if ' ' in data_str:
                data_str = data_str.split(' ')[0]  # Remove horário se tiver
            
            # Tenta parsear
            if '-' in data_str:
                return pd.to_datetime(data_str, format='%Y-%m-%d').strftime('%d/%m/%Y')
            elif '/' in data_str:
                return pd.to_datetime(data_str, format='%d/%m/%Y').strftime('%d/%m/%Y')
            else:
                return None
        except:
            return None
    
    def criar_chave_cliente(self, row):
        """Cria chave única para o cliente"""
        # Prioridade: CPF > Nome + Telefone > ID Vixen
        nome = str(row.get('Nome Completo', '')).strip()
        fone = str(row.get('Fone', '')).strip()
        id_vixen = str(row.get('ID', ''))
        
        # Se tivesse CPF, usaria CPF_xxxxx, mas não temos no Vixen
        # Usar nome + telefone ou ID como chave
        if nome and fone and fone != 'nan':
            chave = f"VIXEN_{nome[:20].replace(' ', '_')}_{re.sub(r'[^\d]', '', fone)[:8]}"
        else:
            chave = f"VIXEN_ID_{id_vixen}"
        
        return chave.upper()
    
    def padronizar_clientes(self):
        """Converte clientes Vixen para o padrão do sistema"""
        print("=" * 80)
        print("PADRONIZADOR DE CLIENTES VIXEN")
        print("=" * 80)
        
        if not self.arquivo_vixen.exists():
            print(f"❌ Arquivo Vixen não encontrado: {self.arquivo_vixen}")
            return None
            
        try:
            # Carregar dados Vixen
            print(f"📄 Carregando: {self.arquivo_vixen.name}")
            df_vixen = pd.read_excel(self.arquivo_vixen)
            print(f"✅ {len(df_vixen):,} clientes Vixen carregados")
            print()
            
            # Criar estrutura padronizada
            clientes_padronizados = []
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            print("🔄 Convertendo para formato padrão...")
            
            for index, row in df_vixen.iterrows():
                # Usar ID original do Vixen (mantém relacionamentos)
                id_vixen_original = row.get('ID')
                id_cliente = f"VXN_{id_vixen_original:07d}"  # VXN_2001552
                
                # Mapear campos
                cliente_padrao = {
                    'ID_CLIENTE': id_cliente,
                    'CHAVE_CLIENTE': self.criar_chave_cliente(row),
                    'METODO_ID': 'VIXEN_ID_ORIGINAL',
                    'nome_completo': str(row.get('Nome Completo', '')).strip(),
                    'cpf': None,  # Vixen não tem CPF
                    'rg': None,   # Vixen não tem RG
                    'data_nascimento': self.processar_data_nascimento(row.get('Dt de aniversário')),
                    'celular': self.limpar_telefone(row.get('Fone')),
                    'email': str(row.get('E-mail', '')).strip() if pd.notna(row.get('E-mail')) else None,
                    'endereco': str(row.get('Endereço', '')).strip(),
                    'cep': self.limpar_cep(row.get('CEP')),
                    'bairro': str(row.get('Bairro', '')).strip(),
                    'origem_loja': 'VIXEN',
                    'origem_arquivo': 'clientes_completos_vixen.XLSX',
                    'total_registros_mesclados': 1,
                    'data_extracao': timestamp,
                    # Campos extras do Vixen (mantém ID original para relacionamentos)
                    'id_vixen_original': id_vixen_original,
                    'cidade': str(row.get('Cidade', '')).strip(),
                    'uf': str(row.get('UF', '')).strip(),
                    'sexo': str(row.get('Sexo', '')).strip(),
                    'vendedor': str(row.get('Vendedor', '')).strip(),
                    'conceito': str(row.get('Conceito', '')).strip(),
                    'como_conheceu': str(row.get('Como nos conheceu', '')).strip()
                }
                
                clientes_padronizados.append(cliente_padrao)
                
                # Progress
                if (index + 1) % 1000 == 0:
                    print(f"   Processados: {index + 1:,} clientes")
            
            # Criar DataFrame final
            df_padronizado = pd.DataFrame(clientes_padronizados)
            
            print(f"✅ {len(df_padronizado):,} clientes convertidos")
            print()
            
            # Salvar arquivo padronizado
            timestamp_arquivo = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo_saida = f"data/analise_especial/BASE_CLIENTES_VIXEN_PADRONIZADO_{timestamp_arquivo}.xlsx"
            
            print(f"💾 Salvando: {arquivo_saida}")
            df_padronizado.to_excel(arquivo_saida, index=False)
            
            # Gerar relatório comparativo
            self.gerar_relatorio_comparativo(df_vixen, df_padronizado, arquivo_saida)
            
            print("✅ CONVERSÃO CONCLUÍDA!")
            print()
            print("📊 ESTATÍSTICAS:")
            print(f"   • Total de clientes: {len(df_padronizado):,}")
            print(f"   • Com telefone: {df_padronizado['celular'].notna().sum():,}")
            print(f"   • Com email: {df_padronizado['email'].notna().sum():,}")
            print(f"   • Com data nascimento: {df_padronizado['data_nascimento'].notna().sum():,}")
            print(f"   • Com endereço: {df_padronizado['endereco'].notna().sum():,}")
            print()
            print("🔄 PRÓXIMO PASSO:")
            print("   Execute script de integração para unificar com base atual")
            
            return df_padronizado
            
        except Exception as e:
            print(f"❌ Erro na conversão: {e}")
            return None
    
    def gerar_relatorio_comparativo(self, df_original, df_padronizado, arquivo_saida):
        """Gera relatório comparando dados originais e padronizados"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        relatorio_path = f"data/analise_especial/RELATORIO_PADRONIZACAO_VIXEN_{timestamp}.xlsx"
        
        with pd.ExcelWriter(relatorio_path, engine='openpyxl') as writer:
            # 1. Resumo da conversão
            resumo = {
                'MÉTRICA': [
                    'Registros Originais',
                    'Registros Padronizados',
                    'Taxa de Conversão',
                    'Campos Originais',
                    'Campos Padronizados',
                    'Arquivo Origem',
                    'Arquivo Destino',
                    'Data Processamento'
                ],
                'VALOR': [
                    len(df_original),
                    len(df_padronizado),
                    '100%',
                    len(df_original.columns),
                    len(df_padronizado.columns),
                    'clientes_completos_vixen.XLSX',
                    arquivo_saida.split('/')[-1],
                    timestamp
                ]
            }
            pd.DataFrame(resumo).to_excel(writer, sheet_name='Resumo_Conversao', index=False)
            
            # 2. Mapeamento de campos
            mapeamento = {
                'CAMPO_VIXEN': ['ID', 'Nome Completo', 'Fone', 'E-mail', 'Endereço', 'CEP', 'Bairro', 'Cidade', 'UF', 'Sexo', 'Dt de aniversário', 'Vendedor'],
                'CAMPO_PADRAO': ['id_vixen_original', 'nome_completo', 'celular', 'email', 'endereco', 'cep', 'bairro', 'cidade', 'uf', 'sexo', 'data_nascimento', 'vendedor'],
                'OBSERVACOES': ['Mantido como referência', 'Mapeamento direto', 'Formatado (XX) XXXXX-XXXX', 'Mapeamento direto', 'Mapeamento direto', 'Limpo apenas números', 'Mapeamento direto', 'Campo extra', 'Campo extra', 'Campo extra', 'Convertido DD/MM/YYYY', 'Campo extra']
            }
            pd.DataFrame(mapeamento).to_excel(writer, sheet_name='Mapeamento_Campos', index=False)
            
            # 3. Amostra dos dados convertidos
            df_padronizado.head(100).to_excel(writer, sheet_name='Amostra_Convertidos', index=False)
        
        print(f"📋 Relatório salvo: {relatorio_path}")

def main():
    padronizador = PadronizadorClientesVixen()
    resultado = padronizador.padronizar_clientes()
    
    if resultado is not None:
        print()
        print("🎯 ARQUIVO PRONTO PARA INTEGRAÇÃO!")
        print("   Compatível com sistema atual BASE_CLIENTES_COM_ID")

if __name__ == "__main__":
    main()