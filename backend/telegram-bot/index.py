import json
import os
import random
import time

def handler(event: dict, context) -> dict:
    '''Telegram бот для розыгрыша призов салона красоты'''
    
    method = event.get('httpMethod', 'POST')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': ''
        }
    
    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        body = json.loads(event.get('body', '{}'))
        
        if not body.get('message'):
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'ok': True})
            }
        
        message = body['message']
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        username = message['from'].get('username', '')
        first_name = message['from'].get('first_name', '')
        text = message.get('text', '')
        
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
        
        if not bot_token:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'ok': True, 'info': 'Bot token not configured'})
            }
        
        if text == '/start':
            response = send_welcome_message(bot_token, chat_id, user_id)
        elif text == 'Бросить кубик':
            response = handle_dice_roll(bot_token, chat_id, user_id, username, first_name)
        else:
            response = {'ok': True}
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'ok': True, 'response': response})
        }
        
    except Exception as e:
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'ok': True, 'error': str(e)})
        }


def check_already_participated(user_id: int) -> bool:
    '''Проверяет участвовал ли пользователь ранее'''
    import psycopg2
    
    db_url = os.environ.get('DATABASE_URL', '')
    if not db_url:
        return False
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM participants WHERE user_id = %s', (user_id,))
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return count > 0
    except:
        return False


def save_participant(user_id: int, username: str, first_name: str, prize_amount: int, prize_label: str):
    '''Сохраняет участника в базу данных'''
    import psycopg2
    
    db_url = os.environ.get('DATABASE_URL', '')
    if not db_url:
        return
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO participants (user_id, username, first_name, prize_amount, prize_label) VALUES (%s, %s, %s, %s, %s)',
            (user_id, username, first_name, prize_amount, prize_label)
        )
        conn.commit()
        cur.close()
        conn.close()
    except:
        pass


def send_welcome_message(bot_token: str, chat_id: int, user_id: int) -> dict:
    '''Отправляет приветственное сообщение с призами'''
    import urllib.request
    
    already_participated = check_already_participated(user_id)
    
    if already_participated:
        welcome_text = (
            "Вы уже участвовали в розыгрыше.\n\n"
            "Ваш приз ожидает вас в салоне."
        )
        keyboard = {'remove_keyboard': True}
    else:
        welcome_text = (
            "Добро пожаловать в розыгрыш призов.\n\n"
            "<b>Вот какие подарки можно выиграть:</b>\n\n"
            "- Любая процедура бесплатно\n"
            "- Сертификат в салон на 1 000₽\n"
            "- Сертификат в салон на 500₽\n\n"
            "Бросьте кубик, чтобы узнать что выпадет именно вам."
        )
        keyboard = {
            'keyboard': [[{'text': 'Бросить кубик'}]],
            'resize_keyboard': True,
            'one_time_keyboard': True
        }
    
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = json.dumps({
        'chat_id': chat_id,
        'text': welcome_text,
        'parse_mode': 'HTML',
        'reply_markup': keyboard
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))


def handle_dice_roll(bot_token: str, chat_id: int, user_id: int, username: str, first_name: str) -> dict:
    '''Обрабатывает бросок кубика и определяет приз'''
    import urllib.request
    
    if check_already_participated(user_id):
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        data = json.dumps({
            'chat_id': chat_id,
            'text': 'Вы уже участвовали в розыгрыше. Ваш приз ожидает вас в салоне.',
            'reply_markup': {'remove_keyboard': True}
        }).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    
    prizes = [
        {'amount': 0, 'label': 'Любая процедура бесплатно', 'chance': 0, 'promo': ''},
        {'amount': 1000, 'label': 'Сертификат в салон на 1 000₽', 'chance': 10, 'promo': 'PROMO1000'},
        {'amount': 500, 'label': 'Сертификат в салон на 500₽', 'chance': 90, 'promo': 'PROMO500'},
    ]
    
    rand = random.random() * 100
    cumulative = 0
    selected_prize = prizes[-1]
    
    for prize in prizes:
        cumulative += prize['chance']
        if rand <= cumulative:
            selected_prize = prize
            break
    
    url_dice = f'https://api.telegram.org/bot{bot_token}/sendDice'
    data_dice = json.dumps({
        'chat_id': chat_id,
        'emoji': '🎲'
    }).encode('utf-8')
    
    req_dice = urllib.request.Request(url_dice, data=data_dice, headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req_dice)
    
    time.sleep(5)
    
    if selected_prize['promo']:
        booking_info = f"Онлайн запись - https://dikidi.net/1815750, в комментариях к записи укажите сообщение {selected_prize['promo']}"
    else:
        booking_info = "Ваш приз ожидает вас в салоне."
    
    result_text = (
        f"<b>Поздравляем!</b>\n\n"
        f"Вы выиграли:\n"
        f"<b>{selected_prize['label']}</b>\n\n"
        f"{booking_info}"
    )
    
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data_result = json.dumps({
        'chat_id': chat_id,
        'text': result_text,
        'parse_mode': 'HTML',
        'reply_markup': {'remove_keyboard': True}
    }).encode('utf-8')
    
    save_participant(user_id, username, first_name, selected_prize['amount'], selected_prize['label'])
    
    req_result = urllib.request.Request(url, data=data_result, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req_result) as response:
        return json.loads(response.read().decode('utf-8'))