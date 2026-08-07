from pydantic import BaseModel, Field, validator
from typing import Optional, Any
from datetime import datetime

MAX_ANEXO_BYTES = 100 * 1024 * 1024  # 100 MB

def _validar_base64(v: str) -> str:
    tamanho_real = len(v) * 3 // 4
    if tamanho_real > MAX_ANEXO_BYTES:
        mb = tamanho_real // (1024 * 1024)
        raise ValueError(f"Arquivo excede o limite de 100 MB ({mb} MB enviado)")
    return v

# ─── Auth ──────────────────────────────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str
    nome: str
    username: str
    role: str

# ─── Usuário ───────────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    username:  str = Field(..., min_length=3, max_length=50)
    nome:      str = Field(..., min_length=2, max_length=100)
    senha:     str = Field(..., min_length=6)
    role:      str = Field("tecnico", pattern="^(tecnico|manutencao|observador|gerencia|admin)$")

class LogAcessoOut(BaseModel):
    id:          int
    acessado_em: Optional[datetime]
    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id:            int
    username:      str
    nome:          str
    role:          str
    criado_em:     Optional[datetime]
    ultimo_acesso: Optional[datetime]

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    nome:     Optional[str] = None
    username: Optional[str] = None
    senha:    Optional[str] = None
    role:     Optional[str] = None

# ─── Manutenção ────────────────────────────────────────────────────────────────
class ManutencaoCreate(BaseModel):
    equipamento:  str = Field(..., min_length=1)
    localizacao:  Optional[str] = None
    tecnico:      Optional[str] = None
    status:       str = Field("Pendente")
    problema:     str = Field(..., min_length=1)
    solucao:      Optional[str] = None
    custo:        float = 0
    pecas:        Optional[str] = None
    substituto:   Optional[str] = None
    prazo:        Optional[datetime] = None
    data_inicio:  Optional[datetime] = None
    data_fim:     Optional[datetime] = None

class ManutencaoUpdate(BaseModel):
    equipamento:  Optional[str] = None
    localizacao:  Optional[str] = None
    tecnico:      Optional[str] = None
    status:       Optional[str] = None
    problema:     Optional[str] = None
    solucao:      Optional[str] = None
    custo:        Optional[float] = None
    pecas:        Optional[str] = None
    substituto:   Optional[str] = None
    prazo:        Optional[datetime] = None
    data_inicio:  Optional[datetime] = None
    data_fim:     Optional[datetime] = None

class FinalizarRequest(BaseModel):
    resultado_reparo:   str = Field(..., pattern="^(Consertado|Sem Reparo)$")
    status_equipamento: Optional[str] = None
    solucao:            Optional[str] = None
    custo:              Optional[float] = None
    pecas:              Optional[str] = None

class ManutencaoOut(BaseModel):
    id:                 int
    numero:             str
    equipamento:        str
    localizacao:        Optional[str]
    tecnico:            Optional[str]
    status:             str
    status_equipamento: Optional[str]
    resultado_reparo:   Optional[str]
    problema:           Optional[str]
    solucao:            Optional[str]
    custo:              float
    pecas:              Optional[str]
    substituto:         Optional[str]
    data_inicio:        Optional[datetime]
    data_fim:           Optional[datetime]
    prazo:              Optional[datetime]
    criado_por:         Optional[str]
    criado_em:          Optional[datetime]
    atualizado_em:      Optional[datetime]
    deletado_em:        Optional[datetime]
    deletado_por:       Optional[str]

    class Config:
        from_attributes = True

class ReopenRequest(BaseModel):
    status: str = Field("Em Manutenção")

# ─── Anexos ────────────────────────────────────────────────────────────────────
class AnexoCreate(BaseModel):
    nome:    str
    tipo:    str
    tamanho: int
    data:    str
    base64:  str
    @validator("base64")
    def validar_tamanho(cls, v):
        return _validar_base64(v)


