import sql, asyncio, main, key_board
from aiogram import types
from random import shuffle
from aiogram.utils.markdown import escape_md as escape




'''def parse_sr(str):
       return str[:1],str[3:str.index('/')],str[str.index('/')+1:str.index('(')], str[str.index('(')+1:str.index(')')],str[str.index(')')+1:]

def leave_player(player_id):
    players ="""1.отсутствует
2.|100/nick(0)check
3.отсутствует"""
    for idx, i in enumerate(players.split('\n'), start = 1):
        if(str(player_id) in i):
            line = parse_sr(i)
            players = players.replace(i, f'{line[0]}.отсутствует')
            return players'''

smile_status = {'check':'☑',
'raise':'📈',
'fold':'✖',
'call':'☑',
'visiter': '👁️‍🗨️'}


class Board(object):
    """docstring"""
 
    def __init__(self, id):
        """Constructor"""
        qq = sql.request_db_without_async(f"SELECT * FROM boards_poker_draw where id = {id};")
        self.id = qq[0][0]
        self.name = qq[0][1]
        self.players = qq[0][2]
        self.ante = qq[0][3]
        self.small_blind = qq[0][4]
        self.date = qq[0][5]
        self.status = qq[0][6]#0 - нет игры, 1-начальные торги, 2 - спрашивают игроков перед началом игры, 3 - конец первых торгов(начало смены карт), 4 - конечные торги
        self.st_pl = qq[0][7]
        self.position = qq[0][8]
        self.last_message = qq[0][9]
        self.cards = qq[0][10]
        self.koloda = qq[0][11]
        
    

    async def parse_sr(self, str):
       return str[:1],str[3:str.index('/')],str[str.index('/')+1:str.index('(')], str[str.index('(')+1:str.index(')')],str[str.index(')')+1:]


    async def add_stavka(self, id_player, add_sum):
        for idx, i in enumerate(self.players.split('\n'), start = 1):
            if(str(id_player) in i):
                line = await self.parse_sr(i)
                self.players = self.players.replace(i,f'{line[0]}.|{line[1]}/{line[2]}({float(line[3])+add_sum})raise')
                await sql.request_db(f"UPDATE boards_poker_draw SET players = '{self.players}' WHERE id = {self.id};")
                break


    async def count_players(self):
        return 9 - self.players.count('отсутствует')


    async def new_player(self, player_id):
        usernm = await sql.request_db(f"SELECT username, firstname from users WHERE user_id = {player_id};")
        usernm = usernm[0][0] if usernm[0][0] != 'None' else usernm[0][1]
        for idx, i in enumerate(self.players.split('\n'), start = 1):
            if('отсутствует' in i):
                self.players = self.players.replace(f'{i}', f'{idx}.|{player_id}/{usernm}(0)visiter')
                await sql.request_db(f"UPDATE boards_poker_draw SET players = '{self.players}' WHERE id = {self.id};")
                break
    

    async def check_player(self, player_id):
        for idx, i in enumerate(self.players.split('\n'), start = 1):
            if(str(player_id) in i):
                line = await self.parse_sr(i)
                self.players = self.players.replace(i, f'{line[0]}.|{line[1]}/{line[2]}({line[3]})check')
                await sql.request_db(f"UPDATE boards_poker_draw SET players = '{self.players}' WHERE id = {self.id};")
                await self.next_position()
                break    
    

    async def call_player(self, player_id):
        maxs = await self.get_max_stavka()
        bal = await sql.request_db(f"SELECT balance FROM users WHERE user_id = {player_id};")
        for idx, i in enumerate(self.players.split('\n'), start = 1):
            if(str(player_id) in i):
                line = await self.parse_sr(i)
                if(bal[0][0]<(maxs-float(line[3]))):
                    await sql.request_db(f"UPDATE users SET balance = balance - {bal[0][0]} WHERE user_id = {player_id};")
                    self.players = self.players.replace(i, f'{line[0]}.|{line[1]}/{line[2]}({float(line[3])+float(bal[0][0])})call')
                else:
                    await sql.request_db(f"UPDATE users SET balance = balance - {maxs - float(line[3])} WHERE user_id = {player_id};")
                    self.players = self.players.replace(i, f'{line[0]}.|{line[1]}/{line[2]}({maxs})call')
                await sql.request_db(f"UPDATE boards_poker_draw SET players = '{self.players}' WHERE id = {self.id};")
                await self.next_position()
                break    
    

    async def fold_player(self, player_id):
        for idx, i in enumerate(self.players.split('\n'), start = 1):
            if(str(player_id) in i):
                line = await self.parse_sr(i)
                self.players = self.players.replace(i, f'{line[0]}.|{line[1]}/{line[2]}({line[3]})fold')
                await sql.request_db(f"UPDATE boards_poker_draw SET players = '{self.players}' WHERE id = {self.id};")
                await self.next_position()
                break    


    async def raise_player(self, player_id):
        await sql.request_db(f"UPDATE users SET status = 36 WHERE user_id = {player_id};")
        msg_text = await self.gen_message_room(f'Нажми размер поднятия')
        kb_ = types.InlineKeyboardMarkup()
        kk = 0
        for idx, i in enumerate(self.players.split('\n'), start = 1):
            if(str(player_id) in i):
                kk = idx
        kb_cards = self.cards.split('\n')[kk-1][2:].split(',')
        kb_.row(types.InlineKeyboardButton(kb_cards[0], callback_data='none'), 
                types.InlineKeyboardButton(kb_cards[1], callback_data='none'), 
                types.InlineKeyboardButton(kb_cards[2], callback_data='none'), 
                types.InlineKeyboardButton(kb_cards[3], callback_data='none'), 
                types.InlineKeyboardButton(kb_cards[4], callback_data='none'))
        kb_.row(types.InlineKeyboardButton(f'+{(2 * self.small_blind) * 0.1}$', callback_data=f'{self.id}_0.1_poker'),
                types.InlineKeyboardButton(f'+{(2 * self.small_blind) * 0.2}$', callback_data=f'{self.id}_0.2_poker'),
                types.InlineKeyboardButton(f'+{(2 * self.small_blind) * 0.3}$', callback_data=f'{self.id}_0.3_poker'),
                types.InlineKeyboardButton(f'+{(2 * self.small_blind) * 0.4}$', callback_data=f'{self.id}_0.4_poker'),
                types.InlineKeyboardButton(f'+{(2 * self.small_blind) * 0.5}$', callback_data=f'{self.id}_0.5_poker'),
                )
        kb_.row(types.InlineKeyboardButton(f'+{(2 * self.small_blind) * 0.6}$', callback_data=f'{self.id}_0.6_poker'),
                types.InlineKeyboardButton(f'+{(2 * self.small_blind) * 0.7}$', callback_data=f'{self.id}_0.7_poker'),
                types.InlineKeyboardButton(f'+{(2 * self.small_blind) * 0.8}$', callback_data=f'{self.id}_0.8_poker'),
                types.InlineKeyboardButton(f'+{(2 * self.small_blind) * 0.9}$', callback_data=f'{self.id}_0.9_poker'),
                types.InlineKeyboardButton(f'+{(2 * self.small_blind)}$', callback_data=f'{self.id}_1.0_poker'),
                )
        kb_.row(types.InlineKeyboardButton(f'Вернуться', callback_data=f'{self.id}_retraise_poker'))
        msg_id = await sql.request_db(f"SELECT last_message_bot FROM users WHERE user_id = {player_id};")
        await main.bot.edit_message_text(msg_text, player_id, msg_id[0][0], parse_mode='MarkdownV2', reply_markup=kb_)



    async def retraise_player(self, player_id):
        await sql.request_db(f"UPDATE users SET status = 35 WHERE user_id = {player_id};")
        msg_text = await self.gen_message_room(f'')
        kb_ = types.InlineKeyboardMarkup()
        kk = 0
        for idx, i in enumerate(self.players.split('\n'), start = 1):
            if(str(player_id) in i):
                kk = idx
        kb_cards = self.cards.split('\n')[kk-1][2:].split(',')
        kb_.row(types.InlineKeyboardButton(kb_cards[0], callback_data='none'), 
                types.InlineKeyboardButton(kb_cards[1], callback_data='none'), 
                types.InlineKeyboardButton(kb_cards[2], callback_data='none'), 
                types.InlineKeyboardButton(kb_cards[3], callback_data='none'), 
                types.InlineKeyboardButton(kb_cards[4], callback_data='none'))
        kb_.row(types.InlineKeyboardButton('CALL', callback_data=f'{self.id}_call_poker'),
                types.InlineKeyboardButton('RAISE', callback_data=f'{self.id}_raise_poker'), 
                types.InlineKeyboardButton('FOLD', callback_data=f'{self.id}_fold_poker'))
        msg_id = await sql.request_db(f"SELECT last_message_bot FROM users WHERE user_id = {player_id};")
        await main.bot.edit_message_text(msg_text, player_id, msg_id[0][0], parse_mode='MarkdownV2', reply_markup=kb_)
        

    async def leave_player(self, player_id):
        for idx, i in enumerate(self.players.split('\n'), start = 1):
            if(str(player_id) in i):
                line = await self.parse_sr(i)
                self.players = self.players.replace(i, f'{line[0]}.отсутствует')
                await sql.request_db(f"UPDATE boards_poker_draw SET players = '{self.players}' WHERE id = {self.id};")
                msg = await main.bot.send_animation(line[1], 'CgACAgIAAxkBAAIIxGN_3XfiqkpKD6yNYcqUDcpwE-Y1AAKhJAACshQBSEG2YpVIleo1KwQ', caption=key_board.start_menu_message, reply_markup=key_board.start_client_kb_inline, parse_mode='MarkdownV2')
                await sql.request_db(f'UPDATE users SET last_message_bot = {msg.message_id} WHERE user_id = {line[1]};')
                return
        

    async def gen_message_room(self, description = ''):
        msg = f'DRAW POKER       *ID*: {self.id}\n*Players:*\n'
        for idx, i in enumerate(self.players.split('\n'), start = 1):
            if('отсутствует' in i):
                msg += f'{idx}\. отсутствует\n'
            else:
                line = await self.parse_sr(i)
                if(line[4].lower() != 'visiter'):
                    summ = escape(line[3])
                    msg += f'{line[0]}\. {escape(line[2])} \| {line[4].upper()}{smile_status[line[4]]} {summ}💲\n'
                else:
                    msg += f'{line[0]}\. {escape(line[2])} \| visiter{smile_status["visiter"]}\n'
        msg += description
        return msg

    
    async def get_max_stavka(self):
        maxk = 0
        for idx, i in enumerate(self.players.split('\n'), start = 1):
            if(('visiter' not in i) and ('отсутствует' not in i)):
                line = await self.parse_sr(i)
                if(float(line[3])>maxk):
                    maxk = float(line[3])
        return maxk
    

    async def razd_kart(self):
        self.cards = ''
        for idx, i in enumerate(self.players.split('\n'), start = 1):
            if('отсутствует' in i):
                self.cards += f'{idx}.\n'
            else:
                self.cards += f"{idx}.{','.join(self.koloda[0:5])}\n"
                self.koloda = self.koloda[5:]                
        print(self.cards)

    
    async def next_position(self):
        for idx, i in enumerate(self.players.split('\n'), start = 1):
            if('отсутствует' not in i and 'fold' not in i and idx != self.position):
                self.position = idx
                return


    async def game_loop(self):
        while(True):
            cnt = await self.count_players()
            if(self.status == 0 and cnt>1):
                self.status = 2
                msg_text = await self.gen_message_room('Нажмите кнопку для подтверждения начала игры\. У вас есть 15 секунд\.\n*15*')
                if(self.last_message!=msg_text):
                    self.last_message = msg_text
                    await sql.request_db(f"UPDATE boards_poker_draw SET last_message = '{escape(msg_text)}' WHERE id = {self.id};")
                    for idx, i in enumerate(self.players.split('\n'), start = 1):
                        if('отсутствует' in i):
                            pass
                        else:
                            line = await self.parse_sr(i)
                            user_id = int(line[1])
                            msg = await main.bot.send_message(user_id, msg_text, 'MarkdownV2')
                            await sql.request_db(f"UPDATE users SET last_message_bot = {msg.message_id} WHERE user_id = {user_id};")
                    await sql.request_db(f"UPDATE boards_poker_draw SET date = NOW(), status = 2 WHERE id = {self.id};")
            elif(self.status == 0):
                msg_text = await self.gen_message_room('Ожидание игроков\.')
                if(self.last_message!=msg_text):
                    self.last_message = msg_text
                    await sql.request_db(f"UPDATE boards_poker_draw SET last_message = '{escape(msg_text)}' WHERE id = {self.id};")
                    for idx, i in enumerate(self.players.split('\n'), start = 1):
                        if('отсутствует' in i):
                            pass
                        else:
                            line = await self.parse_sr(i)
                            user_id = int(line[1])
                            msg_id = await sql.request_db(f"SELECT last_message_bot FROM users WHERE user_id = {user_id};")
                            try:
                                await main.bot.edit_message_text(msg_text, user_id, msg_id[0][0], parse_mode='MarkdownV2')
                            except:
                                msg = await main.bot.send_message(user_id, msg_text, 'MarkdownV2')
                                await sql.request_db(f"UPDATE users SET last_message_bot = {msg.message_id} WHERE user_id = {user_id};")
            elif(self.status == 2):
                tm = await sql.request_db(f"select timestampdiff(second, date, NOW()) from boards_poker_draw where id = {self.id};")
                if(int(tm[0][0])>=15):
                    for idx, i in enumerate(self.players.split('\n'), start = 1):
                        if('отсутствует' in i):
                            pass
                        else:
                            line = await self.parse_sr(i)
                            user_id = int(line[1])
                            if('check' not in i):
                                await self.leave_player(user_id)
                    if(self.players.count('check')>=2):
                        self.koloda = self.koloda.split(',')
                        shuffle(self.koloda)
                        await sql.request_db(f"UPDATE boards_poker_draw SET koloda = '{','.join(self.koloda)}' WHERE id = {self.id};")
                        await self.razd_kart()
                        self.status = 1
                        self.position = self.st_pl + 2
                        await sql.request_db(f"UPDATE boards_poker_draw SET date = NOW(), status = 1 WHERE id = {self.id};")
                        msg_text = await self.gen_message_room('Игра началась')
                        is_small = False
                        is_big = False
                        for idx, i in enumerate(self.players.split('\n'), start = 1):
                            if('отсутствует' in i):
                                pass
                            else:
                                line = await self.parse_sr(i)
                                user_id = int(line[1])
                                if((idx >= self.st_pl) and (not is_small)):#малый блайнд
                                    await sql.request_db(f"UPDATE users SET balance = balance - {self.ante + self.small_blind} WHERE user_id = {user_id};")
                                    is_small = True
                                    await self.add_stavka(user_id, self.ante + self.small_blind)
                                elif((not is_big) and is_small):#big блайнд
                                    self.position = idx
                                    await self.next_position()
                                    await sql.request_db(f"UPDATE users SET balance = balance - {self.ante + 2 * self.small_blind} WHERE user_id = {user_id};")
                                    is_big = True
                                    await self.add_stavka(user_id, self.ante + 2 * self.small_blind)
                        for idx, i in enumerate(self.players.split('\n'), start = 1):
                            if('отсутствует' in i):
                                pass
                            else:
                                line = await self.parse_sr(i)
                                user_id = int(line[1])
                                if((not is_big) and is_small):#big блайнд
                                    self.position = idx
                                    await self.next_position()
                                    await sql.request_db(f"UPDATE users SET balance = balance - {self.ante + 2 * self.small_blind} WHERE user_id = {user_id};")
                                    is_big = True
                                    await self.add_stavka(user_id, self.ante + 2 * self.small_blind)
                                elif(float(line[3])==0.0):#ante
                                    await sql.request_db(f"UPDATE users SET balance = balance - {self.ante} WHERE user_id = {user_id};")
                                    await self.add_stavka(user_id, self.ante)
                    else:
                        for idx, i in enumerate(self.players.split('\n'), start = 1):
                            if('отсутствует' in i):
                                pass
                            else:
                                line = await self.parse_sr(i)
                                self.players = self.players.replace(f'{i}', f'{idx}.|{line[1]}/{line[2]}(0)visiter')                            
                        self.status = 0
                        await sql.request_db(f"UPDATE boards_poker_draw SET status = 0, players = '{self.players}' WHERE id = {self.id};")
                    continue
                msg_text = await self.gen_message_room(f'Нажмите кнопку для подтверждения начала игры\. У вас есть 15 секунд\.\n*{15-int(tm[0][0])}*')
                if(self.last_message!=msg_text):
                    self.last_message = msg_text
                    await sql.request_db(f"UPDATE boards_poker_draw SET last_message = '{escape(msg_text)}' WHERE id = {self.id};")
                    for idx, i in enumerate(self.players.split('\n'), start = 1):
                        if('отсутствует' in i):
                            pass
                        else:
                            line = await self.parse_sr(i)
                            user_id = int(line[1])
                            if(line[-1]=='visiter'):
                                kb_ = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('CHECK', callback_data=f'{self.id}_check_poker'))
                                msg_id = await sql.request_db(f"SELECT last_message_bot FROM users WHERE user_id = {user_id};")
                                await main.bot.edit_message_text(msg_text, user_id, msg_id[0][0], parse_mode='MarkdownV2', reply_markup=kb_)
                            else:
                                msg_id = await sql.request_db(f"SELECT last_message_bot FROM users WHERE user_id = {user_id};")
                                await main.bot.edit_message_text(msg_text, user_id, msg_id[0][0], parse_mode='MarkdownV2')
            elif(self.status == 1):
                msg_text = await self.gen_message_room(f'')
                if(self.last_message!=msg_text):
                    self.last_message = msg_text
                    await sql.request_db(f"UPDATE boards_poker_draw SET last_message = '{escape(msg_text)}' WHERE id = {self.id};")
                    for idx, i in enumerate(self.players.split('\n'), start = 1):
                        if('отсутствует' in i):
                            pass
                        else:
                            line = await self.parse_sr(i)
                            user_id = int(line[1])
                            kb_ = types.InlineKeyboardMarkup()
                            kb_cards = self.cards.split('\n')[idx-1][2:].split(',')
                            kb_.row(types.InlineKeyboardButton(kb_cards[0], callback_data='none'), 
                                    types.InlineKeyboardButton(kb_cards[1], callback_data='none'), 
                                    types.InlineKeyboardButton(kb_cards[2], callback_data='none'), 
                                    types.InlineKeyboardButton(kb_cards[3], callback_data='none'), 
                                    types.InlineKeyboardButton(kb_cards[4], callback_data='none'))
                            if(self.position == idx):
                                bal = await sql.request_db(f"SELECT balance FROM users WHERE user_id = {user_id};")
                                maxs = await self.get_max_stavka()
                                if((maxs==float(line[3])) or (bal[0][0]==0.0)):
                                    kb_.row(types.InlineKeyboardButton('CHECK', callback_data=f'{self.id}_check_poker'), 
                                            types.InlineKeyboardButton('FOLD', callback_data=f'{self.id}_fold_poker'))
                                else:
                                    kb_.row(types.InlineKeyboardButton('CALL', callback_data=f'{self.id}_call_poker'),
                                            types.InlineKeyboardButton('RAISE', callback_data=f'{self.id}_raise_poker'), 
                                            types.InlineKeyboardButton('FOLD', callback_data=f'{self.id}_fold_poker'))
                            msg_id = await sql.request_db(f"SELECT last_message_bot FROM users WHERE user_id = {user_id};")
                            await main.bot.edit_message_text(msg_text, user_id, msg_id[0][0], parse_mode='MarkdownV2', reply_markup=kb_)
            await asyncio.sleep(0.01)

