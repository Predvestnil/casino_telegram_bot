import sql
import main
from aiogram import types
import key_board
import random, math
from aiogram.utils.markdown import escape_md as escape

#const
cards_21 = ['6♠','7♠','8♠','9♠','10♠','В♠','Д♠','К♠','ТУЗ♠','6♥','7♥','8♥','9♥','10♥','В♥','Д♥','К♥','ТУЗ♥','6♦','7♦','8♦','9♦','10♦','В♦','Д♦','К♦','ТУЗ♦','6♣','7♣','8♣','9♣','10♣','В♣','Д♣','К♣','ТУЗ♣']
cards_value_21 = {
    '6♠':6,
    '7♠':7,
    '8♠':8,
    '9♠':9,
    '10♠':10,
    'В♠':2,
    'Д♠':3,
    'К♠':4,
    'ТУЗ♠':11,
    '6♥':6,
    '7♥':7,
    '8♥':8,
    '9♥':9,
    '10♥':10,
    'В♥':2,
    'Д♥':3,
    'К♥':4,
    'ТУЗ♥':11,
    '6♦':6,
    '7♦':7,
    '8♦':8,
    '9♦':9,
    '10♦':10,
    'В♦':2,
    'Д♦':3,
    'К♦':4,
    'ТУЗ♦':11,
    '6♣':6,
    '7♣':7,
    '8♣':8,
    '9♣':9,
    '10♣':10,
    'В♣':2,
    'Д♣':3,
    'К♣':4,
    'ТУЗ♣':11
}
logo_21 = {1:'🧔', 2:'🧔🏻', 3:'🧔🏽', 4:'🧔🏾', 5:'🧔🏿', 6:'🧔🏼'}

async def get_card(id_game):
    cards_21_copy = cards_21
    random.shuffle(cards_21_copy)
    stro = await sql.request_db(f"SELECT cards_1, cards_2, cards_3, cards_4, cards_5, cards_6 FROM game_21 WHERE id = {id_game};")
    for i in cards_21_copy:
        if(i not in ''.join(stro[0])):
            return i


async def create_game_21(user_id):
    req = await sql.request_db(f"SELECT game_21.id, users.playing_game_id_21, users.user_id AS id_player, game_21.is_closed, game_21.max_players FROM game_21 INNER JOIN users ON game_21.id = users.playing_game_id_21 HAVING game_21.is_closed = 0 AND users.user_id = {user_id};")
    if(len(req) == 0):
        req = await sql.request_db("SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'db_cas' AND TABLE_NAME = 'game_21';")
        req = req[0][0]
        await sql.request_db("UPDATE users SET playing_game_id_21 = "+str(req)+" WHERE user_id = "+str(user_id)+";")
        await sql.request_db("INSERT INTO game_21(max_players, stavka) VALUES (1,0);")
        return int(req)
    else:
        if(req[0][-1] == 1):
            await sql.request_db("UPDATE game_21 SET password = '0';")
        return int(req[0][0])


async def search_game_21(id):
    reqq = await sql.request_db(f"SELECT COUNT(*) FROM (SELECT game_21.id,stavka,is_closed,password FROM game_21 INNER JOIN users ON game_21.id = users.playing_game_id_21 HAVING stavka>0 AND is_closed=0 AND password = '0') AS T;")
    if(reqq[0][0]!=0):
        req = await sql.request_db(f"SELECT id, max_players, stavka, count, is_closed, password FROM game_21 INNER JOIN (SELECT COUNT(user_id) AS count, playing_game_id_21 FROM users GROUP BY playing_game_id_21) AS T ON id = playing_game_id_21 HAVING is_closed = 0 AND stavka>0 AND max_players>count AND password = '0' LIMIT 5 OFFSET {id*5};")
        kb_inline = types.InlineKeyboardMarkup()
        for i in req:
            kb_inline.add(types.InlineKeyboardButton(text=f'Ставка: {i[2]}, игроков {i[3]}/{i[1]}', callback_data=f'{i[0]}_join_21'))
        if(id==0 and reqq[0][0]>5):
            kb_inline.add(types.InlineKeyboardButton(text=f'Далее', callback_data=f'{id+1}_public_21'))
        elif(id==int(reqq[0][0]/5) and id>0):
            kb_inline.add(types.InlineKeyboardButton(text=f'Назад', callback_data=f'{id-1}_public_21'))
        elif(id!=0 and id!=reqq[0][0]):
            kb_inline.add(types.InlineKeyboardButton(text=f'Назад', callback_data=f'{id-1}_public_21'), types.InlineKeyboardButton(text=f'Далее', callback_data=f'{id+1}_public_21'))
        kb_inline.add(types.InlineKeyboardButton(text=f'К меню 21 очка', callback_data=f'21_ochko'))
        return kb_inline
    else:
        return '0'


