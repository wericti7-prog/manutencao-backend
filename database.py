from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# A URL vem SEMPRE da variável de ambiente configurada no Railway
# Nunca coloque a senha diretamente no código
DATABASE_URL = os.environ.get("DATABASE_URL", "")

if not DATABASE_URL:
    raise RuntimeError(
        "Variável DATABASE_URL não configurada. "
        "Configure-a nas variáveis de ambiente do Railway."
    )

# Supabase pooler usa "postgres://" — SQLAlchemy precisa de "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgres://"):]

print("Conectando em:", DATABASE_URL.split("@")[-1])  # mostra host sem expor a senha

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
