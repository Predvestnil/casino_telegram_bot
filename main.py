import logging
from qiwi_api import Qiwi
import asyncio
import datetime
import random, string
from copy import deepcopy
import time
import math
import requests, threading
import crypto
import sql
import game
import key_board
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.utils.markdown import escape_md as escape

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="TOKEN")
# Диспетчер
dp = Dispatcher(bot)
sql.init_db()
    

#Константы
id_admins = [1]#ID админов
koef_ref = 0.01#ставка по реферальной программе для клиента
partner_ref = 0.05#ставка по реферальной программе для партнера
komission_casino = (1 - 0.07)#комиссия в играх между игроками(казино не участвует)
channel_of_requests_withdraw = -1001817472066#канал, куда приходят запросы на вывод средств
channel_of_deposit = -1001798291419#канал, куда приходят уведомления о депозите
channel_of_error = -919215284#канал, куда приходят логи с ошибками
id_chat_bot = -980757783 #чат бота
chat_id_group = -1001921794621 #канал бота
game_of_id = {
    14: 'Bowling',
    15: 'Penalty',
    16: 'Darts',
    17: 'Basketball',
    21: 'Dice',
    20: 'Slots'
}
logo_multi = {1:'🧔', 2:'🧔🏻', 3:'🧔🏽', 4:'🧔🏾', 5:'🧔🏿', 6:'🧔🏼'}
smile_of_game = {
    'Bowling': '🎳',
    'Penalty': '⚽️',
    'Darts': '🎯',
    'Basketball': '🏀',
    'Dice': '🎲',
}
id_game_of_smile = {
    '/🎳': 14,
    #'/⚽️': 15,
    '/🎯': 16,
    '/🏀': 17,
    '/🎰': 20,
    '/🎲': 21,
    '/bowl': 14,
    #'/foot': 15,
    '/darts': 16,
    '/bask': 17,
    '/slot': 20,
    '/cube': 21
}
gamedelay_of_smile = {
    '🎳': 3.4,
    '⚽': 3.7,
    '🎯': 2.8,
    '🏀': 4.2,
    '🎲': 3.5,
    '🎰': 2.3
}
gamedelay_of_id = {
    14: 3.4,
    15: 3.7,
    16: 2.8,
    17: 4.2,
    21: 3.5,
    20: 2.3
}
scans_id = {
    'btc': 'https://blockchain.info/q/addressbalance/',
    'eth': 'https://api.blockcypher.com/v1/eth/main/addrs/',
    'trx': 'https://apilist.tronscan.org/api/account?address=',
    'usdt': 'https://apilist.tronscan.org/api/account?address=',
}
time_moneta_id = {
    'btc':90,
    'eth':60,
    'trx':15,
    'usdt':15,
}


async def generate_promo(length = 15):
    try:
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))
    except Exception as e:
        await bot.send_message(channel_of_error, '102\n'+str(e))


async def send_message(user_id, message, reply = key_board.start_client_kb_reply, mode = 'MarkdownV2',key = 0):
    try:
        req = 'SELECT last_message_bot FROM users WHERE user_id = '+str(user_id)+';'
        idx = await sql.request_db(req)
        idx = idx[0]
        if(key==1):
            try:
                await bot.delete_message(chat_id=user_id, message_id=idx[0])
            except:
                pass
            msg = await bot.send_animation(user_id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=message, reply_markup=reply, parse_mode=mode)
            req = 'UPDATE users SET last_message_bot = '+str(msg.message_id)+' WHERE user_id = '+str(user_id)+';'
            await sql.request_db(req)
        else:
            try:
                await bot.edit_message_caption(caption=message, chat_id=user_id, message_id=idx[0], reply_markup=reply, parse_mode=mode)
            except Exception as e:
                if(str(e) =='Message is not modified: specified new message content and reply markup are exactly the same as a current content and reply markup of the message'):
                    pass
                else:
                    try:
                        await bot.delete_message(chat_id=user_id, message_id=idx[0])
                    except:
                        pass
                    msg = await bot.send_animation(user_id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=message, reply_markup=reply, parse_mode=mode)
                    req = 'UPDATE users SET last_message_bot = '+str(msg.message_id)+' WHERE user_id = '+str(user_id)+';'
                    await sql.request_db(req)
    except Exception as e:
        await bot.send_message(channel_of_error, '133\n'+str(e))
'''@dp.message_handler(content_types=[types.ContentType.ANY])
async def group_handler(message: types.Message):
    msg = await bot.send_animation(message.from_user.id, open('logo.gif','rb'))
    print(message)'''
@dp.message_handler(content_types=[types.ContentType.TEXT],chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP])
async def group_handler(message: types.Message):
    is_par = await sql.request_db(f"SELECT chat_id FROM partners WHERE chat_id = {message.chat.id};")
    if(len(is_par)==0 and message.chat.id != id_chat_bot and message.chat.id != -649897954):
        for i in id_admins:
            await bot.send_message(i, str(message.chat))#, key=1)
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {message.from_user.id};")
    if(len(is_par)==0):
        try:
            req = await sql.request_db(f'SELECT username, firstname FROM users WHERE user_id = {message.from_user.id} AND subscribe = 1;')
            if(len(req)>0 and req[0][0]!=message.from_user.username):
                await sql.request_db(f"UPDATE users SET username = '{message.from_user.username}' WHERE user_id = {message.from_user.id};")
            if(len(req)>0 and req[0][1]!=message.from_user.first_name):
                await sql.request_db(f"UPDATE users SET firstname = '{message.from_user.first_name}' WHERE user_id = {message.from_user.id};")
            if(('/start' in message.text.lower() or '/help' in message.text.lower()) and len(req)==0):
                if(len(req)==0):
                    msg = None
                    try:
                        msg = await bot.send_message(message.from_user.id, key_board.welcome_message, reply_markup=key_board.start_welcome_kb, parse_mode='MarkdownV2')
                        msg = msg.message_id
                    except:
                        msg = 0
                    reqq = await sql.request_db(f'SELECT * FROM users WHERE user_id = {message.from_user.id};')
                    if(len(reqq)==0):
                        partner_id = await sql.request_db(f"SELECT user_id FROM partners WHERE chat_id = '{message.chat.id}';")
                        usernm = 'None'        
                        if(message.from_user.username==None):
                            usernm = message.from_user.first_name
                            req = 'INSERT INTO users VALUES ('+str(message.from_user.id)+",'None','"+str(message.from_user.first_name)+"',20,0,0,0,'None',0,0,0,0,"+str(msg)+",0,0,0,0,"+str(partner_id[0][0])+",CURDATE());"
                        else:
                            usernm = message.from_user.username
                            req = 'INSERT INTO users VALUES ('+str(message.from_user.id)+",'"+str(message.from_user.username)+"','"+str(message.from_user.first_name)+"',20,0,0,0,'None',0,0,0,0,"+str(msg)+",0,0,0,0,"+str(partner_id[0][0])+",CURDATE());"
                        await sql.request_db(req)
                        await send_message(partner_id[0][0], key_board.new_ref_message.format(escape(usernm)))
                    await bot.send_message(message.chat.id, key_board.start_chat_message, parse_mode='MarkdownV2', reply_to_message_id=message.message_id, disable_web_page_preview = True)
                    await asyncio.sleep(3)
                    await send_message(message.from_user.id, key_board.reklama_message, reply = None)
                else:
                    await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.help_commands_message, parse_mode='Markdownv2', reply_to_message_id=message.message_id)
            elif(('/start' in message.text.lower() or '/help' in message.text.lower()) and len(req)==1):
                await bot.send_message(message.chat.id, key_board.help_commands_message, parse_mode='MarkdownV2', reply_to_message_id=message.message_id, disable_web_page_preview = True)
            elif(('/btc' in message.text.lower()) and (len(message.text.split(' '))==2)):
                cc1 = crypto.get_curs_BTC_USD()
                await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'BTC', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'BTC'), parse_mode='Markdownv2', reply_to_message_id=message.message_id)
            elif(('/eth' in message.text.lower()) and (len(message.text.split(' '))==2)):
                cc1 = crypto.get_curs_ETH_USD()
                await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'ETH', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'ETH'), parse_mode='Markdownv2', reply_to_message_id=message.message_id)
            elif(('/trx' in message.text.lower()) and (len(message.text.split(' '))==2)):
                cc1 = crypto.get_curs_TRX_USD()
                await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'TRX', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'TRX'), parse_mode='Markdownv2', reply_to_message_id=message.message_id)
            elif(('/ltc' in message.text.lower()) and (len(message.text.split(' '))==2)):
                cc1 = crypto.get_curs_LTC_USD()
                await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'LTC', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'LTC'), parse_mode='Markdownv2', reply_to_message_id=message.message_id)
            elif(('/dash' in message.text.lower()) and (len(message.text.split(' '))==2)):
                cc1 = crypto.get_curs_DASH_USD()
                await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'DASH', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'DASH'), parse_mode='Markdownv2', reply_to_message_id=message.message_id)
            elif(('/bch' in message.text.lower()) and (len(message.text.split(' '))==2)):
                cc1 = crypto.get_curs_BCH_USD()
                await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'BCH', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'BCH'), parse_mode='Markdownv2', reply_to_message_id=message.message_id)
            elif(('/doge' in message.text.lower()) and (len(message.text.split(' '))==2)):
                cc1 = crypto.get_curs_DOGE_USD()
                await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'DOGE', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'DOGE'), parse_mode='Markdownv2', reply_to_message_id=message.message_id)
            elif(('/bnb' in message.text.lower()) and (len(message.text.split(' '))==2)):
                cc1 = crypto.get_curs_BNB_USD()
                await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'BNB', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'BNB'), parse_mode='Markdownv2', reply_to_message_id=message.message_id)
            elif(('/xmr' in message.text.lower()) and (len(message.text.split(' '))==2)):
                cc1 = crypto.get_curs_XMR_USD()
                await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'XMR', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'XMR'), parse_mode='Markdownv2', reply_to_message_id=message.message_id)
            elif(('/ton' in message.text.lower()) and (len(message.text.split(' '))==2)):
                cc1 = crypto.get_curs_TON_USD()
                await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'TON', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'TON'), parse_mode='Markdownv2', reply_to_message_id=message.message_id)
            elif(('/eur' in message.text.lower()) and (len(message.text.split(' '))==2)):
                cc1 = await crypto.get_curs_EUR_USD()
                await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'EUR', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'EUR'), parse_mode='Markdownv2', reply_to_message_id=message.message_id)
            elif(('/kzt' in message.text.lower()) and (len(message.text.split(' '))==2)):
                cc1 = await crypto.get_curs_KZT_USD()
                await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'KZT', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'KZT'), parse_mode='Markdownv2', reply_to_message_id=message.message_id)
            elif(('/rub' in message.text.lower()) and (len(message.text.split(' '))==2)):
                cc1 = await crypto.get_curs_RUB_USD()
                await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'RUB',escape(message.text.split(' ')[1]), 'RUB', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'USD'), parse_mode='Markdownv2', reply_to_message_id=message.message_id)
            elif(('/uah' in message.text.lower()) and (len(message.text.split(' '))==2)):
                cc1 = await crypto.get_curs_UAH_USD()
                await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'UAH', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'UAH'), parse_mode='Markdownv2', reply_to_message_id=message.message_id)
            elif(('/allgames' in message.text.lower()) and (len(message.text.split(' '))==1)):
                q = await sql.request_db(f"SELECT id,stavka,type,players FROM multigames WHERE chat_id = {message.chat.id} AND password = '0' AND status = 0;")
                msg = ''
                for i in q:
                    msg += f"\#ID{i[0]}    {smile_of_game[i[2]]}  {escape(i[1])}💲  {i[3].count('+')+i[3].count('-')}/6👤\n\n"
                q = await sql.request_db(f"SELECT id,stavka FROM rb_game WHERE players NOT LIKE '%:_%' AND chat_id = {message.chat.id};")
                msg = ''
                for i in q:
                    msg += f"\#RB{i[0]}    {escape(i[1])}💲\n\n"
                qq = await sql.request_db(f"SELECT last_allgames_message FROM chats WHERE chat_id = {message.chat.id};")
                try:
                    await bot.delete_message(message.chat.id, qq[0][0])
                except:
                    pass
                mesg = await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.allgames_message.format(msg), parse_mode='Markdownv2', reply_to_message_id=message.message_id)
                await sql.request_db(f"UPDATE chats SET last_allgames_message = {mesg.message_id};")
            elif((message.text.split(' ')[0] in id_game_of_smile) and (len(message.text.split(' '))==2) and (message.text.split(' ')[1].replace('.','',1).isdigit()) and (len(req)>0) and (message.text.split(' ')[0] not in ['/cube', '/🎲'])):
                qq = await sql.request_db(f"SELECT id, chat_id, password FROM multigames WHERE (status = 0 OR status = 2) AND players LIKE '%{message.from_user.id}%';")
                if(len(qq)==0):
                    ss = await sql.request_db(f'SELECT * FROM games WHERE status = 0 AND user_id = {message.from_user.id};')
                    if(len(ss)>0):
                        if(ss[0][2] == 'Dice'):
                            await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.player_another_start_game_message+key_board.game_message_id[list(game_of_id.keys())[list(game_of_id.values()).index(ss[0][2])]].format(ss[0][3],escape(ss[0][4])), parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                        else:
                            await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.player_another_start_game_message+key_board.game_message_id[list(game_of_id.keys())[list(game_of_id.values()).index(ss[0][2])]].format(escape(ss[0][4])), parse_mode='MarkdownV2', reply_to_message_id=message.message_id)      
                    else:
                        idxx = await sql.request_db(f'SELECT balance FROM users WHERE user_id = {message.from_user.id};')
                        idxx = idxx[0]
                        if((float(idxx[0])>=float(message.text.split(' ')[1])) and (float(message.text.split(' ')[1])>=0.2) and (float(message.text.split(' ')[1])<=700)):
                            reqq = await sql.request_db("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = 'games';")
                            reqq = reqq[0][0]
                            await sql.request_db(f"INSERT INTO games(user_id, type, target_number, stavka, date, status, result) VALUES ({message.from_user.id},'{game_of_id[id_game_of_smile[message.text.split(' ')[0]]]}',1,{math.ceil(100*float(message.text.split(' ')[1]))/100},NOW(),0,0);")
                            await sql.request_db(f"UPDATE users SET balance = balance - {math.ceil(100*float(message.text.split(' ')[1]))/100}, playing_game_id_mini = {reqq}, status = {id_game_of_smile[message.text.split(' ')[0]]} WHERE user_id = {message.from_user.id};")
                            await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.game_message_id[id_game_of_smile[message.text.split(' ')[0]]].format(escape(math.ceil(100*float(message.text.split(' ')[1]))/100)), parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                        else:
                            await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.error_value_stavka_message, parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                else:
                    await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.link_multi_message.format(qq[0][0]), parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
            elif((message.text.split(' ')[0] in ['/rb','/br']) and (len(message.text.split(' '))==2) and (message.text.split(' ')[1].replace('.','',1).isdigit()) and (len(req)>0)):
                qq = await sql.request_db(f"SELECT id, chat_id, password FROM multigames WHERE (status = 0 OR status = 2) AND players LIKE '%{message.from_user.id}%';")
                qq1 = await sql.request_db(f"SELECT id FROM rb_game WHERE (players NOT LIKE '%-%' AND players NOT LIKE '%/%|%' AND players NOT LIKE '%|%/%') AND (players LIKE '%{message.from_user.id}+%' OR players LIKE '%{message.from_user.id}/%' OR players LIKE '%{message.from_user.id}|%' OR players LIKE '%{message.from_user.id}*%');")
                if((len(qq)+len(qq1))==0):
                    ss = await sql.request_db(f'SELECT * FROM games WHERE status = 0 AND user_id = {message.from_user.id};')
                    if(len(ss)>0):
                        if(ss[0][2] == 'Dice'):
                            await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.player_another_start_game_message+key_board.game_message_id[list(game_of_id.keys())[list(game_of_id.values()).index(ss[0][2])]].format(ss[0][3],escape(ss[0][4])), parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                        else:
                            await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.player_another_start_game_message+key_board.game_message_id[list(game_of_id.keys())[list(game_of_id.values()).index(ss[0][2])]].format(escape(ss[0][4])), parse_mode='MarkdownV2', reply_to_message_id=message.message_id)      
                    else:
                        idxx = await sql.request_db(f'SELECT balance FROM users WHERE user_id = {message.from_user.id};')
                        idxx = idxx[0]
                        if((float(idxx[0])>=float(message.text.split(' ')[1])) and (float(message.text.split(' ')[1])>=0.2) and (float(message.text.split(' ')[1])<=700)):
                            reqq = await sql.request_db("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = 'rb_game';")
                            reqq = reqq[0][0]
                            rb_keyboard = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('🃏JOIN', callback_data=f'{reqq}_joinrb')).row(types.InlineKeyboardButton('✖LEAVE', callback_data=f'{reqq}_leaverb'))
                            playr = f"@{message.from_user.username}" if message.from_user.username is not None else message.from_user.first_name
                            ms_players, ms_footer = escape(f'{playr} | ОЖИДАЕТ'), escape('🚬Ждём-с достойного противника...')
                            msg = await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.rb_message.format(reqq,escape(math.ceil(100*float(message.text.split(' ')[1]))/100),ms_players, ms_footer), reply_markup = rb_keyboard,parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                            await sql.request_db(f"INSERT INTO rb_game(players, zagad, stavka, date, message_id, chat_id) VALUES ('{message.from_user.id}*:',0,{math.ceil(100*float(message.text.split(' ')[1]))/100},NOW(),{msg.message_id},'{message.chat.id}');")
                            await sql.request_db(f"UPDATE users SET balance = balance - {math.ceil(100*float(message.text.split(' ')[1]))/100}, playing_rb_id = {reqq} WHERE user_id = {message.from_user.id};")                    
                        else:
                            await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.error_value_stavka_message, parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                elif(len(qq)==0):
                    await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.link_multi_message.format(qq1[0][0]), parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                elif(len(qq1)==0):
                    await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.link_multi_message.format(qq[0][0]), parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
            elif((message.text.split(' ')[0] == '/🎲' or message.text.split(' ')[0] == '/cube') and (len(message.text.split(' '))==3) and (message.text.split(' ')[2].replace('.','',1).isdigit()) and (int(message.text.split(' ')[1]) in [1,2,3,4,5,6]) and (len(req)>0)):
                qq = await sql.request_db(f"SELECT id, chat_id, password FROM multigames WHERE (status = 0 OR status = 2) AND players LIKE '%{message.from_user.id}%';")
                if(len(qq)==0):
                    ss = await sql.request_db(f'SELECT * FROM games WHERE status = 0 AND user_id = {message.from_user.id};')
                    if(len(ss)>0):
                        if(ss[0][2] == 'Dice'):
                            await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.player_another_start_game_message+key_board.game_message_id[list(game_of_id.keys())[list(game_of_id.values()).index(ss[0][2])]].format(ss[0][3],escape(ss[0][4])), parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                        else:
                            await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.player_another_start_game_message+key_board.game_message_id[list(game_of_id.keys())[list(game_of_id.values()).index(ss[0][2])]].format(escape(ss[0][4])), parse_mode='MarkdownV2', reply_to_message_id=message.message_id)      
                    else:
                        idxx = await sql.request_db(f'SELECT balance FROM users WHERE user_id = {message.from_user.id};')
                        idxx = idxx[0]
                        if((float(idxx[0])>=float(message.text.split(' ')[2])) and (float(message.text.split(' ')[2])>=0.2) and (float(message.text.split(' ')[2])<=700)):
                            reqq = await sql.request_db("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = 'games';")
                            reqq = reqq[0][0]
                            await sql.request_db(f"INSERT INTO games(user_id, type, target_number, stavka, date, status, result) VALUES ({message.from_user.id},'Dice',{int(message.text.split(' ')[1])},{math.ceil(100*float(message.text.split(' ')[2]))/100},NOW(),0,0);")
                            await sql.request_db(f"UPDATE users SET balance = balance - {math.ceil(100*float(message.text.split(' ')[2]))/100}, playing_game_id_mini = {reqq}, status = {id_game_of_smile[message.text.split(' ')[0]]} WHERE user_id = {message.from_user.id};")
                            #await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.game_message_id[id_game_of_smile[message.text.split(' ')[0]]].format(message.text.split(' ')[1], escape(message.text.split(' ')[2])), parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                            await bot.send_message(message.chat.id, key_board.game_message_id[id_game_of_smile[message.text.split(' ')[0]]].format(message.text.split(' ')[1], escape(math.ceil(100*float(message.text.split(' ')[2]))/100)), parse_mode='MarkdownV2', reply_to_message_id=message.message_id, disable_web_page_preview=True)
                        else:
                            await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.error_value_stavka_message, parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                else:
                    await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.link_multi_message.format(qq[0][0]), parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
            elif((message.text.split(' ')[0] in ['/mult', '/m']) and (message.text.split(' ')[1] in ['bowl','darts','bask','cube','🎳','🎯','🏀','🎲']) and (len(message.text.split(' '))==3) and (message.text.split(' ')[2].replace('.','',1).isdigit()) and (len(req)>0)):
                ss = await sql.request_db(f'SELECT * FROM games WHERE status = 0 AND user_id = {message.from_user.id};')
                ss1 = await sql.request_db(f'SELECT playing_multigame_id FROM users WHERE user_id = {message.from_user.id};')
                if(len(ss)>0):
                    if(ss[0][2] == 'Dice'):
                        await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption='*У вас есть неоконченная игра*\n'+key_board.game_message_id[list(game_of_id.keys())[list(game_of_id.values()).index(ss[0][2])]].format(ss[0][3],escape(ss[0][4])), parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                    else:
                        await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption='*У вас есть неоконченная игра*\n'+key_board.game_message_id[list(game_of_id.keys())[list(game_of_id.values()).index(ss[0][2])]].format(escape(ss[0][4])), parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                elif(ss1[0][0]==0):
                    idxx = await sql.request_db(f'SELECT balance FROM users WHERE user_id = {message.from_user.id};')
                    idxx = idxx[0]
                    if((float(idxx[0])>=float(message.text.split(' ')[2])) and (float(message.text.split(' ')[2])>=0.2)  and (float(message.text.split(' ')[2])<=700)):
                        players = f'{message.from_user.id}-'
                        reqq = await sql.request_db("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = 'multigames';")
                        multiopen_game_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('▪️ГОТОВ▪️', callback_data=f'{reqq[0][0]}_ready_true')).row(types.InlineKeyboardButton('▪️Войти и заплатить ставку▪️', callback_data=f'{reqq[0][0]}_join_multichat')).row(types.InlineKeyboardButton('▪️Выйти▪️', callback_data=f'{reqq[0][0]}_exit_notstartgame'))
                        usernm = f'@{message.from_user.username}' if message.from_user.username != None else message.from_user.first_name
                        msg = await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=f"{key_board.multigame_shapka_message.format(reqq[0][0], smile_of_game[game_of_id[id_game_of_smile['/'+message.text.split(' ')[1]]]], escape(math.ceil(100*float(message.text.split(' ')[2]))/100), escape(f'{logo_multi[1]}{usernm} | ✔️НЕ ГОТОВ'))}\n{key_board.notready_multigame_message}", reply_markup=multiopen_game_inline, parse_mode="MarkdownV2")
                        await sql.request_db(f"INSERT INTO multigames(type, stavka, players, status, date, message_id, chat_id) VALUES ('{game_of_id[id_game_of_smile['/'+message.text.split(' ')[1]]]}',{math.ceil(100*float(message.text.split(' ')[2]))/100},'{players}',0,NOW(),{msg.message_id},{msg.chat.id});")
                        await sql.request_db(f"UPDATE users SET playing_multigame_id = {reqq[0][0]}, balance = balance - {math.ceil(100*float(message.text.split(' ')[2]))/100} WHERE user_id = {message.from_user.id};")
                    else:
                        await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.error_value_stavka_message, parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                else:
                    await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.link_multi_message.format(ss1[0][0]), parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
            elif('/help' in message.text.lower()):
                await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.help_commands_message, parse_mode='Markdownv2', reply_to_message_id=message.message_id)
            elif((message.text.split(' ')[0][0] == '/' and message.text.split(' ')[0][1].isdigit()) or (message.text == '/info')):
                if(message.text == '/info'):
                    if(message.reply_to_message != None):
                        ids = str(message.reply_to_message.from_user.id)
                    else:
                        ids = str(message.from_user.id)
                else:
                    try:
                        ids = str(message.text.split(' ')[0][1:message.text.index('@')])
                    except:
                        ids = str(message.text.split(' ')[0][1:])
                if(ids.isdigit()):
                    res = await sql.request_db(f'SELECT * FROM users WHERE user_id = {ids};')
                    if(len(res)>0):
                        dat = await sql.request_db(f"SELECT username, dat FROM users WHERE user_id = {ids};")
                        qq = await sql.request_db(f"SELECT COUNT(*) FROM games WHERE user_id = {ids} AND status = 1;")
                        su = await sql.request_db(f"SELECT SUM(result) FROM games WHERE user_id = {ids} AND result>0;")
                        await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.profile_chat_message.format(ids, escape(dat[0][0]), escape(dat[0][1]), qq[0][0], escape(su[0][0])), parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                    else:
                        await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.error_profile_chat_message, reply_to_message_id=message.message_id, parse_mode='MarkdownV2')
            elif((message.text.split(' ')[0] in ['/m','/mult','/bask','/bowl','/darts','/slot','/cube','/🎳','/🎯','/🏀','/🎰','/🎲']) and len(req)==0):
                await bot.send_message(message.chat.id, key_board.comand_not_user_message,parse_mode='MarkdownV2')
            elif(message.text.split(' ')[0] in ['/multi','/dice','/m','/mult','/bask','/bowl','/darts','/slot','/cube','/🎳','/🎯','/🏀','/🎰','/🎲']):
                await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.help_commands_message, parse_mode='Markdownv2', reply_to_message_id=message.message_id)
        except Exception as e:
            await bot.send_message(channel_of_error, '358\n'+str(e))


