# =====================================================
# CAOS TICKET DASHBOARD - Backend Principal
# Sistema completo de gerenciamento de tickets
# =====================================================

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import os
import json
import requests
from datetime import datetime, timedelta
from functools import wraps
import sqlite3
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # Sessão expira em 1 hora
CORS(app)

# =====================================================
# CONFIGURAÇÕES DISCORD OAUTH2
# =====================================================
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', '')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET', '')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'http://localhost:5000/callback')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_TOKEN', '')

DISCORD_API_URL = 'https://discord.com/api/v10'
OAUTH2_URL = f'{DISCORD_API_URL}/oauth2/authorize'
TOKEN_URL = f'{DISCORD_API_URL}/oauth2/token'

# IDs dos cargos permitidos (apenas staff para cima)
ALLOWED_ROLES = [
    1365636960651051069,  # 🔥 Founder (mais alto)
    1365636456386789437,  # 🌟 Sub-Dono
    1365633918593794079,  # 👑 Administrador
    1365634226254254150,  # 🛠️ Staff
]

GUILD_ID = os.getenv('GUILD_ID', '1365510151884378214')

# =====================================================
# BANCO DE DADOS
# =====================================================
def init_db():
    """Inicializa o banco de dados SQLite"""
    conn = sqlite3.connect('tickets.db')
    c = conn.cursor()
    
    # Tabela de categorias de tickets
    c.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        emoji TEXT,
        description TEXT,
        channel_category_id TEXT,
        channel_name_template TEXT,
        allowed_roles TEXT,
        mention_role_id TEXT,
        initial_message TEXT,
        buttons_config TEXT,
        color TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Tabela de painéis de tickets
    c.execute('''CREATE TABLE IF NOT EXISTS panels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        title TEXT,
        description TEXT,
        color TEXT,
        image_url TEXT,
        thumbnail_url TEXT,
        footer TEXT,
        channel_id TEXT,
        message_id TEXT,
        panel_type TEXT,
        categories TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Tabela de tickets ativos
    c.execute('''CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_number INTEGER UNIQUE,
        user_id TEXT NOT NULL,
        username TEXT,
        category_id INTEGER,
        channel_id TEXT,
        status TEXT DEFAULT 'open',
        priority TEXT DEFAULT 'normal',
        assigned_to TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        closed_at TIMESTAMP,
        messages_count INTEGER DEFAULT 0,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )''')
    
    # Tabela de mensagens do ticket
    c.execute('''CREATE TABLE IF NOT EXISTS ticket_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INTEGER,
        user_id TEXT,
        username TEXT,
        content TEXT,
        attachments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ticket_id) REFERENCES tickets(id)
    )''')
    
    # Tabela de configurações gerais
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    
    conn.commit()
    conn.close()
    print("✅ Banco de dados inicializado!")

# =====================================================
# DECORADORES DE AUTENTICAÇÃO
# =====================================================
def login_required(f):
    """Requer que o usuário esteja logado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    """Requer que o usuário seja staff"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        
        user_roles = session.get('user', {}).get('roles', [])
        if not any(role in ALLOWED_ROLES for role in user_roles):
            return jsonify({'error': 'Acesso negado - Apenas staff'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# =====================================================
# ROTAS DE AUTENTICAÇÃO
# =====================================================
@app.route('/')
def index():
    """Página inicial - redireciona para dashboard ou login"""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    """Página de login com Discord OAuth2"""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    
    oauth_url = f"{OAUTH2_URL}?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify%20guilds%20guilds.members.read"
    return render_template('login.html', oauth_url=oauth_url)

@app.route('/callback')
def callback():
    """Callback do Discord OAuth2"""
    code = request.args.get('code')
    if not code:
        return "Erro: Código não fornecido", 400
    
    # Trocar código por token
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post(TOKEN_URL, data=data, headers=headers)
    
    if r.status_code != 200:
        return f"Erro ao obter token: {r.text}", 400
    
    token_data = r.json()
    access_token = token_data['access_token']
    
    # Obter informações do usuário
    headers = {'Authorization': f"Bearer {access_token}"}
    user_response = requests.get(f'{DISCORD_API_URL}/users/@me', headers=headers)
    
    if user_response.status_code != 200:
        return "Erro ao obter dados do usuário", 400
    
    user_data = user_response.json()
    
    # Obter cargos do usuário no servidor
    guild_response = requests.get(
        f'{DISCORD_API_URL}/users/@me/guilds/{GUILD_ID}/member',
        headers={'Authorization': f"Bearer {access_token}"}
    )
    
    # Obter cargos do usuário
    user_roles = []
    is_owner = False
    
    if guild_response.status_code == 200:
        member_data = guild_response.json()
        user_roles = [int(role) for role in member_data.get('roles', [])]
        
        # Debug - print user info
        print(f"🔍 DEBUG - User ID: {user_data['id']}")
        print(f"🔍 DEBUG - Username: {user_data['username']}")
        print(f"🔍 DEBUG - User Roles: {user_roles}")
        print(f"🔍 DEBUG - Allowed Roles: {ALLOWED_ROLES}")
    
    # Verificar se é o dono do servidor através do endpoint de guild
    try:
        guild_info = requests.get(
            f'{DISCORD_API_URL}/guilds/{GUILD_ID}',
            headers={'Authorization': f"Bot {DISCORD_BOT_TOKEN}"}
        )
        
        if guild_info.status_code == 200:
            guild_data = guild_info.json()
            owner_id = str(guild_data.get('owner_id'))
            user_id = str(user_data['id'])
            is_owner = (owner_id == user_id)
            
            print(f"🔍 DEBUG - Server Owner ID: {owner_id}")
            print(f"🔍 DEBUG - Is Owner: {is_owner}")
        else:
            print(f"❌ DEBUG - Failed to get guild info: {guild_info.status_code}")
    except Exception as e:
        print(f"❌ DEBUG - Error checking owner: {e}")
    
    # Verificar se tem permissão (Owner OU Staff)
    has_staff_role = any(role in ALLOWED_ROLES for role in user_roles)
    has_permission = is_owner or has_staff_role
    
    print(f"🔍 DEBUG - Has Staff Role: {has_staff_role}")
    print(f"🔍 DEBUG - Has Permission: {has_permission}")
    
    if not has_permission:
        return render_template('error.html', 
            message="Acesso Negado", 
            details=f"Você não tem permissão para acessar o dashboard. Apenas Staff e superiores podem acessar.<br><br>Debug Info:<br>User ID: {user_data['id']}<br>Roles: {user_roles}<br>Is Owner: {is_owner}"
        )
    
    # Salvar na sessão
    session['user'] = {
        'id': user_data['id'],
        'username': user_data['username'],
        'discriminator': user_data.get('discriminator', '0'),
        'avatar': user_data.get('avatar'),
        'roles': user_roles
    }
    
    return redirect(url_for('dashboard'))

# =====================================================
# ROTAS DO DASHBOARD
# =====================================================
@app.route('/logout')
def logout():
    """Fazer logout e limpar sessão"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@staff_required
def dashboard():
    """Dashboard principal"""
    return render_template('dashboard.html', user=session['user'])

# =====================================================
# APIs PARA DROPDOWNS (Buscar dados do Discord)
# =====================================================
@app.route('/api/discord/channels')
@staff_required
def get_discord_channels():
    """Busca todos os canais do servidor"""
    try:
        response = requests.get(
            f'{DISCORD_API_URL}/guilds/{GUILD_ID}/channels',
            headers={'Authorization': f"Bot {DISCORD_BOT_TOKEN}"}
        )
        
        if response.status_code == 200:
            channels = response.json()
            # Filtrar apenas canais de texto
            text_channels = [
                {'id': ch['id'], 'name': ch['name'], 'type': ch['type']}
                for ch in channels
                if ch['type'] in [0, 5]  # 0 = text, 5 = announcement
            ]
            return jsonify(text_channels)
        
        return jsonify({'error': 'Erro ao buscar canais'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/discord/categories')
@staff_required
def get_discord_categories():
    """Busca todas as categorias do servidor"""
    try:
        response = requests.get(
            f'{DISCORD_API_URL}/guilds/{GUILD_ID}/channels',
            headers={'Authorization': f"Bot {DISCORD_BOT_TOKEN}"}
        )
        
        if response.status_code == 200:
            channels = response.json()
            # Filtrar apenas categorias
            categories = [
                {'id': ch['id'], 'name': ch['name']}
                for ch in channels
                if ch['type'] == 4  # 4 = category
            ]
            return jsonify(categories)
        
        return jsonify({'error': 'Erro ao buscar categorias'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/discord/roles')
@staff_required
def get_discord_roles():
    """Busca todos os cargos do servidor"""
    try:
        response = requests.get(
            f'{DISCORD_API_URL}/guilds/{GUILD_ID}/roles',
            headers={'Authorization': f"Bot {DISCORD_BOT_TOKEN}"}
        )
        
        if response.status_code == 200:
            roles = response.json()
            # Ordenar por posição
            sorted_roles = sorted(roles, key=lambda r: r.get('position', 0), reverse=True)
            role_list = [
                {'id': r['id'], 'name': r['name'], 'color': r.get('color', 0)}
                for r in sorted_roles
                if r['name'] != '@everyone'
            ]
            return jsonify(role_list)
        
        return jsonify({'error': 'Erro ao buscar cargos'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
@staff_required
def get_stats():
    """Retorna estatísticas dos tickets"""
    conn = sqlite3.connect('tickets.db')
    c = conn.cursor()
    
    # Total de tickets
    c.execute("SELECT COUNT(*) FROM tickets")
    total = c.fetchone()[0]
    
    # Tickets abertos
    c.execute("SELECT COUNT(*) FROM tickets WHERE status='open'")
    open_tickets = c.fetchone()[0]
    
    # Tickets fechados
    c.execute("SELECT COUNT(*) FROM tickets WHERE status='closed'")
    closed_tickets = c.fetchone()[0]
    
    # Tempo médio de resposta (simulado - implementar lógica real)
    avg_response_time = "18 min"
    
    # Taxa de resolução
    resolution_rate = f"{int((closed_tickets / total * 100) if total > 0 else 0)}%"
    
    conn.close()
    
    return jsonify({
        'total': total,
        'open': open_tickets,
        'waiting': 0,  # Implementar lógica
        'closed': closed_tickets,
        'avg_time': avg_response_time,
        'resolution_rate': resolution_rate
    })

@app.route('/api/tickets')
@staff_required
def get_tickets():
    """Retorna lista de tickets"""
    conn = sqlite3.connect('tickets.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    status_filter = request.args.get('status', 'open')
    
    query = """
        SELECT t.*, c.name as category_name, c.emoji as category_emoji
        FROM tickets t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.status = ?
        ORDER BY t.created_at DESC
        LIMIT 50
    """
    
    c.execute(query, (status_filter,))
    tickets = [dict(row) for row in c.fetchall()]
    
    conn.close()
    
    return jsonify(tickets)

@app.route('/api/ticket/<int:ticket_id>')
@staff_required
def get_ticket(ticket_id):
    """Retorna detalhes de um ticket específico"""
    conn = sqlite3.connect('tickets.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Buscar ticket
    c.execute("""
        SELECT t.*, c.name as category_name, c.emoji as category_emoji
        FROM tickets t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.id = ?
    """, (ticket_id,))
    
    ticket = dict(c.fetchone() or {})
    
    if not ticket:
        conn.close()
        return jsonify({'error': 'Ticket não encontrado'}), 404
    
    # Buscar mensagens
    c.execute("""
        SELECT * FROM ticket_messages
        WHERE ticket_id = ?
        ORDER BY created_at ASC
    """, (ticket_id,))
    
    messages = [dict(row) for row in c.fetchall()]
    ticket['messages'] = messages
    
    conn.close()
    
    return jsonify(ticket)

# =====================================================
# ROTAS DE CATEGORIAS
# =====================================================
@app.route('/categories')
@staff_required
def categories_page():
    """Página de gerenciamento de categorias"""
    return render_template('categories.html', user=session['user'])

@app.route('/api/categories', methods=['GET', 'POST'])
@staff_required
def categories():
    """CRUD de categorias"""
    conn = sqlite3.connect('tickets.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if request.method == 'GET':
        c.execute("SELECT * FROM categories ORDER BY created_at DESC")
        categories_list = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(categories_list)
    
    elif request.method == 'POST':
        data = request.json
        
        c.execute("""
            INSERT INTO categories (
                name, emoji, description, channel_category_id,
                channel_name_template, allowed_roles, mention_role_id,
                initial_message, buttons_config, color
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('name'),
            data.get('emoji'),
            data.get('description'),
            data.get('channel_category_id'),
            data.get('channel_name_template'),
            json.dumps(data.get('allowed_roles', [])),
            data.get('mention_role_id'),
            data.get('initial_message'),
            json.dumps(data.get('buttons_config', [])),
            data.get('color', '#FF8C00')
        ))
        
        conn.commit()
        category_id = c.lastrowid
        conn.close()
        
        return jsonify({'id': category_id, 'message': 'Categoria criada!'}), 201

@app.route('/api/categories/<int:category_id>', methods=['PUT', 'DELETE'])
@staff_required
def category_detail(category_id):
    """Editar ou deletar categoria"""
    conn = sqlite3.connect('tickets.db')
    c = conn.cursor()
    
    if request.method == 'PUT':
        data = request.json
        
        c.execute("""
            UPDATE categories SET
                name=?, emoji=?, description=?, channel_category_id=?,
                channel_name_template=?, allowed_roles=?, mention_role_id=?,
                initial_message=?, buttons_config=?, color=?
            WHERE id=?
        """, (
            data.get('name'),
            data.get('emoji'),
            data.get('description'),
            data.get('channel_category_id'),
            data.get('channel_name_template'),
            json.dumps(data.get('allowed_roles', [])),
            data.get('mention_role_id'),
            data.get('initial_message'),
            json.dumps(data.get('buttons_config', [])),
            data.get('color'),
            category_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Categoria atualizada!'})
    
    elif request.method == 'DELETE':
        c.execute("DELETE FROM categories WHERE id=?", (category_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Categoria deletada!'})

# =====================================================
# ROTAS DE PAINÉIS
# =====================================================
@app.route('/panels')
@staff_required
def panels_page():
    """Página de gerenciamento de painéis"""
    return render_template('panels.html', user=session['user'])

@app.route('/api/panels', methods=['GET', 'POST'])
@staff_required
def panels():
    """CRUD de painéis"""
    conn = sqlite3.connect('tickets.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if request.method == 'GET':
        c.execute("SELECT * FROM panels ORDER BY created_at DESC")
        panels_list = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(panels_list)
    
    elif request.method == 'POST':
        data = request.json
        
        c.execute("""
            INSERT INTO panels (
                name, title, description, color, image_url,
                thumbnail_url, footer, channel_id, panel_type, categories
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('name'),
            data.get('title'),
            data.get('description'),
            data.get('color', '#FF8C00'),
            data.get('image_url'),
            data.get('thumbnail_url'),
            data.get('footer'),
            data.get('channel_id'),
            data.get('panel_type', 'buttons'),
            json.dumps(data.get('categories', []))
        ))
        
        conn.commit()
        panel_id = c.lastrowid
        conn.close()
        
        return jsonify({'id': panel_id, 'message': 'Painel criado!'}), 201

# =====================================================
# INTEGRAÇÃO COM DISCORD BOT
# =====================================================
@app.route('/api/discord/send-panel', methods=['POST'])
@staff_required
def send_panel_to_discord():
    """Envia painel para o Discord via bot"""
    data = request.json
    panel_id = data.get('panel_id')
    
    # Aqui você faria uma requisição para o bot Discord
    # enviando os dados do painel para ele criar no Discord
    
    # Por enquanto, apenas simulamos
    return jsonify({
        'success': True,
        'message': 'Painel enviado para o Discord!',
        'message_id': '123456789'
    })

# =====================================================
# CONFIGURAÇÕES DE SISTEMAS (Welcome, Tickets, etc)
# =====================================================
def load_welcome_config():
    """Carrega configurações do welcome_config.json"""
    try:
        if os.path.exists('welcome_config.json'):
            with open('welcome_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    
    # Padrão se não existir
    return {
        'welcome_enabled': True,
        'goodbye_enabled': True,
        'autorole_enabled': True,
        'tickets_enabled': True,
        'status_message_id': None
    }

def save_welcome_config(config):
    """Salva configurações no welcome_config.json"""
    with open('welcome_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

@app.route('/config')
@staff_required
def config_page():
    """Página de configurações dos sistemas"""
    welcome_config = load_welcome_config()
    return render_template('config.html', user=session['user'], config=welcome_config)

@app.route('/api/config/toggle/<system>', methods=['POST'])
@staff_required
def toggle_system(system):
    """Liga/desliga sistemas (welcome, goodbye, autorole, tickets)"""
    try:
        config = load_welcome_config()
        
        if system == 'welcome':
            config['welcome_enabled'] = not config.get('welcome_enabled', True)
            message = f"Sistema de boas-vindas: {'✅ ATIVADO' if config['welcome_enabled'] else '❌ DESATIVADO'}"
        
        elif system == 'goodbye':
            config['goodbye_enabled'] = not config.get('goodbye_enabled', True)
            message = f"Sistema de saída/ban: {'✅ ATIVADO' if config['goodbye_enabled'] else '❌ DESATIVADO'}"
        
        elif system == 'autorole':
            config['autorole_enabled'] = not config.get('autorole_enabled', True)
            message = f"Sistema de autorole: {'✅ ATIVADO' if config['autorole_enabled'] else '❌ DESATIVADO'}"
        
        elif system == 'tickets':
            config['tickets_enabled'] = not config.get('tickets_enabled', True)
            message = f"Sistema de tickets: {'✅ ATIVADO' if config['tickets_enabled'] else '❌ DESATIVADO'}"
        
        else:
            return jsonify({'success': False, 'message': 'Sistema inválido'}), 400
        
        save_welcome_config(config)
        
        # TODO: Aqui você pode fazer uma requisição para o bot atualizar o painel no Discord
        # usando webhook ou API do bot
        
        return jsonify({
            'success': True,
            'message': message,
            'enabled': config.get(f'{system}_enabled', False)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/config/status')
def get_config_status():
    """Retorna o status atual de todos os sistemas (público para o bot acessar)"""
    config = load_welcome_config()
    return jsonify(config)

# =====================================================
# INICIALIZAÇÃO
# =====================================================
# Inicializar banco de dados sempre
init_db()

if __name__ == '__main__':
    # Modo desenvolvimento (local)
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False') == 'True'
    
    print("🚀 Iniciando CAOS Ticket Dashboard...")
    print(f"✅ Dashboard rodando em http://localhost:{port}")
    print(f"🔐 Configure as variáveis de ambiente:")
    print(f"   - DISCORD_CLIENT_ID")
    print(f"   - DISCORD_CLIENT_SECRET")
    print(f"   - DISCORD_TOKEN")
    print(f"   - GUILD_ID")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
else:
    # Modo produção (Gunicorn)
    print("✅ Dashboard iniciado em modo produção")
