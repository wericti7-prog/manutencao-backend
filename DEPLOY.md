# Guia de Deploy — Sistema de Manutenção de TI

> Tempo estimado: 40–60 minutos seguindo este guia passo a passo.
> Custo: R$ 0 (todos os serviços têm plano gratuito suficiente para uso interno).

---

## Visão geral do que você vai criar

```
Navegadores dos técnicos
        │  HTTPS
        ▼
  Vercel (Frontend)          ← seus arquivos HTML/CSS/JS
        │  HTTPS + JSON
        ▼
  Railway (Backend API)      ← FastAPI Python
        │  SQL
        ▼
  Supabase (Banco de Dados)  ← PostgreSQL
```

---

## PARTE 1 — GitHub (repositório do código)

> O GitHub é onde o código fica guardado. Railway e Vercel vão buscar o código de lá automaticamente.

### 1.1 Criar conta no GitHub
1. Acesse **https://github.com** e clique em **Sign up**
2. Escolha um nome de usuário (ex: `reis-manutencao`) e crie a conta
3. Confirme o e-mail

### 1.2 Criar dois repositórios

**Repositório 1 — Backend:**
1. Clique em **New repository** (botão verde no topo)
2. Nome: `manutencao-backend`
3. Deixe **Private** marcado (código privado)
4. Clique em **Create repository**

**Repositório 2 — Frontend:**
1. Clique em **New repository** novamente
2. Nome: `manutencao-frontend`
3. Deixe **Private** marcado
4. Clique em **Create repository**

### 1.3 Enviar os arquivos para o GitHub

Abra o terminal (Prompt de Comando no Windows) e execute:

```bash
# ── Backend ──────────────────────────────────────────────
cd caminho/para/manutencao-ti/backend

git init
git add .
git commit -m "Backend inicial"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/manutencao-backend.git
git push -u origin main

# ── Frontend ─────────────────────────────────────────────
cd ../frontend

git init
git add .
git commit -m "Frontend inicial"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/manutencao-frontend.git
git push -u origin main
```

> Substitua `SEU-USUARIO` pelo seu nome de usuário do GitHub.
> O terminal vai pedir seu usuário e senha do GitHub na primeira vez.

---

## PARTE 2 — Supabase (banco de dados PostgreSQL)

### 2.1 Criar conta
1. Acesse **https://supabase.com** → **Start your project**
2. Entre com sua conta GitHub (mais fácil)

### 2.2 Criar o projeto
1. Clique em **New project**
2. **Name:** `manutencao-ti`
3. **Database Password:** crie uma senha forte e **ANOTE** — você vai precisar dela
   - Exemplo: `Reis@2024!TI#Seguro`
4. **Region:** South America (São Paulo) — mais rápido para o Brasil
5. Clique em **Create new project**
6. Aguarde ~2 minutos enquanto o banco sobe

### 2.3 Pegar a URL de conexão
1. No painel do Supabase, clique em **Settings** (ícone de engrenagem) → **Database**
2. Role até **Connection string** → selecione **URI**
3. Copie a string. Ela vai ter este formato:
   ```
   postgresql://postgres:[SUA-SENHA]@db.xxxxxxxxxxxx.supabase.co:5432/postgres
   ```
4. **Guarde essa string** — você vai precisar na Parte 3

---

## PARTE 3 — Railway (backend Python)

### 3.1 Criar conta
1. Acesse **https://railway.app** → **Login** → entre com GitHub

### 3.2 Criar o projeto
1. Clique em **New Project**
2. Escolha **Deploy from GitHub repo**
3. Selecione o repositório `manutencao-backend`
4. Railway vai detectar automaticamente que é Python e vai fazer o build

### 3.3 Configurar variáveis de ambiente
> **Importante:** nunca coloque senhas no código. Elas ficam aqui.

1. No painel do seu projeto, clique no serviço criado
2. Clique na aba **Variables**
3. Adicione estas variáveis clicando em **+ New Variable** para cada uma:

