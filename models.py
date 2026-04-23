from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id         = Column(Integer, primary_key=True, index=True)
    username   = Column(String(50), unique=True, nullable=False, index=True)
    nome       = Column(String(100), nullable=False)
    senha_hash = Column(String(200), nullable=False)
    role       = Column(String(20), default="tecnico")   # tecnico | gerencia | admin
    criado_em  = Column(DateTime(timezone=True), server_default=func.now())

class Manutencao(Base):
    __tablename__ = "manutencoes"

    id                 = Column(Integer, primary_key=True, index=True)
    numero             = Column(String(10), unique=True, nullable=False, index=True)
    equipamento        = Column(String(200), nullable=False)
    localizacao        = Column(String(100))              # ex: Loja 001
    tecnico            = Column(String(100))
    status             = Column(String(50), default="Pendente")
    status_equipamento = Column(String(50))               # salvo na finalização
    resultado_reparo   = Column(String(50))               # Consertado | Sem Reparo
    problema           = Column(Text)
    solucao            = Column(Text)
    custo              = Column(Float, default=0)
    pecas              = Column(String(300))
    data_inicio        = Column(DateTime(timezone=True))
    data_fim           = Column(DateTime(timezone=True))
    criado_por         = Column(String(100))
    criado_em          = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em      = Column(DateTime(timezone=True), onupdate=func.now())
    deletado_em        = Column(DateTime(timezone=True), nullable=True)   # soft delete
    deletado_por       = Column(String(100), nullable=True)

    historico = relationship("EditLog", back_populates="manutencao",
                             cascade="all, delete-orphan", order_by="EditLog.id")
    anexos    = relationship("Anexo", back_populates="manutencao",
                             cascade="all, delete-orphan", order_by="Anexo.id")
    respostas = relationship("Resposta", back_populates="manutencao",
                             cascade="all, delete-orphan", order_by="Resposta.id")

class EditLog(Base):
    __tablename__ = "edit_logs"

    id             = Column(Integer, primary_key=True, index=True)
    manutencao_id  = Column(Integer, ForeignKey("manutencoes.id"), nullable=False)
    ts             = Column(DateTime(timezone=True), server_default=func.now())
    editado_por    = Column(String(100))
    motivo         = Column(String(200), default="Edição manual")
    snapshot       = Column(JSON)                         # estado ANTES da edição

    manutencao = relationship("Manutencao", back_populates="historico")

class Anexo(Base):
    __tablename__ = "anexos"

    id            = Column(Integer, primary_key=True, index=True)
    manutencao_id = Column(Integer, ForeignKey("manutencoes.id", ondelete="CASCADE"), nullable=False)
    nome          = Column(String(300), nullable=False)
    tipo          = Column(String(100), nullable=False)
    tamanho       = Column(Integer, nullable=False)
    data          = Column(String(20), nullable=False)
    base64        = Column(Text, nullable=False)
    criado_em     = Column(DateTime(timezone=True), server_default=func.now())

    manutencao = relationship("Manutencao", back_populates="anexos")

class Resposta(Base):
    __tablename__ = "respostas"

    id            = Column(Integer, primary_key=True, index=True)
    manutencao_id = Column(Integer, ForeignKey("manutencoes.id", ondelete="CASCADE"), nullable=False)
    autor         = Column(String(100), nullable=False)   # nome do usuário
    role          = Column(String(20), nullable=False)    # role do autor
    texto         = Column(Text, nullable=True)
    criado_em     = Column(DateTime(timezone=True), server_default=func.now())

    manutencao = relationship("Manutencao", back_populates="respostas")
    anexos_resposta = relationship("AnexoResposta", back_populates="resposta",
                                   cascade="all, delete-orphan", order_by="AnexoResposta.id")

class AnexoResposta(Base):
    __tablename__ = "anexos_resposta"

    id          = Column(Integer, primary_key=True, index=True)
    resposta_id = Column(Integer, ForeignKey("respostas.id", ondelete="CASCADE"), nullable=False)
    nome        = Column(String(300), nullable=False)
    tipo        = Column(String(100), nullable=False)
    tamanho     = Column(Integer, nullable=False)
    data        = Column(String(20), nullable=False)
    base64      = Column(Text, nullable=False)
    criado_em   = Column(DateTime(timezone=True), server_default=func.now())

    resposta = relationship("Resposta", back_populates="anexos_resposta")
