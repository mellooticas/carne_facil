"""
Serviço de deduplicação inteligente de clientes
"""

from typing import List, Dict, Tuple, Optional
import pandas as pd
from fuzzywuzzy import fuzz, process
from unidecode import unidecode
import re
import logging
from dataclasses import dataclass

@dataclass
class ClienteMatch:
    """Representa um match entre dois clientes"""
    cliente_id_1: int
    cliente_id_2: int
    nome_1: str
    nome_2: str
    score_nome: float
    score_cpf: float
    score_telefone: float
    score_endereco: float
    score_final: float
    confianca: str  # alta, media, baixa
    recomendacao: str  # merge, revisar, ignorar

class DeduplicadorClientes:
    def __init__(self, threshold_alto: float = 0.9, threshold_medio: float = 0.75):
        self.threshold_alto = threshold_alto
        self.threshold_medio = threshold_medio
        
    def normalizar_nome(self, nome: str) -> str:
        """Normaliza nome para comparação"""
        if pd.isna(nome):
            return ""
        
        nome = str(nome).strip().upper()
        nome = unidecode(nome)
        
        # Remover títulos comuns
        titulos = ['DR', 'DRA', 'SR', 'SRA', 'SRTA', 'PROF', 'ENG']
        palavras = nome.split()
        palavras = [p for p in palavras if p not in titulos]
        
        # Remover conectores
        conectores = ['DE', 'DA', 'DO', 'DAS', 'DOS', 'E']
        palavras = [p for p in palavras if p not in conectores or len(palavras) <= 2]
        
        return ' '.join(palavras)
    
    def normalizar_cpf(self, cpf: str) -> str:
        """Normaliza CPF removendo formatação"""
        if pd.isna(cpf):
            return ""
        
        return re.sub(r'\D', '', str(cpf))
    
    def normalizar_telefone(self, telefone: str) -> str:
        """Normaliza telefone removendo formatação"""
        if pd.isna(telefone):
            return ""
        
        tel = re.sub(r'\D', '', str(telefone))
        
        # Remover código do país se presente
        if len(tel) > 11 and tel.startswith('55'):
            tel = tel[2:]
        
        # Remover dígito 9 adicional se presente
        if len(tel) == 11 and tel[2] == '9':
            return tel
        elif len(tel) == 10:
            return tel[:2] + '9' + tel[2:]
        
        return tel
    
    def normalizar_endereco(self, endereco: str) -> str:
        """Normaliza endereço para comparação"""
        if pd.isna(endereco):
            return ""
        
        endereco = str(endereco).strip().upper()
        endereco = unidecode(endereco)
        
        # Padronizar abreviações
        substituicoes = {
            r'\bR\b\.?': 'RUA',
            r'\bAV\b\.?': 'AVENIDA',
            r'\bTRAV\b\.?': 'TRAVESSA',
            r'\bAL\b\.?': 'ALAMEDA',
            r'\bPCA\b\.?': 'PRACA',
            r'\bEST\b\.?': 'ESTRADA',
            r'\bROD\b\.?': 'RODOVIA',
            r'\bAPT\b\.?': 'APARTAMENTO',
            r'\bCONJ\b\.?': 'CONJUNTO',
            r'\bBL\b\.?': 'BLOCO',
            r'\bQD\b\.?': 'QUADRA',
            r'\bLT\b\.?': 'LOTE'
        }
        
        for padrao, substituto in substituicoes.items():
            endereco = re.sub(padrao, substituto, endereco)
        
        return endereco
    
    def calcular_score_nome(self, nome1: str, nome2: str) -> float:
        """Calcula score de similaridade entre nomes"""
        nome1_norm = self.normalizar_nome(nome1)
        nome2_norm = self.normalizar_nome(nome2)
        
        if not nome1_norm or not nome2_norm:
            return 0.0
        
        # Usar múltiples métricas
        ratio = fuzz.ratio(nome1_norm, nome2_norm)
        partial = fuzz.partial_ratio(nome1_norm, nome2_norm)
        token_sort = fuzz.token_sort_ratio(nome1_norm, nome2_norm)
        token_set = fuzz.token_set_ratio(nome1_norm, nome2_norm)
        
        # Média ponderada das métricas
        score = (ratio * 0.3 + partial * 0.2 + token_sort * 0.25 + token_set * 0.25) / 100
        
        return score
    
    def calcular_score_cpf(self, cpf1: str, cpf2: str) -> float:
        """Calcula score de similaridade entre CPFs"""
        cpf1_norm = self.normalizar_cpf(cpf1)
        cpf2_norm = self.normalizar_cpf(cpf2)
        
        if not cpf1_norm or not cpf2_norm:
            return 0.0
        
        return 1.0 if cpf1_norm == cpf2_norm else 0.0
    
    def calcular_score_telefone(self, tel1: str, tel2: str) -> float:
        """Calcula score de similaridade entre telefones"""
        tel1_norm = self.normalizar_telefone(tel1)
        tel2_norm = self.normalizar_telefone(tel2)
        
        if not tel1_norm or not tel2_norm:
            return 0.0
        
        # Match exato
        if tel1_norm == tel2_norm:
            return 1.0
        
        # Match dos últimos 8 dígitos (número sem DDD)
        if len(tel1_norm) >= 8 and len(tel2_norm) >= 8:
            if tel1_norm[-8:] == tel2_norm[-8:]:
                return 0.8
        
        # Similaridade usando Levenshtein
        return fuzz.ratio(tel1_norm, tel2_norm) / 100
    
    def calcular_score_endereco(self, end1: str, end2: str) -> float:
        """Calcula score de similaridade entre endereços"""
        end1_norm = self.normalizar_endereco(end1)
        end2_norm = self.normalizar_endereco(end2)
        
        if not end1_norm or not end2_norm:
            return 0.0
        
        return fuzz.token_set_ratio(end1_norm, end2_norm) / 100
    
    def calcular_score_final(self, scores: Dict[str, float]) -> Tuple[float, str]:
        """Calcula score final e determina confiança"""
        # Pesos para diferentes campos
        pesos = {
            'nome': 0.4,
            'cpf': 0.3,
            'telefone': 0.2,
            'endereco': 0.1
        }
        
        # Se CPF é igual, alta confiança
        if scores.get('cpf', 0) == 1.0:
            return 1.0, 'alta'
        
        # Calcular score ponderado
        score_final = sum(scores.get(campo, 0) * peso for campo, peso in pesos.items())
        
        # Determinar confiança
        if score_final >= self.threshold_alto:
            confianca = 'alta'
        elif score_final >= self.threshold_medio:
            confianca = 'media'
        else:
            confianca = 'baixa'
        
        return score_final, confianca
    
    def determinar_recomendacao(self, score_final: float, confianca: str, scores: Dict[str, float]) -> str:
        """Determina recomendação baseada nos scores"""
        # Se CPF é igual, sempre fazer merge
        if scores.get('cpf', 0) == 1.0:
            return 'merge'
        
        # Se nome e telefone são muito similares
        if scores.get('nome', 0) >= 0.9 and scores.get('telefone', 0) >= 0.8:
            return 'merge'
        
        # Baseado na confiança
        if confianca == 'alta':
            return 'merge'
        elif confianca == 'media':
            return 'revisar'
        else:
            return 'ignorar'
    
    def encontrar_duplicatas(self, df: pd.DataFrame) -> List[ClienteMatch]:
        """Encontra todas as duplicatas no DataFrame"""
        duplicatas = []
        
        # Campos necessários
        campos_obrigatorios = ['nome']
        campos_opcionais = ['cpf', 'telefone', 'endereco']
        
        # Verificar se pelo menos nome existe
        if not all(campo in df.columns for campo in campos_obrigatorios):
            raise ValueError(f"DataFrame deve conter pelo menos as colunas: {campos_obrigatorios}")
        
        # Adicionar ID se não existir
        if 'id' not in df.columns:
            df = df.reset_index()
            df = df.rename(columns={'index': 'id'})
        
        # Remover registros sem nome
        df_limpo = df.dropna(subset=['nome']).copy()
        
        total_registros = len(df_limpo)
        processados = 0
        
        for i, row1 in df_limpo.iterrows():
            for j, row2 in df_limpo.iloc[i+1:].iterrows():
                processados += 1
                
                if processados % 1000 == 0:
                    print(f"Processados: {processados}/{total_registros*(total_registros-1)//2}")
                
                # Calcular scores
                scores = {
                    'nome': self.calcular_score_nome(row1['nome'], row2['nome'])
                }
                
                # Só continuar se nome tem similaridade mínima
                if scores['nome'] < 0.6:
                    continue
                
                if 'cpf' in df.columns:
                    scores['cpf'] = self.calcular_score_cpf(row1.get('cpf'), row2.get('cpf'))
                
                if 'telefone' in df.columns:
                    scores['telefone'] = self.calcular_score_telefone(row1.get('telefone'), row2.get('telefone'))
                
                if 'endereco' in df.columns:
                    scores['endereco'] = self.calcular_score_endereco(row1.get('endereco'), row2.get('endereco'))
                
                # Calcular score final
                score_final, confianca = self.calcular_score_final(scores)
                
                # Só incluir se score final é significativo
                if score_final >= 0.6:
                    recomendacao = self.determinar_recomendacao(score_final, confianca, scores)
                    
                    match = ClienteMatch(
                        cliente_id_1=row1['id'],
                        cliente_id_2=row2['id'],
                        nome_1=row1['nome'],
                        nome_2=row2['nome'],
                        score_nome=scores['nome'],
                        score_cpf=scores.get('cpf', 0),
                        score_telefone=scores.get('telefone', 0),
                        score_endereco=scores.get('endereco', 0),
                        score_final=score_final,
                        confianca=confianca,
                        recomendacao=recomendacao
                    )
                    
                    duplicatas.append(match)
        
        # Ordenar por score final decrescente
        duplicatas.sort(key=lambda x: x.score_final, reverse=True)
        
        return duplicatas
    
    def gerar_relatorio_duplicatas(self, duplicatas: List[ClienteMatch]) -> pd.DataFrame:
        """Gera relatório das duplicatas encontradas"""
        if not duplicatas:
            return pd.DataFrame()
        
        dados = []
        for match in duplicatas:
            dados.append({
                'ID_1': match.cliente_id_1,
                'ID_2': match.cliente_id_2,
                'Nome_1': match.nome_1,
                'Nome_2': match.nome_2,
                'Score_Nome': round(match.score_nome, 3),
                'Score_CPF': round(match.score_cpf, 3),
                'Score_Telefone': round(match.score_telefone, 3),
                'Score_Endereco': round(match.score_endereco, 3),
                'Score_Final': round(match.score_final, 3),
                'Confianca': match.confianca,
                'Recomendacao': match.recomendacao
            })
        
        return pd.DataFrame(dados)

if __name__ == "__main__":
    # Exemplo de uso
    deduplicador = DeduplicadorClientes()
    
    # Dados de exemplo
    dados_exemplo = pd.DataFrame({
        'nome': ['João Silva', 'Joao da Silva', 'Maria Santos', 'Maria dos Santos'],
        'cpf': ['123.456.789-00', '12345678900', '987.654.321-00', '98765432100'],
        'telefone': ['(11) 99999-9999', '11999999999', '(11) 88888-8888', '1188888888']
    })
    
    duplicatas = deduplicador.encontrar_duplicatas(dados_exemplo)
    relatorio = deduplicador.gerar_relatorio_duplicatas(duplicatas)
    
    print("Duplicatas encontradas:")
    print(relatorio)