@dp.message_handler(content_types=[types.ContentType.DICE],chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP])
async def group_handler(message: types.Message):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {message.from_user.id};")
    if(len(is_par)==0):
        try:
            is_par = await sql.request_db(f"SELECT user_id, username, firstname FROM users WHERE user_id = {message.from_user.id};")
            if(len(is_par)==0):
                await bot.send_message(message.chat.id, key_board.exist_start_game_message, parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
            elif(message.forward_from == None):
                if(is_par[0][1] != message.from_user.username):
                    await sql.request_db(f"UPDATE users SET username = '{message.from_user.username}' WHERE user_id = {message.from_user.id};")
                if(is_par[0][2] != message.from_user.first_name):
                    await sql.request_db(f"UPDATE users SET firstname = '{message.from_user.first_name}' WHERE user_id = {message.from_user.id};")
                req = 'SELECT status, playing_multigame_id, playing_game_id_mini FROM users WHERE user_id = '+str(message.from_user.id)+';'
                idx = await sql.request_db(req)
                idx = idx[0]
                req = 'SELECT * FROM games WHERE user_id = '+str(message.from_user.id)+' AND status = 0;'
                idx_ = await sql.request_db(req)
                result = message.dice.value
                if(idx[0] in [14,15,16,17,21,20] and len(idx_)>0):#NEED FIX
                    time.sleep(gamedelay_of_id[idx[0]])
                    if(idx[0]==15 and message.dice.emoji == '⚽'):#543
                        stavka = await sql.request_db(f"SELECT stavka FROM games WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Penalty';")
                        if(result in [3,4,5]):
                            await bot.send_message(message.chat.id, key_board.foot_full_victory_message.format(escape(str(int(150 * stavka[0][0])/100))), parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {0.5 * stavka[0][0]}, count_games = count_games + 1, count_prizes = count_prizes + {int(150 * stavka[0][0])/100}, balance = balance + {int(150 * stavka[0][0])/100}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), status = 23, playing_game_id_mini = 0 WHERE user_id = {message.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {int(150 * stavka[0][0])/100}, result_point = {result} WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Penalty';")
                        else:
                            await bot.send_message(message.chat.id, key_board.lose_mini_message,parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {-1 * stavka[0][0]}, count_games = count_games + 1, status = 23, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), playing_game_id_mini = 0 WHERE user_id = {message.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {-1 * stavka[0][0]}, result_point = {result} WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Penalty';")
                    elif(idx[0]==17 and message.dice.emoji == '🏀'):
                        stavka = await sql.request_db(f"SELECT stavka FROM games WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Basketball';")
                        if(result in [4,5]):
                            await bot.send_message(message.chat.id, key_board.basket_full_victory_message.format(escape(str(int(150 * stavka[0][0])/100))),parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {0.5 * stavka[0][0]}, count_games = count_games + 1, count_prizes = count_prizes + {int(150 * stavka[0][0])/100}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), balance = balance + {int(150 * stavka[0][0])/100}, status = 23, playing_game_id_mini = 0 WHERE user_id = {message.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {int(150 * stavka[0][0])/100}, result_point = {result} WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Basketball';")
                        else:
                            await bot.send_message(message.chat.id, key_board.lose_mini_message,parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {-1 * stavka[0][0]}, count_games = count_games + 1, status = 23, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), playing_game_id_mini = 0 WHERE user_id = {message.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {-1 * stavka[0][0]}, result_point = {result} WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Basketball';")
                    elif(idx[0]==14 and message.dice.emoji == '🎳'):
                        stavka = await sql.request_db(f"SELECT stavka FROM games WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Bowling';")
                        if(result == 5):
                            await bot.send_message(message.chat.id, key_board.bowl_nonfull_victory_message.format(escape(str(stavka[0][0]))),parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {0 * stavka[0][0]}, count_games = count_games + 1, count_prizes = count_prizes + {stavka[0][0]}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), balance = balance + {stavka[0][0]}, status = 23, playing_game_id_mini = 0 WHERE user_id = {message.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {stavka[0][0]}, result_point = {result} WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Bowling';")
                        elif(result == 6):
                            await bot.send_message(message.chat.id, key_board.bowl_full_victory_message.format(escape(str(3 * stavka[0][0]))),parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {2 * stavka[0][0]}, count_games = count_games + 1, count_prizes = count_prizes + {3 * stavka[0][0]}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), balance = balance + {3 * stavka[0][0]}, status = 23, playing_game_id_mini = 0 WHERE user_id = {message.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {3 * stavka[0][0]}, result_point = {result} WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Bowling';")
                        else:
                            await bot.send_message(message.chat.id, key_board.lose_mini_message,parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {-1 * stavka[0][0]}, count_games = count_games + 1, status = 23, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), playing_game_id_mini = 0 WHERE user_id = {message.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {-1 * stavka[0][0]}, result_point = {result} WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Bowling';")
                    elif(idx[0]==16 and message.dice.emoji == '🎯'):
                        stavka = await sql.request_db(f"SELECT stavka FROM games WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Darts';")
                        if(result == 5):
                            await bot.send_message(message.chat.id, key_board.darts_nonfull_victory_message.format(escape(str(stavka[0][0]))),parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {0 * stavka[0][0]}, count_games = count_games + 1, count_prizes = count_prizes + {stavka[0][0]}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), balance = balance + {stavka[0][0]}, status = 23, playing_game_id_mini = 0 WHERE user_id = {message.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {stavka[0][0]}, result_point = {result} WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Darts';")
                        elif(result == 6):
                            await bot.send_message(message.chat.id, key_board.darts_full_victory_message.format(escape(str(3 * stavka[0][0]))),parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {2 * stavka[0][0]}, count_games = count_games + 1, count_prizes = count_prizes + {3 * stavka[0][0]}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), balance = balance + {3 * stavka[0][0]}, status = 23, playing_game_id_mini = 0 WHERE user_id = {message.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {3 * stavka[0][0]}, result_point = {result} WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Darts';")
                        else:
                            await bot.send_message(message.chat.id, key_board.lose_mini_message,parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {-1 * stavka[0][0]}, count_games = count_games + 1, status = 23, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), playing_game_id_mini = 0 WHERE user_id = {message.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {-1 * stavka[0][0]}, result_point = {result} WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Darts';")
                    elif(idx[0]==21 and message.dice.emoji == '🎲'):
                        game = await sql.request_db(f"SELECT * FROM games WHERE user_id = {message.from_user.id} AND (status = 2 OR status = 0) AND type = 'Dice';")
                        target = game[0][3]
                        stavka = game[0][4]
                        if(result == target):
                            await bot.send_message(message.chat.id, key_board.dice_full_victory_message.format(escape(str(stavka * 3))),parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {2 * stavka}, count_games = count_games + 1, count_prizes = count_prizes + {3 * stavka}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka} THEN (need_play_for_withdraw - {stavka}) ELSE (0)end), balance = balance + {stavka * 3}, status = 23, playing_game_id_mini = 0 WHERE user_id = {message.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {3 * stavka}, result_point = {result} WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Dice';")
                        elif((result-target == 1) or (result-target == -1) or (result == 1 and target == 6) or (result == 6 and target == 1)):
                            await bot.send_message(message.chat.id, key_board.dice_nonfull_victory_message.format(escape(str(0.5 * stavka))),parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {-0.5 * stavka}, count_games = count_games + 1, count_prizes = count_prizes + {0.5 * stavka}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka} THEN (need_play_for_withdraw - {stavka}) ELSE (0)end), balance = balance + {0.5 * stavka}, status = 23, playing_game_id_mini = 0 WHERE user_id = {message.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {0.5 * stavka}, result_point = {result} WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Dice';")
                        else:
                            await bot.send_message(message.chat.id, key_board.lose_mini_message,parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {-1 * stavka}, count_games = count_games + 1, status = 23, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka} THEN (need_play_for_withdraw - {stavka}) ELSE (0)end), playing_game_id_mini = 0 WHERE user_id = {message.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {-1 * stavka}, result_point = {result} WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Dice';")
                    elif(idx[0]==20 and message.dice.emoji == '🎰'):
                        stavka = await sql.request_db(f"SELECT stavka FROM games WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Slots';")
                        if(result == 64):
                            await bot.send_message(message.chat.id, key_board.slots777_vict_message.format(escape(str(7 * stavka[0][0]))),parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {6 * stavka[0][0]}, count_games = count_games + 1, count_prizes = count_prizes + {7 * stavka[0][0]}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), balance = balance + {7 * stavka[0][0]}, status = 23, playing_game_id_mini = 0 WHERE user_id = {message.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {7 * stavka[0][0]}, result_point = {result} WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Slots';")
                        elif(result in [43,1,22]):
                            await bot.send_message(message.chat.id, key_board.slots111_vict_message.format(escape(str(3 * stavka[0][0]))),parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {2 * stavka[0][0]}, count_games = count_games + 1, count_prizes = count_prizes + {3 * stavka[0][0]}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), balance = balance + {3 * stavka[0][0]}, status = 23, playing_game_id_mini = 0 WHERE user_id = {message.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {3 * stavka[0][0]}, result_point = {result} WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Slots';")
                        elif(result in [11,59,42,27,41,44]):
                            await bot.send_message(message.chat.id, key_board.slotsLL_vict_message.format(escape(str(2 * stavka[0][0]))),parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {1 * stavka[0][0]}, count_games = count_games + 1, count_prizes = count_prizes + {2 * stavka[0][0]}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), balance = balance + {2 * stavka[0][0]}, status = 23, playing_game_id_mini = 0 WHERE user_id = {message.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {2 * stavka[0][0]}, result_point = {result} WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Slots';")
                        elif(result in [48,61,62,63,60,52,32,56,16]):
                            await bot.send_message(message.chat.id, key_board.slots77_vict_message.format(escape(str(2 * stavka[0][0]))),parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {1 * stavka[0][0]}, count_games = count_games + 1, count_prizes = count_prizes + {2 * stavka[0][0]}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), balance = balance + {2 * stavka[0][0]}, status = 23, playing_game_id_mini = 0 WHERE user_id = {message.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {2 * stavka[0][0]}, result_point = {result} WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Slots';")
                        else:
                            await bot.send_message(message.chat.id, key_board.lose_mini_message,parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {-1 * stavka[0][0]}, count_games = count_games + 1, status = 23, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), playing_game_id_mini = 0 WHERE user_id = {message.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {-1 * stavka[0][0]}, result_point = {result} WHERE user_id = {message.from_user.id} AND status = 0 AND type = 'Slots';")
                    else:
                        await bot.send_message(message.chat.id, key_board.error_smile_game_message, parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                    await send_message(message.from_user.id, key_board.start_menu_message, key_board.start_client_kb_reply)
                elif(idx[0]==29 and len(idx_)>0):
                    num = idx[1]
                    rows = await sql.request_db(f"SELECT type FROM games WHERE id = {idx[2]};")
                    time.sleep(gamedelay_of_smile[smile_of_game[rows[0][0]]])
                    if(smile_of_game[rows[0][0]] == str(message.dice.emoji)):
                        await sql.request_db(f"UPDATE games SET status = 1, result_point = {result} WHERE user_id = {message.from_user.id} AND status = 0;")
                        rows = await sql.request_db(f"SELECT games.id,games.user_id, type, stavka, status, result_point, playing_multigame_id, playing_game_id_mini FROM games INNER JOIN (SELECT user_id, playing_multigame_id, playing_game_id_mini FROM users WHERE playing_multigame_id = {num}) AS T ON T.playing_game_id_mini = games.id;")    
                        is_all = True
                        for i in rows:
                            if(i[4]==0):
                                is_all = False
                        if(is_all):
                            basket, foot, point_games = ['Basketball'], ['Penalty'], ['Dice', 'Darts', 'Bowling']
                            maxk = rows[0][5]
                            k = 0
                            st = ''
                            play = await sql.request_db(f"SELECT players FROM multigames WHERE id= {num};")
                            play = len(play[0][0].split(','))
                            if(rows[0][2] in point_games):
                                for i in rows:
                                    if(i[5] > maxk):
                                        maxk = i[5]
                                for idx, i in enumerate(rows, start = 1):
                                    usern = await sql.request_db(f"Select username, firstname FROM users WHERE user_id = {i[1]};")
                                    usernm = f'@{usern[0][0]}' if usern[0][0] != 'None' else usern[0][1]
                                    if(i[5] == maxk):
                                        k+=1
                                        st += f"👑{escape(usernm)} \| " + "{stavka}\n"
                                    else:
                                        st += f"{logo_multi[idx]}{escape(usernm)} \|\n"
                            elif(rows[0][2] in basket):
                                for idx, i in enumerate(rows, start = 1):
                                    usern = await sql.request_db(f"Select username, firstname FROM users WHERE user_id = {i[1]};")
                                    usernm = f'@{usern[0][0]}' if usern[0][0] != 'None' else usern[0][1]
                                    if(i[5] in [4,5]):
                                        k+=1
                                        st += f"👑{escape(usernm)} \| " + "{stavka}\n"
                                    else:
                                        st += f"{logo_multi[idx]}{escape(usernm)} \|\n"
                            elif(rows[0][2] in foot):
                                for idx, i in enumerate(rows, start = 1):
                                    usern = await sql.request_db(f"Select username, firstname FROM users WHERE user_id = {i[1]};")
                                    usernm = f'@{usern[0][0]}' if usern[0][0] != 'None' else usern[0][1]
                                    if(i[5] in [3,4,5]):
                                        k+=1
                                        st += f"👑{escape(usernm)} \| " + "{stavka}\n"
                                    else:
                                        st += f"{logo_multi[idx]}{escape(usernm)} \|\n"
                            if((k>0) and (k!=play)):
                                if(rows[0][2] in point_games):
                                    for i in rows:
                                        if(i[5] == maxk):
                                            await sql.request_db(f"UPDATE users SET count_prizes = count_prizes + {math.floor(100*komission_casino * play * rows[0][3] / k)/100}, balance = balance + {math.floor(100*komission_casino * play * rows[0][3] / k)/100}, playing_game_id_mini = 0, playing_multigame_id = 0 WHERE user_id = {i[1]};")
                                        await sql.request_db(f"UPDATE users SET count_games = count_games + 1, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {rows[0][3]} THEN (need_play_for_withdraw - {rows[0][3]}) ELSE (0)end), playing_game_id_mini = 0, playing_multigame_id = 0 WHERE user_id = {i[1]};")
                                elif(rows[0][2] in basket):
                                    for i in rows:
                                        if(i[5] in [4,5]):
                                            await sql.request_db(f"UPDATE users SET count_prizes = count_prizes + {math.floor(100*komission_casino * play * rows[0][3] / k)/100}, balance = balance + {math.floor(100*komission_casino * play * rows[0][3] / k)/100}, playing_game_id_mini = 0, playing_multigame_id = 0 WHERE user_id = {i[1]};")
                                        await sql.request_db(f"UPDATE users SET count_games = count_games + 1, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {rows[0][3]} THEN (need_play_for_withdraw - {rows[0][3]}) ELSE (0)end), playing_game_id_mini = 0, playing_multigame_id = 0 WHERE user_id = {i[1]};")
                                elif(rows[0][2] in foot):
                                    for i in rows:
                                        if(i[5] in [3,4,5]):
                                            await sql.request_db(f"UPDATE users SET count_prizes = count_prizes + {math.floor(100*komission_casino * play * rows[0][3] / k)/100}, balance = balance + {math.floor(100*komission_casino * play * rows[0][3] / k)/100} WHERE user_id = {i[1]};")
                                        await sql.request_db(f"UPDATE users SET count_games = count_games + 1, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {rows[0][3]} THEN (need_play_for_withdraw - {rows[0][3]}) ELSE (0)end), playing_game_id_mini = 0, playing_multigame_id = 0 WHERE user_id = {i[1]};")
                                st = st.format(stavka=escape(str(math.floor(100*komission_casino * play * rows[0][3] / k)/100)))
                                await bot.send_message(message.chat.id, key_board.victory_multi_message.format(num, smile_of_game[rows[0][2]],escape(rows[0][3]),st), parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                                row1 = await sql.request_db(f"SELECT message_id FROM multigames WHERE id = {num};")
                                await sql.request_db(f"UPDATE multigames SET status = 1 WHERE id = {num};")
                                try:
                                    await bot.delete_message(message.chat.id, message_id=row1[0][0])
                                except:
                                    pass
                            else:
                                reqq = await sql.request_db("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = 'multigames';")
                                await sql.request_db(f"UPDATE multigames SET status = 3 WHERE id = {num};")
                                play = await sql.request_db(f"SELECT players, type, stavka FROM multigames WHERE id= {num};")
                                msge = ''
                                for i in list(play[0][0].split(',')):
                                    usern = await sql.request_db(f"Select username, firstname FROM users WHERE user_id = {i[:-1]};")
                                    usernm = f'@{usern[0][0]}' if usern[0][0] != 'None' else usern[0][1]
                                    stat = '✔️НЕ ГОТОВ' if i[-1] == '-' else '☑️ГОТОВ'
                                    stat = '✖️ВЫШЕЛ' if i[-1] == '*' else stat
                                    msge += escape(f"{usernm} | {stat}\n")
                                    reqq1 = await sql.request_db("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = 'games';")
                                    reqq1 = reqq1[0][0]
                                    await sql.request_db(f"INSERT INTO games(user_id, type, target_number, stavka, date, status, result) VALUES ({i[:-1]},'{play[0][1]}',1,{play[0][2]},NOW(),0,0);")
                                    await sql.request_db(f"UPDATE users SET playing_game_id_mini = {reqq1}, playing_multigame_id = {reqq[0][0]} WHERE user_id = {i[:-1]};")
                                multiopen_game_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('▪️Выйти▪️', callback_data=f'{reqq[0][0]}_exit_multigame'))
                                row1 = await sql.request_db(f"SELECT message_id FROM multigames WHERE id = {num};")
                                try:
                                    await bot.delete_message(message.chat.id, message_id=row1[0][0])
                                except:
                                    pass
                                msg = await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.draw_multi_message+key_board.multigame_shapka_message.format(reqq[0][0], smile_of_game[play[0][1]], escape(play[0][2]), msge)+key_board.multigame_message_name[play[0][1]], reply_markup=multiopen_game_inline, parse_mode='MarkdownV2')
                                await sql.request_db(f"INSERT INTO multigames(type, stavka, players, status, date, message_id, chat_id) VALUES ('{rows[0][2]}',{rows[0][3]},'{play[0][0]}',2,NOW(),{msg.message_id},{msg.chat.id});")                       
                    else:
                        await bot.send_message(message.chat.id, key_board.error_smile_game_message, parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                else:
                    await bot.send_message(message.chat.id, key_board.exist_start_game_message, parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
            else:
                if(is_par[0][1] != message.from_user.username):
                    await sql.request_db(f"UPDATE users SET username = '{message.from_user.username}' WHERE user_id = {message.from_user.id};")
                if(is_par[0][2] != message.from_user.first_name):
                    await sql.request_db(f"UPDATE users SET firstname = '{message.from_user.first_name}' WHERE user_id = {message.from_user.id};")
                idx = await sql.request_db(f'SELECT status FROM users WHERE user_id = {message.from_user.id};')
                idx = idx[0]
                if(idx[0] in [14,15,16,17,21,20]):
                    idx = await sql.request_db(f'SELECT type, stavka FROM games WHERE user_id = {str(message.from_user.id)} AND status = 0;')
                    idx = idx[0]
                    idx_ = list(game_of_id.keys())[list(game_of_id.values()).index(idx[0])]
                    await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.game_message_id[idx_].format(escape(idx[1]))+'\nПересланные сообщения запрещены\.', parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
                else:
                    await bot.send_animation(message.chat.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.exist_start_game_message, parse_mode='MarkdownV2', reply_to_message_id=message.message_id)
        except Exception as e:
            await bot.send_message(channel_of_error, '585\n'+str(e))


###########################################################
#
#
#                         ADMINKA
#
############################################################
@dp.message_handler(commands=["statistics"],chat_type=[types.ChatType.PRIVATE])
async def cmd_start(message: types.Message):
    if(message.from_user.id in id_admins):
        try:
            sum_ = await sql.request_db(f"SELECT SUM(usd), COUNT(*) FROM active_deposits_bots WHERE status = 1;")
            sum_day = await sql.request_db(f"SELECT SUM(usd), COUNT(*) FROM active_deposits_bots WHERE TIMESTAMPDIFF(DAY,date,CURDATE()) = 0 AND status = 1;")
            count_users = await sql.request_db(f"SELECT COUNT(*) FROM users WHERE subscribe = 1;")
            count_users_day = await sql.request_db(f"SELECT COUNT(*) FROM users WHERE subscribe = 1 AND TIMESTAMPDIFF(DAY,dat,CURDATE()) = 0;")
            count_21 = await sql.request_db(f"SELECT COUNT(*) FROM game_21 WHERE is_closed = 1;")
            count_21_day = await sql.request_db(f"SELECT COUNT(*) FROM game_21 WHERE is_closed = 1 AND TIMESTAMPDIFF(DAY,date,CURDATE()) = 0;")
            sum_21 = await sql.request_db(f"SELECT SUM(stavka * max_players) FROM game_21 WHERE is_closed = 1;")
            sum_21_day = await sql.request_db(f"SELECT SUM(max_players * stavka) FROM game_21 WHERE is_closed = 1 AND TIMESTAMPDIFF(DAY,date,CURDATE()) = 0;")
            sum_games = await sql.request_db(f"SELECT SUM(stavka) FROM games WHERE status = 1;")
            sum_games_day = await sql.request_db(f"SELECT SUM(stavka) FROM games WHERE status = 1  AND TIMESTAMPDIFF(DAY,date,CURDATE()) = 0;")
            sum_multigames = await sql.request_db(f"SELECT SUM(stavka * (1+LENGTH(players)-LENGTH(REPLACE(players, ',','')))) FROM multigames WHERE status = 1;")
            sum_multigames_day = await sql.request_db(f"SELECT SUM(stavka * (1+LENGTH(players)-LENGTH(REPLACE(players, ',','')))) FROM multigames WHERE status = 1  AND TIMESTAMPDIFF(DAY,date,CURDATE()) = 0;")
            count_games = await sql.request_db(f"SELECT COUNT(stavka) FROM games WHERE status = 1;")
            count_games_day = await sql.request_db(f"SELECT COUNT(stavka) FROM games WHERE status = 1  AND TIMESTAMPDIFF(DAY,date,CURDATE()) = 0;")
            count_games_frommulti = await sql.request_db(f"SELECT ((1+LENGTH(players)-LENGTH(REPLACE(players, ',',''))) - (LENGTH(players)-LENGTH(REPLACE(players, '*','')))) FROM multigames WHERE status = 1;");
            count_games_frommulti_day = await sql.request_db(f"SELECT ((1+LENGTH(players)-LENGTH(REPLACE(players, ',',''))) - (LENGTH(players)-LENGTH(REPLACE(players, '*','')))) FROM multigames WHERE status = 1  AND TIMESTAMPDIFF(DAY,date,CURDATE()) = 0;");
            count_multigames = await sql.request_db(f"SELECT COUNT(*) FROM multigames WHERE status = 1;")
            if(len(count_games_frommulti_day)==0):
                count_games_frommulti_day = [[0]]
            if(sum_multigames_day[0][0] is None):
                sum_multigames_day = 0
            else:
                sum_multigames_day = sum_multigames_day[0][0]
            if(sum_multigames[0][0] is None):
                sum_multigames = 0
            else:
                sum_multigames = sum_multigames[0][0]
            if(sum_games[0][0] is None):
                sum_games = 0
            else:
                sum_games = sum_games[0][0]
            if(sum_games_day[0][0] is None):
                sum_games_day = 0
            else:
                sum_games_day = sum_games_day[0][0]
            if(sum_21[0][0] is None):
                sum_21 = 0
            else:
                sum_21 = sum_21[0][0]
            if(sum_21_day[0][0] is None):
                sum_21_day = 0
            else:
                sum_21_day = sum_21_day[0][0]
            if(sum_[0][0] is None):
                sum_0 = 0
            else:
                sum_0 = sum_[0][0]
            if(sum_day[0][0] is None):
                sum_day_0 = 0
            else:
                sum_day_0 = sum_day[0][0]
            if(sum_[0][1] is None):
                sum_1 = 0
            else:
                sum_1 = sum_[0][1]
            if(sum_day[0][1] is None):
                sum_day_1 = 0
            else:
                sum_day_1 = sum_day[0][1]
            count_multigames_day = await sql.request_db(f"SELECT COUNT(*) FROM multigames WHERE status = 1  AND TIMESTAMPDIFF(DAY,date,CURDATE()) = 0;")
            await bot.send_message(message.from_user.id, key_board.statistics_message.format(escape(int(100*sum_day_0)/100), escape(int(100*sum_0)/100), escape(int(100*sum_day_1)/100), escape(int(100*sum_1)/100), count_users_day[0][0], count_users[0][0], count_21_day[0][0], count_21[0][0], escape(int(100*sum_21_day)/100), escape(int(100*sum_21)/100),count_games_day[0][0]-count_games_frommulti_day[0][0], count_games[0][0]-count_games_frommulti[0][0], escape(int(100*(sum_games_day-sum_multigames_day))/100), escape(int(100*(sum_games-sum_multigames))/100),count_multigames_day[0][0], count_multigames[0][0], escape(int(100*sum_multigames_day)/100), escape(int(100*sum_multigames)), escape(int(100*((sum_21_day+sum_multigames_day)*(1-komission_casino)))/100), escape(int(100*((sum_21+sum_multigames)*(1-komission_casino)))/100)), parse_mode = 'MarkdownV2')    
        except Exception as e:
            await bot.send_message(channel_of_error, '660\n'+str(e))

@dp.message_handler(commands=["partners"],chat_type=[types.ChatType.PRIVATE])
async def cmd_start(message: types.Message):
    if(message.from_user.id in id_admins):
        try:
            sum_ = await sql.request_db(f"SELECT GROUP_CONCAT(name SEPARATOR '`, `') FROM partners;")
            await bot.send_message(message.from_user.id, escape('`'+sum_[0][0]+'`').replace('\`','`'), parse_mode = 'MarkdownV2')    
        except Exception as e:
            await bot.send_message(channel_of_error, '669\n'+str(e))


@dp.message_handler(commands=["partner"],chat_type=[types.ChatType.PRIVATE])
async def cmd_start(message: types.Message):
    if(message.from_user.id in id_admins):
        try:
            if(len(message.text.split())<2):
                await bot.send_message(message.from_user.id, key_board.admin_message2, 'MarkdownV2')
            else:
                is_par = await sql.request_db(f"SELECT user_id FROM partners WHERE name = '{' '.join(message.text.split()[1:])}';")
                dat = await sql.request_db(f"SELECT username, dat, count_games, count_prizes FROM users WHERE user_id = {is_par[0][0]};")
                if(len(is_par)==0):
                    await bot.send_message(message.from_user.id, key_board.profile_chat_message.format(is_par[0][0], escape(dat[0][0]), escape(dat[0][1]), dat[0][2], escape(dat[0][3])), 'MarkdownV2')
                else:
                    req = await sql.request_db(f"SELECT * FROM partners WHERE user_id = {is_par[0][0]};")
                    req1 = await sql.request_db(f"SELECT SUM(act.usd), users.from_ref_id FROM users INNER JOIN (SELECT * FROM active_deposits_bots WHERE status = 1) act ON users.user_id = act.user_id GROUP BY from_ref_id HAVING from_ref_id = {is_par[0][0]};")
                    req1 = req1[0][0] * partner_ref if len(req1)>0 else 0
                    req2 = await sql.request_db(f"SELECT SUM(act.usd), users.from_ref_id FROM users INNER JOIN (SELECT * FROM active_deposits_bots WHERE status = 1 AND TIMESTAMPDIFF(DAY,date,CURDATE()) = 0) act ON users.user_id = act.user_id GROUP BY from_ref_id HAVING from_ref_id = {is_par[0][0]};")
                    req2 = req2[0][0] * partner_ref if len(req2)>0 else 0
                    req3 = await sql.request_db(f"SELECT COUNT(*) FROM users WHERE from_ref_id = {is_par[0][0]};")
                    req4 = await sql.request_db(f"SELECT COUNT(*) FROM users WHERE from_ref_id = {is_par[0][0]} AND TIMESTAMPDIFF(DAY,dat,CURDATE()) = 0;")
                    await bot.send_message(message.from_user.id, key_board.partner_profile_message.format(escape(req[0][1]), escape(dat[0][1]), req[0][3], escape(req1), escape(req2), req3[0][0], req4[0][0]), 'MarkdownV2')        
        except Exception as e:
            await bot.send_message(channel_of_error, '693\n'+str(e))


@dp.message_handler(commands=["balanceqiwi"],chat_type=[types.ChatType.PRIVATE])
async def cmd_start(message: types.Message):
    if(message.from_user.id in id_admins):
        try:
            token = await sql.request_db(f"SELECT token FROM qiwi;")
            api = Qiwi(token[0][0])
            info = api.balance(only_balance=True)
            await bot.send_message(message.from_user.id, str(info))    
        except Exception as e:
            await bot.send_message(channel_of_error, '705\n'+str(e))


@dp.message_handler(commands=["admin"],chat_type=[types.ChatType.PRIVATE])
async def cmd_start(message: types.Message):
    if(message.from_user.id in id_admins):
        try:
            req = await sql.request_db(f"SELECT table_name FROM information_schema.tables  where table_schema = 'db_cas';")
            msg = ''
            for i in req:
                msg += f'{i[0]}\n'
            await bot.send_message(message.from_user.id, key_board.admin_message1.format(escape(msg)), parse_mode='MarkdownV2')
            await bot.send_message(message.from_user.id, key_board.admin_message2, parse_mode='MarkdownV2')    
        except Exception as e:
            await bot.send_message(channel_of_error, '719\n'+str(e))
@dp.message_handler(commands=["krik"],chat_type=[types.ChatType.PRIVATE])
async def cmd_start(message: types.Message):
    if(message.from_user.id in id_admins):
        try:
            msg = '''test'''
            kb = None
            if(message.text.split()[1]=='admin'):
                await send_message(message.from_user.id, msg,kb,key=1)
            elif(message.text.split()[1]=='users'):
                suc, los = 0, 0
                users = await sql.request_db(f"SELECT user_id FROM users;")
                for idx, i in enumerate(users):
                    try:
                        await send_message(i[0], msg,kb,key=1)
                        suc += 1
                    except:
                        los += 1
                    if(idx%10==0):
                        for j in id_admins:
                            await send_message(j, f'True: {suc}\nFalse: {los}')
                await send_message(message.from_user.id, 'SUCCESS krik')
        except Exception as e:
            await bot.send_message(channel_of_error, '742\n'+str(e))
@dp.message_handler(commands=["add"],chat_type=[types.ChatType.PRIVATE])
async def cmd_start(message: types.Message):
    if(message.from_user.id in id_admins):
        try:
            await sql.request_db(f"UPDATE users SET balance = balance + {message.text.split()[2]} WHERE user_id = {message.text.split()[1]};")
            await send_message(message.text.split()[1], key_board.adding_message.format(escape(message.text.split()[2])))
            await send_message(message.from_user.id, 'SUCCESS')
        except Exception as e:
            await bot.send_message(channel_of_error, '751\n'+str(e))
@dp.message_handler(commands=["sub"],chat_type=[types.ChatType.PRIVATE])
async def cmd_start(message: types.Message):
    if(message.from_user.id in id_admins):
        try:
            await sql.request_db(f"UPDATE users SET balance = balance - {message.text.split()[2]} WHERE user_id = {message.text.split()[1]};")
            await send_message(message.from_user.id, 'SUCCESS')
        except Exception as e:
            await bot.send_message(channel_of_error, '759\n'+str(e))
@dp.message_handler(commands=["blacklist"],chat_type=[types.ChatType.PRIVATE])
async def cmd_start(message: types.Message):
    if(message.from_user.id in id_admins):
        try:
            await sql.request_db(f"INSERT INTO blacklist(user_id) VALUES ({message.text.split()[1]});")
            await send_message(message.from_user.id, 'SUCCESS')
        except Exception as e:
            await bot.send_message(channel_of_error, '767\n'+str(e))
@dp.message_handler(commands=["info"],chat_type=[types.ChatType.PRIVATE])
async def cmd_start(message: types.Message):
    if(message.from_user.id in id_admins):
        try:
            req = await sql.request_db(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = '{message.text.split()[1]}';")
            msg = ''
            for i in req:
                msg += f'{i[0]}\n'
            await send_message(message.from_user.id, f'Столбцы:\n{escape(msg)}')
        except Exception as e:
            await bot.send_message(channel_of_error, '778\n'+str(e))
@dp.message_handler(commands=["request"],chat_type=[types.ChatType.PRIVATE])
async def cmd_start(message: types.Message):
    if(message.from_user.id in id_admins):
        try:
            req = await sql.request_db(' '.join(message.text.split()[1:]))
            if(len(req)<2):
                msg = ''
                for i in req:
                    msg += f'{i[0]}\n'
                await send_message(message.from_user.id, f'{escape(msg)}')
            else:
                await sql.request_db(f'''{message.text.split()[1]} INTO OUTFILE '/mysql-files/temp.csv' FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n';''')  
                await bot.send_document(message.from_user.id, open('/mysql-files/temp.csv', 'rb'))          
        except Exception as e:
            await bot.send_message(channel_of_error, '793\n'+str(e))




###########################################################
#
#
#
#
############################################################

# Хэндлер на команду /start
@dp.message_handler(commands=["start"],chat_type=[types.ChatType.PRIVATE])
async def cmd_start(message: types.Message):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {message.from_user.id};")
    if(len(is_par)==0):
        try:
            req = "SELECT subscribe, username, firstname FROM users WHERE user_id = " + str(message.from_user.id) + ";"
            is_client = await sql.request_db(req)
            if (len(is_client) == 0):
                msg = await bot.send_message(message.from_user.id, key_board.welcome_message, reply_markup=key_board.start_welcome_kb, parse_mode='MarkdownV2')
                if(message.from_user.username==None):
                    req = 'INSERT INTO users VALUES ('+str(message.from_user.id)+",'None','"+str(message.from_user.first_name)+"',20,0,0,0,'None',0,0,0.0,1,"+str(msg.message_id)+",0,0,0,0,1,CURDATE());"
                else:
                    req = 'INSERT INTO users VALUES ('+str(message.from_user.id)+",'"+str(message.from_user.username)+"','"+str(message.from_user.first_name)+"',20,0,0,1,'None',0,0,0.0,0,"+str(msg.message_id)+",0,0,0,0,1,CURDATE());"
                await sql.request_db(req)
                await asyncio.sleep(3)
                await send_message(message.from_user.id, key_board.reklama_message, reply = None)
            elif(is_client[0][0]==1):
                if(is_client[0][1]!=message.from_user.username):
                    await sql.request_db(f"UPDATE users SET username = '{message.from_user.username}' WHERE user_id = {message.from_user.id};")
                if(is_client[0][2]!=message.from_user.first_name):
                    await sql.request_db(f"UPDATE users SET firstname = '{message.from_user.first_name}' WHERE user_id = {message.from_user.id};")
                sq = await sql.request_db(f"SELECT address FROM users WHERE user_id = {message.from_user.id};")
                req = "UPDATE addresses SET status = 0  WHERE status = 1 AND address = '"+sq[0][0]+"';"
                await sql.request_db(req)
                req = 'SELECT last_message_bot FROM users WHERE user_id = '+str(message.from_user.id)+';'
                idx = await sql.request_db(req)
                idx = idx[0]
                try:
                    await bot.delete_message(message.from_user.id, idx[0])
                except:
                    pass
                msg = await bot.send_dice(message.from_user.id, emoji='🎰', reply_markup=key_board.start_client_kb_reply)
                msg = await bot.send_animation(message.from_user.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA', caption=key_board.start_menu_message, reply_markup=key_board.start_client_kb_inline, parse_mode='MarkdownV2')#анимация, лого, кубик или что-то в этом роде
                req = 'UPDATE users SET last_message_bot = '+str(msg.message_id)+' WHERE user_id = '+str(message.from_user.id)+';'
                await sql.request_db(req)
            else:
                await send_message(message.from_user.id, key_board.welcome_message, key_board.start_welcome_kb)
            if(len(message.text.split(' ')) == 2):
                if(len(message.text.split(' ')[1]) == 15):
                    req = "SELECT value, from_user_id FROM gifts WHERE is_activated = 0 AND text = '" + str(message.text.split(' ')[1]) +"';"
                    is_exist_code = await sql.request_db(req)
                    if (len(is_exist_code) > 0):
                        req = 'UPDATE users SET balance = balance + '+str(is_exist_code[0][0])+', need_play_for_withdraw = need_play_for_withdraw + '+str(is_exist_code[0][0])+' WHERE user_id = '+str(message.from_user.id)+';'
                        await sql.request_db(req)
                        req = 'UPDATE gifts SET is_activated = 1, to_user_id = '+str(message.from_user.id)+" WHERE text = '" + str(message.text.split(' ')[1]) +"';"
                        await sql.request_db(req)
                        await send_message(message.from_user.id, key_board.activate_promo_message.format(escape(str(is_exist_code[0][0]))))
                        await send_message(int(is_exist_code[0][1]), key_board.from_activate_promo_message.format(message.text.split(' ')[1], escape(str(is_exist_code[0][0]))))
                elif((len(message.text.split(' ')[1]) > 8) and (len(message.text.split(' ')[1]) <12) and message.text.split(' ')[1].isdigit()):
                    req = "SELECT from_ref_id FROM users WHERE user_id = " + str(message.from_user.id) + ";"
                    is_client = await sql.request_db(req)
                    is_client = is_client[0][0]
                    if (int(is_client) == 1):
                        req = 'UPDATE users SET from_ref_id = '+str(message.text.split(' ')[1])+' WHERE user_id = '+str(message.from_user.id)+';'
                        await sql.request_db(req)
                        usernm = None
                        if(message.from_user.username==None):
                            usernm = 'None'
                        else:
                            usernm = escape(message.from_user.username)
                        await send_message(int(message.text.split(' ')[1]), key_board.new_ref_message.format(usernm))
            await bot.delete_message(message.from_user.id, message.message_id)
        except Exception as e:
            await bot.send_message(channel_of_error, '867\n'+str(e))

#Проверка на подписку
@dp.callback_query_handler(lambda c: c.data == 'subscribe')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            user_channel_status = await bot.get_chat_member(chat_id=id_chat_bot, user_id=callback_query.from_user.id)
            if user_channel_status["status"] != 'left':
                req = 'UPDATE users SET subscribe = 1 WHERE user_id = '+str(callback_query.from_user.id)+';'
                await sql.request_db(req)
                req = 'SELECT last_message_bot FROM users WHERE user_id = '+str(callback_query.from_user.id)+';'
                idx = await sql.request_db(req)
                idx = idx[0]
                try:
                    await bot.delete_message(callback_query.from_user.id, idx[0])
                except:
                    pass
                msg = await bot.send_dice(callback_query.from_user.id, emoji='🎰', reply_markup=key_board.start_client_kb_reply)
                msg = await bot.send_animation(callback_query.from_user.id, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA', caption=key_board.start_menu_message, reply_markup=key_board.start_client_kb_inline, parse_mode='MarkdownV2')#анимация, лого, кубик или что-то в этом роде
                req = 'UPDATE users SET last_message_bot = '+str(msg.message_id)+' WHERE user_id = '+str(callback_query.from_user.id)+';'
                await sql.request_db(req)
            else:
                pass
            await bot.answer_callback_query(callback_query.id)
        except Exception as e:
            await bot.send_message(channel_of_error, '894\n'+str(e))
#########################################################
#          ##      ##      #   #   #####    ##
#          #  #   #  #     # #     #___     # #
#          ##     #  #     # #     #        ##
#          #       ##      #   #   #####    # #
#########################################################

@dp.callback_query_handler(lambda c: c.data == 'poker_menu')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        tbs = await sql.request_db(f"SELECT * FROM boards_poker_draw;")
        _kb = types.InlineKeyboardMarkup()
        for i in tbs:
            cnt = await poker_list[int(i[0])-1].count_players()
            _kb.row(types.InlineKeyboardButton(f'{i[1]} {cnt}/9 {i[3]} {i[4]}', callback_data=f'{i[0]}_add_poker'))
        await send_message(callback_query.from_user.id, '''Выберите стол''', _kb)


@dp.callback_query_handler(lambda c: '_add_poker' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        q = int(callback_query.data[0:callback_query.data.index('_')])
        await poker_list[q-1].new_player(callback_query.from_user.id)


@dp.callback_query_handler(lambda c: '_check_poker' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        q = int(callback_query.data[0:callback_query.data.index('_')])
        await poker_list[q-1].check_player(callback_query.from_user.id)


@dp.callback_query_handler(lambda c: '_fold_poker' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        q = int(callback_query.data[0:callback_query.data.index('_')])
        await poker_list[q-1].fold_player(callback_query.from_user.id)


@dp.callback_query_handler(lambda c: '_call_poker' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        q = int(callback_query.data[0:callback_query.data.index('_')])
        await poker_list[q-1].call_player(callback_query.from_user.id)


@dp.callback_query_handler(lambda c: '_raise_poker' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        q = int(callback_query.data[0:callback_query.data.index('_')])
        await poker_list[q-1].raise_player(callback_query.from_user.id)


@dp.callback_query_handler(lambda c: '_retraise_poker' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        q = int(callback_query.data[0:callback_query.data.index('_')])
        await poker_list[q-1].retraise_player(callback_query.from_user.id)




#########################################################
#
#
#
#########################################################

#######
#      ИГРЫ В ЧАТЕ
#
#######

@dp.callback_query_handler(lambda c: c.data == 'i_tc')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        await send_message(callback_query.from_user.id, key_board.i_tc_message, key = 1)


@dp.callback_query_handler(lambda c: '_ready_true' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            q = callback_query.data[0:callback_query.data.index('_')]
            req = await sql.request_db(f'SELECT * FROM multigames WHERE id = {q} AND status = 0;')
            if(len(req)==0):
                pass
            else:
                players = req[0][3]
                if(str(callback_query.from_user.id) in players):
                    if(f'{callback_query.from_user.id}-' in players):
                        players = players.replace(f'{callback_query.from_user.id}-', f'{callback_query.from_user.id}+')
                    else:
                        players = players.replace(f'{callback_query.from_user.id}+', f'{callback_query.from_user.id}-')
                    if((players.count(',')+1 == players.count('+')) and (players.count('+') > 1)):
                        await sql.request_db(f"UPDATE multigames SET players = '{players}', status = 2, date = NOW() WHERE id = {q};")
                        msg = ''
                        reqq = await sql.request_db(f"SELECT link FROM chats WHERE chat_id = '{req[0][-2]}';")
                        link_game_kb_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('К ИГРЕ', url = reqq[0][0]))
                        for idx, i in enumerate(players.split(','), start = 1):
                            await send_message(i[:-1], key_board.notif_startgame_message.format(q), link_game_kb_inline, mode='MarkdownV2', key = 1)
                            usern = await sql.request_db(f"Select username, firstname FROM users WHERE user_id = {i[:-1]};")
                            usernm = f"@{usern[0][0]}" if usern[0][0] != 'None' else usern[0][1]
                            stat = '✔️НЕ ГОТОВ' if i[-1] == '-' else '☑️ГОТОВ'
                            stat = '✖️ВЫШЕЛ' if i[-1] == '*' else stat
                            msg += escape(f"{logo_multi[idx]}{usernm} | {stat}\n")
                            reqq = await sql.request_db("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = 'games';")
                            reqq = reqq[0][0]
                            await sql.request_db(f"INSERT INTO games(user_id, type, target_number, stavka, date, status, result) VALUES ({i[:-1]},'{req[0][1]}',1,{req[0][2]},NOW(),0,0);")
                            await sql.request_db(f"UPDATE users SET playing_game_id_mini = {reqq}, status = 29 WHERE user_id = {i[:-1]};")
                        msg = key_board.multigame_shapka_message.format(req[0][0],smile_of_game[req[0][1]],escape(req[0][2]), msg)
                        msg += key_board.multigame_message_name[req[0][1]]
                        multiopen_game_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('▪️Выйти▪️', callback_data=f'{q}_exit_multigame'))
                        mesg = await bot.send_animation(req[0][-2], 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=msg,parse_mode='MarkdownV2', reply_markup=multiopen_game_inline)
                        await sql.request_db(f"UPDATE multigames SET message_id = {mesg.message_id} WHERE id = {q};")
                    else:
                        await sql.request_db(f"UPDATE multigames SET players = '{players}' WHERE id = {q};")
                        msg = ''
                        for idx, i in enumerate(players.split(','), start = 1):
                            stat = '✔️НЕ ГОТОВ' if i[-1] == '-' else '☑️ГОТОВ'
                            stat = '✖️ВЫШЕЛ' if i[-1] == '*' else stat
                            usern = await sql.request_db(f"Select username, firstname FROM users WHERE user_id = {i[:-1]};")
                            usernm = f"@{usern[0][0]}" if usern[0][0] != 'None' else usern[0][1]
                            msg += escape(f"{logo_multi[idx]}{usernm} | {stat}\n")
                        msg = f"{key_board.multigame_shapka_message.format(req[0][0],smile_of_game[req[0][1]],escape(req[0][2]), msg)}{key_board.notready_multigame_message}"
                        if(req[0][-1]=='0'):
                            multiopen_game_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('▪️ГОТОВ▪️', callback_data=f'{q}_ready_true')).row(types.InlineKeyboardButton('▪️Войти и заплатить ставку▪️', callback_data=f'{q}_join_multichat')).row(types.InlineKeyboardButton('▪️Выйти▪️', callback_data=f'{q}_exit_notstartgame'))
                        else:
                            multiopen_game_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('▪️ГОТОВ▪️', callback_data=f'{q}_ready_true')).row(types.InlineKeyboardButton('▪️Выйти▪️', callback_data=f'{q}_exit_notstartgame'))
                    await bot.edit_message_caption(caption=msg, chat_id=req[0][-2], message_id=req[0][-3], reply_markup=multiopen_game_inline, parse_mode='MarkdownV2')
                else:
                    await bot.answer_callback_query(callback_query_id=callback_query.id, show_alert=True, text=key_board.keep_tojoin_game_message)
        except Exception as e:
            await bot.send_message(channel_of_error, '964\n'+str(e))


@dp.callback_query_handler(lambda c: '_join_multichat' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            q = callback_query.data[0:callback_query.data.index('_')]
            req = await sql.request_db(f'SELECT * FROM multigames WHERE id = {q} AND status = 0;')
            req1 = await sql.request_db(f'SELECT playing_multigame_id FROM users WHERE user_id = {callback_query.from_user.id};')
            if(len(req)==0 or req1[0][0]!=0 or (req[0][3].count(str(callback_query.from_user.id)) == 1)):
                if(req1[0][0]!=0):
                    await callback_query.answer(key_board.player_another_start_game_message, show_alert = True)
            else:
                bal = await sql.request_db(f'SELECT balance FROM users WHERE user_id = {callback_query.from_user.id};')
                if(float(req[0][2])<=float(bal[0][0])):
                    await sql.request_db(f'UPDATE users SET balance = balance - {req[0][2]},playing_multigame_id = {q} WHERE user_id = {callback_query.from_user.id};')
                    players = req[0][3] + f',{callback_query.from_user.id}-'
                    multiopen_game_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('▪️ГОТОВ▪️', callback_data=f'{q}_ready_true')).row(types.InlineKeyboardButton('▪️Войти и заплатить ставку▪️', callback_data=f'{q}_join_multichat')).row(types.InlineKeyboardButton('▪️Выйти▪️', callback_data=f'{q}_exit_notstartgame'))
                    if(players.count(',') == 5):
                        players = players.replace('-', '+', 6)
                        await sql.request_db(f"UPDATE multigames SET players = '{players}', status = 2, date = NOW() WHERE id = {q};")
                        multiopen_game_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('▪️Выйти▪️', callback_data=f'{q}_exit_multigame'))
                        msg = ''
                        for idx, i in enumerate(players.split(','), start = 1):
                            usern = await sql.request_db(f"Select username, firstname FROM users WHERE user_id = {i[:-1]};")
                            usernm = f'@{usern[0][0]}' if usern[0][0] != 'None' else usern[0][1]
                            stat = '✖️ВЫШЕЛ' if i[-1] == '*' else '☑️ГОТОВ'
                            msg += escape(f"{logo_multi[idx]}{usernm} | {stat}\n")
                            reqq = await sql.request_db("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = 'games';")
                            reqq = reqq[0][0]
                            await sql.request_db(f"INSERT INTO games(user_id, type, target_number, stavka, date, status, result) VALUES ({i[:-1]},'{req[0][1]}',1,{req[0][2]},NOW(),0,0);")
                            await sql.request_db(f"UPDATE users SET playing_game_id_mini = {reqq}, status = 29 WHERE user_id = {i[:-1]};")
                        msg = key_board.multigame_shapka_message.format(req[0][0],smile_of_game[req[0][1]],escape(req[0][2]), msg)
                        msg += key_board.multigame_message_name[req[0][1]]
                        multiopen_game_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('▪️Выйти▪️', callback_data=f'{q}_exit_multigame'))
                    else:
                        await sql.request_db(f"UPDATE multigames SET players = '{players}' WHERE id = {q};")
                        msg = ''
                        for idx, i in enumerate(players.split(','), start = 1):
                            usern = await sql.request_db(f"Select username, firstname FROM users WHERE user_id = {i[:-1]};")
                            usernm = f"@{usern[0][0]}" if usern[0][0] != 'None' else usern[0][1]
                            stat = '✔️НЕ ГОТОВ' if i[-1] == '-' else '☑️ГОТОВ'
                            stat = '✖️ВЫШЕЛ' if i[-1] == '*' else stat
                            fisrt = await sql.request_db(f"SELECT firstname FROM users WHERE user_id = {i[:-1]};")
                            msg += escape(f"{logo_multi[idx]}{usernm} | {stat}\n")
                        msg = f"{key_board.multigame_shapka_message.format(req[0][0],smile_of_game[req[0][1]],escape(req[0][2]), msg)}\n{key_board.notready_multigame_message}"
                    await bot.edit_message_caption(caption=msg, chat_id=req[0][-2], message_id=req[0][-3], reply_markup=multiopen_game_inline, parse_mode='MarkdownV2')
                else:
                    await bot.answer_callback_query(callback_query_id=callback_query.id, show_alert=True, text=key_board.not_enough_balance_message)
        except Exception as e:
            await bot.send_message(channel_of_error, '1016\n'+str(e))

#выход из неначавшейся мультиигры
@dp.callback_query_handler(lambda c: '_exit_notstartgame' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            q = callback_query.data[0:callback_query.data.index('_')]
            req = await sql.request_db(f'SELECT * FROM multigames WHERE id = {q} AND status = 0;')
            if(len(req)==0):
                pass
            else:
                players = req[0][3]
                try:
                    players = players.replace(f'{callback_query.from_user.id}-', '')
                    players = players.replace(f',,', ',')
                except:
                    players = players.replace(f'{callback_query.from_user.id}+', '')
                    players = players.replace(f',,', ',')
                if(len(players)>0):
                    if players[-1] == ',':
                        players = players[:-1]
                    if players[0] == ',':
                        players = players[1:]
                    await sql.request_db(f"UPDATE multigames SET players = '{players}' WHERE id = {q};")
                await sql.request_db(f"UPDATE users SET playing_multigame_id = 0, playing_game_id_mini = 0, status = 0 WHERE user_id = {callback_query.from_user.id};")
                req1 = await sql.request_db(f'SELECT * FROM users WHERE playing_multigame_id = {q};')
                if(len(req1)>0):
                    msg = ''
                    for idx, i in enumerate(players.split(','), start = 1):
                        usern = await sql.request_db(f"Select username, firstname FROM users WHERE user_id = {i[:-1]};")
                        usernm = f'@{usern[0][0]}' if usern[0][0] != 'None' else usern[0][1]
                        stat = '✔️НЕ ГОТОВ' if i[-1] == '-' else '☑️ГОТОВ'
                        stat = '✖️ВЫШЕЛ' if i[-1] == '*' else stat
                        msg += escape(f"{logo_multi[idx]}{usernm} | {stat}\n")
                    msg = f"{key_board.multigame_shapka_message.format(req[0][0],smile_of_game[req[0][1]],escape(req[0][2]), msg)}\n{key_board.notready_multigame_message}"
                    multiopen_game_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('▪️ГОТОВ▪️', callback_data=f'{q}_ready_true')).row(types.InlineKeyboardButton('▪️Войти и заплатить ставку▪️', callback_data=f'{q}_join_multichatchat')).row(types.InlineKeyboardButton('▪️Выйти▪️', callback_data=f'{q}_exit_notstartgame'))
                    await bot.edit_message_caption(caption=msg, chat_id=req[0][-2], message_id=req[0][-3], reply_markup=multiopen_game_inline, parse_mode='MarkdownV2')
                else:
                    await bot.delete_message(chat_id=req[0][-2], message_id=req[0][-3])
                    await sql.request_db(f"UPDATE multigames SET status = -1 WHERE id = {q};")
        except Exception as e:
            await bot.send_message(channel_of_error, '1059\n'+str(e))


#выход из начавшейся мультиигры
@dp.callback_query_handler(lambda c: '_exit_multigame' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            q = callback_query.data[0:callback_query.data.index('_')]
            req = await sql.request_db(f'SELECT * FROM multigames WHERE id = {q} AND status = 2;')
            req1 = await sql.request_db(f'SELECT * FROM users WHERE user_id = {callback_query.from_user.id} AND playing_multigame_id = {q};')
            if(len(req)==0 or len(req1)==0):
                pass
            else:
                players = req[0][3]
                if(players.count(f'{callback_query.from_user.id}+') == 1):
                    players = players.replace(f'{callback_query.from_user.id}+', f'{callback_query.from_user.id}/')
                    await sql.request_db(f"UPDATE multigames SET players = '{players}' WHERE id = {q};")
                    await bot.answer_callback_query(callback_query_id=callback_query.id, show_alert=True, text=key_board.leave_without_dep_message.format())
                elif(players.count(f'{callback_query.from_user.id}/') == 1):
                    await sql.request_db(f"UPDATE users SET playing_multigame_id = 0, playing_game_id_mini = 0, status = 0 WHERE user_id = {callback_query.from_user.id};")
                    await sql.request_db(f"UPDATE games SET status = -1 WHERE user_id = {callback_query.from_user.id} AND status = 0;")
                    msg = ''
                    players = players.replace(f'{callback_query.from_user.id}/', f'{callback_query.from_user.id}*')
                    for idx, i in enumerate(players.split(','), start = 1):
                        usern = await sql.request_db(f"Select username, firstname FROM users WHERE user_id = {i[:-1]};")
                        usernm = f'@{usern[0][0]}' if usern[0][0] != 'None' else usern[0][1]
                        stat = '✔️НЕ ГОТОВ' if i[-1] == '-' else '☑️ГОТОВ'
                        stat = '✖️ВЫШЕЛ' if i[-1] == '*' else stat
                        msg += escape(f"{logo_multi[idx]}{usernm} | {stat}\n")
                    msg = f"{key_board.multigame_shapka_message.format(req[0][0],smile_of_game[req[0][1]],escape(req[0][2]), msg)}\n{key_board.notready_multigame_message}"
                    await sql.request_db(f"UPDATE multigames SET players = '{players}' WHERE id = {q};")
                    multiopen_game_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('▪️Выйти▪️', callback_data=f'{q}_exit_multigame'))
                    msg += key_board.multigame_message_name[req[0][1]]
                    await bot.edit_message_caption(caption=msg, chat_id=req[0][-2], message_id=req[0][-3], reply_markup=multiopen_game_inline, parse_mode='MarkdownV2')
                    play = await sql.request_db(f"SELECT players,stavka, type FROM multigames WHERE id= {q};")
                    play1 = play[0][0].count('+') + play[0][0].count('/')
                    if(play1 == 1):
                        st = ''
                        play1 = play[0][0].count('+') + play[0][0].count('/') + play[0][0].count('*')
                        for idx, i in enumerate(play[0][0].split(','), start = 1):
                            if(i[-1] == '+'):
                                usern = await sql.request_db(f"Select username, firstname FROM users WHERE user_id = {i[:-1]};")
                                usernm = f'@{usern[0][0]}' if usern[0][0] != 'None' else usern[0][1]
                                st += f"👑{escape(usernm)} \| " + "\n К сожалению, игроки вышли из комнаты\.\.\.\n_Вам была возвращена ставка в *полном размере*_"
                                await sql.request_db(f"UPDATE games SET status = -1 WHERE user_id = {i[:-1]} AND status = 0;")
                                await sql.request_db(f"UPDATE users SET count_games = count_games + 1, count_prizes = count_prizes + {play[0][1]}, playing_multigame_id = 0, playing_game_id_mini = 0, balance = balance + {play[0][1]} WHERE user_id = {i[:-1]};")
                        st = st.format()
                        await sql.request_db(f"UPDATE multigames SET status = 3 WHERE id = {q};")
                        await bot.send_animation(req[0][-2], 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.victory_multi_message[:-27].format(q,smile_of_game[play[0][2]], escape(play[0][1]),st), parse_mode='MarkdownV2', reply_to_message_id=req[0][-3])
                        await bot.delete_message(chat_id=req[0][-2], message_id=req[0][-3])
        except Exception as e:
            await bot.send_message(channel_of_error, '1112\n'+str(e))

@dp.callback_query_handler(lambda c: '_join_rb_bot' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            q = int(callback_query.data[0:callback_query.data.index('_')])
            req = await sql.request_db(f"SELECT chat_id FROM rb_game WHERE id = {q};")
            reqq = await sql.request_db(f"SELECT link FROM chats WHERE chat_id = '{req[0][0]}';")
            link_game_kb_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('К ИГРЕ', url = reqq[0][0]))
            await send_message(callback_query.from_user.id, f'''Чтобы подключиться к игре перейдите по ссылке в чат и найдите сообщение с данной игрой по поиску \#RB{q}''', reply=link_game_kb_inline)
        except Exception as e:
            await bot.send_message(channel_of_error, '1125\n'+str(e))

#подключение к публичной игре через бота
@dp.callback_query_handler(lambda c: '_join_multi_bot' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            q = int(callback_query.data[0:callback_query.data.index('_')])
            req = await sql.request_db(f"SELECT * FROM multigames WHERE id = {q} AND status = 0;")
            if(len(req)>0):
                players = req[0][3]
                msg = ''
                for idx, i in enumerate(players.split(','), start = 1):
                    usern = await sql.request_db(f"Select username, firstname FROM users WHERE user_id = {i[:-1]};")
                    usernm = f"@{usern[0][0]}" if usern[0][0] != 'None' else usern[0][1]
                    stat = '✔️НЕ ГОТОВ' if i[-1] == '-' else '☑️ГОТОВ'
                    stat = '✖️ВЫШЕЛ' if i[-1] == '*' else stat
                    msg += escape(f"{logo_multi[idx]}{usernm} | {stat}\n")
                    msg = key_board.multigame_shapka_message.format(req[0][0],smile_of_game[req[0][1]],escape(req[0][2]), msg)
                    msg += key_board.notready_multigame_message
                    if(req[0][-1]=='0'):
                        multiopen_game_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('▪️ГОТОВ▪️', callback_data=f'{q}_ready_true')).row(types.InlineKeyboardButton('▪️Войти и заплатить ставку▪️', callback_data=f'{q}_join_multichat')).row(types.InlineKeyboardButton('▪️Выйти▪️', callback_data=f'{q}_exit_notstartgame'))
                    else:
                        multiopen_game_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('▪️ГОТОВ▪️', callback_data=f'{q}_ready_true')).row(types.InlineKeyboardButton('▪️Выйти▪️', callback_data=f'{q}_exit_notstartgame'))
                try:
                    await bot.delete_message(req[0][-2], req[0][-3])
                except:
                    pass
                mesg = await bot.send_animation(req[0][-2], 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=msg,parse_mode='MarkdownV2', reply_markup=multiopen_game_inline)
                await sql.request_db(f"UPDATE multigames SET message_id = {mesg.message_id} WHERE id = {q};")
                reqq = await sql.request_db(f"SELECT link FROM chats WHERE chat_id = '{req[0][-2]}';")
                link_game_kb_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('К ИГРЕ', url = reqq[0][0]))
                await send_message(callback_query.from_user.id, key_board.link_multi_message.format(q), reply=link_game_kb_inline)
        except Exception as e:
            await bot.send_message(channel_of_error, '1160\n'+str(e))


#создание приватной мультиигры
@dp.callback_query_handler(lambda c: c.data == 'create_multi_private')
async def process_callback_creating(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            req = await sql.request_db(f"SELECT * FROM users WHERE user_id = {callback_query.from_user.id} AND playing_multigame_id = 0;")
            if(len(req)>0):
                await send_message(callback_query.from_user.id, key_board.multi_games_message, reply=key_board.multi_games_inline)
            else:
                await send_message(callback_query.from_user.id, key_board.player_another_start_game_message)
        except Exception as e:
            await bot.send_message(channel_of_error, '1175\n'+str(e))


#join приватной мультиигры
@dp.callback_query_handler(lambda c: c.data == 'join_multichat_private')
async def process_callback_creating(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            req = await sql.request_db(f"SELECT * FROM users WHERE user_id = {callback_query.from_user.id} AND playing_multigame_id = 0;")
            if(len(req)>0):
                await sql.request_db(f"UPDATE users SET status = 31 WHERE user_id = {callback_query.from_user.id};")
                await send_message(callback_query.from_user.id, key_board.input_pass_message, reply=key_board.input_pass_kb_inline)
            else:
                await send_message(callback_query.from_user.id, key_board.player_another_start_game_message)
        except Exception as e:
            await bot.send_message(channel_of_error, '1191\n'+str(e))


#вывод игровых комнат
@dp.callback_query_handler(lambda c: '_game_in_chat' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            await sql.request_db(f"UPDATE users SET status = 34 WHERE user_id = {callback_query.from_user.id};")
            q = int(callback_query.data[0:callback_query.data.index('_')])
            qq = await sql.request_db(f"SELECT id, chat_id, password FROM multigames WHERE (status = 0 OR status = 2) AND players LIKE '%{callback_query.from_user.id}%';")
            msg, menu_game_kb_inline = None, None
            if(len(qq)==0):
                msg = key_board.chat_multigame_message
                menu_game_kb_inline = deepcopy(key_board.shapka_menu_kb_inline)
                req = await sql.request_db(f"SELECT id, type, stavka, count, status, password, chat_id FROM multigames INNER JOIN (SELECT COUNT(user_id) AS count, playing_multigame_id FROM users GROUP BY playing_multigame_id) AS T ON id = playing_multigame_id HAVING status = 0 AND password = '0' LIMIT 5 OFFSET {q*5};")
                reqrb = await sql.request_db(f"SELECT id, stavka, chat_id FROM rb_game WHERE players NOT LIKE '%:_%' LIMIT 1 OFFSET {q*1};")
                sumrb = await sql.request_db(f"SELECT COUNT(*) FROM rb_game WHERE players NOT LIKE '%:_%';")
                reqq = await sql.request_db(f"SELECT COUNT(*) FROM multigames WHERE status = 0 AND password = '0';")
                for i in req:
                    if(i[-1]==str(id_chat_bot)):
                        menu_game_kb_inline.add(types.InlineKeyboardButton(text=f'{smile_of_game[i[1]]}  Ставка: {i[2]}$,  игроков {i[3]}/6', callback_data=f'{i[0]}_join_multi_bot'))
                    else:
                        menu_game_kb_inline.add(types.InlineKeyboardButton(text=f'©️{smile_of_game[i[1]]}  Ставка: {i[2]}$,  игроков {i[3]}/6', callback_data=f'{i[0]}_join_multi_bot'))
                for i in reqrb:
                    if(i[-1]==str(id_chat_bot)):
                        menu_game_kb_inline.add(types.InlineKeyboardButton(text=f'❤RB♠  Ставка: {i[1]}$', callback_data=f'{i[0]}_join_rb_bot'))
                    else:
                        menu_game_kb_inline.add(types.InlineKeyboardButton(text=f'©️❤RB♠  Ставка: {i[1]}$', callback_data=f'{i[0]}_join_rb_bot'))
                if(q==0 and (reqq[0][0]+sumrb[0][0])>6):
                    menu_game_kb_inline.add(types.InlineKeyboardButton(text=f'Далее', callback_data=f'{q+1}_game_in_chat'))
                elif(q==int((reqq[0][0]+sumrb[0][0])/6) and q>0):
                    menu_game_kb_inline.add(types.InlineKeyboardButton(text=f'Назад', callback_data=f'{q-1}_game_in_chat'))
                elif(q>0 and q!=int((reqq[0][0]+sumrb[0][0])/6)):
                    menu_game_kb_inline.add(types.InlineKeyboardButton(text=f'Назад', callback_data=f'{q-1}_game_in_chat'), types.InlineKeyboardButton(text=f'Далее', callback_data=f'{q+1}_game_in_chat'))
            elif(qq[0][2]=='0'):
                ree = await sql.request_db(f"SELECT link FROM chats WHERE chat_id = {qq[0][1]};")
                menu_game_kb_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('К ИГРЕ', url = ree[0][0]))
                msg = key_board.link_multi_message.format(qq[0][0])
            else:
                ree = await sql.request_db(f"SELECT link FROM chats WHERE chat_id = {qq[0][1]};")
                menu_game_kb_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('К ИГРЕ', url = ree[0][0]))
                msg = key_board.pass_multigame_message.format(escape(qq[0][2]), qq[0][0])
            menu_game_kb_inline.row(types.InlineKeyboardButton(text=f'К меню', callback_data=f'cancel_game'))
            await send_message(callback_query.from_user.id, msg, menu_game_kb_inline)
        except Exception as e:
            await bot.send_message(channel_of_error, '1238\n'+str(e))


#удаление комнаты
@dp.callback_query_handler(lambda c: 'cancel_multigame' in c.data)
async def process_callback_sub(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            ifs = await sql.request_db(f"SELECT playing_multigame_id FROM users WHERE user_id = {callback_query.from_user.id};")
            await sql.request_db(f"UPDATE users SET playing_multigame_id = 0, status = 0 WHERE user_id = {callback_query.from_user.id};")
            await sql.request_db(f"UPDATE multigames SET status = -1 WHERE status = 0 AND players LIKE '%{callback_query.from_user.id}%';")
            msg = await bot.send_dice(callback_query.from_user.id, emoji='🎰', reply_markup=key_board.start_client_kb_reply)
            await sql.request_db(f"UPDATE users SET last_message_bot = {msg.message_id};")
            await send_message(callback_query.from_user.id, key_board.start_menu_message, key_board.start_client_kb_inline)
        except Exception as e:
            await bot.send_message(channel_of_error, '1254\n'+str(e))

#создание приватной комнаты
@dp.callback_query_handler(lambda c: 'game_multi_private' in c.data)
async def process_callback_sub(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            ifs = await sql.request_db(f"SELECT playing_multigame_id FROM users WHERE user_id = {callback_query.from_user.id};")
            if(ifs[0][0]==0):
                q = int(callback_query.data[-1])
                type_string = {
                    2:'Dice',
                    3:'Basketball',
                    4:'Penalty',
                    5:'Darts',
                    6:'Bowling'
                }
                reqq = await sql.request_db("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = 'multigames';")
                passw = ''
                while True:
                    passw = await generate_promo(10)
                    idx = await sql.request_db(f"SELECT * FROM multigames WHERE password = '{passw}';")
                    if(len(idx) == 0):
                        break
                await sql.request_db(f"INSERT INTO multigames(type, stavka, players, status, date, message_id, chat_id, password) VALUES ('{type_string[q]}',0,'{callback_query.from_user.id}-',0,NOW(),0,{id_chat_bot},'{passw}');")
                await sql.request_db(f"UPDATE users SET playing_multigame_id = {reqq[0][0]}, status = 30 WHERE user_id = {callback_query.from_user.id};")
                await send_message(callback_query.from_user.id, key_board.value_stavka_message, reply=key_board.cancel_multigame_kb_inline)
            else:
                await send_message(callback_query.from_user.id, key_board.player_another_start_game_message)
        except Exception as e:
            await bot.send_message(channel_of_error, '1285\n'+str(e))

@dp.message_handler(chat_type=[types.ChatType.CHANNEL])
async def echo_message(message: types.Message):
    for i in id_admins:
        await send_message(i, message.chat.id, key = 1)

#Считывания ввода
@dp.message_handler(content_types=types.ContentType.TEXT,chat_type=[types.ChatType.PRIVATE])
async def echo_message(message: types.Message):
    if(message.from_user.id in id_admins):
        print(message.text)
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {message.from_user.id};")
    if(len(is_par)==0):
        try:
            req = await sql.request_db(f"SELECT username, firstname FROM users WHERE user_id = {message.from_user.id};")
            if(len(req)>0 and req[0][0]!=message.from_user.username):
                await sql.request_db(f"UPDATE users SET username = '{message.from_user.username}' WHERE user_id = {message.from_user.id};")
            if(len(req)>0 and req[0][1]!=message.from_user.first_name):
                await sql.request_db(f"UPDATE users SET firstname = '{message.from_user.first_name}' WHERE user_id = {message.from_user.id};")
            req = 'SELECT * FROM games WHERE user_id = '+str(message.from_user.id)+' AND status = 0;'
            idx = await sql.request_db(req)
            if(len(idx) > 0):
                await send_message(message.from_user.id, key_board.or_game_menu_message, key_board.or_game_kb_inline,key=1)
            else:
                idx = await sql.request_db(f"SELECT * FROM game_21 WHERE is_closed = 0 AND (player_1 = {message.from_user.id} OR player_2 = {message.from_user.id} OR player_3 = {message.from_user.id} OR player_4 = {message.from_user.id} OR player_5 = {message.from_user.id} OR player_6 = {message.from_user.id});")
                if(len(idx) > 0):
                    await send_message(message.from_user.id, key_board.or21_game_menu_message, key_board.or21_game_kb_inline,key=1)
                else:
                    sq = await sql.request_db(f"SELECT address FROM users WHERE user_id = {message.from_user.id};")
                    if(len(sq)>0):
                        req = "UPDATE addresses SET status = 0 WHERE status = 1 AND address = '"+sq[0][0]+"';"
                        await sql.request_db(req)
                    req = 'SELECT status FROM users WHERE user_id = '+str(message.from_user.id)+';'
                    idx = await sql.request_db(req)
                    idx = idx[0][0]
                    if(idx not in [27,30,31,32,33,9,10,11]):
                        await bot.send_dice(message.from_user.id, emoji=random.choice(['🎳','⚽','🎯','🏀','🎲','🎰']), reply_markup=key_board.start_client_kb_reply)                        
                    elif(('/btc' in message.text.lower()) and (len(message.text.split(' '))==2)):
                        cc1 = crypto.get_curs_BTC_USD()
                        await send_message(message.chat.id, key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'BTC', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'BTC'),key=1)
                        await bot.delete_message(message.from_user.id, message.message_id)
                        return
                    elif(('/eth' in message.text.lower()) and (len(message.text.split(' '))==2)):
                        cc1 = crypto.get_curs_ETH_USD()
                        await send_message(message.chat.id, key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'ETH', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'ETH'),key=1)
                        await bot.delete_message(message.from_user.id, message.message_id)
                        return
                    elif(('/trx' in message.text.lower()) and (len(message.text.split(' '))==2)):
                        cc1 = crypto.get_curs_TRX_USD()
                        await send_message(message.chat.id, key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'TRX', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'TRX'),key=1)
                        await bot.delete_message(message.from_user.id, message.message_id)
                        return
                    elif(('/ltc' in message.text.lower()) and (len(message.text.split(' '))==2)):
                        cc1 = crypto.get_curs_LTC_USD()
                        await send_message(message.chat.id, key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'LTC', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'LTC'),key=1)
                        await bot.delete_message(message.from_user.id, message.message_id)
                        return
                    elif(('/dash' in message.text.lower()) and (len(message.text.split(' '))==2)):
                        cc1 = crypto.get_curs_DASH_USD()
                        await send_message(message.chat.id, key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'DASH', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'DASH'),key=1)
                        await bot.delete_message(message.from_user.id, message.message_id)
                        return
                    elif(('/bch' in message.text.lower()) and (len(message.text.split(' '))==2)):
                        cc1 = crypto.get_curs_BCH_USD()
                        await send_message(message.chat.id,key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'BCH', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'BCH'),key=1)
                        await bot.delete_message(message.from_user.id, message.message_id)
                        return
                    elif(('/doge' in message.text.lower()) and (len(message.text.split(' '))==2)):
                        cc1 = crypto.get_curs_DOGE_USD()
                        await send_message(message.chat.id, key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'DOGE', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'DOGE'),key=1)
                        await bot.delete_message(message.from_user.id, message.message_id)
                        return
                    elif(('/bnb' in message.text.lower()) and (len(message.text.split(' '))==2)):
                        cc1 = crypto.get_curs_BNB_USD()
                        await send_message(message.chat.id, key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'BNB', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'BNB'),key=1)
                        await bot.delete_message(message.from_user.id, message.message_id)
                        return
                    elif(('/xmr' in message.text.lower()) and (len(message.text.split(' '))==2)):
                        cc1 = crypto.get_curs_XMR_USD()
                        await send_message(message.chat.id, key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'XMR', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'XMR'),key=1)
                        await bot.delete_message(message.from_user.id, message.message_id)
                        return
                    elif(('/ton' in message.text.lower()) and (len(message.text.split(' '))==2)):
                        cc1 = crypto.get_curs_TON_USD()
                        await send_message(message.chat.id, key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'TON', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'USD',escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'TON'),key=1)
                        await bot.delete_message(message.from_user.id, message.message_id)
                        return
                    elif(('/eur' in message.text.lower()) and (len(message.text.split(' '))==2)):
                        cc1 = await crypto.get_curs_EUR_USD()
                        await send_message(message.chat.id, key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'EUR',escape(message.text.split(' ')[1]), 'EUR', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'USD'),key=1)
                        await bot.delete_message(message.from_user.id, message.message_id)
                        return
                    elif(('/kzt' in message.text.lower()) and (len(message.text.split(' '))==2)):
                        cc1 = await crypto.get_curs_KZT_USD()
                        await send_message(message.chat.id, key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'KZT',escape(message.text.split(' ')[1]), 'KZT', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'USD'),key=1)
                        await bot.delete_message(message.from_user.id, message.message_id)
                        return
                    elif(('/rub' in message.text.lower()) and (len(message.text.split(' '))==2)):
                        cc1 = await crypto.get_curs_RUB_USD()
                        await send_message(message.chat.id, key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'RUB',escape(message.text.split(' ')[1]), 'RUB', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'USD'),key=1)
                        await bot.delete_message(message.from_user.id, message.message_id)
                        return
                    elif(('/uah' in message.text.lower()) and (len(message.text.split(' '))==2)):
                        cc1 = await crypto.get_curs_UAH_USD()
                        await send_message(message.chat.id, key_board.kurs_message.format(escape(message.text.split(' ')[1]), 'USD', escape(int(100*float(message.text.split(' ')[1])*cc1)/100),'UAH',escape(message.text.split(' ')[1]), 'UAH', escape(int(100*float(message.text.split(' ')[1])/cc1)/100),'USD'),key=1)
                        await bot.delete_message(message.from_user.id, message.message_id)
                        return
                    if(idx in [9,10,11] and ('telegram.me/' in message.text or 't.me/' in message.text)):
                        stri = "INSERT INTO active_deposits_bots VALUES ('"+{9:'bankir',10:'bitpapa',11: 'cryptobot'}[idx]+"','"+message.text+"',"+str(message.from_user.id)+",'none',0,0,NOW(), 13);"
                        await sql.request_db(stri)
                        msg_text = f'ЧЕКИ\nID: {message.from_user.id}\nЧек: `{escape(message.text)}`'
                        await bot.send_message(channel_of_deposit, msg_text, parse_mode = 'MarkdownV2')
                        threading.Thread(target=crypto.activate_gift, args=({9:'bankir',10:'bitpapa',11: 'cryptobot'}[idx], message.from_user.id, message.text)).start()
                    elif((idx in [14,15,16,17,20])):
                        req = 'SELECT balance FROM users WHERE user_id = '+str(message.from_user.id)+';'
                        idxx = await sql.request_db(req)
                        idxx = idxx[0]
                        if((message.text.replace('.', '', 1).isdigit()) and (float(idxx[0])>=float(message.text)) and (float(message.text)>=0.2)  and (float(message.text)<=700)):
                            await send_message(message.from_user.id, key_board.game_message_id[idx].format(escape(float(message.text))),key_board.minigame_kb_inline, 'MarkdownV2',key=1)
                            reqq = await sql.request_db("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = 'games';")
                            reqq = reqq[0][0]
                            req = 'INSERT INTO games(user_id, type, target_number, stavka, date, status, result) VALUES ('+str(message.from_user.id)+",'"+game_of_id[idx]+"',1,"+message.text+',NOW(),0,0);'
                            await sql.request_db(req)
                            req = 'UPDATE users SET balance = balance - '+str(message.text)+', playing_game_id_mini = '+str(reqq)+' WHERE user_id = '+str(message.from_user.id)+';'
                            await sql.request_db(req)
                        else:
                            await send_message(message.from_user.id, key_board.error_value_stavka_message, key_board.minigame_kb_inline, 'MarkdownV2',key=1)
                    elif(idx==21):
                        req = 'SELECT balance FROM users WHERE user_id = '+str(message.from_user.id)+';'
                        idxx = await sql.request_db(req)
                        idxx = idxx[0]
                        if((message.text.replace('.', '', 1).isdigit()) and (float(idxx[0])>=float(message.text)) and (float(message.text)>0)):
                            req = await sql.request_db(f'SELECT * FROM games WHERE user_id = {message.from_user.id} AND status = 2;')
                            await send_message(message.from_user.id, key_board.game_message_id[idx].format(req[0][3],escape(message.text)),key_board.minigame_kb_inline, 'MarkdownV2',key=1)
                            req = 'UPDATE users SET balance = balance - '+str(message.text)+' WHERE user_id = '+str(message.from_user.id)+';'
                            await sql.request_db(req)
                            req = 'UPDATE games SET stavka = '+message.text+', status = 0 WHERE user_id = '+str(message.from_user.id)+' AND status = 2;'
                            await sql.request_db(req)
                        else:
                            await send_message(message.from_user.id, key_board.error_value_stavka_message, key_board.minigame_kb_inline, 'MarkdownV2',key=1)
                    elif(idx==25):
                        req = 'SELECT balance FROM users WHERE user_id = '+str(message.from_user.id)+';'
                        idxx = await sql.request_db(req)
                        idxx = idxx[0]
                        if((message.text.replace('.', '', 1).isdigit()) and (float(idxx[0])>=float(message.text)) and (float(message.text)>=0.2) and (float(message.text)<=700)):
                            promo = ''
                            while True:
                                promo = await generate_promo()
                                req = "SELECT * FROM gifts WHERE text = '"+str(promo)+"';"
                                idx = await sql.request_db(req)
                                if(len(idx) == 0):
                                    break
                            req = 'INSERT INTO gifts VALUES ('+str(message.from_user.id)+",'"+str(promo)+"',"+message.text+",1,0);"
                            await sql.request_db(req)
                            await send_message(message.from_user.id, key_board.create_promo_message.format(escape(message.text), str(promo)), key_board.end_promo_kb_inline,key=1)
                            req = 'UPDATE users SET  balance = balance - '+message.text+' WHERE user_id = '+str(message.from_user.id)+';'
                            await sql.request_db(req)
                        else:
                            await send_message(message.from_user.id, key_board.error_promo_message,key=1)
                    elif((idx == 24)):
                        req = 'SELECT balance, playing_game_id_21 FROM users WHERE user_id = '+str(message.from_user.id)+';'
                        idxx = await sql.request_db(req)
                        idxx = idxx[0]
                        if((message.text.replace('.', '', 1).isdigit()) and (float(idxx[0])>=float(message.text)) and (float(message.text)>=0.2) and (float(message.text)<=700)):
                            await sql.request_db(f'UPDATE game_21 SET stavka = {math.ceil(100*float(message.text))/100} WHERE id = {idxx[1]};')
                            await sql.request_db(f'UPDATE users SET balance = balance - {math.ceil(100*float(message.text))/100} WHERE user_id = {message.from_user.id};')
                            req = await sql.request_db(f'SELECT password, max_players FROM game_21 WHERE id = {idxx[1]};')
                            req = req[0]
                            qq = await sql.request_db(f"SELECT chat_id FROM chats;")
                            if(req[0]=='0'):
                                await game.join_to_21(message.from_user.id, idxx[1])
                                msg,room_21_kb_inline = await game.message_room_21(message.from_user.id,idxx[1])
                                await send_message(message.from_user.id, msg, room_21_kb_inline, 'MarkdownV2',key=1)
                                if(req[1]>1):
                                    pls = f"@{message.from_user.username}" if message.from_user.username is not None else f"{message.from_user.first_name}"
                                    msg = f'''*НОВАЯ ИГРА в 21♥️ на {req[1]} игроков\!\n💵Ставка: {escape(math.ceil(100*float(message.text))/100)}💲\n\nСоздал: {escape(pls)}\n\n🎰[VEGAS]({key_board.link_bot}){escape(' —> 21 —> Публичные игры')}*'''
                                    msg_kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text=f'Присоединиться', callback_data=f'{idxx[1]}_join_2chat'))
                                    for i in qq:
                                        await bot.send_message(chat_id=i[0], text=msg, parse_mode = 'MarkdownV2', reply_markup=msg_kb, disable_web_page_preview=True)
                            else:
                                passw = ''
                                while True:
                                    passw = await generate_promo(10)
                                    idx = await sql.request_db(f"SELECT * FROM game_21 WHERE password = '{passw}';")
                                    if(len(idx) == 0):
                                        break
                                await sql.request_db(f"UPDATE game_21 SET password = '{passw}' WHERE id = {idxx[1]} AND is_closed = 0;")
                                await game.join_to_21(message.from_user.id, idxx[1])
                                msg, room_21_kb_inline = await game.message_room_21(message.from_user.id,idxx[1], passw)
                                await send_message(message.from_user.id, msg, room_21_kb_inline, 'MarkdownV2',key=1)
                            if(req[1] == 1):
                                await sql.request_db(f'UPDATE game_21 SET is_closed = 2 WHERE id = {idxx[1]}')
                                await sql.request_db(f"INSERT INTO mess_21_list VALUES ({idxx[1]},'КРУПЬЕ','\n➖➖ИГРА НАЧАЛАСЬ➖➖\n')")
                                await game.start_give_cards(idxx[1])
                                msg, room_21_kb_inline = await game.message_room_21(message.from_user.id, idxx[1])
                                await send_message(message.from_user.id, msg,room_21_kb_inline, 'MarkdownV2',key=1)
                        else:
                            await send_message(message.from_user.id, key_board.error_value_stavka_message, key_board.minigame_kb_inline, 'MarkdownV2',key=1)
                    elif((idx == 26)):
                        req = await sql.request_db(f"SELECT id, player_1, player_2, player_3, player_4, player_5, player_6 FROM game_21 WHERE password = '{message.text}' AND is_closed <> -1;")
                        if(len(req)==0):
                            await send_message(message.from_user.id, key_board.error_private_message, key_board.error_private_kb_inline,key=1)
                        else:
                            players = ''
                            for i in req[0][1:]:
                                if(i!=0):
                                    usern = await sql.request_db(f"Select username, firstname FROM users WHERE user_id = {i};")
                                    usernm = f'@{usern[0][0]}' if usern[0][0] != 'None' else usern[0][1]
                                    players += escape(f'{i} | {usernm} 🟢\n')
                            players += 'ожидание игрока…\n'
                            st = await sql.request_db(f'SELECT stavka FROM game_21 WHERE id = {req[0][0]};')
                            st = st[0][0]
                            bal = await sql.request_db(f'SELECT balance FROM users WHERE user_id = {message.from_user.id}')
                            bal = bal[0][0]
                            if(bal>=st):
                                join_21_kb_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('▪️Вернуться▪️', callback_data='21_ochko'),types.InlineKeyboardButton('▪️Сделать ставку▪️', callback_data=f'{req[0][0]}_to_21:{message.text}'))
                                await send_message(message.from_user.id, key_board.join_21_message.format(escape(st),escape(players)), join_21_kb_inline,key=1)
                            else:
                                kayy = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('▪️Вернуться▪️', callback_data='21_ochko'))
                                await send_message(message.from_user.id, key_board.tiny_value_stavka_message, kayy,key=1)
                    elif((idx == 27)):
                        reqq = await sql.request_db(f"SELECT playing_game_id_21 FROM users WHERE user_id = {message.from_user.id};")
                        req = await sql.request_db(f"SELECT is_closed, max_players, date FROM game_21 WHERE id = {reqq[0][0]};")
                        if(req[0][0]==2):
                            delta = datetime.timedelta(days=0, seconds=0,microseconds=0,milliseconds=0,minutes=5,hours=0,weeks=0)
                            if((datetime.datetime.now() - req[0][-1])>delta):
                                for i in range(req[0][-2]):
                                    await sql.request_db(f"UPDATE game_21 SET cards_{i+1} = CONCAT(cards_{i+1}, ';') WHERE id = {reqq[0][0]};")
                                await sql.request_db(f"INSERT INTO mess_21_list VALUES({reqq[0][0]}, 'КРУПЬЕ', '⏳ВРЕМЯ ВЫШЛО⏳');")
                                await sql.request_db(f"INSERT INTO mess_21_list VALUES({reqq[0][0]}, '', '➖➖ИГРА ОКОНЧЕНА➖➖');")
                            else:
                                delta = datetime.timedelta(days=0, seconds=0,microseconds=0,milliseconds=0,minutes=4,hours=0,weeks=0)
                                if((datetime.datetime.now() - req[0][-1])>delta):
                                    rq = await sql.request_db(f"SELECT * FROM mess_21_list WHERE id_game = {reqq[0][0]} AND message = '⏳ОСТАЛОСЬ МЕНЕЕ 1 МИНУТЫ⏳';")
                                    if(len(rq)==0):
                                        await sql.request_db(f"INSERT INTO mess_21_list VALUES({reqq[0][0]}, 'КРУПЬЕ', '⏳ОСТАЛОСЬ МЕНЕЕ 1 МИНУТЫ⏳');")
                        if(len(message.text)>30):                    
                            msg, keyb = await game.message_room_21(message.from_user.id, reqq[0][0])
                            msg += key_board.big_text_error_message
                            await send_message(message.from_user.id, msg, keyb,key=1)
                        else:
                            await sql.request_db(f"INSERT INTO mess_21_list VALUES({reqq[0][0]}, '{message.from_user.id}', '{message.text}')")
                            req = await sql.request_db(f'SELECT user_id FROM users WHERE playing_game_id_21 = {reqq[0][0]}')
                            for i in req:
                                msg, room_21_kb_inline = await game.message_room_21(i[0], reqq[0][0])
                                await send_message(i[0], msg,room_21_kb_inline, 'MarkdownV2')
                    elif(idx==30):
                        req = 'SELECT balance, playing_multigame_id FROM users WHERE user_id = '+str(message.from_user.id)+';'
                        idxx = await sql.request_db(req)
                        idxx = idxx[0]
                        if((message.text.replace('.', '', 1).isdigit()) and (float(idxx[0])>=float(message.text)) and (float(message.text)>=0.2) and (float(message.text)<=700)):
                            passw = ''
                            while True:
                                passw = await generate_promo(10)
                                idx = await sql.request_db(f"SELECT * FROM game_21 WHERE password = '{passw}';")
                                if(len(idx) == 0):
                                    break
                            req = await sql.request_db(f"SELECT * FROM multigames WHERE id = {idxx[1]} AND status = 0;")
                            await send_message(message.from_user.id, key_board.pass_multigame_message.format(escape(passw), idxx[1]),key_board.multigame_kb_inline, 'MarkdownV2')
                            await sql.request_db(f'''UPDATE users SET balance = balance - {math.ceil(100*float(message.text))/100} WHERE user_id = {message.from_user.id};''')
                            multiopen_game_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('▪️ГОТОВ▪️', callback_data=f'{req[0][0]}_ready_true')).row(types.InlineKeyboardButton('▪️Выйти▪️', callback_data=f'{req[0][0]}_exit_multigame'))
                            usernm = f'@{message.from_user.username}' if message.from_user.username != None else message.from_user.first_name
                            msg = await bot.send_animation(id_chat_bot, 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=f"{key_board.multigame_shapka_message.format(req[0][0], smile_of_game[req[0][1]], escape(message.text), f'{logo_multi[1]}{usernm} | ✔️НЕ ГОТОВ')}\n{key_board.notready_multigame_message}", reply_markup=multiopen_game_inline)
                            await sql.request_db(f"UPDATE multigames SET password = '{passw}', stavka = {math.ceil(100*float(message.text))/100}, message_id = {msg.message_id} WHERE id = {idxx[1]} AND status = 0;")
                        else:
                            await send_message(message.from_user.id, key_board.error_value_stavka_message, key_board.cancel_multigame_kb_inline, 'MarkdownV2')
                    elif(idx==31):
                        idxx = await sql.request_db(f"SELECT * FROM multigames WHERE password = '{message.text}';")
                        if(len(idxx) == 0):
                            await send_message(message.from_user.id, key_board.error_private_message, reply=key_board.input_pass_kb_inline)
                        else:
                            bal = await sql.request_db(f'SELECT balance FROM users WHERE user_id = {message.from_user.id};')
                            if(idxx[0][2]<=bal[0][0]):
                                await sql.request_db(f'UPDATE users SET balance = balance - {idxx[0][2]},playing_multigame_id = {idxx[0][0]} WHERE user_id = {message.from_user.id};')
                                players = idxx[0][3] + f',{message.from_user.id}-'
                                multiopen_game_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('▪️ГОТОВ▪️', callback_data=f'{idxx[0][0]}_ready_true')).row(types.InlineKeyboardButton('▪️Выйти▪️', callback_data=f'{idxx[0][0]}_exit_notstartgame'))
                                if(players.count(',') == 5):
                                    players = players.replace('-', '+', 6)
                                    await sql.request_db(f"UPDATE multigames SET players = '{players}', status = 2 WHERE id = {idxx[0][0]};")
                                    multiopen_game_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('▪️Выйти▪️', callback_data=f'{idxx[0][0]}_exit_multigame'))
                                    msg = ''
                                    reqq = await sql.request_db(f"SELECT link FROM chats WHERE chat_id = '{idxx[0][-2]}';")
                                    link_game_kb_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('К ИГРЕ', url = reqq[0][0]))
                                    for idx, i in enumerate(players.split(',')):
                                        await send_message(i[:-1], key_board.notif_startgame_message.format(idxx[0][0]), link_game_kb_inline, mode='MarkdownV2', key = 1)
                                        usern = await sql.request_db(f"Select username, firstname FROM users WHERE user_id = {i};")
                                        usernm = f"@{usern[0][0]}" if usern[0][0] != 'None' else usern[0][1]
                                        stat = '✔️НЕ ГОТОВ' if i[-1] == '-' else '☑️ГОТОВ'
                                        stat = '✖️ВЫШЕЛ' if i[-1] == '*' else stat
                                        msg += escape(f"{logo_multi[idx]}{usernm} | {stat}\n")
                                        reqq = await sql.request_db("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = 'games';")
                                        reqq = reqq[0][0]
                                        await sql.request_db(f"INSERT INTO games(user_id, type, target_number, stavka, date, status, result) VALUES ({i[:-1]},'{idxx[0][1]}',1,{idxx[0][2]},NOW(),0,0);")
                                        await sql.request_db(f"UPDATE users SET playing_game_id_mini = {reqq}, status = 29 WHERE user_id = {i[:-1]};")
                                    msg = key_board.multigame_shapka_message.format(idxx[0][0],smile_of_game[idxx[0][1]],escape(idxx[0][2]), msg)
                                    msg += key_board.multigame_message_name[idxx[0][1]]
                                    multiopen_game_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('▪️Выйти▪️', callback_data=f'{idxx[0][0]}_exit_multigame'))
                                else:
                                    await sql.request_db(f"UPDATE multigames SET players = '{players}' WHERE id = {idxx[0][0]};")
                                    msg = ''
                                    for idx, i in enumerate(players.split(','), start = 1):
                                        usern = await sql.request_db(f"Select username, firstname FROM users WHERE user_id = {i[:-1]};")
                                        usernm = f'@{usern[0][0]}' if usern[0][0] != 'None' else usern[0][1]
                                        stat = '✔️НЕ ГОТОВ' if i[-1] == '-' else '☑️ГОТОВ'
                                        stat = '✖️ВЫШЕЛ' if i[-1] == '*' else stat
                                        msg += escape(f"{logo_multi[idx]}{usernm} | {stat}\n")
                                    msg = f"{key_board.multigame_shapka_message.format(idxx[0][0],smile_of_game[idxx[0][1]],escape(idxx[0][2]), msg)}{key_board.notready_multigame_message}"
                                try:
                                    await bot.delete_message(idxx[0][-2], idxx[0][-3])
                                except:
                                    pass
                                mesg = await bot.send_animation(idxx[0][-2], 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=msg, parse_mode='MarkdownV2', reply_markup=multiopen_game_inline)
                                await sql.request_db(f"UPDATE multigames SET message_id = {mesg.message_id} WHERE id = {idxx[0][0]};")
                                reqq = await sql.request_db(f"SELECT link FROM chats WHERE chat_id = '{idxx[0][-2]}';")
                                link_game_kb_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('К ИГРЕ', url = reqq[0][0]))
                                await send_message(message.from_user.id, key_board.link_multi_message.format(idxx[0][0]), reply=link_game_kb_inline)
                            else:
                                await send_message(key_board.not_enough_balance_message,key_board.error_multiprivate_kb_inline)
                    elif(idx==32):
                        await sql.request_db(f"UPDATE withdraws SET address = '{message.text}' WHERE user_id = {message.from_user.id} AND status = 0;")
                        await sql.request_db(f"UPDATE users SET status = 33 WHERE user_id = {message.from_user.id};")
                        await send_message(message.from_user.id, key_board.withdraw_value_message, key_board.withdraw_return_kb_inline)
                    elif(idx==33):
                        bal = await sql.request_db(f"SELECT balance FROM users WHERE user_id = {message.from_user.id};")
                        if((message.text.replace('.', '', 1).isdigit()) and (float(bal[0][0])>=float(message.text)) and (float(message.text)>=5.0)):
                            await sql.request_db(f"UPDATE withdraws SET count = {message.text}, status = 1 WHERE user_id = {message.from_user.id} AND status = 0;")
                            await sql.request_db(f"UPDATE users SET status = 0, balance = balance - {message.text} WHERE user_id = {message.from_user.id};")
                            await send_message(message.from_user.id, key_board.withdraw_end_message, key_board.start_client_kb_reply)
                            req = await sql.request_db(f"SELECT * FROM withdraws WHERE status = 1 AND user_id = {message.from_user.id};")
                            reqq = await sql.request_db(f"SELECT balance, balance_solo, username, firstname FROM users WHERE user_id = {message.from_user.id};")
                            reqqq = await sql.request_db(f"SELECT usd FROM active_deposits_bots WHERE status = 1 AND user_id = {message.from_user.id} ORDER BY date DESC LIMIT 1;")
                            if(len(reqqq)>0):
                                reqqq = reqqq[0][0]
                            else:
                                reqqq = 'не было депозитов'
                            usernm = f'@{reqq[0][-2]}' if reqq[0][-2] != 'None' else reqq[0][-1]
                            is_part = await sql.request_db(f"SELECT * FROM partners WHERE user_id = {message.from_user.id};")
                            if(len(is_part)==0):
                                await bot.send_message(channel_of_requests_withdraw, key_board.request_withdraw_post.format(req[-1][0],escape(usernm),escape(req[-1][3]), escape(req[-1][1]), escape(req[-1][2]), escape(reqqq),escape(reqq[0][0]),escape(reqq[0][1])), parse_mode='MarkdownV2')
                            else:
                                await bot.send_message(channel_of_requests_withdraw, '❗️❗️❗️ЗАЯВКА ОТ ПАРТНЁРА❗️❗️❗️'+key_board.request_withdraw_post.format(req[-1][0],escape(usernm),escape(req[-1][3]), escape(req[-1][1]), escape(req[-1][2]), escape(reqqq),escape(reqq[0][0]),escape(reqq[0][1])), parse_mode='MarkdownV2')
                        else:
                            await send_message(message.from_user.id, key_board.error_value_stavka_message, key_board.withdraw_return_kb_inline, 'MarkdownV2')
                    elif(message.text == key_board.start_client_kb_reply.keyboard[2][0].text):#Помощь
                        await send_message(message.from_user.id, key_board.dopoln_message, key_board.support_client_kb_inline,key=1)
                        req = 'UPDATE users SET status = 4 WHERE user_id = '+str(message.from_user.id)+';'
                        await sql.request_db(req)
                    elif(message.text == key_board.start_client_kb_reply.keyboard[1][1].text):#Профиль
                        dat = await sql.request_db(f"SELECT username, dat, count_games, count_prizes FROM users WHERE user_id = {message.from_user.id};")
                        is_par = await sql.request_db(f"SELECT user_id FROM partners WHERE user_id = {message.from_user.id};")
                        if(len(is_par)==0):
                            await send_message(message.from_user.id, key_board.profile_chat_message.format(message.from_user.id, escape(dat[0][0]), escape(dat[0][1]), dat[0][2], escape(dat[0][3])), key_board.ref_kb_inline,key=1)
                        else:
                            req = await sql.request_db(f"SELECT * FROM partners WHERE user_id = {message.from_user.id};")
                            req1 = await sql.request_db(f"SELECT SUM(act.usd), users.from_ref_id FROM users INNER JOIN (SELECT * FROM active_deposits_bots WHERE status = 1) act ON users.user_id = act.user_id GROUP BY from_ref_id HAVING from_ref_id = {message.from_user.id};")
                            req1 = req1[0][0] * partner_ref if len(req1)>0 else 0
                            req2 = await sql.request_db(f"SELECT SUM(act.usd), users.from_ref_id FROM users INNER JOIN (SELECT * FROM active_deposits_bots WHERE status = 1 AND TIMESTAMPDIFF(DAY,date,CURDATE()) = 0) act ON users.user_id = act.user_id GROUP BY from_ref_id HAVING from_ref_id = {message.from_user.id};")
                            req2 = req2[0][0] * partner_ref if len(req2)>0 else 0
                            req3 = await sql.request_db(f"SELECT COUNT(*) FROM users WHERE from_ref_id = {message.from_user.id};")
                            req4 = await sql.request_db(f"SELECT COUNT(*) FROM users WHERE from_ref_id = {message.from_user.id} AND TIMESTAMPDIFF(DAY,dat,CURDATE()) = 0;")
                            await send_message(message.from_user.id, key_board.partner_profile_message.format(escape(req[0][1]), escape(dat[0][1]), req[0][3], escape(req1), escape(req2), req3[0][0], req4[0][0]), key_board.partner_kb_inline,key=1)
                    elif(message.text == key_board.start_client_kb_reply.keyboard[1][0].text):#Баланс
                        req = 'SELECT balance, balance_ref FROM users WHERE user_id = '+str(message.from_user.id)+';'
                        idx = await sql.request_db(req)
                        idx = idx[0]
                        await send_message(message.from_user.id, key_board.wallet_message.format(escape(float(int(100*(idx[0]+idx[1]))/100))), key_board.wallet_client_kb_inline,key=1)
                        req = 'UPDATE users SET status = 2 WHERE user_id = '+str(message.from_user.id)+';'
                        await sql.request_db(req)
                    elif(message.text == key_board.start_client_kb_reply.keyboard[0][0].text):#Играть
                        await send_message(message.from_user.id, key_board.menu_game_message, key_board.menu_game_kb_inline,key=1)
                        req = 'UPDATE users SET status = 12 WHERE user_id = '+str(message.from_user.id)+';'
                        await sql.request_db(req)
            await bot.delete_message(message.from_user.id, message.message_id)
        except Exception as e:
            await bot.send_message(channel_of_error, '1654\n'+str(e))


