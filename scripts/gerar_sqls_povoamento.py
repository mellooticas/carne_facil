"""
Script para gerar SQLs de povoamento do Supabase a partir dos dados consolidados
Lê os arquivos parquet e gera blocos SQL executáveis no Supabase SQL Editor
"""
import pandas as pd
from pathlib import Path
import json
import unicodedata

# Configurações
BATCH_SIZE = 200  # Linhas por arquivo SQL (reduzido para limites do Supabase)
OUTPUT_DIR = Path('povoamento/dados')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def remover_acentos(texto):
    """Remove acentos de um texto"""
    if not texto:
        return texto
    # Normaliza para NFD (decomposição canônica) e remove marcas diacríticas
    nfkd = unicodedata.normalize('NFD', str(texto))
    return ''.join([c for c in nfkd if not unicodedata.combining(c)])

def escapar_sql(valor):
    """Escapa valores para SQL"""
    if pd.isna(valor) or valor == '' or valor == 'nan':
        return 'NULL'
    if isinstance(valor, (int, float)):
        if pd.isna(valor):
            return 'NULL'
        return str(valor)
    # String: escapar aspas simples
    valor_str = str(valor).replace("'", "''")
    return f"'{valor_str}'"

def gerar_sql_clientes():
    """Gera SQLs de inserção de clientes"""
    print("📊 Gerando SQLs de clientes...")
    
    # Carregar clientes unificados
    clientes_file = Path('data/clientes/_consolidado/clientes_unificados.parquet')
    if not clientes_file.exists():
        print(f"❌ Arquivo não encontrado: {clientes_file}")
        return
    
    df = pd.read_parquet(clientes_file)
    print(f"✅ {len(df)} clientes carregados")
    
    # Limpar dados
    df['cpf'] = df['cpf'].astype(str).str.replace(r'\D', '', regex=True)
    df.loc[df['cpf'] == '', 'cpf'] = None
    
    # Normalizar telefones
    for col in ['telefone1', 'telefone2']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'\D', '', regex=True)
            df.loc[df[col] == '', col] = None
    
    # Email
    if 'email' in df.columns:
        df.loc[~df['email'].astype(str).str.contains('@', na=False), 'email'] = None
    
    # Gerar blocos SQL
    total_blocos = (len(df) + BATCH_SIZE - 1) // BATCH_SIZE
    
    for bloco_num in range(total_blocos):
        inicio = bloco_num * BATCH_SIZE
        fim = min((bloco_num + 1) * BATCH_SIZE, len(df))
        df_bloco = df.iloc[inicio:fim]
        
        sql_lines = [
            f"-- Bloco {bloco_num + 1}/{total_blocos} - Clientes {inicio + 1} a {fim}",
            "INSERT INTO core.clientes (id_legado, nome, cpf, email, status, created_by, version)",
            "VALUES"
        ]
        
        valores = []
        for _, row in df_bloco.iterrows():
            nome = escapar_sql(str(row['nome'])[:200] if row['nome'] else 'SEM NOME')
            
            # CPF formatado
            cpf = 'NULL'
            if row['cpf'] and len(str(row['cpf']).strip()) == 11:
                cpf_limpo = str(row['cpf']).strip()
                cpf = escapar_sql(f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}")
            
            # Email: remover espaços em branco e acentos
            email = 'NULL'
            if row.get('email'):
                email_str = str(row['email']).strip()
                # Remover acentos do email
                email_str = remover_acentos(email_str)
                if email_str and '@' in email_str and len(email_str) <= 100:
                    email = escapar_sql(email_str)
            
            id_legado = escapar_sql(str(row['id_cliente']))
            origem = str(row.get('origem', 'VIXEN')).upper()
            created_by = escapar_sql(f"MIGRACAO_{origem}")
            
            valores.append(
                f"  ({id_legado}, {nome}, {cpf}, {email}, 'ATIVO', {created_by}, 1)"
            )
        
        sql_lines.append(',\n'.join(valores) + ';')
        
        # Salvar arquivo
        output_file = OUTPUT_DIR / f'clientes_bloco_{bloco_num + 1:03d}.sql'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_lines))
        
        print(f"  ✅ {output_file.name} - {len(df_bloco)} registros")
    
    print(f"✅ {total_blocos} arquivos SQL de clientes gerados")

