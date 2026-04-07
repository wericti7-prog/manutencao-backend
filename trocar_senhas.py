"""
Execute para trocar as senhas dos usuários:
    python trocar_senhas.py
"""
from database import SessionLocal, engine
import models, auth

db = SessionLocal()

usuarios = db.query(models.Usuario).order_by(models.Usuario.nome).all()

if not usuarios:
    print("Nenhum usuário encontrado. Rode seed.py primeiro.")
    db.close()
    exit()

print("=" * 45)
print("  Troca de senhas — Sistema de Manutenção TI")
print("=" * 45)
print("Deixe em branco e pressione Enter para PULAR.\n")

for u in usuarios:
    print(f"Usuário: {u.nome} ({u.username}) [{u.role}]")
    nova = input("  Nova senha (mín. 6 caracteres): ").strip()

    if not nova:
        print("  → Pulado.\n")
        continue

    if len(nova) < 6:
        print("  ✗ Senha muito curta. Pulado.\n")
        continue

    u.senha_hash = auth.hash_password(nova)
    db.commit()
    print(f"  ✓ Senha de {u.nome} atualizada.\n")

db.close()
print("Concluído.")