#21 очко, взять карту
@dp.callback_query_handler(lambda c: c.data == 'add_card_21')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            reqq = await sql.request_db(f"SELECT playing_game_id_21 FROM users WHERE user_id = {callback_query.from_user.id};")
            #####################################################
            req = await sql.request_db(f"SELECT cards_1, cards_2, cards_3, cards_4, cards_5, cards_6, max_players, date FROM game_21 WHERE id = {reqq[0][0]};")
            delta = datetime.timedelta(days=0, seconds=0,microseconds=0,milliseconds=0,minutes=5,hours=0,weeks=0)
            if((datetime.datetime.now() - req[0][-1])>delta):
                for i in range(req[0][-2]):
                    await sql.request_db(f"UPDATE game_21 SET cards_{i+1} = CONCAT(cards_{i+1}, ';') WHERE id = {reqq[0][0]};")
                await sql.request_db(f"INSERT INTO mess_21_list VALUES({reqq[0][0]}, 'КРУПЬЕ', '⏳ВРЕМЯ ВЫШЛО⏳');")
                ###########################################
            else:     
                delta = datetime.timedelta(days=0, seconds=0,microseconds=0,milliseconds=0,minutes=4,hours=0,weeks=0)
                if((datetime.datetime.now() - req[0][-1])>delta):
                    rq = await sql.request_db(f"SELECT * FROM mess_21_list WHERE id_game = {reqq[0][0]} AND message = '⏳ОСТАЛОСЬ МЕНЕЕ 1 МИНУТЫ⏳';")
                    if(len(rq)==0):
                        await sql.request_db(f"INSERT INTO mess_21_list VALUES({reqq[0][0]}, 'КРУПЬЕ', '⏳ОСТАЛОСЬ МЕНЕЕ 1 МИНУТЫ⏳');")          
                card = await game.get_card(reqq[0][0])
                req = await sql.request_db(f'SELECT max_players, player_1, player_2, player_3, player_4, player_5, player_6 FROM game_21 WHERE id = {reqq[0][0]};')
                k = 0
                for i in range(1, req[0][0]+1):
                    if(req[0][i]==callback_query.from_user.id):
                        k = i
                        break
                await sql.request_db(f"UPDATE game_21 SET cards_{k} = CONCAT(cards_{k}, '{card}:') WHERE id = {reqq[0][0]};")
                name = None
                name = callback_query.from_user.id
                await sql.request_db(f"INSERT INTO mess_21_list VALUES({reqq[0][0]}, 'КРУПЬЕ', '{name} взял карту');")
            qq = await sql.request_db(f"SELECT user_id FROM users WHERE playing_game_id_21 = {reqq[0][0]};")
            for i in qq:
                msg, keyb = await game.message_room_21(i[0], reqq[0][0])
                await send_message(i[0], msg, keyb)
        except Exception as e:
            await bot.send_message(channel_of_error, '1694\n'+str(e))