| Variável | Valor |
|---|---|
| `DATABASE_URL` | A string do Supabase que você copiou (com sua senha no lugar) |
| `SECRET_KEY` | Uma string aleatória longa — use: `openssl rand -hex 32` no terminal |
| `TOKEN_HOURS` | `8` |

> **Como gerar o SECRET_KEY sem o terminal:**
> Acesse https://www.uuidgenerator.net/version4 e gere 2 UUIDs, junte-os sem traços.
> Exemplo: `550e8400e29b41d4a716446655440000a987fbc9-4bea-4bca-af67-4be7ca79bd`

4. Clique em **Deploy** para o Railway subir com as novas variáveis

### 3.4 Pegar a URL do backend
1. Depois que o deploy terminar (ícone verde), clique em **Settings**
2. Em **Domains**, clique em **Generate Domain**
3. Você vai receber uma URL como: `manutencao-backend-production.up.railway.app`
4. **Guarde essa URL** — você vai precisar na Parte 4

### 3.5 Criar os usuários iniciais no banco

Com o backend rodando, abra o terminal e execute:

```bash
cd caminho/para/manutencao-ti/backend

# Instale as dependências localmente (só precisa fazer uma vez)
pip install -r requirements.txt

# Configure a variável DATABASE_URL temporariamente no terminal:
# Windows (CMD):
set DATABASE_URL=postgresql://postgres:SUA-SENHA@db.xxxx.supabase.co:5432/postgres

# Mac/Linux:
export DATABASE_URL=postgresql://postgres:SUA-SENHA@db.xxxx.supabase.co:5432/postgres

# Rode o seed para criar os usuários:
python seed.py
```

Você deve ver:
```
  Criado: weric (tecnico)
  Criado: jhean (tecnico)
  ...
  Criado: gerencia (gerencia)
Seed concluído.
```

> **Importante:** depois de rodar o seed, troque as senhas padrão pela interface
> de gerência do sistema assim que tudo estiver funcionando.

---

## PARTE 4 — Atualizar a URL da API no frontend

Antes de fazer o deploy do frontend, você precisa dizer a ele onde está o backend.

1. Abra o arquivo `frontend/api.js`
2. Encontre esta linha:
   ```javascript
   : "https://SEU-BACKEND.railway.app";   // ← troque após o deploy
   ```
3. Substitua pela URL real que o Railway gerou:
   ```javascript
   : "https://manutencao-backend-production.up.railway.app";
   ```
4. Salve o arquivo e envie para o GitHub:
   ```bash
   cd caminho/para/manutencao-ti/frontend
   git add api.js
   git commit -m "Aponta para backend Railway"
   git push
   ```

---

## PARTE 5 — Vercel (frontend)

### 5.1 Criar conta
1. Acesse **https://vercel.com** → **Sign Up** → entre com GitHub

### 5.2 Fazer o deploy
1. No painel da Vercel, clique em **Add New Project**
2. Clique em **Import** ao lado de `manutencao-frontend`
3. Em **Framework Preset**, selecione **Other**
4. **Root Directory:** deixe vazio (raiz do repositório)
5. Clique em **Deploy**
6. Aguarde ~1 minuto

### 5.3 Sua URL pública
Depois do deploy, a Vercel vai mostrar sua URL:
```
https://manutencao-frontend.vercel.app
```

Essa é a URL que você vai compartilhar com a equipe. 🎉

---

## PARTE 6 — Configurar CORS (segurança)

Agora que você tem a URL do frontend, configure o backend para aceitar
requisições **somente** do seu frontend (e não de qualquer site).

1. Abra `backend/main.py`
2. Encontre esta linha:
   ```python
   allow_origins=["*"],
   ```
3. Substitua pela sua URL do Vercel:
   ```python
   allow_origins=[
       "https://manutencao-frontend.vercel.app",
       "http://localhost:3000",   # para testes locais
   ],
   ```
