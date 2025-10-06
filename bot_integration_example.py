# =====================================================
# EXEMPLO DE INTEGRAÇÃO COM BOT DISCORD
# Adicione este código ao seu caosbot_railway.py
# =====================================================

import aiohttp
import json

# URL do dashboard (ajuste conforme seu deploy)
DASHBOARD_URL = "https://seu-dashboard.onrender.com"
DASHBOARD_SECRET = "sua_chave_secreta_compartilhada"  # Mesma em ambos

# =====================================================
# FUNÇÃO PARA NOTIFICAR DASHBOARD SOBRE NOVO TICKET
# =====================================================
async def notify_dashboard_new_ticket(ticket_data):
    """
    Notifica o dashboard quando um novo ticket é criado
    
    ticket_data = {
        'ticket_number': 123,
        'user_id': '123456789',
        'username': 'João Silva',
        'category_id': 1,
        'channel_id': '987654321',
        'created_at': '2025-10-05T22:00:00'
    }
    """
    async with aiohttp.ClientSession() as session:
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {DASHBOARD_SECRET}'
            }
            
            async with session.post(
                f'{DASHBOARD_URL}/api/webhook/ticket-created',
                json=ticket_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    print(f"✅ Dashboard notificado sobre ticket #{ticket_data['ticket_number']}")
                else:
                    print(f"⚠️ Erro ao notificar dashboard: {response.status}")
        except Exception as e:
            print(f"❌ Erro ao conectar com dashboard: {e}")

# =====================================================
# FUNÇÃO PARA REGISTRAR MENSAGEM NO DASHBOARD
# =====================================================
async def register_ticket_message(ticket_id, message_data):
    """
    Registra uma nova mensagem no dashboard
    
    message_data = {
        'ticket_id': 123,
        'user_id': '123456789',
        'username': 'João Silva',
        'content': 'Olá, preciso de ajuda!',
        'attachments': []
    }
    """
    async with aiohttp.ClientSession() as session:
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {DASHBOARD_SECRET}'
            }
            
            async with session.post(
                f'{DASHBOARD_URL}/api/webhook/ticket-message',
                json=message_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    print(f"✅ Mensagem registrada no dashboard")
        except Exception as e:
            print(f"❌ Erro ao registrar mensagem: {e}")

# =====================================================
# FUNÇÃO PARA FECHAR TICKET NO DASHBOARD
# =====================================================
async def close_ticket_on_dashboard(ticket_id):
    """Notifica dashboard que ticket foi fechado"""
    async with aiohttp.ClientSession() as session:
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {DASHBOARD_SECRET}'
            }
            
            data = {'ticket_id': ticket_id, 'status': 'closed'}
            
            async with session.post(
                f'{DASHBOARD_URL}/api/webhook/ticket-closed',
                json=data,
                headers=headers
            ) as response:
                if response.status == 200:
                    print(f"✅ Ticket #{ticket_id} fechado no dashboard")
        except Exception as e:
            print(f"❌ Erro ao fechar ticket no dashboard: {e}")

# =====================================================
# EXEMPLO DE USO NO SEU BOT
# =====================================================

# Quando criar um ticket:
@bot.event
async def on_interaction(interaction):
    if interaction.type == discord.InteractionType.component:
        # Usuário clicou em botão de categoria
        category_id = int(interaction.data['custom_id'].split('_')[1])
        
        # Criar canal do ticket (seu código existente)
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category
        )
        
        # Registrar no banco de dados local
        ticket_number = get_next_ticket_number()  # Sua função
        
        # NOTIFICAR DASHBOARD
        await notify_dashboard_new_ticket({
            'ticket_number': ticket_number,
            'user_id': str(interaction.user.id),
            'username': interaction.user.name,
            'category_id': category_id,
            'channel_id': str(ticket_channel.id),
            'created_at': datetime.utcnow().isoformat()
        })

