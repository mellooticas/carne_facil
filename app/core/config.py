# Configurações do Sistema de Gestão de Óticas

import os
from pathlib import Path

# Diretórios do projeto
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXPORTS_DIR = DATA_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"

# Criar diretórios se não existirem
for dir_path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, EXPORTS_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Configurações de banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./oticas.db")

# Configurações de processamento
EXCEL_EXTENSIONS = [".xlsx", ".xls"]
MAX_FILE_SIZE_MB = 50
CHUNK_SIZE = 1000

# Configurações de deduplicação
SIMILARITY_THRESHOLD_HIGH = 0.9
SIMILARITY_THRESHOLD_MEDIUM = 0.75
DEDUP_WEIGHTS = {
    "nome": 0.4,
    "cpf": 0.3,
    "telefone": 0.2,
    "endereco": 0.1
}

# Configurações de logging
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
LOG_RETENTION = "30 days"

# Padrões de arquivo
OS_FILE_PATTERN = "OS_NOVA*.xlsx"
BACKUP_PREFIX = "backup_"

# Validações
CPF_REQUIRED = False
TELEFONE_REQUIRED = True
ENDERECO_REQUIRED = False

# Configurações da aplicação web
APP_HOST = "0.0.0.0"
APP_PORT = 8000
DEBUG_MODE = True

# Diretórios externos (configuráveis)
LOJAS_BASE_DIR = os.getenv("LOJAS_DIR", r"D:\OneDrive - Óticas Taty Mello\LOJAS")
LOJAS = [
    "PERUS",
    # Adicionar outras lojas conforme necessário
]

# Mapeamento de colunas padrão
COLUMN_MAPPING = {
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

# Ranges válidos para dioptrias
DIOPTRIA_RANGES = {
    'esferico': (-20.0, 20.0),
    'cilindrico': (-10.0, 10.0),
    'eixo': (0, 180),
    'adicao': (0.25, 3.5),
    'dp': (45.0, 85.0)
}

# Status válidos para OS
STATUS_OS_VALIDOS = [
    'pendente',
    'em_producao',
    'pronto',
    'entregue',
    'cancelado'
]

# Tipos de lente válidos
TIPOS_LENTE_VALIDOS = [
    'monofocal',
    'bifocal',
    'multifocal',
    'progressiva',
    'antireflex',
    'transitions'
]

# Configurações de backup
BACKUP_ENABLED = True
BACKUP_FREQUENCY_HOURS = 24
MAX_BACKUPS = 30