import psycopg2
from sqlalchemy import create_engine

urls = {
    "Pooler (padrão)": "postgresql://postgres.ezhzkxitwocrouohtsax:Reis2411789567@aws-1-sa-east-1.pooler.supabase.com:5432/postgres",
    "Sem pooler (direto)": "postgresql://postgres.ezhzkxitwocrouohtsax:Reis2411789567@db.ezhzkxitwocrouohtsax.supabase.co:5432/postgres",
    "Pooler (porta 6543)": "postgresql://postgres.ezhzkxitwocrouohtsax:Reis2411789567@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"
}

for nome, url in urls.items():
    print(f"\n🔍 Testando: {nome}")
    print(f"   URL: {url[:80]}...")
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            result = conn.execute("SELECT current_user, version()")
            user, version = result.fetchone()
            print(f"   ✅ SUCESSO! Usuário: {user}")
            print(f"   📦 Versão: {version[:60]}...")
            break
    except Exception as e:
        error_msg = str(e)
        if "Tenant or user not found" in error_msg:
            print("   ❌ Tenant/usuário não encontrado - verifique se o projeto está ativo")
        elif "password authentication failed" in error_msg:
            print("   ❌ Senha incorreta")
        else:
            print(f"   ❌ Erro: {error_msg[:100]}")