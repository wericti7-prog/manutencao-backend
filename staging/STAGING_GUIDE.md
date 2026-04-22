# 🚧 Guia de Staging — Sistema de Manutenção de TI

Documento completo para configurar, usar e manter o ambiente de homologação.

---

## Estrutura de pastas

```
projeto/
│
├── index.html          ← Produção (site oficial)
├── script.js           ← Produção
├── styles.css          ← Produção
├── api.js              ← Produção (aponta para Railway produção)
├── tests.html          ← Painel de testes automatizados
├── promote.py          ← Script de promoção staging → produção
│
├── staging/            ← Homologação (pasta separada)
│   ├── index.html      ← Cópia com banner laranja
│   ├── script.js       ← Cópia (import aponta para api.js local)
│   ├── styles.css      ← Tema laranja (importa ../styles.css)
│   └── api.js          ← ⚠️ Aponta para backend de STAGING
│
└── _backups/           ← Criado automaticamente pelo promote.py
    └── 20250120_143022/
        ├── index.html
        ├── script.js
        ├── styles.css
        └── BACKUP_INFO.txt
```

---

## Passo 1 — Criar o backend de staging no Railway

O frontend de staging precisa de um backend separado para não tocar nos dados reais.

1. Acesse [railway.app](https://railway.app) → abra seu projeto
2. Clique em **"+ New Service"** → **"GitHub Repo"**
3. Selecione o mesmo repositório do backend de produção
4. Dê um nome diferente, por exemplo: **`manutencao-staging`**
5. Na aba **Variables**, copie todas as variáveis de produção, **exceto** `DATABASE_URL`
6. Adicione um banco novo:
   - Clique em **"+ New Service"** → **"Database"** → **PostgreSQL**
   - Copie a `DATABASE_URL` gerada e cole no serviço de staging
7. Aguarde o deploy. Copie a URL gerada (ex: `https://manutencao-staging.up.railway.app`)

> **Por que banco separado?**  
> Para que dados de teste (criados durante a homologação) nunca apareçam em produção.

---

## Passo 2 — Configurar o api.js de staging

Abra `staging/api.js` e edite a linha:

```js
const STAGING_URL = "https://SEU-BACKEND-STAGING.up.railway.app"; // ← altere aqui
```

Substitua pela URL do serviço de staging criado no Passo 1.

---

## Passo 3 — Hospedar o staging (duas opções)

### Opção A — Subpasta no mesmo servidor (mais simples)

Se você serve os arquivos estáticos via nginx, Apache ou Netlify:

```
site/
├── index.html          → acessível em: meusite.com/
└── staging/
    ├── index.html      → acessível em: meusite.com/staging/
    ├── script.js
    ├── styles.css
    └── api.js
```

Acesse o staging em: **`meusite.com/staging/`**

### Opção B — Subdomínio separado

Configure um subdomínio `staging.meusite.com` apontando para a pasta `staging/`.

Com Netlify:
1. Crie um segundo site em Netlify
2. Faça upload (ou conecte via Git) apenas da pasta `staging/`
3. Configure o domínio personalizado `staging.meusite.com`

### Opção C — Localmente (para testes rápidos)

```bash
# Rode na raiz do projeto
python3 -m http.server 3000

# Acesse:
# Produção: http://localhost:3000/
# Staging:  http://localhost:3000/staging/
```

---

## Workflow diário

### Ciclo completo de uma atualização

```
┌─────────────────────────────────────────────────────────────┐
│  1. Você faz alterações em  staging/script.js  ou outros   │
│                                                             │
│  2. Abre o staging no navegador e testa manualmente        │
│     → meusite.com/staging/                                 │
│                                                             │
│  3. Roda o painel de testes automatizados                  │
│     → meusite.com/tests.html  (selecione backend staging)  │
│                                                             │
│  4. Tudo OK? Promove para produção:                        │
│     → python promote.py                                    │
│                                                             │
│  5. Algo deu errado? Rollback com:                         │
│     → python promote.py --rollback                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Script de promoção (promote.py)

O script cuida de tudo: compara arquivos, faz backup automático e copia para produção.

### Uso normal (interativo)

```bash
python promote.py
```

Mostra quais arquivos foram alterados e pede confirmação antes de qualquer ação.

### Simular sem alterar nada

```bash
python promote.py --dry-run
```

Útil para ver o que seria alterado sem risco algum.

### Promover sem perguntar (CI/CD ou scripts)

```bash
python promote.py --force
```

### Desfazer a última promoção (rollback)

```bash
python promote.py --rollback
```

Lista todos os backups disponíveis e restaura o escolhido.

### Exemplo de saída

```
═══════════════════════════════════════════════════════
  Promoção Staging → Produção
═══════════════════════════════════════════════════════

  ℹ  Comparando staging com produção:
  ────────────────────────────────────────────────────
  📄 script.js  [ALTERADO]
     Staging   →  hash:a3f9c1d2e4b5  tamanho:28.4 KB
     Produção  →  hash:f7b2a8c3d1e6  tamanho:27.9 KB

  ℹ  styles.css: sem alterações (hash idêntico)
  ────────────────────────────────────────────────────

  Promover 2 arquivo(s) para produção? [s/N]: s

  ℹ  Criando backup dos arquivos de produção atual...
  ✔  Backup: script.js → _backups/20250120_143022/
  ✔  Backup: styles.css → _backups/20250120_143022/

  ℹ  Copiando arquivos...
  ✔  staging/script.js  →  script.js  (28.4 KB)
  ✔  staging/styles.css →  styles.css (12.1 KB)

  ✅ Promoção concluída com sucesso!
```

---

## Regras importantes

| Arquivo | Produção | Staging | Promovido pelo script? |
|---|---|---|---|
| `index.html` | ✅ | ✅ | ✅ Sim |
| `script.js` | ✅ | ✅ | ✅ Sim |
| `styles.css` | ✅ | ✅ | ✅ Sim |
| `api.js` | ✅ Produção | ✅ Staging | ❌ **Nunca** (cada um aponta para seu backend) |
| `tests.html` | Opcional | Opcional | Manual |

> **`api.js` nunca é promovido automaticamente.** Cada ambiente tem o seu, com URL e prefixo de localStorage diferentes. Isso garante que os ambientes nunca se misturem.

---

## Diferenças visuais entre os ambientes

| Elemento | Produção | Staging |
|---|---|---|
| Faixa no topo | Nenhuma | 🚧 Banner laranja pulsante |
| Cor do header | Azul | Âmbar/laranja |
| Cor dos botões | Azul | Laranja |
| Título da aba | "Sistema de Manutenção" | "[STAGING] Sistema de Manutenção" |
| LocalStorage | `jwt_token` | `stg_jwt_token` |

---

## Dúvidas frequentes

**Posso usar o mesmo usuário nos dois ambientes?**  
Não necessariamente — o banco de dados é diferente. Você precisará criar os usuários no backend de staging também (via API ou painel do Railway).

**As senhas são as mesmas?**  
Só se você configurar as mesmas no banco de staging. Recomenda-se usar senhas iguais para facilitar os testes.

**O localStorage mistura dados dos dois ambientes?**  
Não — o `api.js` de staging usa o prefixo `stg_` em todas as chaves (`stg_jwt_token`, `stg_usuario_logado`), então nunca conflita com produção mesmo no mesmo navegador.

**Posso rodar os dois ao mesmo tempo?**  
Sim. Abra produção em uma aba e staging em outra. As sessões são independentes.

**Preciso do Python para o promote.py?**  
Sim, Python 3.8+. Verifique com `python3 --version`. Não é necessário instalar nada além disso — o script usa apenas a biblioteca padrão.