async def join_to_21(user_id, id_game):
    await sql.request_db(f'UPDATE game_21 SET player_1 = (CASE WHEN player_1 = 0 THEN {user_id} ELSE player_1 END) WHERE id = {id_game};')
    await sql.request_db(f'UPDATE game_21 SET player_2 = (CASE WHEN (player_2 = 0 AND player_1 <> {user_id} AND max_players>1) THEN {user_id} ELSE player_2 END) WHERE id = {id_game};')
    await sql.request_db(f'UPDATE game_21 SET player_3 = (CASE WHEN (player_3 = 0 AND player_2 <> {user_id} AND player_1 <> {user_id} AND max_players>2) THEN {user_id} ELSE player_3 END) WHERE id = {id_game};')
    await sql.request_db(f'UPDATE game_21 SET player_4 = (CASE WHEN (player_4 = 0 AND player_3 <> {user_id} AND player_2 <> {user_id} AND player_1 <> {user_id} AND max_players>3) THEN {user_id} ELSE player_4 END) WHERE id = {id_game};')
    await sql.request_db(f'UPDATE game_21 SET player_5 = (CASE WHEN (player_5 = 0 AND player_4 <> {user_id} AND player_3 <> {user_id} AND player_2 <> {user_id} AND player_1 <> {user_id} AND max_players>4) THEN {user_id} ELSE player_5 END) WHERE id = {id_game};')
    await sql.request_db(f'UPDATE game_21 SET player_6 = (CASE WHEN (player_6 = 0 AND player_5 <> {user_id} AND player_4 <> {user_id} AND player_3 <> {user_id} AND player_2 <> {user_id} AND player_1 <> {user_id} AND max_players>5) THEN {user_id} ELSE player_6 END) WHERE id = {id_game};')


async def start_give_cards(id_game):
    req = await sql.request_db(f'SELECT max_players FROM game_21 WHERE id = {id_game};')
    req = req[0]
    for i in range(1, req[0]+1):
        card = await get_card(id_game)
        await sql.request_db(f"UPDATE game_21 SET cards_{i} = '{card}:' WHERE id = {id_game};")


async def count_point(strin):
    strin = strin.replace(';', '')
    strin = strin.split(":")[:-1]
    count = 0
    for i in strin:
        count += cards_value_21[i]
    return count


