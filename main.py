from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import models, schemas, crud, auth
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Manutenção de TI", version="1.0.0")

# ─── CORS ─────────────────────────────────────────────────────────────────────
# IMPORTANTE: allow_origins=["*"] NÃO funciona com allow_credentials=True.
# Liste aqui TODAS as URLs do seu frontend (produção e testes locais).
# A URL de produção da Vercel é a mais curta — sem hashes no meio.
# Exemplo: https://manutencao-frontend-nu.vercel.app
#
# Se o login continuar bloqueado, abra o DevTools (F12) → Console e veja
# qual URL está sendo bloqueada, depois adicione ela aqui.
ALLOWED_ORIGINS = [
    "https://manutencao-frontend-5rho02ke7-manutencao-ti.vercel.app",  # ← URL atual do Vercel
    "https://manutencao-frontend-nu.vercel.app",
    "https://manutencao-frontend.vercel.app",
    "https://manutencao-frontend-8jlws4i46-manutencao-ti.vercel.app",
    "http://localhost:3000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")
    token = auth.create_token({"sub": user.username, "nome": user.nome, "role": user.role})
    return {"access_token": token, "token_type": "bearer",
            "nome": user.nome, "username": user.username, "role": user.role}

@app.get("/auth/me", response_model=schemas.UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user

# ─── Usuários (somente gerência) ───────────────────────────────────────────────
def require_gerencia(current_user=Depends(get_current_user)):
    if current_user.role not in ("gerencia", "admin"):
        raise HTTPException(status_code=403, detail="Acesso restrito à gerência")
    return current_user

@app.get("/usuarios", response_model=list[schemas.UserOut])
def listar_usuarios(db: Session = Depends(get_db), _=Depends(require_gerencia)):
    return crud.get_all_users(db)

@app.post("/usuarios", response_model=schemas.UserOut, status_code=201)
def criar_usuario(data: schemas.UserCreate, db: Session = Depends(get_db), _=Depends(require_gerencia)):
    if crud.get_user_by_username(db, data.username):
        raise HTTPException(status_code=400, detail="Usuário já existe")
    return crud.create_user(db, data)

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
def excluir(id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    if not crud.delete_manutencao(db, id):
        raise HTTPException(status_code=404, detail="Não encontrado")

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
