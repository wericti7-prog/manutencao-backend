import os

# Carrega .env apenas se disponível (desenvolvimento local)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DATABASE_URL = os.getenv("DATABASE_URL")
print("DATABASE_URL:", DATABASE_URL)

"""
Execute UMA VEZ para criar os usuários iniciais:
    python seed.py
"""
from database import SessionLocal, engine
import models, auth

models.Base.metadata.create_all(bind=engine)

USUARIOS_INICIAIS = [
    {"username": "weric",       "nome": "Weric",       "senha": "weric@123",      "role": "tecnico"},
    {"username": "jhean",       "nome": "Jhean",       "senha": "jhean@123",      "role": "tecnico"},
    {"username": "paulo",       "nome": "Paulo",       "senha": "paulo@123",      "role": "tecnico"},
    {"username": "lucas",       "nome": "Lucas",       "senha": "lucas@123",      "role": "tecnico"},
    {"username": "volney",      "nome": "Volney",      "senha": "volney@123",     "role": "tecnico"},
    {"username": "wendel",      "nome": "Wendel",      "senha": "wendel@123",     "role": "tecnico"},
    {"username": "suprimentos", "nome": "Suprimentos", "senha": "suprimentos2411","role": "observador"},
    {"username": "infotech",    "nome": "Infotech",    "senha": "infotech2026",   "role": "manutencao"},
    {"username": "gerencia",    "nome": "Gerência",    "senha": "gerencia@67",    "role": "gerencia"},
]

db = SessionLocal()

for u in USUARIOS_INICIAIS:
    user = db.query(models.Usuario).filter(models.Usuario.username == u["username"]).first()

    if user:
        user.senha_hash = auth.hash_password(u["senha"])
        user.nome = u["nome"]
        user.role = u["role"]
        print(f"  Atualizado: {u['username']}")
    else:
        novo = models.Usuario(
            username=u["username"],
            nome=u["nome"],
            senha_hash=auth.hash_password(u["senha"]),
            role=u["role"],
        )
        db.add(novo)
        print(f"  Criado: {u['username']}")

db.commit()
db.close()
print("\nSeed concluído.")