class AnexoOut(BaseModel):
    id:      int
    nome:    str
    tipo:    str
    tamanho: int
    data:    str
    base64:  str

    class Config:
        from_attributes = True

# ─── Respostas ─────────────────────────────────────────────────────────────────
class AnexoRespostaCreate(BaseModel):
    nome:    str
    tipo:    str
    tamanho: int
    data:    str
    base64:  str
    @validator("base64")
    def validar_tamanho(cls, v):
        return _validar_base64(v)


class AnexoRespostaOut(BaseModel):
    id:      int
    nome:    str
    tipo:    str
    tamanho: int
    data:    str
    base64:  str

    class Config:
        from_attributes = True

class RespostaCreate(BaseModel):
    texto:  Optional[str] = None
    anexos: list[AnexoRespostaCreate] = []

class RespostaOut(BaseModel):
    id:         int
    autor:      str
    role:       str
    texto:      Optional[str]
    criado_em:  Optional[datetime]
    anexos_resposta: list[AnexoRespostaOut] = []

    class Config:
        from_attributes = True

# ─── Log de edições ────────────────────────────────────────────────────────────
class EditLogOut(BaseModel):
    id:           int
    ts:           Optional[datetime]
    editado_por:  Optional[str]
    motivo:       Optional[str]
    snapshot:     Optional[Any]

    class Config:
        from_attributes = True

# ─── Aguardando Coleta ─────────────────────────────────────────────────────────
class AguardandoColetaCreate(BaseModel):
    equipamento: str = Field(..., min_length=1)
    localizacao: Optional[str] = None

class AguardandoColetaOut(BaseModel):
    id:          int
    equipamento: str
    localizacao: Optional[str]
    criado_por:  Optional[str]
    criado_em:   Optional[datetime]

    class Config:
        from_attributes = True

# ─── Chat Global ───────────────────────────────────────────────────────────────
class ChatAnexoCreate(BaseModel):
    nome:    str
    tipo:    str
    tamanho: int
    data:    str
    base64:  str
    @validator("base64")
    def validar_tamanho(cls, v):
        return _validar_base64(v)


class ChatAnexoOut(BaseModel):
    id:      int
    nome:    str
    tipo:    str
    tamanho: int
    data:    str
    base64:  str
    class Config:
        from_attributes = True

class ChatMensagemCreate(BaseModel):
    texto:  Optional[str] = None
    anexos: list[ChatAnexoCreate] = []

class ChatMensagemOut(BaseModel):
    id:        int
    autor:     str
    role:      str
    texto:     Optional[str]
    criado_em: Optional[datetime]
    anexos:    list[ChatAnexoOut] = []
    class Config:
        from_attributes = True

# ─── Estoque ───────────────────────────────────────────────────────────────────
class EstoqueItemCreate(BaseModel):
    nome:           str = Field(..., min_length=1, max_length=200)
    categoria:      Optional[str] = None
    unidade:        str = Field("un", max_length=20)
    quantidade:     int = Field(0, ge=0)
    estoque_minimo: int = Field(0, ge=0)

class EstoqueItemUpdate(BaseModel):
    nome:           Optional[str] = None
    categoria:      Optional[str] = None
    unidade:        Optional[str] = None
    estoque_minimo: Optional[int] = None

class EstoqueItemOut(BaseModel):
    id:             int
    nome:           str
    categoria:      Optional[str]
    unidade:        str
    quantidade:     int
    estoque_minimo: int
    criado_por:     Optional[str]
    criado_em:      Optional[datetime]
    atualizado_em:  Optional[datetime]

    class Config:
        from_attributes = True

class EstoqueMovimentoCreate(BaseModel):
    tipo:       str = Field(..., pattern="^(entrada|saida)$")
    quantidade: int = Field(..., gt=0)
    motivo:     Optional[str] = None

class EstoqueMovimentoOut(BaseModel):
    id:         int
    tipo:       str
    quantidade: int
    motivo:     Optional[str]
    usuario:    str
    criado_em:  Optional[datetime]

    class Config:
        from_attributes = True
