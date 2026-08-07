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
    role         = Column(String(20), default="tecnico")   # tecnico | gerencia | admin
    criado_em    = Column(DateTime(timezone=True), server_default=func.now())
    ultimo_acesso = Column(DateTime(timezone=True), nullable=True)

    log_acessos = relationship("LogAcesso", back_populates="usuario",
                               cascade="all, delete-orphan", order_by="LogAcesso.id.desc()")

class LogAcesso(Base):
    __tablename__ = "log_acessos"

    id         = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    acessado_em = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", back_populates="log_acessos")

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
    substituto         = Column(String(300), nullable=True)   # equipamento substituto enviado
    data_inicio        = Column(DateTime(timezone=True))
    data_fim           = Column(DateTime(timezone=True))
    prazo              = Column(DateTime(timezone=True), nullable=True)   # prazo esperado de conclusão
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

class AguardandoColeta(Base):
    __tablename__ = "aguardando_coleta"

    id          = Column(Integer, primary_key=True, index=True)
    equipamento = Column(String(200), nullable=False)
    localizacao = Column(String(100))              # ex: Loja 001
    criado_por  = Column(String(100))
    criado_em   = Column(DateTime(timezone=True), server_default=func.now())

class ChatMensagem(Base):
    __tablename__ = "chat_mensagens"

    id        = Column(Integer, primary_key=True, index=True)
    autor     = Column(String(100), nullable=False)
    role      = Column(String(20),  nullable=False)
    texto     = Column(Text,        nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    anexos    = relationship("ChatAnexo", back_populates="mensagem",
                             cascade="all, delete-orphan", order_by="ChatAnexo.id")

class ChatAnexo(Base):
    __tablename__ = "chat_anexos"

    id          = Column(Integer, primary_key=True, index=True)
    mensagem_id = Column(Integer, ForeignKey("chat_mensagens.id", ondelete="CASCADE"), nullable=False)
    nome        = Column(String(300), nullable=False)
    tipo        = Column(String(100), nullable=False)
    tamanho     = Column(Integer,     nullable=False)
    data        = Column(String(20),  nullable=False)
    base64      = Column(Text,        nullable=False)
    criado_em   = Column(DateTime(timezone=True), server_default=func.now())

    mensagem = relationship("ChatMensagem", back_populates="anexos")

class EstoqueItem(Base):
    __tablename__ = "estoque_itens"

    id             = Column(Integer, primary_key=True, index=True)
    nome           = Column(String(200), nullable=False, index=True)
    categoria      = Column(String(100), nullable=True)
    unidade        = Column(String(20), default="un")
    quantidade     = Column(Integer, default=0)
    estoque_minimo = Column(Integer, default=0)
    criado_por     = Column(String(100))
    criado_em      = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em  = Column(DateTime(timezone=True), onupdate=func.now())

    movimentos = relationship("EstoqueMovimento", back_populates="item",
                              cascade="all, delete-orphan", order_by="EstoqueMovimento.id.desc()")

class EstoqueMovimento(Base):
    __tablename__ = "estoque_movimentos"

    id         = Column(Integer, primary_key=True, index=True)
    item_id    = Column(Integer, ForeignKey("estoque_itens.id", ondelete="CASCADE"), nullable=False)
    tipo       = Column(String(10), nullable=False)     # entrada | saida
    quantidade = Column(Integer, nullable=False)
    motivo     = Column(String(300), nullable=True)
    usuario    = Column(String(100), nullable=False)
    criado_em  = Column(DateTime(timezone=True), server_default=func.now())

    item = relationship("EstoqueItem", back_populates="movimentos")
