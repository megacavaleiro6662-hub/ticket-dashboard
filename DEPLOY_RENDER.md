# 🚀 DEPLOY NO RENDER.COM - Guia Completo

## 📋 Pré-requisitos

- ✅ Conta GitHub
- ✅ Conta Render.com (grátis)
- ✅ Discord Application configurada

---

## 🔧 Passo 1: Preparar Repositório GitHub

### 1.1 Criar repositório

```bash
cd ticket-dashboard
git init
git add .
git commit -m "Initial commit - CAOS Ticket Dashboard"
```

### 1.2 Criar no GitHub

1. Acesse: https://github.com/new
2. Nome: `ticket-dashboard`
3. Público ou Privado (sua escolha)
4. Não adicione README, .gitignore ou license
5. Clique em **"Create repository"**

### 1.3 Push para GitHub

```bash
git remote add origin https://github.com/SEU_USUARIO/ticket-dashboard.git
git branch -M main
git push -u origin main
```

---

## 🌐 Passo 2: Deploy no Render

### 2.1 Criar Web Service

1. Acesse: https://dashboard.render.com
2. Clique em **"New +"** → **"Web Service"**
3. Clique em **"Connect a repository"**
4. Conecte sua conta GitHub (se ainda não conectou)
5. Selecione o repositório `ticket-dashboard`
6. Clique em **"Connect"**

### 2.2 Configurar o Service

Preencha os campos:

```
Name: caos-ticket-dashboard
Region: Oregon (US West) ou Frankfurt (Europe Central)
Branch: main
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: python app.py
Instance Type: Free
```

### 2.3 Configurar Environment Variables

Clique em **"Advanced"** → **"Add Environment Variable"**

Adicione todas estas variáveis:

| Key | Value |
|-----|-------|
| `DISCORD_CLIENT_ID` | Seu Client ID do Discord |
| `DISCORD_CLIENT_SECRET` | Seu Client Secret do Discord |
| `DISCORD_REDIRECT_URI` | `https://seu-app.onrender.com/callback` |
| `DISCORD_TOKEN` | Token do bot Discord |
| `GUILD_ID` | ID do seu servidor Discord |
| `SECRET_KEY` | Clique em "Generate" |
| `PORT` | `10000` |
| `DEBUG` | `False` |

**⚠️ IMPORTANTE:** 
- A `DISCORD_REDIRECT_URI` deve usar a URL do seu app no Render
- Você pode usar o placeholder `https://caos-ticket-dashboard.onrender.com/callback` e atualizar depois
- Clique em **"Generate"** para `SECRET_KEY` (gera automaticamente)

### 2.4 Deploy!

1. Clique em **"Create Web Service"**
2. Aguarde 5-10 minutos para o primeiro deploy

---

## 🔄 Passo 3: Atualizar Discord Application

### 3.1 Pegar URL do Render

Após o deploy, você verá a URL do seu app:
```
https://caos-ticket-dashboard.onrender.com
```

### 3.2 Atualizar Redirect URI

1. Acesse: https://discord.com/developers/applications
2. Selecione sua aplicação
3. Menu → **OAuth2** → **General**
4. Em **Redirects**, adicione:
   ```
   https://caos-ticket-dashboard.onrender.com/callback
   ```
5. Clique em **"Save Changes"**

### 3.3 Atualizar Environment Variable

1. Volte no Render Dashboard
2. Seu service → **Environment**
3. Edite `DISCORD_REDIRECT_URI`:
   ```
   https://caos-ticket-dashboard.onrender.com/callback
   ```
4. Salve (vai fazer redeploy automático)

---

## ✅ Passo 4: Testar

### 4.1 Acessar Dashboard

Abra: `https://caos-ticket-dashboard.onrender.com`

### 4.2 Fazer Login

1. Clique em **"Entrar com Discord"**
2. Autorize a aplicação
3. Você deve ser redirecionado para o dashboard!

### 4.3 Verificar Acesso

Se ver erro **"Acesso Negado"**:
- ✅ Verifique se você tem um dos cargos em `ALLOWED_ROLES`
- ✅ Edite `app.py` e adicione seus IDs de cargo
- ✅ Faça commit e push (Render redeploy automaticamente)

---

## 🔧 Passo 5: Configurar ALLOWED_ROLES

### 5.1 Editar app.py localmente

```python
# Linha 22-27 em app.py
ALLOWED_ROLES = [
    1234567890,  # Substitua pelo ID do seu cargo Admin
    9876543210,  # Substitua pelo ID do seu cargo Staff
    # Adicione mais IDs aqui
]
```

### 5.2 Commit e Push

```bash
git add app.py
git commit -m "Update ALLOWED_ROLES with correct IDs"
git push
```

Render fará redeploy automaticamente em 2-3 minutos.

---

## 📊 Passo 6: Configurar Database (Opcional)

Por padrão, usa SQLite (arquivo local). Para produção, recomenda-se PostgreSQL.

### 6.1 Criar PostgreSQL no Render

1. Render Dashboard → **"New +"** → **"PostgreSQL"**
2. Nome: `ticket-dashboard-db`
3. Database: `tickets`
4. User: `tickets_user`
5. Region: Mesma do Web Service
6. Clique em **"Create Database"**

### 6.2 Atualizar app.py

Instale psycopg2:
```bash
pip install psycopg2-binary
echo "psycopg2-binary==2.9.9" >> requirements.txt
```

Edite `app.py` para usar PostgreSQL (código fornecido em documentação separada).

---

## 🎉 Deploy Completo!

Seu dashboard está rodando em:
```
https://caos-ticket-dashboard.onrender.com
```

### Funcionalidades Disponíveis:

- ✅ Login com Discord OAuth2
- ✅ Dashboard com estatísticas
- ✅ Gerenciamento de categorias
- ✅ Editor de painéis visual
- ✅ WebSocket para tempo real
- ✅ Sistema completo de tickets

---

## 🔄 Atualizações Futuras

Para atualizar o dashboard:

```bash
# Faça suas alterações
git add .
git commit -m "Descrição das mudanças"
git push
```

Render fará redeploy automaticamente!

---

## 🐛 Troubleshooting

### Deploy falhou
- ✅ Verifique os logs no Render Dashboard
- ✅ Certifique-se que `requirements.txt` está correto
- ✅ Verifique se todas env vars estão configuradas

### Site não carrega
- ✅ Aguarde 2-3 minutos após deploy
- ✅ Render free tier pode dormir (primeiro acesso demora ~30s)
- ✅ Verifique logs de erro

### "Redirect URI mismatch"
- ✅ Certifique-se que URI no Discord = URI no Render env var
- ✅ Sem barra "/" no final
- ✅ HTTPS obrigatório em produção

### "Access Denied"
- ✅ Adicione seus IDs de cargo em `ALLOWED_ROLES`
- ✅ Commit, push e aguarde redeploy

---

## 📞 Suporte

Problemas? Verifique:
- Logs do Render
- Console do navegador (F12)
- Network requests

---

**Versão:** 1.0.0
**Plataforma:** Render.com
**Custo:** GRÁTIS (750 horas/mês)
