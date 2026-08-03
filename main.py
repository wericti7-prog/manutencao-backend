from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import re, models, schemas, crud, auth
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Manutenção de TI", version="1.0.0")

# ─── Limite global de tamanho de requisição (110 MB com margem para base64) ───
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    MAX_BODY = 110 * 1024 * 1024  # 110 MB (margem sobre os 100 MB do arquivo)
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_BODY:
        return JSONResponse(
            status_code=413,
            content={"detail": f"Requisição muito grande. Limite: 100 MB por arquivo."}
        )
    return await call_next(request)

# ─── Rate Limiting ─────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=[])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── CORS — aceita qualquer origem ────────────────────────────────────────────
def _cors_headers(origin: str) -> dict:
    return {
        "Access-Control-Allow-Origin":      origin,
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods":     "GET,POST,PUT,DELETE,OPTIONS,PATCH",
        "Access-Control-Allow-Headers":     "Authorization,Content-Type,Accept",
        "Access-Control-Max-Age":           "3600",
    }

@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    origin = request.headers.get("origin", "")
    if request.method == "OPTIONS":
        return Response(status_code=200, headers=_cors_headers(origin) if origin else {})
    response = await call_next(request)
    if origin:
        for k, v in _cors_headers(origin).items():
            response.headers[k] = v
    return response

