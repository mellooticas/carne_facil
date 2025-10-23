"""
Script para limpar clientes existentes e povoar banco Supabase
com dados consolidados do projeto Carnê Fácil
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import json
import time

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERRO] Credenciais não configuradas!")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configurações de rate limiting
BATCH_SIZE = 100  # Reduzido para respeitar limites Supabase (500 req/min)
MAX_RETRIES = 3
RETRY_DELAY = 2  # segundos entre tentativas
DELAY_BETWEEN_BATCHES = 0.5  # segundos entre lotes

def retry_request(func, *args, **kwargs):
    """Executa requisição com retry em caso de rate limiting"""
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_str = str(e)
            if 'rate limit' in error_str.lower() or '429' in error_str:
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_DELAY * (attempt + 1)
                    print(f"[RATE LIMIT] Aguardando {wait_time}s antes de tentar novamente...")
                    time.sleep(wait_time)
                    continue
            raise e
    raise Exception("Max retries excedido")

print("=" * 100)
print("LIMPEZA E POVOAMENTO DO BANCO SUPABASE")
print("=" * 100)
print(f"\nConectado: {SUPABASE_URL}\n")
print(f"[CONFIG] Batch size: {BATCH_SIZE} | Max retries: {MAX_RETRIES} | Delay: {DELAY_BETWEEN_BATCHES}s\n")

# ============================================================================
# ETAPA 1: LIMPEZA DE CLIENTES EXISTENTES (DADOS INCORRETOS)
# ============================================================================
print("\n" + "=" * 100)
print("ETAPA 1: LIMPEZA DE CLIENTES EXISTENTES (12,845 registros)")
print("=" * 100)

print("\n[ATENÇÃO] Isso vai DELETAR todos os 12,845 clientes existentes!")
print("Os dados atuais foram povoados incorretamente e serão substituídos.")
print("Nenhum backup será feito pois esses dados estão incorretos.")
print("\nDeseja continuar? (S/n): ", end='')
resposta = input().strip().upper()

if resposta != 'S':
    print("\n[CANCELADO] Operação abortada pelo usuário.")
    sys.exit(0)

print("\n[Deletando clientes...]")
try:
    # Supabase PostgREST precisa do schema correto
    # Vamos usar SQL via RPC ou executar manualmente
    print("\n[ATENÇÃO] A API do Supabase não expõe diretamente tabelas do schema 'core'")
    print("\n[SOLUÇÃO] Execute este SQL no Supabase SQL Editor:")
    print("-" * 80)
    print("TRUNCATE TABLE core.clientes CASCADE;")
    print("-" * 80)
    print("\nApós executar o SQL acima, pressione Enter para continuar...")
    input()
    print("[OK] Assumindo que a limpeza foi feita manualmente")

except Exception as e:
    print(f"\n[ERRO] Falha na limpeza: {e}")
    print("\n[SUGESTÃO] Execute manualmente no SQL Editor:")
    print("  TRUNCATE TABLE core.clientes CASCADE;")
    sys.exit(1)

# ============================================================================
# ETAPA 2: INSERIR LOJAS
# ============================================================================
print("\n" + "=" * 100)
print("ETAPA 2: INSERIR LOJAS")
print("=" * 100)

lojas_data = [
    {'codigo': '042', 'nome': 'Loja 042', 'cidade': 'São Paulo', 'estado': 'SP', 'ativo': True},
    {'codigo': '048', 'nome': 'Loja 048', 'cidade': 'São Paulo', 'estado': 'SP', 'ativo': True},
    {'codigo': '011', 'nome': 'Loja 011', 'cidade': 'São Paulo', 'estado': 'SP', 'ativo': True},
    {'codigo': '012', 'nome': 'Loja 012', 'cidade': 'São Paulo', 'estado': 'SP', 'ativo': True},
]

print("\n[Inserindo {len(lojas_data)} lojas...]")
try:
    for loja in lojas_data:
        retry_request(supabase.table('core.lojas').upsert(loja).execute)
        time.sleep(0.2)  # Pequeno delay entre inserções
    print(f"[OK] {len(lojas_data)} lojas inseridas")
except Exception as e:
    print(f"[ERRO] Falha ao inserir lojas: {e}")

# ============================================================================
# ETAPA 3: INSERIR CLIENTES CONSOLIDADOS
# ============================================================================
print("\n" + "=" * 100)
print("ETAPA 3: INSERIR CLIENTES CONSOLIDADOS (13,646 registros)")
print("=" * 100)

# Carregar clientes consolidados
clientes_file = Path('data/clientes/_consolidado/clientes_unificados.parquet')
if not clientes_file.exists():
    print(f"[ERRO] Arquivo não encontrado: {clientes_file}")
    sys.exit(1)

print(f"\n[Carregando {clientes_file.name}...]")
df_clientes = pd.read_parquet(clientes_file)
print(f"[OK] {len(df_clientes)} clientes carregados")

# Limpar dados
print("\n[Limpeza de dados...]")
# CPF: normalizar para apenas números
df_clientes['cpf'] = df_clientes['cpf'].astype(str).str.replace(r'\D', '', regex=True)
df_clientes.loc[df_clientes['cpf'] == '', 'cpf'] = None

# Telefones: normalizar
for col in ['telefone1', 'telefone2']:
    if col in df_clientes.columns:
        df_clientes[col] = df_clientes[col].astype(str).str.replace(r'\D', '', regex=True)
        df_clientes.loc[df_clientes[col] == '', col] = None

# Email: validar básico
if 'email' in df_clientes.columns:
    df_clientes.loc[~df_clientes['email'].astype(str).str.contains('@', na=False), 'email'] = None

# Preencher NaN
df_clientes = df_clientes.fillna('')
df_clientes = df_clientes.replace('nan', '')

print(f"[OK] Dados limpos")

# Mapear para estrutura core.clientes
# Estrutura confirmada:
# - id: uuid (auto-gerado)
# - id_legado: varchar(50) - UNIQUE - usar nosso id_cliente original
# - nome: varchar(200) - OBRIGATÓRIO
# - nome_normalizado: varchar(200) - normalizado lowercase
# - cpf: varchar(14) - UNIQUE (pode ser NULL)
# - email: varchar(100)
# - status: enum (default ATIVO)
# - created_by: varchar(100) - rastreabilidade

print("\n[Mapeando para estrutura core.clientes...]")
clientes_insert = []
for idx, row in df_clientes.iterrows():
    # Nome normalizado (lowercase, sem acentos)
    nome = str(row['nome'])[:200] if row['nome'] else 'SEM NOME'
    nome_normalizado = nome.lower()
    
    # CPF: apenas números, max 14 chars (com formatação)
    cpf = None
    if row['cpf']:
        cpf_limpo = str(row['cpf']).strip()
        if len(cpf_limpo) == 11:  # CPF válido
            # Formatar: 000.000.000-00
            cpf = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        elif cpf_limpo and cpf_limpo != 'nan':
            cpf = cpf_limpo[:14]  # Usar como está se já formatado
    
    # Email
    email = None
    if row['email'] and '@' in str(row['email']):
        email = str(row['email'])[:100]
    
    cliente = {
        # Campos obrigatórios
        'id_legado': str(row['id_cliente']),  # ID original para rastreabilidade
        'nome': nome,
        'nome_normalizado': nome_normalizado,
        
        # Campos opcionais
        'cpf': cpf,
        'email': email,
        'status': 'ATIVO',
        'created_by': f"MIGRACAO_{row['origem'].upper()}",  # VIXEN ou OS
        'version': 1
    }
    
    clientes_insert.append(cliente)

print(f"\n[Preparados {len(clientes_insert)} clientes para inserção]")

# Inserir em lotes menores com retry e rate limiting
print(f"\n[Inserindo clientes em lotes de {BATCH_SIZE}...]")
total_inserted = 0
errors = 0

for i in range(0, len(clientes_insert), BATCH_SIZE):
    batch = clientes_insert[i:i+BATCH_SIZE]
    batch_num = i // BATCH_SIZE + 1
    try:
        # Usar retry_request para lidar com rate limiting
        retry_request(supabase.table('core.clientes').insert(batch).execute)
        total_inserted += len(batch)
        print(f"  Lote {batch_num}: {total_inserted}/{len(clientes_insert)} ({(total_inserted/len(clientes_insert)*100):.1f}%)", end='\r')
        # Aguardar entre lotes para evitar rate limiting
        if i + BATCH_SIZE < len(clientes_insert):
            time.sleep(DELAY_BETWEEN_BATCHES)
    except Exception as e:
        errors += 1
        print(f"\n[ERRO] Batch {batch_num} falhou: {e}")
        if errors > 10:
            print("\n[ABORTANDO] Muitos erros consecutivos!")
            break
        # Aguardar mais tempo após erro
        time.sleep(RETRY_DELAY * 2)

print(f"\n[OK] Total inserido: {total_inserted} clientes")

if total_inserted < len(clientes_insert) * 0.9:
    print(f"[AVISO] Apenas {(total_inserted/len(clientes_insert)*100):.1f}% inseridos. Verifique erros acima.")

# ============================================================================
# ETAPA 4: INSERIR TELEFONES (tabela core.telefones separada)
# ============================================================================
print("\n" + "=" * 100)
print("ETAPA 4: INSERIR TELEFONES")
print("=" * 100)

print("\n[Preparando telefones para inserção...]")

# Primeiro, precisamos buscar os IDs dos clientes inseridos (mapear id_legado -> id uuid)
print("[Buscando mapeamento id_legado -> id...]")
try:
    clientes_map = {}
    offset = 0
    batch_size = 1000
    
    while True:
        response = retry_request(
            supabase.table('core.clientes').select('id, id_legado').range(offset, offset + batch_size - 1).execute
        )
        if not response.data:
            break
        for c in response.data:
            clientes_map[c['id_legado']] = c['id']
        offset += batch_size
        print(f"  Mapeados: {len(clientes_map)} clientes...", end='\r')
        time.sleep(0.2)  # Pequeno delay entre requests
    
    print(f"\n[OK] {len(clientes_map)} clientes mapeados")

except Exception as e:
    print(f"[ERRO] Falha no mapeamento: {e}")
    print("[PULANDO] Telefones não serão inseridos")
    clientes_map = {}

if clientes_map:
    # Preparar telefones para inserção
    telefones_insert = []
    
    for idx, row in df_clientes.iterrows():
        id_legado = str(row['id_cliente'])
        cliente_id = clientes_map.get(id_legado)
        
        if not cliente_id:
            continue
        
        # Telefone 1
        if row.get('telefone1'):
            tel1 = str(row['telefone1']).strip()
            if tel1 and tel1 != 'nan' and len(tel1) >= 10:
                telefones_insert.append({
                    'cliente_id': cliente_id,
                    'numero': tel1,
                    'tipo': 'CELULAR' if len(tel1) == 11 else 'FIXO',
                    'principal': True,
                    'ativo': True
                })
        
        # Telefone 2
        if row.get('telefone2'):
            tel2 = str(row['telefone2']).strip()
            if tel2 and tel2 != 'nan' and len(tel2) >= 10:
                telefones_insert.append({
                    'cliente_id': cliente_id,
                    'numero': tel2,
                    'tipo': 'CELULAR' if len(tel2) == 11 else 'FIXO',
                    'principal': False,
                    'ativo': True
                })
    
    print(f"\n[Preparados {len(telefones_insert)} telefones para inserção]")
    
    # Inserir em lotes com retry
    if telefones_insert:
        print(f"\n[Inserindo telefones em lotes de {BATCH_SIZE}...]")
        total_inserted = 0
        errors = 0
        
        for i in range(0, len(telefones_insert), BATCH_SIZE):
            batch = telefones_insert[i:i+BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1
            
            try:
                retry_request(supabase.table('core.telefones').insert(batch).execute)
                total_inserted += len(batch)
                print(f"  Lote {batch_num}: {total_inserted}/{len(telefones_insert)} ({(total_inserted/len(telefones_insert)*100):.1f}%)", end='\r')
                
                if i + BATCH_SIZE < len(telefones_insert):
                    time.sleep(DELAY_BETWEEN_BATCHES)
                    
            except Exception as e:
                errors += 1
                print(f"\n[ERRO] Batch {batch_num} falhou: {e}")
                if errors > 10:
                    break
                time.sleep(RETRY_DELAY * 2)
        
        print(f"\n[OK] Total inserido: {total_inserted} telefones")
else:
    print("\n[PULADO] Sem mapeamento de clientes, telefones não inseridos")

# ============================================================================
# ETAPA 5: VALIDAÇÃO
# ============================================================================
print("\n" + "=" * 100)
print("ETAPA 5: VALIDAÇÃO")
print("=" * 100)

print("\n[Contando registros inseridos...]")
try:
    count_clientes = supabase.table('core.clientes').select('*', count='exact').limit(0).execute()
    count_lojas = supabase.table('core.lojas').select('*', count='exact').limit(0).execute()
    count_telefones = supabase.table('core.telefones').select('*', count='exact').limit(0).execute()
    
    print(f"\n✓ core.clientes: {count_clientes.count} registros")
    print(f"✓ core.lojas: {count_lojas.count} registros")
    print(f"✓ core.telefones: {count_telefones.count} registros")
    
    # Validar com dados esperados
    esperado_clientes = len(df_clientes)
    esperado_lojas = len(lojas_data)
    
    if count_clientes.count >= esperado_clientes * 0.95:  # 95% de sucesso
        print(f"\n✅ Clientes: OK ({count_clientes.count}/{esperado_clientes})")
    else:
        print(f"\n⚠️  Clientes: ATENÇÃO ({count_clientes.count}/{esperado_clientes})")
    
    if count_lojas.count == esperado_lojas:
        print(f"✅ Lojas: OK ({count_lojas.count}/{esperado_lojas})")
    else:
        print(f"⚠️  Lojas: ATENÇÃO ({count_lojas.count}/{esperado_lojas})")
    
    if count_telefones.count > 0:
        print(f"✅ Telefones: OK ({count_telefones.count} registros)")
    else:
        print(f"⚠️  Telefones: Nenhum telefone inserido")

except Exception as e:
    print(f"[ERRO] Falha na validação: {e}")

print("\n" + "=" * 100)
print("PROCESSO CONCLUÍDO!")
print("=" * 100)
print("\n📋 PRÓXIMOS PASSOS:")
print("  1. Verificar registros no Supabase Table Editor")
print("  2. Popular vendas.vendas com os dados consolidados")
print("  3. Popular telefones se necessário")
print("  4. Validar integridade referencial")