# Quando alguém mandar mensagem no ticket:
@bot.event
async def on_message(message):
    if message.channel.name.startswith('ticket-'):
        # Verificar se é um canal de ticket
        ticket_id = get_ticket_id_from_channel(message.channel.id)  # Sua função
        
        if ticket_id:
            # REGISTRAR MENSAGEM NO DASHBOARD
            await register_ticket_message(ticket_id, {
                'ticket_id': ticket_id,
                'user_id': str(message.author.id),
                'username': message.author.name,
                'content': message.content,
                'attachments': [att.url for att in message.attachments]
            })

# Quando fechar um ticket:
@bot.command()
async def close(ctx):
    """Fecha o ticket atual"""
    if ctx.channel.name.startswith('ticket-'):
        ticket_id = get_ticket_id_from_channel(ctx.channel.id)
        
        # Fechar ticket no bot (seu código existente)
        await ctx.channel.delete()
        
        # NOTIFICAR DASHBOARD
        await close_ticket_on_dashboard(ticket_id)

# =====================================================
# WEBHOOK HANDLER NO DASHBOARD (app.py)
# =====================================================

"""
Adicione estas rotas no app.py do dashboard:

@app.route('/api/webhook/ticket-created', methods=['POST'])
def webhook_ticket_created():
    # Verificar autorização
    auth = request.headers.get('Authorization')
    if auth != f'Bearer {DASHBOARD_SECRET}':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    
    # Salvar no banco de dados
    conn = sqlite3.connect('tickets.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO tickets (
            ticket_number, user_id, username, category_id,
            channel_id, status, created_at
        ) VALUES (?, ?, ?, ?, ?, 'open', ?)
    ''', (
        data['ticket_number'],
        data['user_id'],
        data['username'],
        data['category_id'],
        data['channel_id'],
        data['created_at']
    ))
    
    ticket_id = c.lastrowid
    conn.commit()
    conn.close()
    
    # Notificar via WebSocket
    socketio.emit('ticket_created', {
        'id': ticket_id,
        'ticket_number': data['ticket_number'],
        'username': data['username']
    })
    
    return jsonify({'success': True, 'ticket_id': ticket_id})

@app.route('/api/webhook/ticket-message', methods=['POST'])
def webhook_ticket_message():
    auth = request.headers.get('Authorization')
    if auth != f'Bearer {DASHBOARD_SECRET}':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    
    # Salvar mensagem
    conn = sqlite3.connect('tickets.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO ticket_messages (
            ticket_id, user_id, username, content, attachments
        ) VALUES (?, ?, ?, ?, ?)
    ''', (
        data['ticket_id'],
        data['user_id'],
        data['username'],
        data['content'],
        json.dumps(data.get('attachments', []))
    ))
    
    # Atualizar contador de mensagens do ticket
    c.execute('''
        UPDATE tickets 
        SET messages_count = messages_count + 1
        WHERE id = ?
    ''', (data['ticket_id'],))
    
    conn.commit()
    conn.close()
    
    # Notificar via WebSocket
    socketio.emit('ticket_update', {
        'ticket_id': data['ticket_id'],
        'new_message': True
    })
    
    return jsonify({'success': True})

@app.route('/api/webhook/ticket-closed', methods=['POST'])
def webhook_ticket_closed():
    auth = request.headers.get('Authorization')
    if auth != f'Bearer {DASHBOARD_SECRET}':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    
    # Marcar como fechado
    conn = sqlite3.connect('tickets.db')
    c = conn.cursor()
    
    c.execute('''
        UPDATE tickets 
        SET status = 'closed', closed_at = ?
        WHERE id = ?
    ''', (datetime.utcnow().isoformat(), data['ticket_id']))
    
    conn.commit()
    conn.close()
    
    # Notificar via WebSocket
    socketio.emit('ticket_update', {
        'ticket_id': data['ticket_id'],
        'status': 'closed'
    })
    
    return jsonify({'success': True})
"""