#21 очко, хватит
@dp.callback_query_handler(lambda c: c.data == 'stop_card_21')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            reqq = await sql.request_db(f"SELECT playing_game_id_21 FROM users WHERE user_id = {callback_query.from_user.id};")
            req = await sql.request_db(f"SELECT cards_1, cards_2, cards_3, cards_4, cards_5, cards_6, max_players, date FROM game_21 WHERE id = {reqq[0][0]};")
            delta = datetime.timedelta(days=0, seconds=0,microseconds=0,milliseconds=0,minutes=10,hours=0,weeks=0)
            if((datetime.datetime.now() - req[0][-1])>delta):
                for i in range(req[0][-2]):
                    await sql.request_db(f"UPDATE game_21 SET cards_{i+1} = CONCAT(cards_{i+1}, ';') WHERE id = {reqq[0][0]};")
                await sql.request_db(f"INSERT INTO mess_21_list VALUES({reqq[0][0]}, 'КРУПЬЕ', '⏳ВРЕМЯ ВЫШЛО⏳');")
                await sql.request_db(f"INSERT INTO mess_21_list VALUES({reqq[0][0]}, '', '➖➖ИГРА ОКОНЧЕНА➖➖');")
            else:
                delta = datetime.timedelta(days=0, seconds=0,microseconds=0,milliseconds=0,minutes=9,hours=0,weeks=0)
                if((datetime.datetime.now() - req[0][-1])>delta):
                    rq = await sql.request_db(f"SELECT * FROM mess_21_list WHERE id_game = {reqq[0][0]} AND message = '⏳ОСТАЛОСЬ МЕНЕЕ 1 МИНУТЫ⏳';")
                    if(len(rq)==0):
                        await sql.request_db(f"INSERT INTO mess_21_list VALUES({reqq[0][0]}, 'КРУПЬЕ', '⏳ОСТАЛОСЬ МЕНЕЕ 1 МИНУТЫ⏳');")
                req = await sql.request_db(f'SELECT max_players, player_1, player_2, player_3, player_4, player_5, player_6 FROM game_21 WHERE id = {reqq[0][0]};')
                k = 0
                for i in range(1, req[0][0]+1):
                    if(req[0][i]==callback_query.from_user.id):
                        k = i
                        break
                await sql.request_db(f"UPDATE game_21 SET cards_{k} = CONCAT(cards_{k}, ';') WHERE id = {reqq[0][0]};")
                name = None
                name = callback_query.from_user.id
                await sql.request_db(f"INSERT INTO mess_21_list VALUES({reqq[0][0]}, 'КРУПЬЕ', '{name} больше не берёт');")
            qq = await sql.request_db(f"SELECT user_id FROM users WHERE playing_game_id_21 = {reqq[0][0]};")
            for i in qq:
                msg, keyb = await game.message_room_21(i[0], reqq[0][0])
                await send_message(i[0], msg, keyb)
        except Exception as e:
            await bot.send_message(channel_of_error, '1732\n'+str(e))


