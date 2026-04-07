from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Em produção esta variável vem do Railway/Render (nunca coloque a senha no código)
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres.ezhzkxitwocrouohtsax:Reis2411789567@aws-1-sa-east-1.pooler.supabase.com:5432/postgres"
)

# Correção necessária para o Supabase/Railway (usam postgres:// mas SQLAlchemy precisa postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
