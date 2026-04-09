from dotenv import load_dotenv
import os

load_dotenv()

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
    {"username": "weric",   "nome": "Weric",   "senha": "weric123",  "role": "tecnico"},
    {"username": "jhean",   "nome": "Jhean",   "senha": "jhean123",  "role": "tecnico"},
    {"username": "paulo",   "nome": "Paulo",   "senha": "paulo123",  "role": "tecnico"},
    {"username": "lucas",   "nome": "Lucas",   "senha": "lucas123",  "role": "tecnico"},
    {"username": "volney",  "nome": "Volney",  "senha": "volney123", "role": "tecnico"},
    {"username": "wendel",  "nome": "Wendel",  "senha": "wendel123", "role": "tecnico"},
    # Conta de gerência — TROQUE A SENHA antes de usar em produção
    {"username": "gerencia", "nome": "Gerência", "senha": "gerencia123", "role": "gerencia"},
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
