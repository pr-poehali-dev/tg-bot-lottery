import json
import os
import random

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
        text = message.get('text', '')
        
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
        
        if not bot_token:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'ok': True, 'info': 'Bot token not configured'})
            }
        
        if text == '/start':
            response = send_welcome_message(bot_token, chat_id)
        elif text == '🎲 БРОСИТЬ КУБИК':
            response = handle_dice_roll(bot_token, chat_id)
        else:
            response = send_help_message(bot_token, chat_id)
        
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


def send_welcome_message(bot_token: str, chat_id: int) -> dict:
    '''Отправляет приветственное сообщение с призами'''
    import urllib.request
    
    welcome_text = (
        "✨ <b>Добро пожаловать в розыгрыш призов!</b> ✨\n\n"
        "🎁 <b>Вот какие подарки можно выиграть:</b>\n\n"
        "🏆 Сертификат на 10 000₽\n"
        "💎 Сертификат на 5 000₽\n"
        "💰 Сертификат на 1 000₽\n"
        "🎀 Сертификат на 500₽\n\n"
        "🎲 <b>Бросай кубик, чтобы узнать что выпадет именно тебе!</b>"
    )
    
    keyboard = {
        'keyboard': [[{'text': '🎲 БРОСИТЬ КУБИК'}]],
        'resize_keyboard': True,
        'one_time_keyboard': False
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


def handle_dice_roll(bot_token: str, chat_id: int) -> dict:
    '''Обрабатывает бросок кубика и определяет приз'''
    import urllib.request
    
    prizes = [
        {'amount': 10000, 'label': '🏆 Сертификат на 10 000₽', 'chance': 5, 'emoji': '🏆'},
        {'amount': 5000, 'label': '💎 Сертификат на 5 000₽', 'chance': 15, 'emoji': '💎'},
        {'amount': 1000, 'label': '💰 Сертификат на 1 000₽', 'chance': 30, 'emoji': '💰'},
        {'amount': 500, 'label': '🎀 Сертификат на 500₽', 'chance': 50, 'emoji': '🎀'},
    ]
    
    rand = random.random() * 100
    cumulative = 0
    selected_prize = prizes[-1]
    
    for prize in prizes:
        cumulative += prize['chance']
        if rand <= cumulative:
            selected_prize = prize
            break
    
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    
    wait_text = "🎲 Бросаем кубик..."
    data_wait = json.dumps({
        'chat_id': chat_id,
        'text': wait_text
    }).encode('utf-8')
    
    req_wait = urllib.request.Request(url, data=data_wait, headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req_wait)
    
    result_text = (
        f"🎉 <b>ПОЗДРАВЛЯЕМ!</b> 🎉\n\n"
        f"{selected_prize['emoji']} <b>Вы выиграли:</b>\n"
        f"<b>{selected_prize['label']}</b>\n\n"
        f"✨ Ваш приз уже ждёт вас в салоне!\n\n"
        f"📍 Приходите к нам за сертификатом"
    )
    
    keyboard = {
        'keyboard': [[{'text': '🎲 БРОСИТЬ КУБИК'}]],
        'resize_keyboard': True,
        'one_time_keyboard': False
    }
    
    data_result = json.dumps({
        'chat_id': chat_id,
        'text': result_text,
        'parse_mode': 'HTML',
        'reply_markup': keyboard
    }).encode('utf-8')
    
    req_result = urllib.request.Request(url, data=data_result, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req_result) as response:
        return json.loads(response.read().decode('utf-8'))


def send_help_message(bot_token: str, chat_id: int) -> dict:
    '''Отправляет справочное сообщение'''
    import urllib.request
    
    help_text = (
        "ℹ️ <b>Как участвовать в розыгрыше:</b>\n\n"
        "1️⃣ Нажмите кнопку <b>🎲 БРОСИТЬ КУБИК</b>\n"
        "2️⃣ Узнайте ваш приз\n"
        "3️⃣ Приходите в салон за сертификатом!\n\n"
        "Удачи! ✨"
    )
    
    keyboard = {
        'keyboard': [[{'text': '🎲 БРОСИТЬ КУБИК'}]],
        'resize_keyboard': True,
        'one_time_keyboard': False
    }
    
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = json.dumps({
        'chat_id': chat_id,
        'text': help_text,
        'parse_mode': 'HTML',
        'reply_markup': keyboard
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))