from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False, index=True)
    cpf = Column(String(14), unique=True, index=True)
    telefone = Column(String(20))
    email = Column(String(255))
    endereco = Column(Text)
    data_nascimento = Column(DateTime)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ativo = Column(Boolean, default=True)
    
    # Relacionamentos
    ordens_servico = relationship("OrdemServico", back_populates="cliente")
    dioptrias = relationship("Dioptria", back_populates="cliente")

class OrdemServico(Base):
    __tablename__ = "ordens_servico"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_os = Column(String(50), unique=True, nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    data_compra = Column(DateTime, nullable=False)
    data_entrega = Column(DateTime)
    valor_total = Column(Float)
    status = Column(String(50), default="pendente")  # pendente, em_producao, pronto, entregue
    observacoes = Column(Text)
    loja = Column(String(100))
    vendedor = Column(String(255))
    data_criacao = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="ordens_servico")
    dioptrias = relationship("Dioptria", back_populates="ordem_servico")

class Dioptria(Base):
    __tablename__ = "dioptrias"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    ordem_servico_id = Column(Integer, ForeignKey("ordens_servico.id"))
    
    # Olho Direito
    od_esferico = Column(Float)
    od_cilindrico = Column(Float)
    od_eixo = Column(Integer)
    od_adicao = Column(Float)
    
    # Olho Esquerdo
    oe_esferico = Column(Float)
    oe_cilindrico = Column(Float)
    oe_eixo = Column(Integer)
    oe_adicao = Column(Float)
    
    # Distância Pupilar
    dp = Column(Float)
    
    # Tipo de lente
    tipo_lente = Column(String(100))  # monofocal, bifocal, multifocal, etc.
    material_lente = Column(String(100))  # cr39, policarbonato, etc.
    tratamento = Column(String(255))  # antirreflexo, blue_light, etc.
    
    data_receita = Column(DateTime)
    medico = Column(String(255))
    data_criacao = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    cliente = relationship("Cliente", back_populates="dioptrias")
    ordem_servico = relationship("OrdemServico", back_populates="dioptrias")

class ClienteDuplicado(Base):
    __tablename__ = "clientes_duplicados"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_principal_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    cliente_duplicado_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    similaridade = Column(Float)  # Score de similaridade
    status = Column(String(50), default="pendente")  # pendente, confirmado, rejeitado
    metodo_deteccao = Column(String(100))  # nome, cpf, telefone, etc.
    data_deteccao = Column(DateTime, default=datetime.utcnow)
    data_resolucao = Column(DateTime)
    
class LogProcessamento(Base):
    __tablename__ = "logs_processamento"
    
    id = Column(Integer, primary_key=True, index=True)
    arquivo_nome = Column(String(255), nullable=False)
    arquivo_tamanho = Column(Integer)
    linhas_processadas = Column(Integer)
    linhas_erro = Column(Integer)
    clientes_novos = Column(Integer)
    clientes_atualizados = Column(Integer)
    duplicatas_detectadas = Column(Integer)
    tempo_processamento = Column(Float)
    status = Column(String(50))  # sucesso, erro, parcial
    erro_detalhes = Column(Text)
    data_processamento = Column(DateTime, default=datetime.utcnow)