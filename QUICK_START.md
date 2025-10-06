# 🚀 QUICK START - CAOS Ticket Dashboard

## ⚡ Início Rápido (5 minutos)

### 1. Configure o Discord

**a) Crie uma aplicação Discord:**
1. Acesse: https://discord.com/developers/applications
2. Clique em **"New Application"**
3. Nome: `CAOS Ticket Dashboard`
4. Clique em **"Create"**

**b) Configure OAuth2:**
1. Menu lateral → **OAuth2 → General**
2. **Redirects:**
   - Adicione: `http://localhost:5000/callback`
3. **Copie:**
   - Client ID
   - Client Secret (clique em "Reset Secret" se necessário)

**c) Obtenha o Bot Token:**
1. Menu lateral → **Bot**
2. Clique em **"Reset Token"**
3. Copie o token

**d) Pegue os IDs necessários:**
1. Ative o **Developer Mode** no Discord:
   - Discord → Configurações → Avançado → Modo Desenvolvedor
2. **ID do Servidor:**
   - Clique com botão direito no servidor → "Copiar ID"
3. **IDs dos Cargos:**
   - Servidor → Configurações → Cargos → Clique direito no cargo → "Copiar ID"

---

### 2. Configure o Dashboard

**a) Copie o arquivo de ambiente:**
```bash
cp .env.example .env
```

**b) Edite o `.env`:**
```env
DISCORD_CLIENT_ID=SEU_CLIENT_ID_AQUI
DISCORD_CLIENT_SECRET=SEU_CLIENT_SECRET_AQUI
DISCORD_REDIRECT_URI=http://localhost:5000/callback
DISCORD_TOKEN=SEU_BOT_TOKEN_AQUI
GUILD_ID=ID_DO_SEU_SERVIDOR
SECRET_KEY=qualquer_texto_aleatorio_longo_aqui
PORT=5000
DEBUG=True
```

**c) Edite `app.py` (linha 22-27):**
```python
ALLOWED_ROLES = [
    1234567890,  # Seu cargo Admin (substitua pelo ID real)
    9876543210,  # Seu cargo Staff (substitua pelo ID real)
]
```

---

### 3. Instale e Execute

**a) Instale as dependências:**
```bash
pip install -r requirements.txt
```

**b) Execute o dashboard:**
```bash
python app.py
```

**c) Acesse:**
```
http://localhost:5000
```

---

### 4. Primeiro Login

1. Clique em **"Entrar com Discord"**
2. Autorize a aplicação
3. Você será redirecionado para o dashboard!

---

## 🎯 Próximos Passos

### Criar sua primeira categoria:

1. Dashboard → **🏷️ Categorias**
2. Clique em **"➕ Nova Categoria"**
3. Preencha:
   ```
   Nome: Suporte
   Emoji: 🔧
   Descrição: Precisa de ajuda?
   Categoria Discord ID: [ID da categoria onde tickets serão criados]
   Template: 🔧-suporte-{username}
   ```
4. Salve!

### Criar seu primeiro painel:

1. Dashboard → **🎨 Painéis**
2. Clique em **"➕ Novo Painel"**
3. Configure:
   ```
   Nome: Sistema de Tickets
   Canal ID: [ID do canal onde o painel aparecerá]
   Título: 📋 Abrir Ticket
   Descrição: Selecione uma categoria:
   ```
4. Selecione as categorias que criou
5. Veja o **Preview** ao vivo!
6. Clique em **"💾 Salvar"**

---

## ❓ Problemas Comuns

### "Access Denied"
- ✅ Verifique se os IDs em `ALLOWED_ROLES` estão corretos
- ✅ Certifique-se que você tem um dos cargos no servidor

### "Redirect URI mismatch"
- ✅ Verifique se a URI no `.env` está igual à do Discord Developer Portal
- ✅ Formato correto: `http://localhost:5000/callback` (sem barra no final)

### "Invalid Client"
- ✅ Verifique se `DISCORD_CLIENT_ID` e `DISCORD_CLIENT_SECRET` estão corretos
- ✅ Tente resetar o Client Secret no Discord

### Bot não aparece
- ✅ Certifique-se que o bot está adicionado ao servidor
- ✅ Link de convite: `https://discord.com/api/oauth2/authorize?client_id=SEU_CLIENT_ID&permissions=8&scope=bot`

---

## 🎉 Tudo Funcionando!

Agora você pode:
- ✅ Criar categorias de tickets
- ✅ Configurar painéis visuais
- ✅ Gerenciar tickets pelo dashboard
- ✅ Ver estatísticas em tempo real

**Próximo:** Veja o `README.md` para funcionalidades avançadas e deploy em produção!

---

## 📞 Suporte

Problemas? Entre em contato no Discord do CAOS Hub!