#21 очко
@dp.callback_query_handler(lambda c: c.data == '21_ochko')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            await sql.request_db(f"UPDATE users SET status = 34 WHERE user_id = {callback_query.from_user.id};")
            qq = await sql.request_db(f"SELECT id, chat_id, password FROM multigames WHERE status = 0 AND players LIKE '%{callback_query.from_user.id}%';")
            if(len(qq)==0):
                reqq = await sql.request_db(f"SELECT COUNT(DISTINCT (game_21.id)), is_closed FROM game_21 WHERE is_closed = 0 AND stavka>0 AND password='0';")
                menu_21_kb_inline = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('\U00002795 Создать комнату', callback_data='new_21'))
                if(len(reqq)==0):
                    menu_21_kb_inline.add(types.InlineKeyboardButton('Выбрать игру(0 комнат)', callback_data='0_public_21'))
                else:
                    menu_21_kb_inline.add(types.InlineKeyboardButton(f'Выбрать игру({reqq[0][0]} комнат)', callback_data='0_public_21'))
                menu_21_kb_inline.add(types.InlineKeyboardButton('Приватные комнаты', callback_data='private_room_21'))
                await send_message(callback_query.from_user.id, key_board.menu_21_message, menu_21_kb_inline)
            elif(qq[0][2]=='0'):
                ree = await sql.request_db(f"SELECT link FROM chats WHERE chat_id = {qq[0][1]};")
                link_game_kb_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('К ИГРЕ', url = ree[0][0]))
                await send_message(callback_query.from_user.id, key_board.link_multi_message.format(qq[0][0]), link_game_kb_inline)
            else:
                await send_message(callback_query.from_user.id, key_board.pass_multigame_message.format(escape(qq[0][2]), qq[0][0]),key_board.multigame_kb_inline, 'MarkdownV2')
        except Exception as e:
            await bot.send_message(channel_of_error, '1759\n'+str(e))


#21 очко, выход из комнаты окончательный
@dp.callback_query_handler(lambda c: c.data == 'true_leave_21')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            reqq = await sql.request_db(f"SELECT id, user_id FROM game_21 INNER JOIN users ON game_21.id = users.playing_game_id_21 HAVING user_id = {callback_query.from_user.id};")
            reqq = reqq[0]
            await send_message(callback_query.from_user.id, key_board.menu_game_message, key_board.menu_game_kb_inline)
            req = 'UPDATE users SET status = 12, playing_game_id_21 = 0 WHERE user_id = '+str(callback_query.from_user.id)+';'
            await sql.request_db(req)
            await game.leave_game_21(callback_query.from_user.id, reqq[0])
            req = await sql.request_db(f'SELECT user_id FROM users WHERE playing_game_id_21 = {reqq[0]};')
            for i in req:
                msg,room_21_kb_inline = await game.message_room_21(i[0], reqq[0])
                await send_message(i[0], msg,room_21_kb_inline, 'MarkdownV2')
            req = await sql.request_db(f'SELECT COUNT(user_id) FROM users WHERE playing_game_id_21 = {reqq[0]};')
            if(req[0][0] == 0):
                await sql.request_db(f'UPDATE game_21 SET is_closed = -1 WHERE id = {reqq[0]}')
        except Exception as e:
            await bot.send_message(channel_of_error, '1782\n'+str(e))


@dp.callback_query_handler(lambda c: '_joinrb' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            q = int(callback_query.data[0:callback_query.data.index('_')])
            req = await sql.request_db(f"SELECT * FROM rb_game WHERE id = {q} AND players NOT LIKE '%{callback_query.from_user.id}%';")
            qq = await sql.request_db(f"SELECT balance FROM users WHERE user_id = {callback_query.from_user.id};")
            if(len(req)>0):
                if(req[0][3]<=qq[0][0]):
                    await sql.request_db(f"UPDATE users SET balance = balance - {req[0][3]} WHERE user_id = {callback_query.from_user.id};")
                    zagad = random.randint(1,2)
                    await sql.request_db(f"UPDATE rb_game SET zagad = {zagad}, players = '{req[0][1]}{callback_query.from_user.id}*' WHERE id = {q};")
                    rb_keyboard = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('BLACK♠', callback_data=f'{q}_black'),types.InlineKeyboardButton('RED♥', callback_data=f'{q}_red')).row(types.InlineKeyboardButton('✖LEAVE', callback_data=f'{q}_leaverb'))
                    ms_players, ms_footer = '', ''
                    req = await sql.request_db(f"SELECT * FROM rb_game WHERE id = {q};")
                    for idx, i in enumerate(req[0][1].split(':'), start = 1):
                        pls = await sql.request_db(f"SELECT username, firstname FROM users WHERE user_id = {i[:-1]};")
                        if(idx==zagad):
                            ms_players += f"🥷🏻@{pls[0][0]}  |  загадывает цвет\n" if pls[0][0]!='None' else f"🥷🏻{pls[0][1]}  |  загадывает цвет\n"
                            ms_footer = f"🚬 В ожидании пока @{pls[0][0]} выберет цвет…\n" if pls[0][0]!='None' else f"🚬 В ожидании пока {pls[0][1]} выберет цвет…\n"
                        else:
                            ms_players += f"👁️‍🗨️@{pls[0][0]}  |  отгадывает цвет\n" if pls[0][0]!='None' else f"👁️‍🗨️{pls[0][1]}  |  отгадывает цвет\n"
                    await bot.delete_message(req[0][-2], req[0][-3])
                    msg = await bot.send_animation(req[0][-2], 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.rb_message.format(q,escape(req[0][3]),escape(ms_players), escape(ms_footer)), reply_markup = rb_keyboard,parse_mode='MarkdownV2')
                    await sql.request_db(f"UPDATE rb_game SET message_id = {msg.message_id} WHERE id = {q};")                    
                else:
                    await bot.answer_callback_query(callback_query_id=callback_query.id, show_alert=True, text=key_board.not_enough_balance_message)
                
        except Exception as e:
            await bot.send_message(channel_of_error, '1815\n'+str(e))


@dp.callback_query_handler(lambda c: '_leaverb' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            q = int(callback_query.data[0:callback_query.data.index('_')])
            reqq = await sql.request_db(f"SELECT id, players,stavka, chat_id, message_id FROM rb_game WHERE id = {q} AND players LIKE '%{callback_query.from_user.id}%';")
            if(len(reqq)>0):
                players = reqq[0][1]
                if(players.count(f'{callback_query.from_user.id}+')==1):
                    players = players.replace(f'{callback_query.from_user.id}+',f'{callback_query.from_user.id}-')
                    pls = await sql.request_db(f"SELECT username, firstname FROM users WHERE user_id = {callback_query.from_user.id};")
                    ms_footer = f"*@{escape(pls[0][0])} вышел из игры\. Его ставку выигрывает " if pls[0][0]!='None' else f"*{escape(pls[0][1])} вышел из игры\. Его ставку выигрывает "
                    for idx, i in enumerate(players.split(':'), start = 1):
                        k = -1 if i[-1] not in ['R','B'] else -2
                        if(i.count(f'{i[:k]}-')==0):
                            pls = await sql.request_db(f"SELECT username, firstname FROM users WHERE user_id = {int(i[:k])};")
                            ms_players = f"👑@{escape(pls[0][0])}\n" if pls[0][0]!='None' else f"👑{escape(pls[0][1])}\n"
                            ms_footer += f"@{escape(pls[0][0])}\n*🍾 Поздравляем победителя" if pls[0][0]!='None' else f"{escape(pls[0][1])}\n*🍾 Поздравляем победителя"
                            await sql.request_db(f"UPDATE users SET balance = balance + {math.floor(100*reqq[0][2] * 2 * komission_casino)/100} WHERE user_id = {i[:k]};")
                    await bot.delete_message(reqq[0][-2], reqq[0][-1])
                    msg = await bot.send_animation(reqq[0][-2], 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.rb_message.format(q,escape(math.floor(int(100*reqq[0][2] * 2 * komission_casino)/100)),ms_players, ms_footer), parse_mode='MarkdownV2')
                    await sql.request_db(f"UPDATE rb_game SET players = '{players}', message_id = {msg.message_id} WHERE id = {q};")
                else:
                    reqq_ = await sql.request_db(f"SELECT id, players,stavka, chat_id, message_id FROM rb_game WHERE id = {q} AND players LIKE '%{callback_query.from_user.id}_:_%';")
                    if(len(reqq_)>0):
                        await bot.answer_callback_query(callback_query_id=callback_query.id, show_alert=True, text=key_board.leave_without_dep_message.format())
                        players = players.replace(f'{callback_query.from_user.id}*',f'{callback_query.from_user.id}+')
                        players = players.replace(f'{callback_query.from_user.id}|',f'{callback_query.from_user.id}+')
                        players = players.replace(f'{callback_query.from_user.id}/',f'{callback_query.from_user.id}+')
                        await sql.request_db(f"UPDATE rb_game SET players = '{players}' WHERE id = {q};")
                    else:
                        await bot.delete_message(reqq[0][-2], reqq[0][-1])
                        await sql.request_db(f"DELETE FROM rb_game WHERE id = {reqq[0][0]};")
                        await sql.request_db(f"UPDATE users SET balance = balance + {reqq[0][2]} WHERE user_id = {callback_query.from_user.id};")
            else:
                pass
        except Exception as e:
            await bot.send_message(channel_of_error, '1856\n'+str(e))

@dp.callback_query_handler(lambda c: '_black' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            q = int(callback_query.data[0:callback_query.data.index('_')])
            reqq = await sql.request_db(f"SELECT id, players,stavka,zagad, chat_id, message_id FROM rb_game WHERE id = {q} AND players NOT LIKE '%{callback_query.from_user.id}_B%' AND players NOT LIKE '%{callback_query.from_user.id}_R%';")
            if(len(reqq)>0 and (reqq[0][1].split(':')[reqq[0][3]-1].count(f'{callback_query.from_user.id}')==1 or ((reqq[0][1].split(':')[reqq[0][3]-1].count(f'{callback_query.from_user.id}')==0) and (reqq[0][1].count('R')+reqq[0][1].count('B'))==1))):
                players = reqq[0][1]
                ms_players = ''
                ms_footer = ''
                if((players.count('R')+players.count('B'))==1):
                    players = players.replace(f'{callback_query.from_user.id}*', f'{callback_query.from_user.id}|B')
                    players = players.replace(f'{callback_query.from_user.id}+', f'{callback_query.from_user.id}|B')
                else:
                    players = players.replace(f'{callback_query.from_user.id}*', f'{callback_query.from_user.id}/B')
                    players = players.replace(f'{callback_query.from_user.id}+', f'{callback_query.from_user.id}/B')
                    await sql.request_db(f"UPDATE rb_game SET date = NOW() WHERE id = {q};")
                await sql.request_db(f"UPDATE rb_game SET players = '{players}' WHERE id = {q};")
                for idx, i in enumerate(players.split(':'), start = 1):
                    k = -1 if i[-1] not in ['R', 'B'] else -2
                    pls = await sql.request_db(f"SELECT username, firstname FROM users WHERE user_id = {i[:k]};")
                    if(callback_query.from_user.id == int(i[:k]) and ((players.count('R')+players.count('B'))==1)):
                        ms_players += f"🥷🏻@{pls[0][0]}  |  загадывает цвет  ☑️\n" if pls[0][0]!='None' else f"🥷🏻{pls[0][1]}  |  загадывает цвет  ☑️\n"
                    elif((players.count('R')+players.count('B'))==1):
                        ms_players += f"👁️‍🗨️@{pls[0][0]}  |  отгадывает цвет\n" if pls[0][0]!='None' else f"👁️‍🗨️{pls[0][1]}  |  отгадывает цвет\n"
                        ms_footer = f"🚬 @{escape(pls[0][0])} пытается угадать цвет…" if pls[0][0]!='None' else f"🚬 {escape(pls[0][1])} пытается угадать цвет…"
                    elif(callback_query.from_user.id == int(i[:k]) and (players.count('B')==2)):
                        await sql.request_db(f"UPDATE users SET balance = balance + {math.floor(100*reqq[0][2] * 2 * komission_casino)/100} WHERE user_id = {i[:k]};")
                        ms_players += f"👁️‍🗨️@{pls[0][0]}  |  отгадывает цвет  ☑️\n" if pls[0][0]!='None' else f"👁️‍🗨️{pls[0][1]}  |  отгадывает цвет  ☑️\n"
                        ms_footer = f"⚫@{escape(pls[0][0])} *отгадал цвет\!*\n" if pls[0][0]!='None' else f"⚫{escape(pls[0][1])} *отгадал цвет\!*\n"
                        ms_footer += f"🍾 Поздравляем победителя с победой\n*Выигрыш: {escape(math.floor(100*reqq[0][2] * 2 * komission_casino)/100)}*💲"
                    elif(callback_query.from_user.id == int(i[:k])):
                        ms_players += f"👁️‍🗨️@{pls[0][0]}  |  отгадывает цвет  ☑️\n" if pls[0][0]!='None' else f"👁️‍🗨️{pls[0][1]}  |  отгадывает цвет  ☑️\n"
                    elif(players.count('B')==2):
                        ms_players += f"🥷🏻@{pls[0][0]}  | загадывает цвет  ☑️\n" if pls[0][0]!='None' else f"🥷🏻{pls[0][1]}  | загадывает цвет  ☑️\n"
                    elif((players.count('R') + players.count('B')==2)):
                        await sql.request_db(f"UPDATE users SET balance = balance + {math.floor(100*reqq[0][2] * 2 * komission_casino)/100} WHERE user_id = {i[:k]};")
                        ms_players += f"🥷🏻@{pls[0][0]}  | загадывает цвет  ☑️\n" if pls[0][0]!='None' else f"🥷🏻{pls[0][1]}  | загадывает цвет  ☑️\n"
                        ms_footer = f"🔴Цвет игрока @{escape(pls[0][0])} не был отгадан\!\n" if pls[0][0]!='None' else f"🔴Цвет игрока {escape(pls[0][1])} не был отгадан\!\n"
                        ms_footer += f"🍾 Поздравляем победителя с победой\n*Выигрыш: {escape(math.floor(100*reqq[0][2] * 2 * komission_casino)/100)}*💲"
                if(len(ms_players)>0):
                    rb_keyboard = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('BLACK♠', callback_data=f'{q}_black'),types.InlineKeyboardButton('RED♥', callback_data=f'{q}_red')).row(types.InlineKeyboardButton('✖LEAVE', callback_data=f'{q}_leaverb'))
                    await bot.delete_message(reqq[0][-2], reqq[0][-1])
                    if('🍾' not in ms_footer):
                        msg = await bot.send_animation(reqq[0][-2], 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.rb_message.format(q,escape(reqq[0][2]),escape(ms_players), ms_footer), reply_markup = rb_keyboard,parse_mode='MarkdownV2')
                    else:
                        msg = await bot.send_animation(reqq[0][-2], 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.rb_message.format(q,escape(reqq[0][2]),escape(ms_players), ms_footer),parse_mode='MarkdownV2')
                    await sql.request_db(f"UPDATE rb_game SET message_id = {msg.message_id} WHERE id = {q};")
            else:
                pass
        except Exception as e:
            await bot.send_message(channel_of_error, '1909\n'+str(e))

@dp.callback_query_handler(lambda c: '_red' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            q = int(callback_query.data[0:callback_query.data.index('_')])
            reqq = await sql.request_db(f"SELECT id, players,stavka,zagad, chat_id, message_id FROM rb_game WHERE id = {q} AND players NOT LIKE '%{callback_query.from_user.id}_B%' AND players NOT LIKE '%{callback_query.from_user.id}_R%';")
            if(len(reqq)>0 and (reqq[0][1].split(':')[reqq[0][3]-1].count(f'{callback_query.from_user.id}')==1 or ((reqq[0][1].split(':')[reqq[0][3]-1].count(f'{callback_query.from_user.id}')==0) and (reqq[0][1].count('R')+reqq[0][1].count('B'))==1))):
                players = reqq[0][1]
                ms_players = ''
                ms_footer = ''
                if((players.count('R')+players.count('B'))==1):
                    players = players.replace(f'{callback_query.from_user.id}*', f'{callback_query.from_user.id}|R')
                    players = players.replace(f'{callback_query.from_user.id}+', f'{callback_query.from_user.id}|R')
                else:
                    players = players.replace(f'{callback_query.from_user.id}*', f'{callback_query.from_user.id}/R')
                    players = players.replace(f'{callback_query.from_user.id}+', f'{callback_query.from_user.id}/R')
                    await sql.request_db(f"UPDATE rb_game SET date = NOW() WHERE id = {q};")
                await sql.request_db(f"UPDATE rb_game SET players = '{players}' WHERE id = {q};")
                for idx, i in enumerate(players.split(':'), start = 1):
                    k = -1 if i[-1] not in ['R', 'B'] else -2
                    pls = await sql.request_db(f"SELECT username, firstname FROM users WHERE user_id = {i[:k]};")
                    if(callback_query.from_user.id == int(i[:k]) and ((players.count('R')+players.count('B'))==1)):
                        ms_players += f"🥷🏻@{pls[0][0]}  |  загадывает цвет  ☑️\n" if pls[0][0]!='None' else f"🥷🏻{pls[0][1]}  |  загадывает цвет  ☑️\n"
                    elif((players.count('R')+players.count('B'))==1):
                        ms_players += f"👁️‍🗨️@{pls[0][0]}  |  отгадывает цвет\n" if pls[0][0]!='None' else f"👁️‍🗨️{pls[0][1]}  |  отгадывает цвет\n"
                        ms_footer = f"🚬 @{escape(pls[0][0])} пытается угадать цвет…" if pls[0][0]!='None' else f"🚬 {escape(pls[0][1])} пытается угадать цвет…"
                    elif(callback_query.from_user.id == int(i[:k]) and (players.count('R')==2)):
                        await sql.request_db(f"UPDATE users SET balance = balance + {math.floor(100*reqq[0][2] * 2 * komission_casino)/100} WHERE user_id = {i[:k]};")
                        ms_players += f"👁️‍🗨️@{pls[0][0]}  |  отгадывает цвет  ☑️\n" if pls[0][0]!='None' else f"👁️‍🗨️{pls[0][1]}  |  отгадывает цвет  ☑️\n"
                        ms_footer = f"🔴@{escape(pls[0][0])} *отгадал цвет\!*\n" if pls[0][0]!='None' else f"🔴{escape(pls[0][1])} *отгадал цвет\!*\n"
                        ms_footer += f"🍾 Поздравляем победителя с победой\n*Выигрыш: {escape(math.floor(100*reqq[0][2] * 2 * komission_casino)/100)}*💲"
                    elif(callback_query.from_user.id == int(i[:k])):
                        ms_players += f"👁️‍🗨️@{pls[0][0]}  |  отгадывает цвет  ☑️\n" if pls[0][0]!='None' else f"👁️‍🗨️{pls[0][1]}  |  отгадывает цвет  ☑️\n"
                    elif(players.count('R')==2):
                        ms_players += f"🥷🏻@{pls[0][0]}  | загадывает цвет  ☑️\n" if pls[0][0]!='None' else f"🥷🏻{pls[0][1]}  | загадывает цвет  ☑️\n"
                    elif((players.count('R') + players.count('B')==2)):
                        await sql.request_db(f"UPDATE users SET balance = balance + {math.floor(100*reqq[0][2] * 2 * komission_casino)/100} WHERE user_id = {i[:k]};")
                        ms_players += f"🥷🏻@{pls[0][0]}  | загадывает цвет  ☑️\n" if pls[0][0]!='None' else f"🥷🏻{pls[0][1]}  | загадывает цвет  ☑️\n"
                        ms_footer = f"⚫Цвет игрока @{escape(pls[0][0])} не был отгадан\!\n" if pls[0][0]!='None' else f"⚫Цвет игрока {escape(pls[0][1])} не был отгадан\!\n"
                        ms_footer += f"🍾 Поздравляем победителя с победой\n*Выигрыш: {escape(math.floor(100*reqq[0][2] * 2 * komission_casino)/100)}*💲"
                if(len(ms_players)>0):
                    rb_keyboard = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('BLACK♠', callback_data=f'{q}_black'),types.InlineKeyboardButton('RED♥', callback_data=f'{q}_red')).row(types.InlineKeyboardButton('✖LEAVE', callback_data=f'{q}_leaverb'))
                    await bot.delete_message(reqq[0][-2], reqq[0][-1])
                    if('🍾' not in ms_footer):
                        msg = await bot.send_animation(reqq[0][-2], 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.rb_message.format(q,escape(reqq[0][2]),escape(ms_players), ms_footer), reply_markup = rb_keyboard,parse_mode='MarkdownV2')
                    else:
                        msg = await bot.send_animation(reqq[0][-2], 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.rb_message.format(q,escape(reqq[0][2]),escape(ms_players), ms_footer),parse_mode='MarkdownV2')
                    await sql.request_db(f"UPDATE rb_game SET message_id = {msg.message_id} WHERE id = {q};")
            else:
                pass
        except Exception as e:
            await bot.send_message(channel_of_error, '1962\n'+str(e))


#21 очко, выход из комнаты отменённый
@dp.callback_query_handler(lambda c: c.data == 'false_leave_21')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            reqq = await sql.request_db(f"SELECT id, user_id FROM game_21 INNER JOIN users ON game_21.id = users.playing_game_id_21 HAVING user_id = {callback_query.from_user.id};")
            msg, room_21_kb_inline = await game.message_room_21(callback_query.from_user.id, reqq[0][0])
            await send_message(callback_query.from_user.id, msg,room_21_kb_inline, 'MarkdownV2')
        except Exception as e:
            await bot.send_message(channel_of_error, '1975\n'+str(e))


#21 очко, выход из комнаты неокончательный
@dp.callback_query_handler(lambda c: c.data == 'leave_21')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            reqq = await sql.request_db(f"SELECT is_closed, id, user_id, stavka, winner_1 FROM game_21 INNER JOIN users ON game_21.id = users.playing_game_id_21 HAVING user_id = {callback_query.from_user.id};")
            if(reqq[0][0]==2):
                await send_message(callback_query.from_user.id, key_board.leave_21_message, key_board.leave_21_kb_inline)
            else:
                await send_message(callback_query.from_user.id, key_board.menu_game_message, key_board.menu_game_kb_inline)
                req = f'UPDATE users SET status = 12, playing_game_id_21 = 0 WHERE user_id = '+str(callback_query.from_user.id)+';'
                await sql.request_db(req)
                if(reqq[0][-1] == None):
                    req = f'UPDATE users SET balance = balance + {reqq[0][-2]} WHERE user_id = '+str(callback_query.from_user.id)+';'
                    await sql.request_db(req)
                await game.leave_game_21(callback_query.from_user.id, reqq[0][1])
                msg,room_21_kb_inline = await game.message_room_21(callback_query.from_user.id, reqq[0][1])
                req = await sql.request_db(f'SELECT player_1,player_2,player_3,player_4,player_5,player_6,max_players FROM game_21 WHERE id = {reqq[0][1]}')
                k = 0
                for i in req[0][:-1]:
                    reqqq = await sql.request_db(f"SELECT playing_game_id_21 FROM users WHERE user_id = {i};")
                    if(len(reqqq)>0):
                        if(reqqq[0][0]==reqq[0][1]):
                            k+=1
                            await send_message(i, msg,room_21_kb_inline, 'MarkdownV2')
                if(k==0):
                    await sql.request_db(f'UPDATE game_21 SET is_closed = -1 WHERE id = {reqq[0][1]}')
        except Exception as e:
            await bot.send_message(channel_of_error, '2007\n'+str(e))


#21 очко, создание комнаты
@dp.callback_query_handler(lambda c: c.data == 'new_21')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            await sql.request_db("UPDATE users SET status = 24 WHERE user_id = "+str(callback_query.from_user.id)+";")
            id_game = await game.create_game_21(callback_query.from_user.id)
            req = await sql.request_db(f"SELECT max_players, password FROM game_21 WHERE id = {id_game};")
            create_21_kb_inline = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Настройки', callback_data='none'))
            create_21_kb_inline.row(types.InlineKeyboardButton(f'Количество игроков: {req[0][0]}', callback_data='none'))
            create_21_kb_inline.row(types.InlineKeyboardButton('+', callback_data='+1_21_game'))
            create_21_kb_inline.row(types.InlineKeyboardButton(f'Назад', callback_data='21_ochko'))
            await send_message(callback_query.from_user.id, key_board.create_21_message, reply=create_21_kb_inline)
        except Exception as e:
            await bot.send_message(channel_of_error, '2025\n'+str(e))


#21 очко, публичные комнаты
@dp.callback_query_handler(lambda c: '_public_21' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            idx = int(callback_query.data[:callback_query.data.index('_')])
            inline = await game.search_game_21(idx)
            if(inline == '0'):
                menu_21_kb_inline = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('\U00002795 Создать комнату', callback_data='new_21'))
                menu_21_kb_inline.add(types.InlineKeyboardButton('Выбрать игру(0 комнат)', callback_data='0_public_21'))
                menu_21_kb_inline.add(types.InlineKeyboardButton('Приватные комнаты', callback_data='private_room_21'))
                await send_message(callback_query.from_user.id, key_board.empty_public_21_message, reply=menu_21_kb_inline)
            else:
                await send_message(callback_query.from_user.id, key_board.public_21_message, reply=inline)
        except Exception as e:
            await bot.send_message(channel_of_error, '2044\n'+str(e))


#21 очко, приватные комнаты
@dp.callback_query_handler(lambda c: c.data == 'private_room_21')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            await sql.request_db("UPDATE users SET status = 26 WHERE user_id = "+str(callback_query.from_user.id)+";")
            await send_message(callback_query.from_user.id, key_board.to_private_21_message, key_board.error_private_kb_inline)
        except Exception as e:
            await bot.send_message(channel_of_error, '2056\n'+str(e))


#21 очко, вход в публичную комнату, cherez ssulky v chate
@dp.callback_query_handler(lambda c: '_join_2chat' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            idx = int(callback_query.data[:callback_query.data.index('_')])
            st = await sql.request_db(f'SELECT stavka, player_1, player_2, player_3, player_4, player_5, player_6 FROM game_21 WHERE id = {idx}')
            st = st[0]
            players = ''
            for i in st[1:]:
                if(i!=0):
                    reqq = await sql.request_db(f'SELECT username FROM users WHERE user_id = {i}')
                    players += f'@{escape(reqq[0][0])} \n'
            bal = await sql.request_db(f'SELECT balance FROM users WHERE user_id = {callback_query.from_user.id}')
            bal = bal[0][0]
            if(bal>=st[0]):
                join_21_kb_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('Вернуться', callback_data='0_public_21'),types.InlineKeyboardButton('Сделать ставку', callback_data=f'{idx}_to_21'))
                await send_message(callback_query.from_user.id, key_board.join_21_message.format(escape(st[0]),players), join_21_kb_inline, key=1)
                await bot.answer_callback_query(callback_query_id=callback_query.id, show_alert=True, text='Игровой бот уже прислал вам сообщение с подробностями комнаты. Перейдите в бота для того, чтобы начать игру.')
            else:
                await bot.answer_callback_query(callback_query_id=callback_query.id, show_alert=True, text=key_board.not_enough_balance_message)
        except Exception as e:
            await bot.send_message(channel_of_error, '2082\n'+str(e))


#21 очко, вход в публичную комнату, запрос на ставу
@dp.callback_query_handler(lambda c: '_join_21' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            idx = int(callback_query.data[:callback_query.data.index('_')])
            st = await sql.request_db(f'SELECT stavka, player_1, player_2, player_3, player_4, player_5, player_6 FROM game_21 WHERE id = {idx}')
            st = st[0]
            players = ''
            for i in st[1:]:
                if(i!=0):
                    reqq = await sql.request_db(f'SELECT username FROM users WHERE user_id = {i}')
                    players += f'@{escape(reqq[0][0])} \n'
            bal = await sql.request_db(f'SELECT balance FROM users WHERE user_id = {callback_query.from_user.id}')
            bal = bal[0][0]
            if(bal>=st[0]):
                join_21_kb_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('Вернуться', callback_data='0_public_21'),types.InlineKeyboardButton('Сделать ставку', callback_data=f'{idx}_to_21'))
                await send_message(callback_query.from_user.id, key_board.join_21_message.format(escape(st[0]),players), join_21_kb_inline)
            else:
                kayy = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('Вернуться', callback_data='0_public_21'))
                await send_message(callback_query.from_user.id, key_board.tiny_value_stavka_message, kayy)
        except Exception as e:
            await bot.send_message(channel_of_error, '2108\n'+str(e))