async def message_room_21(user_id, id_game, passw = None):
    reqq = await sql.request_db(f'SELECT stavka, max_players, player_1, player_2, player_3, player_4, player_5, player_6, password, is_closed FROM game_21 WHERE id = {id_game};')
    reqq = reqq[0]
    if(reqq[1]==1):
        mes = key_board.room_21_message.format(id_game, escape(reqq[0]), '21 ОЧКО', escape(reqq[0]*2))
    else:
        mes = key_board.room_21_message.format(id_game, escape(reqq[0]), '21 ОЧКО', escape(reqq[0]*reqq[1]))
    keyb_inline = types.InlineKeyboardMarkup()
    k = 0
    dic_logo = {'КРУПЬЕ':'🎩', '':''}
    for i in range(1, reqq[1]+1):
        if(reqq[1+i]==0):
            mes += f'{logo_21[i]} отсутствует\n'
        else:
            if(reqq[1+i]==user_id):
                k = i
            qq = await sql.request_db(f'SELECT username FROM users WHERE user_id = {reqq[1+i]};')
            qq = qq[0][0]
            mes += escape(f'{logo_21[i]}{reqq[1+i]} | @{qq}\n')
            dic_logo[str(reqq[1+i])] = logo_21[i]
    if(reqq[-2]!='0' and reqq[1]!=1):
        mes += f'Пароль для подключения: `{passw}`\n'
    req = await sql.request_db(f"SELECT * FROM mess_21_list WHERE id_game = {id_game};")
    if(len(req)==0):
        pass
    else:
        mes += '💬Просто отправьте сообщение боту чтобы оно появилось в чате\n'
        if(len(req)>30):
            req = req[-30:]
        for i in req:
            mes += f"{dic_logo[i[1]]}*{escape(i[1])}*: {escape(i[2])}\n"
        await sql.request_db(f"UPDATE users SET status = 27 WHERE playing_game_id_21 = {id_game};")
        if(k!=0):
            req = await sql.request_db(f"SELECT cards_{k} FROM game_21 WHERE id = {id_game};")
            count = await count_point(req[0][0])
            if((';' in req[0][0]) or (count>=21)):
                name = None
                req = req[0][0].replace(':', '')
                req = req.replace(';', '')
                keyb_inline.add(types.InlineKeyboardButton(text=f"Ваша рука: {req}", callback_data=f'none'))
                rq = await sql.request_db(f"SELECT * FROM mess_21_list WHERE id_game = {id_game} AND (message = '\n➖➖ИГРА ОКОНЧЕНА➖➖\n' OR message = '{user_id} больше не берёт');")
                if(len(rq)==0):
                    keyb_inline.row(types.InlineKeyboardButton(text=f'✖️Хватит✖️', callback_data=f'stop_card_21'))
            else:
                req = req[0][0].replace(':', '')
                keyb_inline.add(types.InlineKeyboardButton(text=f"Ваша рука: {req}", callback_data=f'none'))
                keyb_inline.row(types.InlineKeyboardButton(text=f'➕Взять еще➕', callback_data=f'add_card_21'), types.InlineKeyboardButton(text=f'✖️Хватит✖️', callback_data=f'stop_card_21'))
    req = await sql.request_db(f'SELECT max_players, cards_1, cards_2, cards_3, cards_4, cards_5, cards_6, is_closed FROM game_21 WHERE id = {id_game};')
    if(req[0][-1]==2):
        max = req[0][0]
        result = None
        kk = 0
        for idx, i in enumerate(req[0][1:max+1], start = 1):
            if(';' not in i):
                kk += 1
            if(kk>=1):
                break
            if(idx == max):
                if(idx > 1):
                    result = await closed_game_21(id_game)
                else:
                    result = await closed_game_21(id_game)
        if(result == 1):#у вас перебор
            req = await sql.request_db(f'SELECT max_players, cards_1, cards_2, cards_3, cards_4, cards_5, cards_6, player_1, player_2, player_3, player_4, player_5, player_6, stavka FROM game_21 WHERE id = {id_game};')
            await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, 'КРУПЬЕ', '\n➖➖ИГРА ОКОНЧЕНА➖➖\n');")
            for idx, i in enumerate(req[0][1:max+1], start = 1):
                count = await count_point(i)
                id_user = req[0][6+idx]
                name = None
                sel = await sql.request_db(f"SELECT username FROM users WHERE user_id = {id_user};")
                if(sel[0][0] != 'None'):
                    name = sel[0][0]
                else:
                    name = id_user
                await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, 'КРУПЬЕ', '{name}: {count} очков');")
            st = req[0][-1]
            await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, 'КРУПЬЕ', '{key_board.not_winner_message}');")
            await sql.request_db(f'UPDATE game_21 SET is_closed = 1, winner_1 = 1 WHERE id = {id_game};')
            res = await message_room_21(user_id, id_game)
            return res
        elif(result == -1):#крупье победил
            req = await sql.request_db(f'SELECT cards_1, cards_2, player_1, stavka FROM game_21 WHERE id = {id_game};')
            req = req[0]
            count = await count_point(req[0])
            id_user = req[-2]
            name = None
            sel = await sql.request_db(f"SELECT username FROM users WHERE user_id = {id_user};")
            name = id_user
            await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, 'КРУПЬЕ', '\n➖➖ИГРА ОКОНЧЕНА➖➖\n');")
            await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, '{name}', '{count} очка(ов)');")
            count = await count_point(req[1])
            st = req[-1] * 2
            req = req[1].replace(':','')
            req = req.replace(';','')
            if(count==21):
                await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, 'КРУПЬЕ', '{req} - {count} очко!*');")
            else:
                await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, 'КРУПЬЕ', '{req} - {count} очка(ов)');")
            await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, 'КРУПЬЕ', 'КРУПЬЕ получает {st}💲');")
            await sql.request_db(f'UPDATE game_21 SET is_closed = 1, winner_1 = 1 WHERE id = {id_game};')
            res = await message_room_21(user_id, id_game)
            return res
        elif(result == -2):#перебор у участника
            req = await sql.request_db(f'SELECT cards_1, player_1, stavka FROM game_21 WHERE id = {id_game};')
            req = req[0]
            count = await count_point(req[0])
            id_user = req[-2]
            name = None
            sel = await sql.request_db(f"SELECT username FROM users WHERE user_id = {id_user};")
            name = id_user
            await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, 'КРУПЬЕ', '\n➖➖ИГРА ОКОНЧЕНА➖➖\n');")
            await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, '{name}', '{count} очка(ов)');")
            await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, 'КРУПЬЕ', 'У вас ПЕРЕБОР')")
            await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, 'КРУПЬЕ', 'получает {2*req[-1]}💲');")
            await sql.request_db(f'UPDATE game_21 SET is_closed = 1, winner_1 = 1 WHERE id = {id_game};')
            res = await message_room_21(user_id, id_game)
            return res
        elif(result == 0):#выход остальных 
            req = await sql.request_db(f"SELECT user_id FROM users WHERE playing_game_id_21 = {id_game};")
            req = req[0][0]
            id_user = req
            name = None
            sel = await sql.request_db(f"SELECT username FROM users WHERE user_id = {id_user};")
            name = id_user
            req = await sql.request_db(f'SELECT max_players, stavka FROM game_21 WHERE id = {id_game};')
            bank = req[0][0] * req[0][-1]
            await sql.request_db(f"UPDATE users SET count_prizes = count_prizes + {bank}, balance = balance + {bank}, count_games = count_games + 1, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {req[0][-1]} THEN (need_play_for_withdraw - {req[0][-1]}) ELSE (0)end) WHERE user_id = {id_user};")
            await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, 'КРУПЬЕ', '\n➖➖ИГРА ОКОНЧЕНА➖➖\n');")
            await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, 'КРУПЬЕ', '{name} получает банк комнаты из-за выхода остальных игроков');")
            await sql.request_db(f'UPDATE game_21 SET is_closed = 1, winner_1 = {id_user} WHERE id = {id_game};')
            res = await message_room_21(user_id, id_game)
            return res
        elif(result != None):#получен список участников
            req = await sql.request_db(f'SELECT max_players, cards_1, cards_2, cards_3, cards_4, cards_5, cards_6, player_1, player_2, player_3, player_4, player_5, player_6, stavka FROM game_21 WHERE id = {id_game};')
            max = req[0][0]
            if(max!=1):
                for idx, i in enumerate(req[0][1:max+1], start = 1):
                    count = await count_point(i)
                    id_user = req[0][6+idx]
                    await sql.request_db(f'UPDATE users SET count_games = count_games + 1, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {req[0][-1]} THEN (need_play_for_withdraw - {req[0][-1]}) ELSE (0)end) WHERE user_id = {id_user};')
                    name = None
                    sel = await sql.request_db(f"SELECT username FROM users WHERE user_id = {id_user};")
                    name = id_user
                    if(count==21):
                        await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, '{name}', '{count} очко!*');")
                    else:
                        await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, '{name}', '{count} очка(ов)');")
                bank = req[0][0] * req[0][-1]
                bank = math.floor(100*main.komission_casino *bank / float(len(result)))/100
                await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, 'КРУПЬЕ', '\n➖➖ИГРА ОКОНЧЕНА➖➖\n');")
                ms = '\n🚀'
                for idx, i in enumerate(result):
                    await sql.request_db(f"UPDATE game_21 SET winner_{idx+1} = player_{result[idx]} WHERE id = {id_game};")
                    qq = await sql.request_db(f"SELECT player_{result[idx]} FROM game_21 WHERE id = {id_game};")
                    await sql.request_db(f'UPDATE users SET count_prizes = count_prizes + {bank}, balance = balance + {bank} WHERE user_id = {qq[0][0]};')
                    qq = await sql.request_db(f"SELECT user_id, username FROM users WHERE user_id = {qq[0][0]};")
                    if(qq[0][1] != 'None'):
                        ms += f'👑@{qq[0][1]},'
                    else:
                        ms += f'👑{qq[0][0]},'
                ms = ms[:-1] + f' получают по {bank}💲🎆\n'
                await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, 'КРУПЬЕ', '{ms}');")
            else:
                id_user = req[0][7]
                name = None
                sel = await sql.request_db(f"SELECT username FROM users WHERE user_id = {id_user};")
                name = id_user
                req = await sql.request_db(f'SELECT cards_1, cards_2, stavka FROM game_21 WHERE id = {id_game};')
                req = req[0]
                bank = req[2] * 2
                count = await count_point(req[0])
                if(count==21):
                    await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, '{name}', '{count} очко!*');")
                else:
                    await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, 'КРУПЬЕ', '{name}: {count} очков');")
                count = await count_point(req[1])
                req = req[1].replace(':','')
                req = req.replace(';','')
                await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, 'КРУПЬЕ', '{req}: {count} очков');")
                await sql.request_db(f'UPDATE users SET count_games = count_games + 1, count_prizes = count_prizes + {bank}, need_play_for_withdraw = (CASE WHEN need_play_for_withdraw > {bank / 2} THEN (need_play_for_withdraw - {bank / 2}) ELSE (0)end), balance = balance + {bank} WHERE user_id = {id_user};')
                await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, 'КРУПЬЕ', '\n👑{name} выигрывает {bank}💲🎆');")
            await sql.request_db(f'UPDATE game_21 SET is_closed = 1, winner_1 = {id_user} WHERE id = {id_game};')
            res = await message_room_21(user_id, id_game)
            return res


    keyb_inline.row(types.InlineKeyboardButton('Покинуть', callback_data='leave_21'))
    return mes, keyb_inline



