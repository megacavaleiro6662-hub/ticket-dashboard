# 🎫 CAOS Ticket Dashboard

Sistema completo de gerenciamento de tickets para Discord com dashboard web profissional.

## ✨ Funcionalidades

### 🎨 Dashboard Web
- ✅ **Login seguro** com Discord OAuth2
- ✅ **Estatísticas em tempo real** de tickets
- ✅ **Gráficos interativos** (Chart.js)
- ✅ **Gerenciamento completo** de tickets
- ✅ **Sistema de notificações** em tempo real (WebSocket)

### 🏷️ Sistema de Categorias
- ✅ **Criar categorias personalizadas** de tickets
- ✅ **Configurar canais de destino** para cada categoria
- ✅ **Definir permissões** por cargo
- ✅ **Mensagens automáticas** personalizadas
- ✅ **Templates de nome** de canal

### 🎨 Editor de Painéis
- ✅ **Editor visual** drag-and-drop
- ✅ **Preview ao vivo** do painel
- ✅ **Múltiplos tipos** (Botões, Dropdown)
- ✅ **Personalização completa** de cores e textos
- ✅ **Envio direto** para Discord

### 💬 Gerenciamento de Tickets
- ✅ **Ver todos os tickets** (abertos/fechados)
- ✅ **Histórico completo** de mensagens
- ✅ **Responder pelo dashboard**
- ✅ **Fechar tickets** remotamente
- ✅ **Exportar transcrições**
- ✅ **Sistema de prioridades**

---

## 📦 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/ticket-dashboard.git
cd ticket-dashboard
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e configure:

```env
DISCORD_CLIENT_ID=seu_client_id
DISCORD_CLIENT_SECRET=seu_client_secret
DISCORD_REDIRECT_URI=http://localhost:5000/callback
DISCORD_TOKEN=seu_bot_token
GUILD_ID=id_do_seu_servidor
SECRET_KEY=chave_secreta_aleatoria
```

### 4. Crie uma aplicação Discord

1. Acesse: https://discord.com/developers/applications
2. Clique em **"New Application"**
3. Nomeie sua aplicação (ex: "CAOS Ticket Dashboard")
4. Vá em **OAuth2 → General**
5. Adicione a Redirect URL: `http://localhost:5000/callback`
6. Copie o **Client ID** e **Client Secret** para o `.env`

### 5. Configure os cargos permitidos

Edite o arquivo `app.py` e configure os IDs dos cargos que podem acessar:

```python
ALLOWED_ROLES = [
    1365630916939710545,  # Admin
    1365630919552749598,  # Staff
    # Adicione mais IDs aqui
]
```

### 6. Execute o dashboard

```bash
python app.py
```

Acesse: http://localhost:5000

---

## 🚀 Deploy no Render.com

### 1. Crie um Web Service no Render

1. Acesse: https://dashboard.render.com
2. Clique em **"New +" → "Web Service"**
3. Conecte seu repositório GitHub
4. Configure:
   - **Name:** ticket-dashboard
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`

### 2. Configure as variáveis de ambiente

No Render, vá em **Environment** e adicione:

```
DISCORD_CLIENT_ID=...
DISCORD_CLIENT_SECRET=...
DISCORD_REDIRECT_URI=https://seu-app.onrender.com/callback
DISCORD_TOKEN=...
GUILD_ID=...
SECRET_KEY=...
PORT=10000
DEBUG=False
```

### 3. Atualize a Redirect URI no Discord

1. Volte no Discord Developer Portal
2. Vá em **OAuth2 → General**
3. Adicione: `https://seu-app.onrender.com/callback`

### 4. Deploy!

Clique em **"Create Web Service"** e aguarde o deploy.

---

## 🔧 Uso

### Como criar uma categoria

1. Acesse o dashboard
2. Vá em **🏷️ Categorias**
3. Clique em **"➕ Nova Categoria"**
4. Preencha:
   - Nome (ex: "Carrinho de Compras")
   - Emoji (ex: 🛒)
   - Descrição
   - ID da categoria do Discord onde os tickets serão criados
   - Template do nome do canal (ex: `🛒-carrinho-{username}`)
   - Cargos permitidos (IDs separados por vírgula)
   - Mensagem inicial
5. Clique em **"💾 Salvar Categoria"**

### Como criar um painel

1. Vá em **🎨 Painéis**
2. Clique em **"➕ Novo Painel"**
3. Configure:
   - Nome do painel
   - ID do canal onde o painel será enviado
   - Título e descrição do embed
   - Cor
   - Selecione as categorias que aparecerão
4. Veja o **Preview Ao Vivo** do lado esquerdo
5. Clique em **"💾 Salvar"** ou **"📤 Enviar para Discord"**

### Como gerenciar tickets

1. Vá em **📊 Dashboard**
2. Veja estatísticas e gráficos
3. Lista de tickets ativos aparece abaixo
4. Clique em **"Ver Ticket"** para:
   - Ver histórico de mensagens
   - Responder
   - Fechar ticket
   - Exportar transcrição

---

## 🔌 Integração com o Bot Discord

### Webhook para criar tickets

O dashboard se comunica com o bot via API. Configure o webhook no bot:

```python
# No seu bot Discord (caosbot_railway.py)
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/webhook/ticket', methods=['POST'])
def create_ticket_webhook():
    data = request.json
    # Processar criação de ticket
    # ...
    return jsonify({'success': True})
```

---

## 📊 Banco de Dados

O dashboard usa **SQLite** por padrão. Os dados são armazenados em `tickets.db`.

### Tabelas:
- `categories` - Categorias de tickets
- `panels` - Painéis configurados
- `tickets` - Tickets criados
- `ticket_messages` - Mensagens dos tickets
- `settings` - Configurações gerais

Para produção, considere migrar para **PostgreSQL** (disponível grátis no Render).

---

## 🎨 Personalização

### Cores

Edite `templates/*.html` e altere as classes do Tailwind CSS.

### Logo

Substitua o emoji 🎫 pelo logo da sua escolha em:
- `templates/login.html`
- `templates/dashboard.html`
- etc.

---

## 🐛 Troubleshooting

### Erro: "Access Denied"

- Verifique se os IDs dos cargos em `ALLOWED_ROLES` estão corretos
- Certifique-se que o usuário tem pelo menos um dos cargos configurados

### Erro: "Redirect URI mismatch"

- Verifique se a `DISCORD_REDIRECT_URI` no `.env` está igual à configurada no Discord Developer Portal

### WebSocket não conecta

- Verifique se a porta está correta
- Em produção, use HTTPS (obrigatório para WebSocket seguro)

---

## 📝 Licença

MIT License - Sinta-se livre para usar e modificar!

---

## 💡 Suporte

Dúvidas? Entre em contato:
- Discord: Seu servidor aqui
- Email: seu@email.com

---

## 🎉 Créditos

Desenvolvido por **CAOS Hub** com ❤️

**Stack:**
- Flask (Backend)
- Tailwind CSS (Design)
- Chart.js (Gráficos)
- Socket.IO (Tempo Real)
- Discord.py (Bot)

---

**Versão:** 1.0.0
**Data:** 2025-10-05