#21 очко, вход в комнату, ставка сделана
@dp.callback_query_handler(lambda c: '_to_21' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            idx = int(callback_query.data[:callback_query.data.index('_')])
            stat = await sql.request_db(f"SELECT is_closed FROM game_21 WHERE id = {idx};")
            if(stat[0][0] == 0):
                await game.join_to_21(callback_query.from_user.id, idx)
                req = await sql.request_db(f'SELECT max_players, stavka FROM game_21 WHERE id = {idx}')
                req = req[0]
                await sql.request_db(f'UPDATE users SET balance = balance - {req[1]}, playing_game_id_21 = {idx} WHERE user_id = {callback_query.from_user.id}')
                qq = await sql.request_db(f"SELECT user_id FROM users WHERE playing_game_id_21 = {idx};")
                k = 0
                for i in qq:
                    k+=1
                    msg, room_21_kb_inline = await game.message_room_21(i[0], idx)
                    await send_message(i[0], msg,room_21_kb_inline, 'MarkdownV2')
                if(k==req[0]):
                    await sql.request_db(f'UPDATE game_21 SET is_closed = 2, date = NOW() WHERE id = {idx}')
                    await sql.request_db(f"INSERT INTO mess_21_list VALUES ({idx},'КРУПЬЕ','\n➖➖ИГРА НАЧАЛАСЬ➖➖\n')")
                    await game.start_give_cards(idx)
                    for i in qq:
                        qq = await sql.request_db(f"SELECT last_message_bot FROM users WHERE user_id = {i[0]};")
                        try:
                            await bot.delete_message(i[0],qq[0][0])
                        except:
                            pass
                        msg, room_21_kb_inline = await game.message_room_21(i[0], idx)
                        await sql.request_db(f'UPDATE users SET status = 27 WHERE user_id = {i[0]}')
                        await send_message(i[0], msg,room_21_kb_inline, 'MarkdownV2')
            else:
                await bot.answer_callback_query(callback_query.id, 'К сожалению, данная игра уже начата', True)
        except Exception as e:
            await bot.send_message(channel_of_error, '2146\n'+str(e))



#21 очко, +-1 человек
@dp.callback_query_handler(lambda c: '1_21_game' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            idx = int(callback_query.data[:callback_query.data.index('_')])
            if(idx==1):
                idx = '+1'
            await sql.request_db(f'UPDATE game_21 INNER JOIN users ON game_21.id = users.playing_game_id_21 SET max_players = (CASE WHEN max_players < 1 THEN 1 ELSE (max_players {idx})end)  WHERE users.user_id = {callback_query.from_user.id};')
            req = await sql.request_db(f"SELECT max_players, password, users.user_id FROM game_21 INNER JOIN users ON game_21.id = users.playing_game_id_21 HAVING users.user_id = {callback_query.from_user.id};")
            create_21_kb_inline = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Настройки', callback_data='none'))
            create_21_kb_inline.row(types.InlineKeyboardButton(f'Количество игроков: {req[0][0]}', callback_data='none'))
            if(req[0][0]==6):
                create_21_kb_inline.row(types.InlineKeyboardButton('-', callback_data=f'-1_21_game_'))
                is_private = '❌' if req[0][1]=='0' else '✅'
                create_21_kb_inline.row(types.InlineKeyboardButton(f'Приватная игра: {is_private}', callback_data='status_private_21'))
            elif(req[0][0]==1):
                create_21_kb_inline.row(types.InlineKeyboardButton('+', callback_data='+1_21_game'))
            else:
                create_21_kb_inline.row(types.InlineKeyboardButton('-', callback_data=f'-1_21_game_'),types.InlineKeyboardButton('+', callback_data='+1_21_game'))
                is_private = '❌' if req[0][1]=='0' else '✅'
                create_21_kb_inline.row(types.InlineKeyboardButton(f'Приватная игра: {is_private}', callback_data='status_private_21'))
            create_21_kb_inline.row(types.InlineKeyboardButton(f'Назад', callback_data='21_ochko'))
            await send_message(callback_query.from_user.id, key_board.create_21_message, reply=create_21_kb_inline)
        except Exception as e:
            await bot.send_message(channel_of_error, '2176\n'+str(e))


#21 очко, смена приватности комнаты
@dp.callback_query_handler(lambda c: 'status_private_21' == c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            reqq = await sql.request_db(f"SELECT id, user_id FROM game_21 INNER JOIN users ON game_21.id = users.playing_game_id_21 HAVING user_id = {callback_query.from_user.id};")
            reqq = reqq[0][0]
            await sql.request_db(f"UPDATE game_21 SET password = (CASE WHEN password = '0' THEN '1' ELSE '0' end)  WHERE id = {reqq};")
            req = await sql.request_db(f"SELECT max_players, password FROM game_21 WHERE id = {reqq};")
            create_21_kb_inline = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Настройки', callback_data='none'))
            create_21_kb_inline.row(types.InlineKeyboardButton(f'Количество игроков: {req[0][0]}', callback_data='none'))
            if(req[0][0]==6):
                create_21_kb_inline.row(types.InlineKeyboardButton('-', callback_data=f'-1_21_game_'))
                is_private = '❌' if req[0][1]=='0' else '✅'
                create_21_kb_inline.row(types.InlineKeyboardButton(f'Приватная игра: {is_private}', callback_data='status_private_21'))
            elif(req[0][0]==1):
                create_21_kb_inline.row(types.InlineKeyboardButton('+', callback_data='+1_21_game'))
            else:
                create_21_kb_inline.row(types.InlineKeyboardButton('-', callback_data=f'-1_21_game_'),types.InlineKeyboardButton('+', callback_data='+1_21_game'))
                is_private = '❌' if req[0][1]=='0' else '✅'
                create_21_kb_inline.row(types.InlineKeyboardButton(f'Приватная игра: {is_private}', callback_data='status_private_21'))
            create_21_kb_inline.row(types.InlineKeyboardButton(f'Назад', callback_data='21_ochko'))
            await send_message(callback_query.from_user.id, key_board.create_21_message, reply=create_21_kb_inline)
        except Exception as e:
            await bot.send_message(channel_of_error, '2204\n'+str(e))


#Реф ссылка
@dp.callback_query_handler(lambda c: c.data == 'ref_link')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            req1 = await sql.request_db(f"SELECT SUM(act.usd), users.from_ref_id FROM (SELECT * FROM active_deposits_bots WHERE status = 1) act INNER JOIN users ON users.user_id = act.user_id GROUP BY from_ref_id HAVING from_ref_id = {callback_query.from_user.id};")
            is_par = await sql.request_db(f"SELECT user_id FROM partners WHERE user_id = {callback_query.from_user.id};")
            if(len(is_par)==0):
                koef = koef_ref
            else:
                koef = partner_ref
            req1 = escape(req1[0][0] * koef) if len(req1)>0 else escape(0)
            req2 = await sql.request_db(f"SELECT COUNT(*) FROM users WHERE from_ref_id = {callback_query.from_user.id};")
            reqq = await sql.request_db(f"SELECT * FROM partners WHERE user_id = {callback_query.from_user.id}")
            reqq = 1 if len(reqq)==0 else 5
            await send_message(callback_query.from_user.id, key_board.ref_message.format(reqq, req2[0][0], req1, str(callback_query.from_user.id)), key_board.reflink_kb_inline)
        except Exception as e:
            await bot.send_message(channel_of_error, '2225\n'+str(e))


#Профиль
@dp.callback_query_handler(lambda c: c.data == 'profile_link')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            dat = await sql.request_db(f"SELECT username, dat, count_games, count_prizes FROM users WHERE user_id = {callback_query.from_user.id};")
            is_par = await sql.request_db(f"SELECT user_id FROM partners WHERE user_id = {callback_query.from_user.id};")
            if(len(is_par)==0):
                await send_message(callback_query.from_user.id, key_board.profile_chat_message.format(callback_query.from_user.id, escape(dat[0][0]), escape(dat[0][1]), dat[0][2], escape(dat[0][3])), key_board.ref_kb_inline,key=1)
            else:
                req = await sql.request_db(f"SELECT * FROM partners WHERE user_id = {callback_query.from_user.id};")
                req1 = await sql.request_db(f"SELECT SUM(act.usd), users.from_ref_id FROM users INNER JOIN (SELECT * FROM active_deposits_bots ) act ON users.user_id = act.user_id GROUP BY from_ref_id HAVING from_ref_id = {callback_query.from_user.id};")
                req1 = req1[0][0] * partner_ref if len(req1)>0 else 0
                req2 = await sql.request_db(f"SELECT SUM(act.usd), users.from_ref_id FROM users INNER JOIN (SELECT * FROM active_deposits_bots WHERE TIMESTAMPDIFF(DAY,date,CURDATE()) = 0) act ON users.user_id = act.user_id GROUP BY from_ref_id HAVING from_ref_id = {callback_query.from_user.id};")
                req2 = req2[0][0] * partner_ref if len(req2)>0 else 0
                req3 = await sql.request_db(f"SELECT COUNT(*) FROM users WHERE from_ref_id = {callback_query.from_user.id};")
                req4 = await sql.request_db(f"SELECT COUNT(*) FROM users WHERE from_ref_id = {callback_query.from_user.id} AND TIMESTAMPDIFF(DAY,dat,CURDATE()) = 0;")
                await send_message(callback_query.from_user.id, key_board.partner_profile_message.format(escape(req[0][1]), escape(dat[0][1]), req[0][3], escape(req1), escape(req2), req3[0][0], req4[0][0]), key_board.partner_kb_inline,key=1)
        except Exception as e:
            await bot.send_message(channel_of_error, '2248\n'+str(e))


#Вывод средств
@dp.callback_query_handler(lambda c: c.data == 'withdraw_money')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            req = await sql.request_db(f"SELECT need_play_for_withdraw FROM users WHERE user_id = {callback_query.from_user.id};")
            if(req[0][0]<0.1):
                await sql.request_db(f"DELETE withdraws FROM withdraws WHERE user_id = {callback_query.from_user.id} AND status = 0;")
                await send_message(callback_query.from_user.id, key_board.withdraw_menu_message, key_board.withdraw_menu_kb_inline)
            else:
                await send_message(callback_query.from_user.id, key_board.withdraw_error_message.format(escape(int(100*req[0][0])/100)), key_board.wallet_client_kb_inline)
        except Exception as e:
            await bot.send_message(channel_of_error, '2264\n'+str(e))


#Вывод средств
@dp.callback_query_handler(lambda c: '_withdraw_method' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            method = callback_query.data[:callback_query.data.index('_')]
            await sql.request_db(f"INSERT INTO withdraws(user_id, type) VALUES ({callback_query.from_user.id},'{method}');")
            await sql.request_db(f"UPDATE users SET status = 32 WHERE user_id = {callback_query.from_user.id};")
            await send_message(callback_query.from_user.id, key_board.withdraw_address_message, key_board.withdraw_return_kb_inline)
        except Exception as e:
            await bot.send_message(channel_of_error, '2278\n'+str(e))


#Подарить промокод
@dp.callback_query_handler(lambda c: c.data == 'input_value_promo')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            await send_message(callback_query.from_user.id, key_board.value_promo_message)
            req = 'UPDATE users SET status = 25 WHERE user_id = '+str(callback_query.from_user.id)+';'
            await sql.request_db(req)
        except Exception as e:
            await bot.send_message(channel_of_error, '2291\n'+str(e))


#СПисок промокодов
@dp.callback_query_handler(lambda c: c.data == 'my_promo')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            req = 'SELECT COUNT(*) FROM gifts WHERE to_user_id = '+str(callback_query.from_user.id)+';'
            idx1 = await sql.request_db(req)
            idx1 = idx1[0][0]
            req = 'SELECT COUNT(*) FROM gifts WHERE from_user_id = '+str(callback_query.from_user.id)+';'
            idx2 = await sql.request_db(req)
            idx2 = idx2[0][0]
            await send_message(callback_query.from_user.id, key_board.list_my_promo.format(str(idx1),str(idx2)), key_board.list_promo_kb_inline)
        except Exception as e:
            await bot.send_message(channel_of_error, '2308\n'+str(e))


#СПисок неактивированных промокодов
@dp.callback_query_handler(lambda c: c.data == 'list_my_promo')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            req = 'SELECT text, value FROM gifts WHERE from_user_id = '+str(callback_query.from_user.id)+' AND is_activated = 0;'
            idx = await sql.request_db(req)
            strok = ''
            for i in idx:
                strok += '<a href="{}?start={}">Промокод</a> - {}💲\n'.format(key_board.link_bot, i[0], i[1])
            if(len(strok)==0):
                strok = 'У вас нет неактивированных промокодов'
            await send_message(callback_query.from_user.id, strok, mode='HTML')
        except Exception as e:
            await bot.send_message(channel_of_error, '2326\n'+str(e))


#Пополнение
@dp.callback_query_handler(lambda c: c.data == 'add_money')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            await send_message(callback_query.from_user.id, key_board.addmoney_message, key_board.addmoney_client_kb_inline,'MarkdownV2')
            req = 'UPDATE users SET status = 5 WHERE user_id = '+str(callback_query.from_user.id)+';'
            await sql.request_db(req)
        except Exception as e:
            await bot.send_message(channel_of_error, '2339\n'+str(e))


#Возвращение к балансу
@dp.callback_query_handler(lambda c: c.data == 'return_wallet')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            await sql.request_db(f"DELETE withdraws FROM withdraws WHERE user_id = {callback_query.from_user.id} AND status = 0;")
            req = 'SELECT balance FROM users WHERE user_id = '+str(callback_query.from_user.id)+';'
            idx = await sql.request_db(req)
            idx = idx[0]
            await send_message(callback_query.from_user.id, key_board.wallet_message.format(escape(float(idx[0]))), key_board.wallet_client_kb_inline)
            req = 'UPDATE users SET status = 2 WHERE user_id = '+str(callback_query.from_user.id)+';'
            await sql.request_db(req)
        except Exception as e:
            await bot.send_message(channel_of_error, '2356\n'+str(e))


#DICE
@dp.message_handler(content_types=types.ContentType.DICE, chat_type=[types.ChatType.PRIVATE])
async def Dice(m: types.Message):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {m.from_user.id};")
    if(len(is_par)==0):
        try:
            sq = await sql.request_db(f"SELECT address, username, firstname FROM users WHERE user_id = {m.from_user.id};")
            if(sq[0][1]!=m.from_user.username):
                await sql.request_db(f"UPDATE users SET username = '{m.from_user.username}' WHERE user_id = {m.from_user.id};")
            if(sq[0][2]!=m.from_user.first_name):
                await sql.request_db(f"UPDATE users SET firstname = '{m.from_user.first_name}' WHERE user_id = {m.from_user.id};")
            req = "UPDATE addresses SET status = 0 WHERE status = 1 AND address = '"+sq[0][0]+"';"
            await sql.request_db(req)
            if(m.forward_from == None):
                req = 'SELECT status, last_message_bot FROM users WHERE user_id = '+str(m.from_user.id)+';'
                idx = await sql.request_db(req)
                idx = idx[0]
                await sql.request_db(f"UPDATE users SET last_message_bot = 0 WHERE user_id = {m.from_user.id};")
                if(idx[0] in [14,15,16,17,21,20]):#NEED FIX
                    time.sleep(gamedelay_of_id[idx[0]])
                    result = m.dice.value
                    if(idx[0]==15 and m.dice.emoji == '⚽'):#543
                        stavka = await sql.request_db(f"SELECT stavka FROM games WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Penalty';")
                        if(result in [3,4,5]):
                            await send_message(m.from_user.id, key_board.foot_full_victory_message.format(escape(str(int(150 * stavka[0][0])/100))),key_board.restart_minigame_kb_inline[idx[0]], 'MarkdownV2',key=1)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {int(50 * stavka[0][0])/100}, count_games = count_games + 1, count_prizes = count_prizes + {int(150 * stavka[0][0])/100}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), balance = balance + {int(150 * stavka[0][0])/100}, status = 23, playing_game_id_mini = 0 WHERE user_id = {m.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {1.5 * stavka[0][0]} WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Penalty';")
                        else:
                            await send_message(m.from_user.id, key_board.lose_mini_message,key_board.restart_minigame_kb_inline[idx[0]], 'MarkdownV2',key=1)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {-1 * stavka[0][0]}, count_games = count_games + 1, status = 23, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), playing_game_id_mini = 0 WHERE user_id = {m.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {-1 * stavka[0][0]} WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Penalty';")
                    elif(idx[0]==17 and m.dice.emoji == '🏀'):
                        stavka = await sql.request_db(f"SELECT stavka FROM games WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Basketball';")
                        if(result in [4,5]):
                            await send_message(m.from_user.id, key_board.basket_full_victory_message.format(escape(str(int(150 * stavka[0][0])/100))),key_board.restart_minigame_kb_inline[idx[0]], 'MarkdownV2',key=1)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {int(50 * stavka[0][0])/100}, count_games = count_games + 1, count_prizes = count_prizes + {int(150 * stavka[0][0])/100}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), balance = balance + {int(150 * stavka[0][0])/100}, status = 23, playing_game_id_mini = 0 WHERE user_id = {m.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {1.5 * stavka[0][0]} WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Basketball';")
                        else:
                            await send_message(m.from_user.id, key_board.lose_mini_message,key_board.restart_minigame_kb_inline[idx[0]], 'MarkdownV2',key=1)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {-1 * stavka[0][0]}, count_games = count_games + 1, status = 23, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), playing_game_id_mini = 0 WHERE user_id = {m.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {-1 * stavka[0][0]} WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Basketball';")
                    elif(idx[0]==14 and m.dice.emoji == '🎳'):
                        stavka = await sql.request_db(f"SELECT stavka FROM games WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Bowling';")
                        if(result == 5):
                            await send_message(m.from_user.id, key_board.bowl_nonfull_victory_message.format(escape(str(stavka[0][0]))),key_board.restart_minigame_kb_inline[idx[0]], 'MarkdownV2',key=1)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {0 * stavka[0][0]}, count_games = count_games + 1, count_prizes = count_prizes + {stavka[0][0]}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), balance = balance + {stavka[0][0]}, status = 23, playing_game_id_mini = 0 WHERE user_id = {m.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {stavka[0][0]} WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Bowling';")
                        elif(result == 6):
                            await send_message(m.from_user.id, key_board.bowl_full_victory_message.format(escape(str(3 * stavka[0][0]))),key_board.restart_minigame_kb_inline[idx[0]], 'MarkdownV2',key=1)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {2 * stavka[0][0]}, count_games = count_games + 1, count_prizes = count_prizes + {3 * stavka[0][0]}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), balance = balance + {3 * stavka[0][0]}, status = 23, playing_game_id_mini = 0 WHERE user_id = {m.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {3 * stavka[0][0]} WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Bowling';")
                        else:
                            await send_message(m.from_user.id, key_board.lose_mini_message,key_board.restart_minigame_kb_inline[idx[0]], 'MarkdownV2',key=1)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {-1 * stavka[0][0]}, count_games = count_games + 1, status = 23, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), playing_game_id_mini = 0 WHERE user_id = {m.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {-1 * stavka[0][0]} WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Bowling';")
                    elif(idx[0]==16 and m.dice.emoji == '🎯'):
                        stavka = await sql.request_db(f"SELECT stavka FROM games WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Darts';")
                        if(result == 5):
                            await send_message(m.from_user.id, key_board.darts_nonfull_victory_message.format(escape(str(stavka[0][0]))),key_board.restart_minigame_kb_inline[idx[0]], 'MarkdownV2',key=1)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {0 * stavka[0][0]}, count_games = count_games + 1, count_prizes = count_prizes + {stavka[0][0]}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), balance = balance + {stavka[0][0]}, status = 23, playing_game_id_mini = 0 WHERE user_id = {m.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {stavka[0][0]} WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Darts';")
                        elif(result == 6):
                            await send_message(m.from_user.id, key_board.darts_full_victory_message.format(escape(str(3 * stavka[0][0]))),key_board.restart_minigame_kb_inline[idx[0]], 'MarkdownV2',key=1)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {2 * stavka[0][0]}, count_games = count_games + 1, count_prizes = count_prizes + {3 * stavka[0][0]}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), balance = balance + {3 * stavka[0][0]}, status = 23, playing_game_id_mini = 0 WHERE user_id = {m.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {3 * stavka[0][0]} WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Darts';")
                        else:
                            await send_message(m.from_user.id, key_board.lose_mini_message,key_board.restart_minigame_kb_inline[idx[0]], 'MarkdownV2')
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {-1 * stavka[0][0]}, count_games = count_games + 1, status = 23, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), playing_game_id_mini = 0 WHERE user_id = {m.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {-1 * stavka[0][0]} WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Darts';",key=1)
                    elif(idx[0]==21 and m.dice.emoji == '🎲'):
                        game = await sql.request_db(f"SELECT * FROM games WHERE user_id = {m.from_user.id} AND (status = 2 OR status = 0) AND type = 'Dice';")
                        target = game[0][3]
                        stavka = game[0][4]
                        if(result == target):
                            await send_message(m.from_user.id, key_board.dice_full_victory_message.format(escape(str(stavka * 3))),key_board.restart_minigame_kb_inline[idx[0]], 'MarkdownV2',key=1)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {2 * stavka}, count_games = count_games + 1, count_prizes = count_prizes + {3 * stavka}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka} THEN (need_play_for_withdraw - {stavka}) ELSE (0)end), balance = balance + {stavka * 3}, status = 23, playing_game_id_mini = 0 WHERE user_id = {m.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {3 * stavka} WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Dice';")
                        elif((result-target == 1) or (result-target == -1) or (result == 1 and target == 6) or (result == 6 and target == 1)):
                            await send_message(m.from_user.id, key_board.dice_nonfull_victory_message.format(escape(str(0.5 * stavka))),key_board.restart_minigame_kb_inline[idx[0]], 'MarkdownV2',key=1)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {-1 * int(50 * stavka)/100}, count_games = count_games + 1, count_prizes = count_prizes + {int(50 * stavka)/100}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka} THEN (need_play_for_withdraw - {stavka}) ELSE (0)end), balance = balance + {int(50 * stavka)/100}, status = 23, playing_game_id_mini = 0 WHERE user_id = {m.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {int(50 * stavka)/100} WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Dice';")
                        else:
                            await send_message(m.from_user.id, key_board.lose_mini_message,key_board.restart_minigame_kb_inline[idx[0]], 'MarkdownV2',key=1)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {-1 * stavka}, count_games = count_games + 1, status = 23, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka} THEN (need_play_for_withdraw - {stavka}) ELSE (0)end), playing_game_id_mini = 0 WHERE user_id = {m.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {-1 * stavka} WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Dice';")
                    elif(idx[0]==20 and m.dice.emoji == '🎰'):
                        stavka = await sql.request_db(f"SELECT stavka FROM games WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Slots';")
                        if(result == 64):
                            await send_message(m.from_user.id, key_board.slots777_vict_message.format(escape(str(7 * stavka[0][0]))),key_board.restart_minigame_kb_inline[idx[0]], 'MarkdownV2',key=1)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {6 * stavka[0][0]}, count_games = count_games + 1, count_prizes = count_prizes + {7 * stavka[0][0]}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), balance = balance + {7 * stavka[0][0]}, status = 23, playing_game_id_mini = 0 WHERE user_id = {m.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {7 * stavka[0][0]} WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Slots';")
                        elif(result in [43,1,22]):
                            await send_message(m.from_user.id, key_board.slots111_vict_message.format(escape(str(3 * stavka[0][0]))),key_board.restart_minigame_kb_inline[idx[0]], 'MarkdownV2',key=1)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {2 * stavka[0][0]}, count_games = count_games + 1, count_prizes = count_prizes + {3 * stavka[0][0]}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), balance = balance + {3 * stavka[0][0]}, status = 23, playing_game_id_mini = 0 WHERE user_id = {m.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {3 * stavka[0][0]} WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Slots';")
                        elif(result in [11,59,42,27,41,44]):
                            await send_message(m.from_user.id, key_board.slotsLL_vict_message.format(escape(str(2 * stavka[0][0]))),key_board.restart_minigame_kb_inline[idx[0]], 'MarkdownV2',key=1)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {1 * stavka[0][0]}, count_games = count_games + 1, count_prizes = count_prizes + {2 * stavka[0][0]}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), balance = balance + {2 * stavka[0][0]}, status = 23, playing_game_id_mini = 0 WHERE user_id = {m.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {2 * stavka[0][0]} WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Slots';")
                        elif(result in [48,61,62,63,60,52,32,56,16]):
                            await send_message(m.from_user.id, key_board.slots77_vict_message.format(escape(str(2 * stavka[0][0]))),key_board.restart_minigame_kb_inline[idx[0]], 'MarkdownV2',key=1)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {1 * stavka[0][0]}, count_games = count_games + 1, count_prizes = count_prizes + {2 * stavka[0][0]}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), balance = balance + {2 * stavka[0][0]}, status = 23, playing_game_id_mini = 0 WHERE user_id = {m.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {2 * stavka[0][0]} WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Slots';")
                        else:
                            await send_message(m.from_user.id, key_board.lose_mini_message,key_board.restart_minigame_kb_inline[idx[0]], 'MarkdownV2',key=1)
                            await sql.request_db(f"UPDATE users SET balance_solo = balance_solo + {-1 * stavka[0][0]}, count_games = count_games + 1, status = 23, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {stavka[0][0]} THEN (need_play_for_withdraw - {stavka[0][0]}) ELSE (0)end), playing_game_id_mini = 0 WHERE user_id = {m.from_user.id};")
                            await sql.request_db(f"UPDATE games SET status = 1, result = {-1 * stavka[0][0]} WHERE user_id = {m.from_user.id} AND status = 0 AND type = 'Slots';")
            else:
                idx = await sql.request_db(f'SELECT status, last_message_bot FROM users WHERE user_id = {m.from_user.id};')
                idx = idx[0]
                if(idx[0] in [14,15,16,17,21,20]):
                    idx = await sql.request_db(f'SELECT type, stavka FROM games WHERE user_id = {str(m.from_user.id)} AND status = 0;')
                    idx = idx[0]
                    idx_ = list(game_of_id.keys())[list(game_of_id.values()).index(idx[0])]
                    await send_message(m.from_user.id, key_board.game_message_id[idx_].format(escape(idx[1]))+'\nПересланные сообщения запрещены\.', key_board.minigame_kb_inline, 'MarkdownV2',key=1)
        except Exception as e:
            await bot.send_message(channel_of_error, '2475\n'+str(e))


#Отмена Миниигры
@dp.callback_query_handler(lambda c: c.data == 'cancel_game')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            await send_message(callback_query.from_user.id, key_board.menu_game_message, key_board.menu_game_kb_inline)
            req = await sql.request_db(f'SELECT stavka FROM games WHERE user_id = {callback_query.from_user.id} AND status = 0;')
            if(len(req)):
                await sql.request_db(f'UPDATE users SET status = 12, balance = balance + {req[0][0]} WHERE user_id = {callback_query.from_user.id};')
                await sql.request_db(f"UPDATE games SET status = -1 WHERE user_id = {callback_query.from_user.id} AND status = 0;")
            req = await sql.request_db(f'SELECT stavka FROM game_21 WHERE player_1 = {callback_query.from_user.id} AND is_closed = 0;')
            if(len(req)):
                await sql.request_db(f'UPDATE users SET status = 12, balance = balance + {req[0][0]} WHERE user_id = {callback_query.from_user.id};')
                await sql.request_db(f"DELETE FROM game_21 WHERE user_id = {callback_query.from_user.id} AND is_closed = 0;")
        except Exception as e:
            await bot.send_message(channel_of_error, '2494\n'+str(e))


#Продолжение миниигры
@dp.callback_query_handler(lambda c: c.data == 'continue_game')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            idx = await sql.request_db(f'SELECT type, stavka, target_number FROM games WHERE user_id = {callback_query.from_user.id} AND status = 0;')
            idx = idx[0]
            idx_ = list(game_of_id.keys())[list(game_of_id.values()).index(idx[0])]
            if(idx[0]=='Dice'):
                await send_message(callback_query.from_user.id, key_board.game_message_id[idx_].format(idx[2],escape(idx[1])), key_board.minigame_kb_inline, 'MarkdownV2')
            else:
                await send_message(callback_query.from_user.id, key_board.game_message_id[idx_].format(escape(idx[1])), key_board.minigame_kb_inline, 'MarkdownV2')
        except Exception as e:
            await bot.send_message(channel_of_error, '2511\n'+str(e))


#Меню миниигр
@dp.callback_query_handler(lambda c: c.data == 'minigames')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            qq = await sql.request_db(f"SELECT id, chat_id, password FROM multigames WHERE status = 0 AND players LIKE '%{callback_query.from_user.id}%';")
            if(len(qq)==0):
                await send_message(callback_query.from_user.id, key_board.menu_game_message,key_board.menu_minigame_kb_inline)
                req = 'UPDATE users SET status = 13 WHERE user_id = '+str(callback_query.from_user.id)+';'
                await sql.request_db(req)
            elif(qq[0][2]=='0'):
                ree = await sql.request_db(f"SELECT link FROM chats WHERE chat_id = {qq[0][1]};")
                link_game_kb_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('К ИГРЕ', url = ree[0][0]))
                await send_message(callback_query.from_user.id, key_board.link_multi_message.format(qq[0][0]), link_game_kb_inline)
            else:
                await send_message(callback_query.from_user.id, key_board.pass_multigame_message.format(escape(qq[0][2]), qq[0][0]),key_board.multigame_kb_inline, 'MarkdownV2')
        except Exception as e:
            await bot.send_message(channel_of_error, '2532\n'+str(e))