def gerar_sql_telefones():
    """Gera SQLs de inserção de telefones"""
    print("\n📞 Gerando SQLs de telefones...")
    
    # Carregar clientes unificados
    clientes_file = Path('data/clientes/_consolidado/clientes_unificados.parquet')
    if not clientes_file.exists():
        print(f"❌ Arquivo não encontrado: {clientes_file}")
        return
    
    df = pd.read_parquet(clientes_file)
    
    # Preparar telefones
    telefones = []
    for _, row in df.iterrows():
        id_legado = str(row['id_cliente'])
        
        # Telefone 1
        if row.get('telefone1'):
            tel1 = str(row['telefone1']).strip()
            if tel1 and tel1 != 'nan' and len(tel1) >= 10:
                telefones.append({
                    'cliente_id_legado': id_legado,
                    'numero': tel1,
                    'tipo': 'CELULAR' if len(tel1) == 11 else 'FIXO',
                    'principal': True
                })
        
        # Telefone 2
        if row.get('telefone2'):
            tel2 = str(row['telefone2']).strip()
            if tel2 and tel2 != 'nan' and len(tel2) >= 10:
                telefones.append({
                    'cliente_id_legado': id_legado,
                    'numero': tel2,
                    'tipo': 'CELULAR' if len(tel2) == 11 else 'FIXO',
                    'principal': False
                })
    
    print(f"✅ {len(telefones)} telefones preparados")
    
    # Gerar blocos SQL (com subquery para obter UUID do cliente)
    total_blocos = (len(telefones) + BATCH_SIZE - 1) // BATCH_SIZE
    
    for bloco_num in range(total_blocos):
        inicio = bloco_num * BATCH_SIZE
        fim = min((bloco_num + 1) * BATCH_SIZE, len(telefones))
        telefones_bloco = telefones[inicio:fim]
        
        sql_lines = [
            f"-- Bloco {bloco_num + 1}/{total_blocos} - Telefones {inicio + 1} a {fim}",
            "INSERT INTO core.telefones (cliente_id, numero, tipo, principal, ativo)",
            "VALUES"
        ]
        
        valores = []
        for tel in telefones_bloco:
            # Subquery para obter UUID do cliente pelo id_legado
            cliente_id_legado = escapar_sql(tel['cliente_id_legado'])
            numero = escapar_sql(tel['numero'])
            tipo = escapar_sql(tel['tipo'])
            principal = str(tel['principal']).upper()
            
            valores.append(
                f"  ((SELECT id FROM core.clientes WHERE id_legado = {cliente_id_legado} LIMIT 1), {numero}, {tipo}, {principal}, TRUE)"
            )
        
        sql_lines.append(',\n'.join(valores) + ';')
        
        # Salvar arquivo
        output_file = OUTPUT_DIR / f'telefones_bloco_{bloco_num + 1:03d}.sql'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_lines))
        
        print(f"  ✅ {output_file.name} - {len(telefones_bloco)} registros")
    
    print(f"✅ {total_blocos} arquivos SQL de telefones gerados")

def main():
    print("=" * 80)
    print("GERAÇÃO DE SQLs DE POVOAMENTO - SUPABASE")
    print("=" * 80)
    print(f"\n📁 Diretório de saída: {OUTPUT_DIR}")
    print(f"📦 Tamanho dos blocos: {BATCH_SIZE} registros\n")
    
    # Gerar SQLs
    gerar_sql_clientes()
    gerar_sql_telefones()
    
    print("\n" + "=" * 80)
    print("✅ GERAÇÃO CONCLUÍDA!")
    print("=" * 80)
    print(f"\n📋 PRÓXIMOS PASSOS:")
    print("  1. Execute os arquivos SQL na pasta '{OUTPUT_DIR}' no Supabase SQL Editor")
    print("  2. Comece pelos arquivos de clientes (ordem numérica)")
    print("  3. Depois execute os arquivos de telefones")
    print("  4. Valide os dados com as queries em povoamento/06_validacao.sql")

if __name__ == "__main__":
    main()