async def closed_game_21(id):
    stat = await sql.request_db(f"SELECT is_closed, max_players FROM game_21 WHERE id = {id};")
    if(stat[0][0] == 2):
        qq = await sql.request_db(f"SELECT user_id FROM users WHERE playing_game_id_21 = {id};")
        if(len(qq)==1 and stat[0][1]!=1):
            await sql.request_db("UPDATE game_21 SET winner_1 = "+str(qq[0][0])+" WHERE id = "+str(id)+";")
            return 0
        elif(stat[0][1]==1):
            req = await sql.request_db(f'SELECT cards_1 FROM game_21 WHERE id = {id};')
            count = await count_point(req[0][0])
            if(count>21):
                return -2
            else:
                count1 = 0
                while(count1<17):
                    card = await get_card(id)
                    await sql.request_db(f"UPDATE game_21 SET cards_2 = CONCAT(cards_2, '{card}:') WHERE id = {id};")
                    count1 = await sql.request_db(f'SELECT cards_2 FROM game_21 WHERE id = {id};')
                    count1 = await count_point(count1[0][0])
                if(count>count1 or count1>21):
                    return [qq[0][0]]
                else:
                    await sql.request_db("UPDATE game_21 SET winner_1 = 1 WHERE id = "+str(id)+";")
                    return -1
        else:
            req = await sql.request_db(f'SELECT max_players, cards_1, cards_2, cards_3, cards_4, cards_5, cards_6 FROM game_21 WHERE id = {id};')
            max = req[0][0]
            all_over_21 = True
            exist_21 = False
            for idx, i in enumerate(req[0][1:max+1]):
                count = await count_point(i)
                if(count == 21):
                    exist_21 = True
                    all_over_21 = False
                elif(count < 21):
                    all_over_21 = False
            if(all_over_21):
                return 1
            elif(exist_21):
                winners = []
                for idx, i in enumerate(req[0][1:max+1],start=1):
                    count = await count_point(i)
                    if(count == 21):
                        winners.append(idx)
                return winners
            else:
                maxx = 0
                for idx, i in enumerate(req[0][1:max+1]):
                    count = await count_point(i)
                    if(count > maxx and count < 21):
                        maxx = count
                winners = []
                for idx, i in enumerate(req[0][1:max+1], start = 1):
                    count = await count_point(i)
                    if(count == maxx):
                        winners.append(idx)
                return winners
    return 0
        