#Кубик
@dp.callback_query_handler(lambda c: 'req_dice' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            qq = await sql.request_db(f"SELECT id, chat_id, password FROM multigames WHERE status = 0 AND players LIKE '%{callback_query.from_user.id}%';")
            if(len(qq)==0):
                if(callback_query.data[0] == '1'):
                    idxx = await sql.request_db(f'SELECT balance FROM users WHERE user_id = {str(callback_query.from_user.id)};')
                    idxx = idxx[0]
                    req = await sql.request_db(f'SELECT * FROM games WHERE user_id = {callback_query.from_user.id} ORDER BY id DESC LIMIT 1;')
                    req = req[0]
                    if(idxx[0]>=req[4]):
                        await send_message(callback_query.from_user.id, key_board.game_message_id[21].format(req[3],escape(req[4])),key_board.minigame_kb_inline, 'MarkdownV2')
                        reqq = await sql.request_db("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = 'games';")
                        reqq = reqq[0][0]
                        await sql.request_db(f"INSERT INTO games(user_id, type, target_number, stavka, date, status, result) VALUES ({callback_query.from_user.id},'Dice',{req[3]},{req[4]},NOW(),0,0);")
                        await sql.request_db(f"UPDATE users SET balance = balance - {req[4]}, playing_game_id_mini = {reqq}, status = 21 WHERE user_id = {callback_query.from_user.id};")
                    else:
                        await send_message(callback_query.from_user.id, key_board.error_value_stavka_message, key_board.minigame_kb_inline, 'MarkdownV2')
                else:
                    await send_message(callback_query.from_user.id, key_board.game_message_id[21][:389]+key_board.number_dice_message,key_board.dice_number_kb_inline, 'MarkdownV2')
                    req = 'UPDATE users SET status = 21 WHERE user_id = '+str(callback_query.from_user.id)+';'
                    await sql.request_db(req)
            elif(qq[0][2]=='0'):
                ree = await sql.request_db(f"SELECT link FROM chats WHERE chat_id = {qq[0][1]};")
                link_game_kb_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('К ИГРЕ', url = ree[0][0]))
                await send_message(callback_query.from_user.id, key_board.link_multi_message.format(qq[0][0]), link_game_kb_inline)
            else:
                await send_message(callback_query.from_user.id, key_board.pass_multigame_message.format(escape(qq[0][2]), qq[0][0]),key_board.multigame_kb_inline, 'MarkdownV2')
        except Exception as e:
            await bot.send_message(channel_of_error, '2567\n'+str(e))


#Кубик(выбор номера)
@dp.callback_query_handler(lambda c: c.data[:11] == 'dice_number')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            await send_message(callback_query.from_user.id, key_board.game_message_id[21][:252]+key_board.value_stavka_message,key_board.minigame_kb_inline, 'MarkdownV2')
            req = 'INSERT INTO games(user_id, type, target_number, stavka, date, status) VALUES ('+str(callback_query.from_user.id)+",'Dice',"+callback_query.data[11:12]+",0.0,NOW(),2);"
            await sql.request_db(req)
        except Exception as e:
            await bot.send_message(channel_of_error, '2580\n'+str(e))


#Слоты
@dp.callback_query_handler(lambda c: 'slots' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            qq = await sql.request_db(f"SELECT id, chat_id, password FROM multigames WHERE status = 0 AND players LIKE '%{callback_query.from_user.id}%';")
            if(len(qq)==0):
                if(callback_query.data[0] == '1'):
                    idxx = await sql.request_db(f'SELECT balance FROM users WHERE user_id = {str(callback_query.from_user.id)};')
                    idxx = idxx[0]
                    req = await sql.request_db(f'SELECT * FROM games WHERE user_id = {callback_query.from_user.id} ORDER BY id DESC LIMIT 1;')
                    req = req[0]
                    if(idxx[0]>=req[4]):
                        await send_message(callback_query.from_user.id, key_board.game_message_id[20].format(escape(req[4])),key_board.minigame_kb_inline, 'MarkdownV2')
                        reqq = await sql.request_db("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = 'games';")
                        reqq = reqq[0][0]
                        await sql.request_db(f"INSERT INTO games(user_id, type, target_number, stavka, date, status, result) VALUES ({callback_query.from_user.id},'Slots',1,{req[4]},NOW(),0,0);")
                        await sql.request_db(f"UPDATE users SET balance = balance - {req[4]}, playing_game_id_mini = {reqq}, status = 20 WHERE user_id = {callback_query.from_user.id};")
                    else:
                        await send_message(callback_query.from_user.id, key_board.error_value_stavka_message, key_board.minigame_kb_inline, 'MarkdownV2')
                else:
                    await send_message(callback_query.from_user.id, key_board.game_message_id[20][:-74]+key_board.value_stavka_message,key_board.minigame_kb_inline, 'MarkdownV2')
                    req = 'UPDATE users SET status = 20 WHERE user_id = '+str(callback_query.from_user.id)+';'
                    await sql.request_db(req)
            elif(qq[0][2]=='0'):
                ree = await sql.request_db(f"SELECT link FROM chats WHERE chat_id = {qq[0][1]};")
                link_game_kb_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('К ИГРЕ', url = ree[0][0]))
                await send_message(callback_query.from_user.id, key_board.link_multi_message.format(qq[0][0]), link_game_kb_inline)
            else:
                await send_message(callback_query.from_user.id, key_board.pass_multigame_message.format(escape(qq[0][2]), qq[0][0]),key_board.multigame_kb_inline, 'MarkdownV2')
        except Exception as e:
            await bot.send_message(channel_of_error, '2615\n'+str(e))