4. Salve e envie para o GitHub:
   ```bash
   cd caminho/para/manutencao-ti/backend
   git add main.py
   git commit -m "CORS: restringe ao domínio do frontend"
   git push
   ```
5. O Railway vai detectar o push e refazer o deploy automaticamente

---

## PARTE 7 — Verificação final

Acesse sua URL do Vercel e teste:

- [ ] A tela de login aparece
- [ ] Login com `weric` / `weric123` funciona
- [ ] Login com senha errada mostra erro
- [ ] Criar uma manutenção aparece na lista
- [ ] Editar salva e aparece no histórico
- [ ] Finalizar pede Consertado / Sem Reparo
- [ ] Login com `gerencia` / `gerencia123` mostra a aba Usuários
- [ ] Criar um novo usuário funciona

---

## PARTE 8 — Trocar as senhas padrão

**Faça isso antes de compartilhar o link com a equipe.**

1. Acesse o sistema com a conta `gerencia`
2. Vá na aba **Usuários**
3. Delete cada técnico e recrie com senhas novas e pessoais
   - Ou peça que cada técnico acesse e você troca a senha deles pelo painel

---

## Manutenção futura

### Como atualizar o sistema
Sempre que você editar um arquivo e quiser publicar:
```bash
git add .
git commit -m "Descrição do que mudou"
git push
```
Railway e Vercel vão detectar automaticamente e fazer o novo deploy em ~2 minutos.

### Se o banco precisar ser reiniciado
No Supabase, vá em **SQL Editor** e cole:
```sql
DROP TABLE IF EXISTS edit_logs CASCADE;
DROP TABLE IF EXISTS manutencoes CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;
```
Depois rode `python seed.py` novamente.

### Limites do plano gratuito
| Serviço | Limite gratuito | Suficiente para? |
|---|---|---|
| Railway | 500h de execução/mês | Uso contínuo (24/7 cobre ~20 dias; desligue à noite se precisar) |
| Supabase | 500MB de banco, 50.000 rows | Vários anos de manutenções |
| Vercel | Ilimitado para sites estáticos | Sempre suficiente |

> **Dica Railway:** Se o plano gratuito não cobrir 24/7, o Railway tem um plano
> de ~US$ 5/mês (≈ R$ 28) que é mais que suficiente para uso interno.

---

## Problemas comuns

**"Cannot connect to database"**
→ Verifique se a variável `DATABASE_URL` no Railway está correta (com a senha certa do Supabase)

**"CORS error" no navegador**
→ Verifique se a URL do Vercel está listada em `allow_origins` no `main.py`

**"401 Unauthorized" em todas as requisições**
→ Verifique se `SECRET_KEY` no Railway é uma string longa e aleatória

**O seed falhou com "connection refused"**
→ Verifique se a `DATABASE_URL` está configurada corretamente no terminal antes de rodar `python seed.py`

**Login funciona mas não carrega dados**
→ Abra o DevTools (F12) → aba Network → veja qual requisição está falhando e o erro

---

## Estrutura final de arquivos

```
manutencao-ti/
├── backend/                  → sobe para o Railway
│   ├── main.py               API FastAPI (endpoints)
│   ├── models.py             tabelas do banco
│   ├── schemas.py            validação de dados
│   ├── crud.py               operações no banco
│   ├── auth.py               JWT + bcrypt
│   ├── database.py           conexão PostgreSQL
│   ├── seed.py               cria usuários iniciais
│   ├── requirements.txt      dependências Python
│   ├── railway.json          config de deploy
│   └── runtime.txt           versão do Python
│
└── frontend/                 → sobe para a Vercel
    ├── index.html            HTML do sistema
    ├── script.js             lógica da interface
    ├── api.js                chamadas à API
    ├── styles.css            estilos
    └── vercel.json           config de deploy
```
