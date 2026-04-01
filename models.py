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

    historico = relationship("EditLog", back_populates="manutencao",
                             cascade="all, delete-orphan", order_by="EditLog.id")

class EditLog(Base):
    __tablename__ = "edit_logs"

    id             = Column(Integer, primary_key=True, index=True)
    manutencao_id  = Column(Integer, ForeignKey("manutencoes.id"), nullable=False)
    ts             = Column(DateTime(timezone=True), server_default=func.now())
    editado_por    = Column(String(100))
    motivo         = Column(String(200), default="Edição manual")
    snapshot       = Column(JSON)                         # estado ANTES da edição

    manutencao = relationship("Manutencao", back_populates="historico")