#Боулинг
@dp.callback_query_handler(lambda c: 'bowling' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            if(callback_query.data[0] == '1'):
                idxx = await sql.request_db(f'SELECT balance FROM users WHERE user_id = {str(callback_query.from_user.id)};')
                idxx = idxx[0]
                req = await sql.request_db(f'SELECT * FROM games WHERE user_id = {callback_query.from_user.id} ORDER BY id DESC LIMIT 1;')
                req = req[0]
                if(idxx[0]>=req[4]):
                    await send_message(callback_query.from_user.id, key_board.game_message_id[14].format(escape(req[4])),key_board.minigame_kb_inline, 'MarkdownV2')
                    reqq = await sql.request_db("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = 'games';")
                    reqq = reqq[0][0]
                    await sql.request_db(f"INSERT INTO games(user_id, type, target_number, stavka, date, status, result) VALUES ({callback_query.from_user.id},'Bowling',1,{req[4]},NOW(),0,0);")
                    await sql.request_db(f"UPDATE users SET balance = balance - {req[4]}, playing_game_id_mini = {reqq}, status = 14 WHERE user_id = {callback_query.from_user.id};")
                else:
                    await send_message(callback_query.from_user.id, key_board.error_value_stavka_message, key_board.minigame_kb_inline, 'MarkdownV2')
            else:
                await send_message(callback_query.from_user.id, key_board.game_message_id[14][:-74]+key_board.value_stavka_message,key_board.minigame_kb_inline, 'MarkdownV2')
                req = 'UPDATE users SET status = 14 WHERE user_id = '+str(callback_query.from_user.id)+';'
                await sql.request_db(req)
        except Exception as e:
            await bot.send_message(channel_of_error, '2642\n'+str(e))
#Дартс
@dp.callback_query_handler(lambda c: 'darts' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            if(callback_query.data[0] == '1'):
                idxx = await sql.request_db(f'SELECT balance FROM users WHERE user_id = {str(callback_query.from_user.id)};')
                idxx = idxx[0]
                req = await sql.request_db(f'SELECT * FROM games WHERE user_id = {callback_query.from_user.id} ORDER BY id DESC LIMIT 1;')
                req = req[0]
                if(idxx[0]>=req[4]):
                    await send_message(callback_query.from_user.id, key_board.game_message_id[16].format(escape(req[4])),key_board.minigame_kb_inline, 'MarkdownV2')
                    reqq = await sql.request_db("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = 'games';")
                    reqq = reqq[0][0]
                    await sql.request_db(f"INSERT INTO games(user_id, type, target_number, stavka, date, status, result) VALUES ({callback_query.from_user.id},'Darts',1,{req[4]},NOW(),0,0);")
                    await sql.request_db(f"UPDATE users SET balance = balance - {req[4]}, playing_game_id_mini = {reqq}, status = 16 WHERE user_id = {callback_query.from_user.id};")
                else:
                    await send_message(callback_query.from_user.id, key_board.error_value_stavka_message, key_board.minigame_kb_inline, 'MarkdownV2')
            else:
                await send_message(callback_query.from_user.id, key_board.game_message_id[16][:-74]+key_board.value_stavka_message,key_board.minigame_kb_inline, 'MarkdownV2')
                req = 'UPDATE users SET status = 16 WHERE user_id = '+str(callback_query.from_user.id)+';'
                await sql.request_db(req)
        except Exception as e:
            await bot.send_message(channel_of_error, '2667\n'+str(e))
#Пенальти
@dp.callback_query_handler(lambda c: 'penalty' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            if(callback_query.data[0] == '1'):
                idxx = await sql.request_db(f'SELECT balance FROM users WHERE user_id = {str(callback_query.from_user.id)};')
                idxx = idxx[0]
                req = await sql.request_db(f'SELECT * FROM games WHERE user_id = {callback_query.from_user.id} ORDER BY id DESC LIMIT 1;')
                req = req[0]
                if(idxx[0]>=req[4]):
                    await send_message(callback_query.from_user.id, key_board.game_message_id[15].format(escape(req[4])),key_board.minigame_kb_inline, 'MarkdownV2')
                    reqq = await sql.request_db("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = 'games';")
                    reqq = reqq[0][0]
                    await sql.request_db(f"INSERT INTO games(user_id, type, target_number, stavka, date, status, result) VALUES ({callback_query.from_user.id},'Penalty',1,{req[4]},NOW(),0,0);")
                    await sql.request_db(f"UPDATE users SET balance = balance - {req[4]}, playing_game_id_mini = {reqq}, status = 15 WHERE user_id = {callback_query.from_user.id};")
                else:
                    await send_message(callback_query.from_user.id, key_board.error_value_stavka_message, key_board.minigame_kb_inline, 'MarkdownV2')
            else:
                await send_message(callback_query.from_user.id, key_board.game_message_id[15][:-74]+key_board.value_stavka_message,key_board.minigame_kb_inline, 'MarkdownV2')
                req = 'UPDATE users SET status = 15 WHERE user_id = '+str(callback_query.from_user.id)+';'
                await sql.request_db(req)
        except Exception as e:
            await bot.send_message(channel_of_error, '2692\n'+str(e))
#Бasket
@dp.callback_query_handler(lambda c: 'basketball' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            if(callback_query.data[0] == '1'):
                idxx = await sql.request_db(f'SELECT balance FROM users WHERE user_id = {str(callback_query.from_user.id)};')
                idxx = idxx[0]
                req = await sql.request_db(f'SELECT * FROM games WHERE user_id = {callback_query.from_user.id} ORDER BY id DESC LIMIT 1;')
                req = req[0]
                if(idxx[0]>=req[4]):
                    await send_message(callback_query.from_user.id, key_board.game_message_id[17].format(escape(req[4])),key_board.minigame_kb_inline, 'MarkdownV2')
                    reqq = await sql.request_db("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = 'games';")
                    reqq = reqq[0][0]
                    await sql.request_db(f"INSERT INTO games(user_id, type, target_number, stavka, date, status, result) VALUES ({callback_query.from_user.id},'Basketball',1,{req[4]},NOW(),0,0);")
                    await sql.request_db(f"UPDATE users SET balance = balance - {req[4]}, playing_game_id_mini = {reqq}, status = 17 WHERE user_id = {callback_query.from_user.id};")
                else:
                    await send_message(callback_query.from_user.id, key_board.error_value_stavka_message, key_board.minigame_kb_inline, 'MarkdownV2')
            else:
                await send_message(callback_query.from_user.id, key_board.game_message_id[17][:-74]+key_board.value_stavka_message,key_board.minigame_kb_inline, 'MarkdownV2')
                req = 'UPDATE users SET status = 17 WHERE user_id = '+str(callback_query.from_user.id)+';'
                await sql.request_db(req)
        except Exception as e:
            await bot.send_message(channel_of_error, '2717\n'+str(e))


@dp.callback_query_handler(lambda c: 'coming_soon' in c.data)
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            await send_message(callback_query.from_user.id, key_board.coming_soon_message)
        except Exception as e:
            await bot.send_message(channel_of_error, '2733\n'+str(e))


#Пополнение через БТС Банкир
@dp.callback_query_handler(lambda c: c.data == 'btc_bankir')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            rub = await crypto.get_curs_RUB_USD()
            kzt = await crypto.get_curs_KZT_USD()
            uah = await crypto.get_curs_UAH_USD()
            await send_message(callback_query.from_user.id, key_board.btc_bankir_message.format(escape(int(100*rub)/100),escape(int(100*uah)/100),escape(int(100*kzt)/100)), key_board.return_change_kb_inline)
            req = 'UPDATE users SET status = 9 WHERE user_id = '+str(callback_query.from_user.id)+';'
            await sql.request_db(req)
        except Exception as e:
            await bot.send_message(channel_of_error, '2733\n'+str(e))


#Пополнение через bitpapa
@dp.callback_query_handler(lambda c: c.data == 'bitpapa')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            rub = await crypto.get_curs_RUB_USD()
            kzt = await crypto.get_curs_KZT_USD()
            uah = await crypto.get_curs_UAH_USD()
            await send_message(callback_query.from_user.id, key_board.bit_papa_message.format(escape(int(100*rub)/100),escape(int(100*uah)/100),escape(int(100*kzt)/100)), key_board.return_change_kb_inline)
            req = 'UPDATE users SET status = 10 WHERE user_id = '+str(callback_query.from_user.id)+';'
            await sql.request_db(req)
        except Exception as e:
            await bot.send_message(channel_of_error, '2749\n'+str(e))


#Пополнение через cryptobot
@dp.callback_query_handler(lambda c: c.data == 'cryptobot')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            rub = await crypto.get_curs_RUB_USD()
            kzt = await crypto.get_curs_KZT_USD()
            uah = await crypto.get_curs_UAH_USD()
            await send_message(callback_query.from_user.id, key_board.crypto_bot_message.format(escape(int(100*rub)/100),escape(int(100*uah)/100),escape(int(100*kzt)/100)), key_board.return_change_kb_inline)
            req = 'UPDATE users SET status = 11 WHERE user_id = '+str(callback_query.from_user.id)+';'
            await sql.request_db(req)
        except Exception as e:
            await bot.send_message(channel_of_error, '2765\n'+str(e))


#Назад к способам пополнения
@dp.callback_query_handler(lambda c: c.data == 'return_change_add')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            sq = await sql.request_db(f"SELECT address FROM users WHERE user_id = {callback_query.from_user.id};")
            req = "UPDATE addresses SET status = 0 WHERE status = 1 AND address = '"+sq[0][0]+"';"
            await sql.request_db(req)
            await send_message(callback_query.from_user.id, key_board.addmoney_message, key_board.addmoney_client_kb_inline, 'MarkdownV2')
            req = 'UPDATE users SET status = 5 WHERE user_id = '+str(callback_query.from_user.id)+';'
            await sql.request_db(req)
        except Exception as e:
            await bot.send_message(channel_of_error, '2781\n'+str(e))


#Способы прямого пополнения
@dp.callback_query_handler(lambda c: c.data == 'to_crypto')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            await send_message(callback_query.from_user.id, key_board.list_crypto_message , key_board.list_crypto_kb_inline, 'MarkdownV2')
            req = 'UPDATE users SET status = 22 WHERE user_id = '+str(callback_query.from_user.id)+';'
            await sql.request_db(req)
        except Exception as e:
            await bot.send_message(channel_of_error, '2794\n'+str(e))


#Qiwi пополнение
@dp.callback_query_handler(lambda c: c.data == 'to_qiwi')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            randomcomment = ''
            while True:
                randomcomment = await generate_promo(40)
                req = "SELECT * FROM request_qiwi WHERE comment = '"+str(randomcomment)+"';"
                idx = await sql.request_db(req)
                if(len(idx) == 0):
                    break
            number = await sql.request_db(f"SELECT number FROM qiwi;")
            number = number[0][0]
            sendRequests = f"https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={number}&amountFraction=0&extra%5B%27comment%27%5D={randomcomment}&currency=643&blocked%5B0%5D=sum&blocked%5B1%5D=comment&blocked%5B2%5D=account"
            stri = f"INSERT INTO request_qiwi(user_id, comment, amount, amount_dollar, data) VALUES ({callback_query.from_user.id}, '{randomcomment}', 0, 0, NOW());"
            await sql.request_db(stri)
            msg_text = f'QIWI\nID: `{callback_query.from_user.id}`\nComment: {randomcomment}'
            await bot.send_message(channel_of_deposit, msg_text, parse_mode = 'MarkdownV2')
            check_keyboard = types.InlineKeyboardMarkup()
            check_keyboard.add(types.InlineKeyboardButton(text = "💲Перейти к оплате", url = sendRequests))
            check_keyboard.row(types.InlineKeyboardButton(text = "✖️Вернуться", callback_data='return_wallet'))
            usd_rub = await crypto.get_curs_RUB_USD()
            await send_message(callback_query.from_user.id, key_board.qiwi_message.format(escape(usd_rub)), check_keyboard)
            await sql.request_db(f'UPDATE users SET status = 28 WHERE user_id = {callback_query.from_user.id};')
        except Exception as e:
            await bot.send_message(channel_of_error, '2824\n'+str(e))


@dp.callback_query_handler(lambda c: c.data == 'set_2_address')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            req = 'SELECT address FROM users WHERE user_id = '+str(callback_query.from_user.id)+';'
            idx = await sql.request_db(req)
            idx = idx[0][0]
            req = "SELECT type, status FROM addresses WHERE address = '" + idx + "';"
            qq = await sql.request_db(req)
            if(qq[0][1]==1):
                req = "UPDATE addresses SET status = 2 WHERE address = '" + idx + "';"
                await sql.request_db(req)
                req = "INSERT INTO active_deposits_bots VALUES ('"+idx+"','pryamoi',"+str(callback_query.from_user.id)+",'"+qq[0][0].upper()+"',0,0,NOW(),11);"
                await sql.request_db(req)
                msg_text = f'ПРЯМОЙ\nID: {callback_query.from_user.id}\nType: {qq[0][0].upper()}\nAddress: `{idx}`'
                await bot.send_message(channel_of_deposit, msg_text, parse_mode='MarkdownV2')
        except Exception as e:
            await bot.send_message(channel_of_error, '2845\n'+str(e))

#Прямое пополнение
@dp.callback_query_handler(lambda c: c.data[-3:] == '_to')
async def process_callback_subscribe(callback_query: types.CallbackQuery):
    is_par = await sql.request_db(f"SELECT user_id FROM blacklist WHERE user_id = {callback_query.from_user.id};")
    if(len(is_par)==0):
        try:
            type_moneta = callback_query.data[:-3]
            req = 'SELECT last_message_bot, address FROM users WHERE user_id = '+str(callback_query.from_user.id)+';'
            idx = await sql.request_db(req)
            idx = idx[0]
            await sql.request_db(f"UPDATE addresses SET status = 0 WHERE status = 1 AND address = '{idx[1]}';")
            try:
                await bot.delete_message(callback_query.from_user.id, idx[0])
            except:
                pass
            req = "SELECT * FROM addresses WHERE address = '"+idx[1]+"' AND status = 2 AND type = '"+type_moneta.upper()+"';"
            idxx = await sql.request_db(req)
            kursi = {
                    'BTC': crypto.get_curs_BTC_USD(),
                    'ETH': crypto.get_curs_ETH_USD(),
                    'USDT': 1,
                    'TRX': crypto.get_curs_TRX_USD(),
                }
            if(len(idxx) > 0):
                msg = await bot.send_message(callback_query.from_user.id, key_board.keep_address_message.format(idx[1], time_moneta_id[type_moneta.lower()], type_moneta.upper(), escape(kursi[type_moneta.upper()]), type_moneta.lower(), type_moneta.lower()), reply_markup=key_board.keep_address_kb_inline, parse_mode='MarkdownV2')
                req = 'UPDATE users SET last_message_bot = '+str(msg.message_id)+' WHERE user_id = '+str(callback_query.from_user.id)+';'
                await sql.request_db(req)
            else:
                req = "SELECT * FROM addresses WHERE status = 0 AND type = '"+type_moneta.upper()+"';"
                req = await sql.request_db(req)
                if(len(req)==0):
                    msg = await bot.send_message(callback_query.from_user.id, key_board.not_free_address_message, reply_markup=key_board.not_free_address_kb_inline, parse_mode='MarkdownV2')
                    req = 'UPDATE users SET last_message_bot = '+str(msg.message_id)+' WHERE user_id = '+str(callback_query.from_user.id)+';'
                    await sql.request_db(req)
                else:
                    address = req[0]
                    req = "UPDATE addresses SET status = 1, date = NOW() WHERE address = '"+address[0]+"';"
                    await sql.request_db(req)
                    req = "UPDATE users SET address = '"+address[0]+"' WHERE user_id = "+str(callback_query.from_user.id)+';'
                    await sql.request_db(req)
                    msg = await bot.send_message(callback_query.from_user.id, key_board.keep_address_message.format(address[0], time_moneta_id[type_moneta.lower()], type_moneta.upper(), escape(kursi[type_moneta.upper()]), type_moneta.lower(), type_moneta.lower()), reply_markup=key_board.keep_address_kb_inline, parse_mode='MarkdownV2')
                    req = 'UPDATE users SET last_message_bot = '+str(msg.message_id)+' WHERE user_id = '+str(callback_query.from_user.id)+';'
                    await sql.request_db(req)
        except Exception as e:
            await bot.send_message(channel_of_error, '2891\n'+str(e))



async def deposit_checker():
    # Функция обновления баланса
    async def update_balance(user_id, deposit_sum):
        try:
            ref_id = await sql.request_db(f"SELECT from_ref_id FROM users WHERE user_id = {user_id};")
            if(ref_id[0][0] != 1):
                await sql.request_db(f"UPDATE users SET balance_ref = balance_ref + {koef_ref * float(deposit_sum)} WHERE user_id = {ref_id[0][0]};")
                await send_message(ref_id[0][0], key_board.dep_ref_message.format(user_id, escape(deposit_sum), escape(float(deposit_sum) * koef_ref)), key = 1)
            sqli = "UPDATE users SET balance = balance + "+str(float(deposit_sum))+", need_play_for_withdraw = need_play_for_withdraw + "+str(deposit_sum)+" WHERE user_id = "+str(user_id)+";"
            await sql.request_db(sqli)
        except Exception as e:
            await bot.send_message(channel_of_error, '2906\n'+str(e))


    while True:
        # QIWI
        try:
            deposits = await sql.request_db(f"SELECT * FROM request_qiwi WHERE amount = 0 AND DATEDIFF(NOW(), data)<=1;")

            if(len(deposits)>0):
                dt = await sql.request_db(f"SELECT * FROM qiwi;")
                if(len(dt)>0):
                    s = requests.Session()
                    s.headers['authorization'] = 'Bearer ' + dt[0][1]
                    parameters = {'rows': '50','operation':'IN'}
                    h = s.get(f'https://edge.qiwi.com/payment-history/v2/persons/{dt[0][0]}/payments', params = parameters)
                    if(h.status_code != 200):
                        await bot.send_message(channel_of_requests_withdraw, key_board.qiwi_notwork_message, parse_mode='MarkdownV2')
                    h = h.json()
                    for i in h['data']:
                        if(i['comment'] == None or i['status'] != 'SUCCESS'):
                            continue
                        req = await sql.request_db(f"SELECT * FROM request_qiwi WHERE comment = '{i['comment']}' AND amount > 0;")
                        if(len(req)>0):
                            break
                        else:
                            req = await sql.request_db(f"SELECT * FROM request_qiwi WHERE comment = '{i['comment']}';")
                            if(len(req)>0):
                                if(i['total']['currency'] == 840):
                                    await sql.request_db(f"UPDATE request_qiwi SET amount = {i['total']['amount']}, amount_dollar = {i['total']['amount']} WHERE comment = '{i['comment']}';")
                                    await update_balance(req[0][0], i['total']['amount'])
                                    idm = await sql.request_db(f"SELECT last_message_bot FROM users WHERE user_id = {req[0][0]};")
                                    await bot.delete_message(req[0][0], idm[0][0])
                                    await bot.send_message(req[0][0], key_board.adding_message.format(escape(i['total']['amount'])), parse_mode='MarkdownV2', reply_markup=key_board.adding_inline)
                                elif(i['total']['currency'] == 643):
                                    curs = await crypto.get_curs_RUB_USD()
                                    await sql.request_db(f"UPDATE request_qiwi SET valuta = 'RUB', amount = {i['total']['amount']}, amount_dollar = {i['total']['amount'] / curs} WHERE comment = '{i['comment']}';")
                                    await update_balance(req[0][0], i['total']['amount'] / curs)
                                    idm = await sql.request_db(f"SELECT last_message_bot FROM users WHERE user_id = {req[0][0]};")
                                    await bot.delete_message(req[0][0], idm[0][0])
                                    await bot.send_message(req[0][0], key_board.adding_message.format(escape(i['total']['amount'] / curs)), parse_mode='MarkdownV2', reply_markup=key_board.adding_inline)
                                elif(i['total']['currency'] == 978):
                                    curs = await crypto.get_curs_EUR_USD()
                                    await sql.request_db(f"UPDATE request_qiwi SET valuta = 'EUR', amount = {i['total']['amount']}, amount_dollar = {i['total']['amount'] / curs} WHERE comment = '{i['comment']}';")
                                    await update_balance(req[0][0], i['total']['amount'] / curs)
                                    idm = await sql.request_db(f"SELECT last_message_bot FROM users WHERE user_id = {req[0][0]};")
                                    await bot.delete_message(req[0][0], idm[0][0])
                                    await bot.send_message(req[0][0], key_board.adding_message.format(escape(i['total']['amount'] / curs)), parse_mode='MarkdownV2', reply_markup=key_board.adding_inline)
                                elif(i['total']['currency'] == 398):
                                    curs = await crypto.get_curs_KZT_USD()
                                    await sql.request_db(f"UPDATE request_qiwi SET valuta = 'KZT', amount = {i['total']['amount']}, amount_dollar = {i['total']['amount'] / curs} WHERE comment = '{i['comment']}';")
                                    await update_balance(req[0][0], i['total']['amount'] / curs)
                                    idm = await sql.request_db(f"SELECT last_message_bot FROM users WHERE user_id = {req[0][0]};")
                                    await bot.delete_message(req[0][0], idm[0][0])
                                    await bot.send_message(req[0][0], key_board.adding_message.format(escape(i['total']['amount'] / curs)), parse_mode='MarkdownV2', reply_markup=key_board.adding_inline)
                                elif(i['total']['currency'] == 980):
                                    curs = await crypto.get_curs_UAH_USD()
                                    await sql.request_db(f"UPDATE request_qiwi SET valuta = 'UAH', amount = {i['total']['amount']}, amount_dollar = {i['total']['amount'] / curs} WHERE comment = '{i['comment']}';")
                                    await update_balance(req[0][0], i['total']['amount'] / curs)
                                    idm = await sql.request_db(f"SELECT last_message_bot FROM users WHERE user_id = {req[0][0]};")
                                    await bot.delete_message(req[0][0], idm[0][0])
                                    await bot.send_message(req[0][0], key_board.adding_message.format(escape(i['total']['amount'] / curs)), parse_mode='MarkdownV2', reply_markup=key_board.adding_inline)
                                else:
                                    continue
                            else:
                                continue


            deposits = await sql.request_db("SELECT * FROM active_deposits_bots WHERE status = 11")

            for deposit in deposits:
                try:
                    blc = await sql.request_db("SELECT value FROM addresses WHERE address = '" + str(deposit[0])+"';")
                    blc = float(blc[0][0])
                    new_blc = blc
                    value_usd = 0
                    url = scans_id[deposit[3].lower()] + deposit[0]
                    htmlContent = requests.get(url)#, headers)
                    if(deposit[3] in ['TRX']):
                        js_data = htmlContent.json()['balance']
                        new_blc = float(js_data)/1000000
                        value_usd = float(int(100 * ((new_blc-blc) * crypto.get_curs_TRX_USD())) / 100)
                    elif(deposit[3] in ['USDT']):
                        js_data = htmlContent.json()['trc20token_balances']
                        for rw in js_data:
                            if(rw['tokenAbbr']=='USDT'):
                                new_blc = float(rw['balance'])/10000
                                new_blc = float(int(new_blc)/100)
                                break
                        value_usd = (new_blc-blc)
                    elif(deposit[3] in ['BTC', 'ETH']):
                        '''print(htmlContent.text)
                        soup = BeautifulSoup(htmlContent.text, "html.parser")
                        alltrans = soup.findAll('span', class_='sc-fb66ec17-2 gITEex')
                        if(deposit[3] == 'BTC'):
                            print(alltrans)
                            new_blc = float(alltrans[4].text[:-4])
                            value_usd = float(int(100 * ((new_blc-blc) * crypto.get_curs_BTC_USD())) / 100)
                        else:
                            new_blc = float(alltrans[6].text[:-4])
                            value_usd = float(int(100 * ((new_blc-blc) * crypto.get_curs_ETH_USD())) / 100)
                            '''
                    if(new_blc>blc):
                        sqli = "UPDATE addresses SET value = "+str(new_blc)+", status = 0 WHERE address = '"+str(deposit[0])+"';"
                        await sql.request_db(sqli)
                        await update_balance(deposit[2], value_usd)
                        idm = await sql.request_db(f"SELECT last_message_bot FROM users WHERE user_id = {deposit[2]};")
                        try:
                            await bot.delete_message(deposit[2], idm[0][0])
                        except:
                            pass
                        await bot.send_message(deposit[2], key_board.adding_message.format(escape(str(value_usd))), parse_mode='MarkdownV2', reply_markup=key_board.adding_inline)
                        req = "UPDATE active_deposits_bots SET status = 1, value = "+str(new_blc-blc)+", usd = "+str(value_usd)+" WHERE bot = '"+str(deposit[0])+"' AND status = 11;"
                        await sql.request_db(req)
                    
                except:
                    pass
                delta = datetime.timedelta(days=0, seconds=0,microseconds=0,milliseconds=0,minutes=time_moneta_id[deposit[3].lower()],hours=0,weeks=0)
                if((datetime.datetime.now() - deposit[-2])>delta):
                    req = "UPDATE active_deposits_bots SET status = -3 WHERE bot = '"+str(deposit[0])+"' AND status = 11;"
                    await sql.request_db(req)
                    sqli = "UPDATE addresses SET status = 0 WHERE address = '"+str(deposit[0])+"';"
                    await sql.request_db(sqli)
                    await send_message(deposit[2], key_board.error_timeout_message, key_board.addmoney_client_kb_inline)


            deposits = await sql.request_db("SELECT * FROM active_deposits_bots WHERE status = 13")

            for deposit in deposits:
                try:
                    if((datetime.datetime.now() - deposit[6]).total_seconds()>60):
                        await send_message(deposit[2], key_board.error_deposit, key_board.addmoney_client_kb_inline)
                        sqli = "UPDATE active_deposits_bots SET status = -3 WHERE gift = '"+str(deposit[1])+"';"
                        await sql.request_db(sqli)
                except:
                    pass
                

            deposits = await sql.request_db("SELECT * FROM active_deposits_bots WHERE status = 0")

            for deposit in deposits:
                await update_balance(deposit[2], deposit[4])
                try:
                    idm = await sql.request_db(f"SELECT last_message_bot FROM users WHERE user_id = {deposit[2]};")
                    await bot.delete_message(deposit[2], idm[0][0])
                    await bot.send_message(deposit[2], key_board.adding_message.format(escape(deposit[5])), parse_mode='MarkdownV2', reply_markup=key_board.adding_inline)
                except:
                    pass
                sqli = "UPDATE active_deposits_bots SET status = 1 WHERE gift = '"+str(deposit[1])+"';"
                await sql.request_db(sqli)
            

            deposits = await sql.request_db("SELECT * FROM active_deposits_bots WHERE status = -1")

            for deposit in deposits:
                try:
                    send_message(deposit[2], text=" Ваш чек просрочен")
                except:
                    pass
                sqli = "UPDATE active_deposits_bots SET status = 2 WHERE gift = '"+str(deposit[1])+"';"
                await sql.request_db(sqli)


            deposits = await sql.request_db("SELECT * FROM active_deposits_bots WHERE status = -2")

            for deposit in deposits:
                try:
                    send_message(deposit[2], text=" Проверьте ваш чек")
                except:
                    pass
                sqli = "UPDATE active_deposits_bots SET status = 2 WHERE gift = '"+str(deposit[1])+"';"
                await sql.request_db(sqli)

            games_21 = await sql.request_db("SELECT * FROM game_21 WHERE is_closed = 2;")
            for game_ in games_21:
                delta = datetime.timedelta(days=0, seconds=0,microseconds=0,milliseconds=0,minutes=10,hours=0,weeks=0)
                if((datetime.datetime.now() - game_[-1])>delta):
                    rq = await sql.request_db(f"SELECT * FROM mess_21_list WHERE id_game = {game_[0]} AND message = '⏳ВРЕМЯ ВЫШЛО⏳';")
                    if(len(rq)==0):
                        for i in range(game_[1]):
                            await sql.request_db(f"UPDATE game_21 SET cards_{i+1} = CONCAT(cards_{i+1}, ';') WHERE id = {game_[0]};")
                        await sql.request_db(f"INSERT INTO mess_21_list VALUES({game_[0]}, 'КРУПЬЕ', '⏳ВРЕМЯ ВЫШЛО⏳');")
                        await sql.request_db(f"INSERT INTO mess_21_list VALUES({game_[0]}, '', '➖➖ИГРА ОКОНЧЕНА➖➖');")
                        for i in game_[11:11+game_[1]]:
                            if(int(i)!=0):
                                msg, keyb = await game.message_room_21(i, game_[0])
                                await send_message(i, msg, keyb)
                else:
                    delta = datetime.timedelta(days=0, seconds=0,microseconds=0,milliseconds=0,minutes=9,hours=0,weeks=0)
                    if((datetime.datetime.now() - game_[-1])>delta):
                        rq = await sql.request_db(f"SELECT * FROM mess_21_list WHERE id_game = {game_[0]} AND message = '⏳ОСТАЛОСЬ МЕНЕЕ 1 МИНУТЫ⏳';")
                        if(len(rq)==0):
                            await sql.request_db(f"INSERT INTO mess_21_list VALUES({game_[0]}, 'КРУПЬЕ', '⏳ОСТАЛОСЬ МЕНЕЕ 1 МИНУТЫ⏳');")
                            for i in game_[11:11+game_[1]]:
                                if(int(i)!=0):
                                    msg, keyb = await game.message_room_21(i, game_[0])
                                    await send_message(i, msg, keyb)

            
            multigames = await sql.request_db("SELECT id, date, players, message_id, chat_id FROM multigames WHERE status = 2;")
            for game_ in multigames:
                delta = datetime.timedelta(days=0, seconds=0,microseconds=0,milliseconds=0,minutes=10,hours=0,weeks=0)
                if((datetime.datetime.now() - game_[-4])>delta):
                    rows = await sql.request_db(f"SELECT games.id,games.user_id, type, stavka, status, result_point, playing_multigame_id, playing_game_id_mini FROM games INNER JOIN (SELECT user_id, playing_multigame_id, playing_game_id_mini FROM users WHERE playing_multigame_id = {game_[0]}) AS T ON T.playing_game_id_mini = games.id HAVING status<>0;")
                    rows_ = await sql.request_db(f"SELECT games.id,games.user_id, type, stavka, status, result_point, playing_multigame_id, playing_game_id_mini FROM games INNER JOIN (SELECT user_id, playing_multigame_id, playing_game_id_mini FROM users WHERE playing_multigame_id = {game_[0]}) AS T ON T.playing_game_id_mini = games.id HAVING status=0;")    
                    for i in rows_:
                        if(i[4]==0):
                            await sql.request_db(f"UPDATE users SET status = 12 WHERE user_id = {i[1]};")
                            await sql.request_db(f"UPDATE games SET status = -1 WHERE id = {i[0]};")
                    k_live = len(rows)
                    if(k_live==0):
                        await sql.request_db(f"UPDATE multigames SET status = 5 WHERE id = {game_[0]};")
                        ids = await sql.request_db(f"SELECT user_id FROM users WHERE playing_multigame_id = {game_[0]};")
                        for i in ids:
                            await sql.request_db(f"UPDATE games SET status = -1 WHERE status = 0 AND user_id = {i[0]};")
                        await sql.request_db(f"UPDATE users SET playing_game_id_mini = 0, playing_multigame_id = 0 WHERE playing_multigame_id = {game_[0]};")
                        await bot.send_animation(game_[-1], 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.end_still_multigame, parse_mode='MarkdownV2', reply_to_message_id=game_[-2])
                    else:
                        await sql.request_db(f"UPDATE users SET playing_game_id_mini = 0, playing_multigame_id = 0 WHERE playing_multigame_id = {game_[0]};")
                        full_players = game_[2].replace("/",'') 
                        full_players = full_players.replace("*",'')              
                        full_players = full_players.replace("+",'')
                        full_players = [int(n) for n in full_players.split(',')]
                        leave_players = full_players
                        players = []
                        lose_players = []
                        st = ''
                        k = 0
                        maxk = 0
                        for i in rows:
                            players.append(i[1])
                            try:
                                leave_players.remove(i[1])
                            except:
                                pass
                        basket, foot, point_games = ['Basketball'], ['Penalty'], ['Dice', 'Darts', 'Bowling']
                        if(rows[0][2] in point_games):
                            for i in rows:
                                if(i[1] not in leave_players):
                                    if(i[5] > maxk):
                                        maxk = i[5]
                                else:
                                    await sql.request_db(f"UPDATE games SET status = -1 WHERE user_id = {i[1]} AND status = 0;")
                            for idx, i in enumerate(rows, start = 1):
                                usern = await sql.request_db(f"Select username, firstname FROM users WHERE user_id = {i[1]};")
                                usernm = f'@{usern[0][0]}' if usern[0][0] != 'None' else usern[0][1]
                                if(i[1] in leave_players):
                                    st += f"💀{escape(usernm)} \| *AFK*\n"
                                elif(i[5] == maxk):
                                    k+=1
                                    st += f"👑{escape(usernm)} \| " + "{stavka}\n"
                                else:
                                    st += f"{logo_multi[idx]}{escape(usernm)} \|\n"
                                    lose_players.append(i[1])
                        elif(rows[0][2] in basket):
                            for idx, i in enumerate(rows, start = 1):
                                usern = await sql.request_db(f"Select username, firstname FROM users WHERE user_id = {i[1]};")
                                usernm = f'@{usern[0][0]}' if usern[0][0] != 'None' else usern[0][1]
                                if(i[1] in leave_players):
                                    await sql.request_db(f"UPDATE games SET status = -1 WHERE user_id = {i[1]} AND status = 0;")
                                    st += f"💀{escape(usernm)} \| *AFK*\n"
                                elif(i[5] in [4,5]):
                                    k+=1
                                    st += f"👑{escape(usernm)} \| " + "{stavka}\n"
                                else:
                                    st += f"{logo_multi[idx]}{escape(usernm)} \|\n"
                                    lose_players.append(i[1])
                        elif(rows[0][2] in foot):
                            for idx, i in enumerate(rows, start = 1):
                                usern = await sql.request_db(f"Select username, firstname FROM users WHERE user_id = {i[1]};")
                                usernm = f'@{usern[0][0]}' if usern[0][0] != 'None' else usern[0][1]
                                if(i[1] in leave_players):
                                    await sql.request_db(f"UPDATE games SET status = -1 WHERE user_id = {i[1]} AND status = 0;")
                                    st += f"💀{escape(usernm)} \| *AFK*\n"
                                elif(i[5] in [3,4,5]):
                                    k+=1
                                    st += f"👑{escape(usernm)} \| " + "{stavka}\n"
                                else:
                                    st += f"{logo_multi[idx]}{escape(usernm)} \|\n"
                                    lose_players.append(i[1])
                        if((k>0) and (k!=k_live) or (k==1) and (k_live==1)):#есть победители
                            if(rows[0][2] in point_games):
                                for i in rows:
                                    if((i[5] == maxk) and (i[1] not in leave_players)):
                                        await sql.request_db(f"UPDATE users SET count_games = count_games + 1, count_prizes = count_prizes + {komission_casino * k_live * rows[0][3] / k}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {rows[0][3]} THEN (need_play_for_withdraw - {rows[0][3]}) ELSE (0)end), balance = balance + {komission_casino * k_live * rows[0][3] / k}, playing_game_id_mini = 0, playing_multigame_id = 0 WHERE user_id = {i[1]};")
                                    else:
                                        await sql.request_db(f"UPDATE users SET count_games = count_games + 1, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {rows[0][3]} THEN (need_play_for_withdraw - {rows[0][3]}) ELSE (0)end), playing_game_id_mini = 0, playing_multigame_id = 0 WHERE user_id = {i[1]};")
                            elif(rows[0][2] in basket):
                                for i in rows:
                                    if((i[5] in [4,5]) and (i[1] not in leave_players)):
                                        await sql.request_db(f"UPDATE users SET count_games = count_games + 1, count_prizes = count_prizes + {komission_casino * k_live * rows[0][3] / k}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {rows[0][3]} THEN (need_play_for_withdraw - {rows[0][3]}) ELSE (0)end), balance = balance + {komission_casino * k_live * rows[0][3] / k}, playing_game_id_mini = 0, playing_multigame_id = 0 WHERE user_id = {i[1]};")
                                    else:
                                        await sql.request_db(f"UPDATE users SET count_games = count_games + 1, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {rows[0][3]} THEN (need_play_for_withdraw - {rows[0][3]}) ELSE (0)end), playing_game_id_mini = 0, playing_multigame_id = 0 WHERE user_id = {i[1]};")
                            elif(rows[0][2] in foot):
                                for i in rows:
                                    if((i[5] in [3,4,5]) and (i[1] not in leave_players)):
                                        await sql.request_db(f"UPDATE users SET count_games = count_games + 1, count_prizes = count_prizes + {komission_casino * k_live * rows[0][3] / k}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {rows[0][3]} THEN (need_play_for_withdraw - {rows[0][3]}) ELSE (0)end), balance = balance + {komission_casino * k_live * rows[0][3] / k}, playing_game_id_mini = 0, playing_multigame_id = 0 WHERE user_id = {i[1]};")
                                    else:
                                        await sql.request_db(f"UPDATE users SET count_games = count_games + 1, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {rows[0][3]} THEN (need_play_for_withdraw - {rows[0][3]}) ELSE (0)end), playing_game_id_mini = 0, playing_multigame_id = 0 WHERE user_id = {i[1]};")
                            st = st.format(stavka=escape(str(k_live * rows[0][3] / k)))
                            await bot.send_animation(game_[-1], 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.victory_multi_message.format(game_[0], smile_of_game[rows[0][2]],escape(rows[0][3]),st), parse_mode='MarkdownV2', reply_to_message_id=game_[-2])
                            await sql.request_db(f"UPDATE multigames SET status = 1 WHERE id = {game_[0]};")
                            try:
                                await bot.delete_message(game_[-1], message_id=game_[-2])
                            except:
                                pass
                        elif((k==0) and (k!=k_live)):#нет победителей(возврат ставки)
                            st = ''
                            for i in lose_players:
                                usern = await sql.request_db(f"Select username, firstname FROM users WHERE user_id = {i};")
                                usernm = f'@{usern[0][0]}' if usern[0][0] != 'None' else usern[0][1]
                                st += f"👑{escape(usernm)} \| {rows[0][3]}\n"
                                await sql.request_db(f"UPDATE users SET count_games = count_games + 1, count_prizes = count_prizes + {rows[0][3]}, balance = balance + {rows[0][3]}, playing_game_id_mini = 0, playing_multigame_id = 0 WHERE user_id = {i};")
                            await bot.send_animation(game_[-1], 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.victory_multi_message.format(game_[0], smile_of_game[rows[0][2]],escape(rows[0][3]),st), parse_mode='MarkdownV2', reply_to_message_id=game_[-2])
                            await sql.request_db(f"UPDATE multigames SET status = 4 WHERE id = {game_[0]};")
                            try:
                                await bot.delete_message(game_[-1], message_id=game_[-2])
                            except:
                                pass
                        elif((k>0) and (k==k_live)):#ничья
                            reqq = await sql.request_db("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = 'multigames';")
                            await sql.request_db(f"UPDATE multigames SET status = 3 WHERE id = {game_[0]};")
                            msge = ''
                            for idx, i in enumerate(players, start = 1):
                                usern = await sql.request_db(f"Select username, firstname FROM users WHERE user_id = {i};")
                                usernm = f'@{usern[0][0]}' if usern[0][0] != 'None' else usern[0][1]
                                stat = '☑️ГОТОВ'
                                msge += escape(f"{logo_multi[idx]}{usernm} | {stat}\n")
                                reqq1 = await sql.request_db("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = 'games';")
                                reqq1 = reqq1[0][0]
                                await sql.request_db(f"INSERT INTO games(user_id, type, target_number, stavka, date, status, result) VALUES ({i},'{rows[0][2]}',1,{rows[0][3]},NOW(),0,0);")
                                await sql.request_db(f"UPDATE users SET playing_game_id_mini = {reqq1}, playing_multigame_id = {reqq[0][0]} WHERE user_id = {i};")
                            multiopen_game_inline = types.InlineKeyboardMarkup().row(types.InlineKeyboardButton('▪️Выйти▪️', callback_data=f'{reqq[0][0]}_exit_multigame'))
                            msg = await bot.send_animation(game_[-1], 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.draw_multi_message+key_board.multigame_shapka_message.format(reqq[0][0], smile_of_game[rows[0][2]], escape(rows[0][3]), msge)+key_board.multigame_message_name[rows[0][2]], reply_markup=multiopen_game_inline, parse_mode='MarkdownV2')
                            plays = ''
                            for i in players:
                                plays += f'{i}+,'
                            plays = plays[:-1]
                            await sql.request_db(f"INSERT INTO multigames(type, stavka, players, status, date, message_id, chat_id) VALUES ('{rows[0][2]}',{rows[0][3]},'{plays}',2,NOW(),{msg.message_id},{msg.chat.id});")
            #ne zagadal
            rbgames = await sql.request_db("SELECT * FROM rb_game WHERE players NOT LIKE '%-%' AND players LIKE '%:_%' AND (players NOT LIKE '%/%' AND players NOT LIKE '%+B%' AND players NOT LIKE '%+R%') AND date <= DATE_SUB(NOW(), INTERVAL 10 MINUTE);")
            for game_ in rbgames:
                players = game_[1]
                ms_players = f""
                ms_footer = ''
                for idx, i in enumerate(game_[1].split(':'), start = 1):
                    pls = await sql.request_db(f"SELECT username, firstname FROM users WHERE user_id = {int(i[:-1])};")
                    if(idx==game_[2]):
                        players = players.replace(f'{i[:-1]}*',f'{i[:-1]}-')
                        players = players.replace(f'{i[:-1]}+',f'{i[:-1]}-')
                        ms_players += f"🥷🏻@{escape(pls[0][0])} \| загадывает цвет\n" if pls[0][0]!='None' else f"🥷🏻{escape(pls[0][1])}  \| загадывает цвет\n"
                        ms_footer += f"Время игрока @{escape(pls[0][0])} истекло\. " if pls[0][0]!='None' else f"Время игрока {escape(pls[0][1])} истекло\. "
                    else:
                        ms_players += f"👁️‍🗨️@{escape(pls[0][0])} \| отгадывает цвет\n" if pls[0][0]!='None' else f"👁️‍🗨️{escape(pls[0][1])}  \| отгадывает цвет\n"
                        ms_footer += f"@{escape(pls[0][0])} получает ставку соперника\. " if pls[0][0]!='None' else f"{escape(pls[0][1])} получает ставку соперника\. "
                        await sql.request_db(f"UPDATE users SET balance = balance + {math.floor(100*game_[3] * 2 * komission_casino)/100} WHERE user_id = {i[:-1]};")
                ms_footer = f"*{ms_footer}*\nПоздравляем победителя 🍾"
                await bot.delete_message(game_[-2], game_[-3])
                msg = await bot.send_animation(game_[-2], 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.rb_message.format(game_[0],escape(game_[3]),ms_players, ms_footer), parse_mode='MarkdownV2')
                await sql.request_db(f"UPDATE rb_game SET players = '{players}', message_id = {msg.message_id} WHERE id = {game_[0]};")
            #ne otgadal
            rbgames = await sql.request_db("SELECT * FROM rb_game WHERE players NOT LIKE '%-%' AND players LIKE '%/%' AND players NOT LIKE '%|%' AND date <= DATE_SUB(NOW(), INTERVAL 10 MINUTE);")
            for game_ in rbgames:
                players = game_[1]
                ms_players = f""
                ms_footer = ''
                for idx, i in enumerate(game_[1].split(':'), start = 1):
                    if(idx==game_[2]):
                        pls = await sql.request_db(f"SELECT username, firstname FROM users WHERE user_id = {int(i[:-2])};")
                        ms_players += f"🥷🏻@{escape(pls[0][0])} \| загадывает цвет☑️\n" if pls[0][0]!='None' else f"🥷🏻{escape(pls[0][1])}  \| загадывает цвет☑️\n"
                        ms_footer += f"@{escape(pls[0][0])} получает ставку соперника\. " if pls[0][0]!='None' else f"{escape(pls[0][1])} получает ставку соперника\. "
                        await sql.request_db(f"UPDATE users SET balance = balance + {math.floor(100*game_[3] * 2 * komission_casino)/100} WHERE user_id = {i[:-1]};")
                    else:
                        players = players.replace(f'{i[:-1]}*',f'{i[:-1]}-')
                        players = players.replace(f'{i[:-1]}+',f'{i[:-1]}-')
                        pls = await sql.request_db(f"SELECT username, firstname FROM users WHERE user_id = {int(i[:-1])};")
                        ms_players += f"👁️‍🗨️@{escape(pls[0][0])} \| отгадывает цвет\n" if pls[0][0]!='None' else f"👁️‍🗨️{escape(pls[0][1])}  \| отгадывает цвет\n"
                        ms_footer += f"Время игрока @{escape(pls[0][0])} истекло\. " if pls[0][0]!='None' else f"Время игрока {escape(pls[0][1])} истекло\. "
                ms_footer = f"*{ms_footer}*\nПоздравляем победителя 🍾"
                await bot.delete_message(game_[-2], game_[-3])
                msg = await bot.send_animation(game_[-2], 'CgACAgIAAxkBAAOOY61g26FF82m27Ih5XpxK2S6Uhn0AApgkAAKxC3FJNnO1x_lK2iksBA',caption=key_board.rb_message.format(game_[0],escape(game_[3]),ms_players, ms_footer), parse_mode='MarkdownV2')
                await sql.request_db(f"UPDATE rb_game SET players = '{players}', message_id = {msg.message_id} WHERE id = {game_[0]};")
            await asyncio.sleep(50)
        except Exception as e:
            await bot.send_message(channel_of_error, '3289\n'+str(e))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(deposit_checker())
    executor.start_polling(dp)
    