# ─── Keep-Alive / Health check ───────────────────────────────────────────────
@app.get("/ping")
def ping():
    return {"status": "ok"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ─── Dependência: usuário logado ───────────────────────────────────────────────
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = auth.decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    user = crud.get_user_by_username(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user

# ─── Auth ──────────────────────────────────────────────────────────────────────
@app.post("/auth/login", response_model=schemas.Token)
@limiter.limit("5/minute")
def login(request: Request, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")
    crud.registrar_acesso(db, user)
    token = auth.create_token({"sub": user.username, "nome": user.nome, "role": user.role})
    return {"access_token": token, "token_type": "bearer",
            "nome": user.nome, "username": user.username, "role": user.role}

@app.get("/auth/me", response_model=schemas.UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user

# ─── Usuários ──────────────────────────────────────────────────────────────────
def require_gerencia(current_user=Depends(get_current_user)):
    if current_user.role not in ("gerencia", "admin"):
        raise HTTPException(status_code=403, detail="Acesso restrito à gerência")
    return current_user

def require_tecnico_ou_gerencia(current_user=Depends(get_current_user)):
    if current_user.role not in ("tecnico", "gerencia", "admin"):
        raise HTTPException(status_code=403, detail="Acesso restrito a técnicos e gerência")
    return current_user

@app.get("/usuarios", response_model=list[schemas.UserOut])
def listar_usuarios(db: Session = Depends(get_db), _=Depends(require_gerencia)):
    return crud.get_all_users(db)

@app.post("/usuarios", response_model=schemas.UserOut, status_code=201)
def criar_usuario(data: schemas.UserCreate, db: Session = Depends(get_db), _=Depends(require_gerencia)):
    if crud.get_user_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="Usuário já existe")
    return crud.create_user(db, data)

@app.get("/usuarios/{user_id}/acessos", response_model=list[schemas.LogAcessoOut])
def historico_acessos(user_id: int, db: Session = Depends(get_db), _=Depends(require_gerencia)):
    return crud.get_log_acessos(db, user_id)

@app.put("/usuarios/{user_id}", response_model=schemas.UserOut)
def editar_usuario(user_id: int, data: schemas.UserUpdate, db: Session = Depends(get_db), _=Depends(require_gerencia)):
    user = crud.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@app.delete("/usuarios/{user_id}", status_code=204)
def remover_usuario(user_id: int, db: Session = Depends(get_db), _=Depends(require_gerencia)):
    if not crud.delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

# ─── Manutenções ───────────────────────────────────────────────────────────────
@app.get("/manutencoes", response_model=list[schemas.ManutencaoOut])
def listar(
    status: Optional[str] = None,
    localizacao: Optional[str] = None,
    busca: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    return crud.get_manutencoes(db, status=status, localizacao=localizacao, busca=busca)

@app.post("/manutencoes", response_model=schemas.ManutencaoOut, status_code=201)
def criar(data: schemas.ManutencaoCreate, db: Session = Depends(get_db),
          current_user=Depends(get_current_user)):
    return crud.create_manutencao(db, data, criado_por=current_user.nome)

@app.get("/manutencoes/{id}", response_model=schemas.ManutencaoOut)
def detalhe(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    m = crud.get_manutencao(db, id)
    if not m:
        raise HTTPException(status_code=404, detail="Não encontrado")
    return m

@app.put("/manutencoes/{id}", response_model=schemas.ManutencaoOut)
def editar(id: int, data: schemas.ManutencaoUpdate, db: Session = Depends(get_db),
           current_user=Depends(get_current_user)):
    m = crud.update_manutencao(db, id, data, editado_por=current_user.nome)
    if not m:
        raise HTTPException(status_code=404, detail="Não encontrado")
    return m

@app.delete("/manutencoes/{id}", status_code=204)
def excluir(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if not crud.delete_manutencao(db, id, deletado_por=current_user.nome):
        raise HTTPException(status_code=404, detail="Não encontrado")

@app.post("/manutencoes/{id}/reabrir", response_model=schemas.ManutencaoOut)
def reabrir(id: int, data: schemas.ReopenRequest, db: Session = Depends(get_db),
            current_user=Depends(require_gerencia)):
    m = crud.reabrir_manutencao(db, id, data.status, reaberto_por=current_user.nome)
    if not m:
        raise HTTPException(status_code=404, detail="Não encontrado")
    return m

@app.get("/lixeira", response_model=list[schemas.ManutencaoOut])
def listar_lixeira(db: Session = Depends(get_db), _=Depends(require_gerencia)):
    return crud.get_lixeira(db)

@app.post("/lixeira/{id}/restaurar", response_model=schemas.ManutencaoOut)
def restaurar(id: int, db: Session = Depends(get_db), current_user=Depends(require_gerencia)):
    m = crud.restaurar_manutencao(db, id, restaurado_por=current_user.nome)
    if not m:
        raise HTTPException(status_code=404, detail="Não encontrado ou não está na lixeira")
    return m

@app.post("/manutencoes/{id}/finalizar", response_model=schemas.ManutencaoOut)
def finalizar(id: int, data: schemas.FinalizarRequest, db: Session = Depends(get_db),
              current_user=Depends(get_current_user)):
    m = crud.finalizar_manutencao(db, id, data, finalizado_por=current_user.nome)
    if not m:
        raise HTTPException(status_code=404, detail="Não encontrado")
    return m

@app.get("/manutencoes/{id}/historico", response_model=list[schemas.EditLogOut])
def historico(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return crud.get_historico(db, id)

@app.get("/equipamentos/sugestoes")
def sugestoes(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return crud.get_equipamentos_usados(db)

# ─── Anexos ────────────────────────────────────────────────────────────────────
@app.get("/manutencoes/{id}/anexos", response_model=list[schemas.AnexoOut])
def listar_anexos(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return crud.get_anexos(db, id)

@app.post("/manutencoes/{id}/anexos", response_model=schemas.AnexoOut, status_code=201)
def adicionar_anexo(id: int, data: schemas.AnexoCreate,
                    db: Session = Depends(get_db), _=Depends(get_current_user)):
    if not crud.get_manutencao(db, id):
        raise HTTPException(status_code=404, detail="Manutenção não encontrada")
    return crud.create_anexo(db, id, data)

@app.delete("/manutencoes/{id}/anexos/{anexo_id}", status_code=204)
def remover_anexo(id: int, anexo_id: int,
                  db: Session = Depends(get_db), _=Depends(get_current_user)):
    if not crud.delete_anexo(db, id, anexo_id):
        raise HTTPException(status_code=404, detail="Anexo não encontrado")

# ─── Respostas ────────────────────────────────────────────────────────────────
@app.get("/manutencoes/{id}/respostas", response_model=list[schemas.RespostaOut])
def listar_respostas(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if not crud.get_manutencao(db, id):
        raise HTTPException(status_code=404, detail="Manutenção não encontrada")
    return crud.get_respostas(db, id)

@app.post("/manutencoes/{id}/respostas", response_model=schemas.RespostaOut, status_code=201)
def criar_resposta(id: int, data: schemas.RespostaCreate,
                   db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):
    # Todos os perfis podem enviar mensagens no chat do equipamento
    if not crud.get_manutencao(db, id):
        raise HTTPException(status_code=404, detail="Manutenção não encontrada")
    if not data.texto and not data.anexos:
        raise HTTPException(status_code=400, detail="Envie um texto ou anexo.")
    return crud.create_resposta(db, id, data, autor=current_user.nome, role=current_user.role)

# ─── Aguardando Coleta ──────────────────────────────────────────────────────────
@app.get("/aguardando-coleta", response_model=list[schemas.AguardandoColetaOut])
def listar_aguardando_coleta(db: Session = Depends(get_db), _=Depends(require_tecnico_ou_gerencia)):
    return crud.get_aguardando_coleta(db)

@app.post("/aguardando-coleta", response_model=schemas.AguardandoColetaOut, status_code=201)
def criar_aguardando_coleta(data: schemas.AguardandoColetaCreate, db: Session = Depends(get_db),
                            current_user=Depends(require_tecnico_ou_gerencia)):
    return crud.create_aguardando_coleta(db, data, criado_por=current_user.nome)

@app.delete("/aguardando-coleta/{id}", status_code=204)
def remover_aguardando_coleta(id: int, db: Session = Depends(get_db), _=Depends(require_tecnico_ou_gerencia)):
    if not crud.delete_aguardando_coleta(db, id):
        raise HTTPException(status_code=404, detail="Não encontrado")

@app.post("/aguardando-coleta/{id}/enviar", response_model=schemas.ManutencaoOut, status_code=201)
def enviar_para_manutencao(id: int, db: Session = Depends(get_db),
                           current_user=Depends(require_tecnico_ou_gerencia)):
    item = crud.get_aguardando_coleta_by_id(db, id)
    if not item:
        raise HTTPException(status_code=404, detail="Não encontrado")
    dados = schemas.ManutencaoCreate(
        equipamento=item.equipamento,
        localizacao=item.localizacao,
        tecnico=current_user.nome,
        status="Em Manutenção",
        problema="Equipamento coletado da sala de aguardando coleta para manutenção.",
    )
    m = crud.create_manutencao(db, dados, criado_por=current_user.nome)
    crud.delete_aguardando_coleta(db, id)
    return m

# ─── Chat Global (Suprimentos ↔ Manutenção) ────────────────────────────────────
CHAT_ROLES = {"observador", "manutencao", "gerencia", "admin", "tecnico"}

@app.get("/chat", response_model=list[schemas.ChatMensagemOut])
def listar_chat(desde_id: int = 0, db: Session = Depends(get_db),
                _=Depends(get_current_user)):
    return crud.get_chat_mensagens(db, desde_id=desde_id)

@app.post("/chat", response_model=schemas.ChatMensagemOut, status_code=201)
def enviar_chat(data: schemas.ChatMensagemCreate,
                db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    if not data.texto and not data.anexos:
        raise HTTPException(status_code=400, detail="Envie um texto ou anexo.")
    return crud.create_chat_mensagem(db, data, autor=current_user.nome, role=current_user.role)