async def leave_game_21(user_id, id_game):
    stat = await sql.request_db(f"SELECT is_closed FROM game_21 WHERE id = {id_game};")
    if(stat[0][0]==2):
        await sql.request_db(f"UPDATE game_21 SET cards_1 = ';' WHERE id = {id_game} AND player_1 = {user_id};")
        await sql.request_db(f"UPDATE game_21 SET cards_2 = ';' WHERE id = {id_game} AND player_2 = {user_id};")
        await sql.request_db(f"UPDATE game_21 SET cards_3 = ';' WHERE id = {id_game} AND player_3 = {user_id};")
        await sql.request_db(f"UPDATE game_21 SET cards_4 = ';' WHERE id = {id_game} AND player_4 = {user_id};")
        await sql.request_db(f"UPDATE game_21 SET cards_5 = ';' WHERE id = {id_game} AND player_5 = {user_id};")
        await sql.request_db(f"UPDATE game_21 SET cards_6 = ';' WHERE id = {id_game} AND player_6 = {user_id};")
        await sql.request_db(f"INSERT INTO mess_21_list VALUES({id_game}, 'КРУПЬЕ', '{user_id} вышел');")
    elif(stat[0][0]==0):
        await sql.request_db(f'UPDATE game_21 SET player_1 = (CASE WHEN player_1 = {user_id} THEN 0 ELSE player_1 END) WHERE id = {id_game};')
        await sql.request_db(f'UPDATE game_21 SET player_2 = (CASE WHEN player_2 = {user_id} THEN 0 ELSE player_2 END) WHERE id = {id_game};')
        await sql.request_db(f'UPDATE game_21 SET player_3 = (CASE WHEN player_3 = {user_id} THEN 0 ELSE player_3 END) WHERE id = {id_game};')
        await sql.request_db(f'UPDATE game_21 SET player_4 = (CASE WHEN player_4 = {user_id} THEN 0 ELSE player_4 END) WHERE id = {id_game};')
        await sql.request_db(f'UPDATE game_21 SET player_5 = (CASE WHEN player_5 = {user_id} THEN 0 ELSE player_5 END) WHERE id = {id_game};')
        await sql.request_db(f'UPDATE game_21 SET player_6 = (CASE WHEN player_6 = {user_id} THEN 0 ELSE player_6 END) WHERE id = {id_game};')
