from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import escape_md as escape

##### CONSTANTS
link_bot = ''#ссылка на бота
link_channel = ''#ссылка на канал
link_chat = ''#ссылка на чат
link_admin = ''#ссылка на админа
link_support = ''#ссылка
link_soglash = ''#ссылка на пользовательское соглашение
link_video_create_room = ''#ссылка на видео по созданию комнаты в 21
link_message_adding = ''#ссылка на сообщение из канала



welcome_message = f'''❕*Для полноценного использования бота необходимо быть участником* [чата]({link_chat})\(_кликабельно_\)\.'''
start_welcome_kb = InlineKeyboardMarkup().add(InlineKeyboardButton('🗒️Я вступил', callback_data='subscribe'))


start_client_kb_reply = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('🍀Играть🍀'))
start_client_kb_reply.row(KeyboardButton('💲Кошелек'),KeyboardButton('👁️‍🗨️Профиль'))
start_client_kb_reply.add(KeyboardButton('🗄️Дополнительно🗄️'))
start_client_kb_inline = InlineKeyboardMarkup().add(InlineKeyboardButton('Соглашение📝', url=link_soglash))
start_menu_message = '🎇Добро пожаловать в *GAS* _casino_\!'



ref_message = '''👨‍👧‍👧Приводи новых пользователей и получай {}% с их депозитов\!

👏🏻Вы привели: {} человек
🤝🏻Суммарный бонус: {}💲

Ваша реферальная ссылка: [ `'''+escape(link_bot)+'''?start\={}` ]'''
ref_kb_inline = InlineKeyboardMarkup().add(InlineKeyboardButton('👩‍👦Реферальная программа', callback_data='ref_link'))
reflink_kb_inline = InlineKeyboardMarkup().add(InlineKeyboardButton('👈🏻Вернуться в профиль', callback_data='profile_link'))

dopoln_message = '🎆 *VEGAS HELP MENU* 🎆'
support_client_kb_inline = InlineKeyboardMarkup().row(InlineKeyboardButton('💬 Наш чат', url=link_chat),InlineKeyboardButton('🪧Наш канал', url=link_channel))
support_client_kb_inline.row(InlineKeyboardButton('📃Соглашение', url=link_soglash),InlineKeyboardButton('⌨️Поддержка', url=link_support))
support_client_kb_inline.row(InlineKeyboardButton('Я-владелец тимы/канала/чата', callback_data='i_tc'))


i_tc_message = '''*Если вы владеете источником трафика*, мы можем предоставить вам дополнительную монетизацию путем подключения вас к нашей партнерской сети\. Напишите [совладельцу проекта](https://t.me/mister_minister_invegas), ответственному за коммуникацию с партнерами указав хештег \#партнер в сообщении\. Вы получите ответ в приоритетном порядке\.'''



wallet_message = '💎ВАШ БАЛАНС:  {}💲'
wallet_client_kb_inline = InlineKeyboardMarkup().add(InlineKeyboardButton('📥Пополнить ', callback_data='add_money'))
wallet_client_kb_inline.row(InlineKeyboardButton('💌Подарить', callback_data='input_value_promo'),InlineKeyboardButton('📨Мои промокоды', callback_data='my_promo'))
wallet_client_kb_inline.add(InlineKeyboardButton('📤Вывод средств', callback_data='withdraw_money'))


new_ref_message = '👨‍👧У вас новый реферал\! @{}'



list_my_promo = 'Вы создали:\n🪙 {} промокодов\n⚪️ {} из них активировано'
list_promo_kb_inline = InlineKeyboardMarkup().add(InlineKeyboardButton('🎾Активные промокоды', callback_data='list_my_promo'))

qiwi_message = '''💳Нажмите на кнопку чтобы перейти на страницу оплаты\.
📨Зачисление средств происходит автоматически в течение 60 секунд\.

Минимальная сумма пополнения — 350₽ \(5💲\)
Актуальный курс:
1💲 \= {}₽
Чтобы точно рассчитать сумму:
Отправьте боту команду /rub число\.
В качестве числа введите количество рублей которые хотите отправить и тогда бот скажет вам сколько 💲 вы получите\. Если числом будет количество долларов которое вы хотите получить на баланс \- бот сообщит вам сколько рублей потребуется отправить\.
Например, при отправленной команде /rub 1000 бот пришлет подобное [сообщение]('''+f'{link_message_adding}'+''')\.'''
error_promo_message = '''🗑️*Некорректно введена сумма\!
Пожалуйста, отправьте число\.*
Например, 1\.08\.\n*Либо у вас недостаточно средств*\.'''
value_promo_message = '🖋️Введите сумму промокода в 💲'
create_promo_message = '✔️Промокод на сумму {}💲 успешно создан\!\n💱Отправьте ссылку тому, кому вы хотите подарить средства\.\n\n*[* `'+escape(link_bot) + '?start\={}` *]*\n\n_Вы получите уведомление тогда, когда промокод активируют\. До этого момента промокод доступен во вкладке «Мои промокоды»_'
activate_promo_message = '✔️Промокод на сумму {}💲 успешно активирован\!\n💱Средства уже зачислены на ваш баланс'
from_activate_promo_message = '💱Ваш промокод `{}` на сумму {}💲 только что был активирован\!'

end_promo_kb_inline = InlineKeyboardMarkup().add(InlineKeyboardButton('➕Создать еще', callback_data='input_value_promo'))
end_promo_kb_inline.row(InlineKeyboardButton('🔙В меню', callback_data='return_wallet'))


addmoney_message = f'➕Выберите удобный способ автоматического пополнения\n🔝Минимальная сумма депозита: 5💲\nНе нашли нужного способа?\n[Обратитесь к нам]({link_support})\!'
addmoney_client_kb_inline = InlineKeyboardMarkup().add(InlineKeyboardButton('🤖Banker ', callback_data='btc_bankir'))
addmoney_client_kb_inline.row(InlineKeyboardButton('🤖BitPapa', callback_data='bitpapa'),InlineKeyboardButton('🤖CryptoBot', callback_data='cryptobot'))
addmoney_client_kb_inline.add(InlineKeyboardButton('🔛Прямой криптоперевод', callback_data='to_crypto'))
addmoney_client_kb_inline.add(InlineKeyboardButton('🟠QIWI', callback_data='to_qiwi'))
addmoney_client_kb_inline.add(InlineKeyboardButton('🔙В меню', callback_data='return_wallet'))



list_crypto_message = '👁️‍🗨️Выберите токен в котором вам удобно совершить перевод:\nНе нашли нужного токена?\n[Обратитесь к нам]({link_support})\!'
list_crypto_kb_inline = InlineKeyboardMarkup().row(InlineKeyboardButton('🪙BTC', callback_data='btc_to'),InlineKeyboardButton('🪙ETH', callback_data='eth_to'))
list_crypto_kb_inline.row(InlineKeyboardButton('🪙TRX', callback_data='trx_to'),InlineKeyboardButton('🪙USDT(TRC-20)', callback_data='usdt_to'))
list_crypto_kb_inline.add(InlineKeyboardButton('🔦Назад', callback_data='return_change_add'))


keep_address_message = '''🔛Переведите желаемую сумму на адрес:
*\[ `{}` \]* 
Этот адрес зафиксирован за вами на {} минут, начиная с этого момента\. Учитывайте время обработки транзакции\.
После выполненного перевода нажмите на кнопку «Я оплатил»
Бот самостоятельно определит сумму которую вы отправили\.
Оплата может фиксироваться до 5 минут\.

💱Актуальный курс:
*1 {} \= {}*💲

Чтобы рассчитать точную сумму:
Отправьте боту команду `/{} число`\.
В качестве числа введите количество монет которые хотите отправить и тогда бот скажет вам сколько 💲 вы получите\. Если числом будет количество долларов которое вы хотите получить на баланс \- бот сообщит вам сколько монет потребуется отправить\.
Например, при отправленной команде `/{} 10` бот пришлет подобное [сообщение]('''+link_message_adding+''')\.'''
keep_address_kb_inline = InlineKeyboardMarkup().add(InlineKeyboardButton('🎾Я оплатил', callback_data='set_2_address'))
keep_address_kb_inline.row(InlineKeyboardButton('🔙Назад', callback_data='return_change_add'))
not_free_address_message = '😔К сожалению, на данный момент все адреса для пополнения заняты другими пользователями\.\n🕑Пожалуйста, попробуйте снова через несколько минут\.'
not_free_address_kb_inline = InlineKeyboardMarkup().row(InlineKeyboardButton('🔙Назад', callback_data='return_change_add'))

return_change_kb_inline = InlineKeyboardMarkup().add(InlineKeyboardButton('Назад', callback_data='return_change_add'))


btc_bankir_message = '''🔛*Пришлите чек банкира вида \[`telegram.me/………`\]*
Зачисление средств производится в течение 60 секунд после получения чека\. Бот самостоятельно определит сумму которую вы отправили\.


*💱Актуальный курс:
1💲 \= {} rub          `/rub`
1💲 \= {} uah       `/uah`
1💲 \= {} kzt     `/kzt`

Чтобы рассчитать точную сумму:*
Отправьте боту команду */валюта _число_*\.
_В качестве числа введите количество вашей валюты которые хотите отправить и тогда бот скажет вам сколько 💲 вы получите\. Если числом будет количество долларов которое вы хотите получить на баланс \- бот сообщит вам сколько вашей валюты  потребуется отправить\.
Например, при отправленной команде `/rub 1000` бот пришлет подобное [сообщение]('''+f'{link_message_adding}'+''')_'''
bit_papa_message = '''🔛*Пришлите чек bitpapa вида \[`telegram.me/………`\]*
Зачисление средств производится в течение 60 секунд после получения чека\. Бот самостоятельно определит сумму которую вы отправили\.


*💱Актуальный курс:
1💲 \= {} rub          `/rub`
1💲 \= {} uah       `/uah`
1💲 \= {} kzt     `/kzt`

Чтобы рассчитать точную сумму:*
Отправьте боту команду */валюта _число_*\.
_В качестве числа введите количество вашей валюты которые хотите отправить и тогда бот скажет вам сколько 💲 вы получите\. Если числом будет количество долларов которое вы хотите получить на баланс \- бот сообщит вам сколько вашей валюты  потребуется отправить\.
Например, при отправленной команде `/rub 1000` бот пришлет подобное [сообщение]('''+f'{link_message_adding}'+''')_'''
crypto_bot_message = '''🔛*Пришлите чек криптобота вида \[`telegram.me/………`\]*
Зачисление средств производится в течение 60 секунд после получения чека\. Бот самостоятельно определит сумму которую вы отправили\.


*💱Актуальный курс:
1💲 \= {} rub          `/rub`
1💲 \= {} uah       `/uah`
1💲 \= {} kzt     `/kzt`

Чтобы рассчитать точную сумму:*
Отправьте боту команду */валюта* _число_\.
_В качестве числа введите количество вашей валюты которые хотите отправить и тогда бот скажет вам сколько 💲 вы получите\. Если числом будет количество долларов которое вы хотите получить на баланс \- бот сообщит вам сколько вашей валюты  потребуется отправить\.
Например, при отправленной команде `/rub 1000` бот пришлет подобное [сообщение]('''+f'{link_message_adding}'+''')_'''


adding_message = '''💸*Перевод на {}💲 обнаружен\!
💲Средства зачислены на ваш баланс\.*'''
adding_inline = InlineKeyboardMarkup().add(InlineKeyboardButton('☎️Создать новую заявку', callback_data='return_wallet'))
error_timeout_message = '⏰Время заявки на пополнение вышло\!'

chat_multigame_message = '''⭐️ *Здесь вы можете войти в публичную или приватную игру\.*

💣*Создать публичную игру можно только в нашем чате\.*
🥷🏻*Создать приватную игру можно только здесь\.*

🕶[процесс входа, создания комнат]({link_video_create_room})'''

menu_game_message = '''🎆 *LAS VEGAS MENU* 🎆'''
menu_game_kb_inline = InlineKeyboardMarkup().row(InlineKeyboardButton('🎳⚽MINI GAMES🎯🏀', callback_data='minigames'))
menu_game_kb_inline.row(InlineKeyboardButton('🎲DICE🎲', callback_data='req_dice'),InlineKeyboardButton('🎰SLOTS🎰', callback_data='slots'))
menu_game_kb_inline.row(InlineKeyboardButton('♠POKER♠', callback_data='coming_soon'),InlineKeyboardButton('♥21♥', callback_data='21_ochko'))
menu_game_kb_inline.add(InlineKeyboardButton('💬ИГРЫ В ЧАТЕ', callback_data='0_game_in_chat'))


menu_minigame_kb_inline = InlineKeyboardMarkup().row(InlineKeyboardButton('🎳BOWLING🎳', callback_data='bowling'),InlineKeyboardButton('⚽PENALTY⚽', callback_data='penalty'))
menu_minigame_kb_inline.row(InlineKeyboardButton('🎯DARTS🎯', callback_data='darts'),InlineKeyboardButton('🏀BASKETBALL🏀', callback_data='basketball'))
menu_minigame_kb_inline.add(InlineKeyboardButton('Назад', callback_data='cancel_game'))


error_game_message = '''*Выберите игру через главное меню и введя ставку*'''


dice_number_kb_inline = InlineKeyboardMarkup().row(InlineKeyboardButton('1', callback_data='dice_number1'),InlineKeyboardButton('2', callback_data='dice_number2'),InlineKeyboardButton('3', callback_data='dice_number3'))
dice_number_kb_inline.row(InlineKeyboardButton('4', callback_data='dice_number4'),InlineKeyboardButton('5', callback_data='dice_number5'),InlineKeyboardButton('6', callback_data='dice_number6'))
dice_number_kb_inline.row(InlineKeyboardButton('✖️Отменить игру', callback_data='cancel_game'))


number_dice_message = '''💡*Выберите число на которое вы готовы поставить*'''
value_stavka_message = '''🖊️*Введите сумму ставки в 💲
min: 0\.2💲                  max:700*💲
Например, 50\.'''
error_value_stavka_message = '''❗️*Пожалуйста, введите сумму ставки, которая не превышает ваш баланс\.*\n📍Например, `10`\.'''


game_message_id = {
    14: '''⚜️Выигрыши в боулинге🎳\n\n💢Сбил все кегли: *_3X_*\n♨️Сбил 5 кеглей: возврат ставки в *полном размере*\n🤯Сбил всё 5 раз подряд: *_50Х_*\n\n[гарантии честности]({link_garant})\n\n*Пришлите стикер* `🎳` *\(клик чтобы скопировать\) боту*\n💰Ваша ставка:  {}💲''',
    15: '''⚜️Выигрыши в футболе⚽\n\n👉👌Попал: *_1\.5X_*\n🤯Забил гол 10 раз подряд: *_50Х_*\n\n[гарантии честности]({link_garant})\n\n*Пришлите стикер* `⚽` *\(клик чтобы скопировать\) боту*\n💰Ваша ставка:  {}💲''',
    16: '''⚜️Выигрыши в дартс🎯\n\n⭐️Попал в центр: *_3X_*\n🌟Попал в белое кольцо возле центра: возврат ставки в *полном размере*\n🤯Попал в центр 5 раз подряд: *_50Х_*\n\n[гарантии честности]({link_garant})\n\n*Пришлите стикер* `🎯` *\(клик чтобы скопировать\) боту*\n💰Ваша ставка:  {}💲''',
    17: '''⚜️Выигрыши в баскетболе🏀\n\n👉👌Попал: *_1\.5X_*\n🤯Закинул мяч 10 раз подряд: *_100Х_*\n\n[гарантии честности]({link_garant})\n\n*Пришлите стикер* `🏀` *\(клик чтобы скопировать\) боту*\n💰Ваша ставка:  {}💲''',
    21: '''⚜️Выигрыши в дайсе🎲\n\n💡Угадал выпавшее число: *_3Х_*\n🕯️Выпало одно из соседних чисел: возврат *половины ставки*\n🤯Угадал число 5 раз подряд: *_50Х_*\n⚡️_У тройки, например, соседними числами считаются двойка и четверка, у единицы\-двойка и шестерка, у шестерки\-единица и пятерка и т\.д\._\n\n[гарантии честности]({link_garant})\n\nВы загадали:*_ {} _* \n *Пришлите стикер* `🎲` *\(клик чтобы скопировать\) боту*\n💰Ваша ставка:  {}💲''',
    20: '''⚜️Комбинации и выигрыши:\n\n❤️‍🔥Три семерки: *_7X_*\n❤️Три любых предмета в ряд: *_3X_*\n❣️Две семерки на любых позициях: *_2X_*\n❣️Два лимона рядом: *_2X_*\n🤯Три семерки 2 раза подряд: *_50Х_*\n\n[гарантии честности]({link_garant})\n❓[подробнее о комбинациях и позициях]({link_slots})\n\n*Пришлите стикер* `🎰` *\(клик чтобы скопировать\) боту*\n💰Ваша ставка:  {}💲'''
}
minigame_kb_inline = InlineKeyboardMarkup().add(InlineKeyboardButton('✖️Отменить игру', callback_data='cancel_game'))


restart_minigame_kb_inline = {
    14: InlineKeyboardMarkup().add(InlineKeyboardButton('✅Еще раз', callback_data='1bowling'),InlineKeyboardButton('🔫К мини-играм', callback_data='minigames')).row(InlineKeyboardButton('♻️Сменить ставку', callback_data='bowling')),
    15: InlineKeyboardMarkup().add(InlineKeyboardButton('✅Еще раз', callback_data='1penalty'),InlineKeyboardButton('🔫К мини-играм', callback_data='minigames')).row(InlineKeyboardButton('♻️Сменить ставку', callback_data='penalty')),
    16: InlineKeyboardMarkup().add(InlineKeyboardButton('✅Еще раз', callback_data='1darts'),InlineKeyboardButton('🔫К мини-играм', callback_data='minigames')).row(InlineKeyboardButton('♻️Сменить ставку', callback_data='darts')),
    17: InlineKeyboardMarkup().add(InlineKeyboardButton('✅Еще раз', callback_data='1basketball'),InlineKeyboardButton('🔫К мини-играм', callback_data='minigames')).row(InlineKeyboardButton('♻️Сменить ставку', callback_data='basketball')),
    20: InlineKeyboardMarkup().add(InlineKeyboardButton('✅Еще раз', callback_data='1slots'),InlineKeyboardButton('🔫К мини-играм', callback_data='minigames')).row(InlineKeyboardButton('♻️Сменить ставку', callback_data='slots')),
    21: InlineKeyboardMarkup().add(InlineKeyboardButton('✅Еще раз', callback_data='1req_dice'),InlineKeyboardButton('🔫К мини-играм', callback_data='minigames')).row(InlineKeyboardButton('♻️Сменить ставку', callback_data='req_dice')),
}

victory_mini_message = '*Поздравляем🍾\.* *Вы выиграли  {}*💲'
slots777_vict_message = '💥*КУШШШШШШШ\!\!*  Поздравляем🍾 🥂\n 🤯*Вы выиграли {}*💲'
slots111_vict_message = '*ТРИ В РРРЯЯЯЯЯД\!\!*  🎇Поздравляем🎆\n🤑*Вы выиграли {}*💲'
slots77_vict_message = '*Семь и еще раз СЕМЬ\!\!* Поздравляем🍾\n🔥*Вы выиграли {}*💲'
slotsLL_vict_message = '*Два козырных ЛИМОНА\!\!* Поздравляем⚡️\n🧨*Вы выиграли {}*💲'
lose_mini_message = '*😕Повезет в следующий раз…*'
dice_full_victory_message = '🔥*То самое число\!\!* Поздравляем\!🍾\n*Вы выиграли {}*💲'
dice_nonfull_victory_message = '🔛*СОСЕДНЕЕ* с загаданным число\!\n*Выигрыш:  {}*💲'
darts_full_victory_message = '⚡️*Прямо в яблочко\!\!\!* Поздравляем🎇\n*Вы выиграли  {}*💲'
darts_nonfull_victory_message = '*Почти\!* Но у вас есть второй шанс💣\n*Ваш выигрыш: {}*💲'
bowl_full_victory_message = '💥*СТРАААЙК\!\!\!* Поздравляем🍾\n*Вы выиграли {}*💲'
bowl_nonfull_victory_message = '*Одна устояла\!\!* У вас есть второй шанс💣\n*Ваш выигрыш: {}*💲'
foot_full_victory_message = '☄️*ГООООЛ\!\!* Поздравляем🔥\n*Вы выиграли {}*💲'
basket_full_victory_message = '☄️*Заброшенный мяч\!* Поздравляем🔥\n*Вы выиграли {}*💲'



or_game_menu_message = '''❗️*У вас есть незаконченная игра\.*\n❓*Хотите ее покинуть?*'''
or_game_kb_inline = InlineKeyboardMarkup().row(InlineKeyboardButton('✔️Да', callback_data='cancel_game'),InlineKeyboardButton('✖️Нет', callback_data='continue_game'))


or21_game_menu_message = '''❗️*У вас есть незаконченная игра\. При выходе из игры  ваша ставка останется в банке\.\n❓Хотите покинуть игру?*'''
or21_game_kb_inline = InlineKeyboardMarkup().row(InlineKeyboardButton('✔️Да', callback_data='true_leave_21'),InlineKeyboardButton('✖️Нет', callback_data='false_leave_21'))


menu_21_message = '🤍*21*🤍 in *GAS*'


public_21_message = '💘 *Выберите комнату\.*'
empty_public_21_message = '''🌒На данный момент публичных комнат в которых еще не началась игра нет'''
create_21_message = f'⚙️Установите настройки комнаты и отправьте боту сообщение содержащее размер ставки\.\n*min: 0\.2💲                  max:700*💲\n\n🔦[Видео\-процесс создания комнаты]({link_video_create_room})'
tiny_value_stavka_message = '❗️Пожалуйста, введите сумму ставки которая не привыкала бы ваш баланс\.'
tiny_private_value_stavka_message = '❗️Пожалуйста, введите сумму ставки которая не привыкала бы ваш баланс\. Ставка: {}💲'


error_private_message = '❌*Не найдено комнаты с таким паролем*'
error_private_kb_inline = InlineKeyboardMarkup().row(InlineKeyboardButton('🔻   Вернуться   🔻', callback_data='21_ochko'))

to_private_21_message = '🔐*Введите пароль от комнаты в которую хотите войти:*'

join_21_message = '🔍*Комната найдена\!*\n\n💸*Ставка:*  {}💲\n{}\n\n*Присоединиться к игре?*'


room_21_message = '*ID*: {}ㅤㅤㅤㅤㅤㅤ💸 {} 💲\n🖤{}🖤ㅤ  💰{}💲\n'

leave_21_message = 'Если вы покинете комнату, будет засчитано, что вы проиграли\.'
leave_21_kb_inline = InlineKeyboardMarkup().row(InlineKeyboardButton('▪️Покинуть▪️', callback_data='true_leave_21'),InlineKeyboardButton('▪️Остаться▪️', callback_data='false_leave_21'))

big_text_error_message = '❕*Слишком длинное сообщение\!*'


not_winner_message = '📈*У всех игроков перебор\!Банк остается у крупье*'



kurs_message = '*{} {} \= {} {}\n{} {} \= {} {}*'

exist_start_game_message = '❕*У вас нет начатых игр*, поэтому этот стикер проигнорирован ботом\.\n*Список команд* для начала игры доступен по команде `/help`\.'

comand_not_user_message = '❕*Эта команда используется для создания игры на деньги\.*\nПерейдите в [бота]({link_bot}), внесите средства любым удобным способом и играйте в соло или мультиигры\!'

error_smile_game_message = '⛔️*Предупреждение\.* Вы отправили не соответствующий типу игры стикер\!'

player_another_start_game_message = 'У вас есть неоконченная игра\n'


partner_profile_message = '''🖥️*Кабинет партнера {}*
*Подключен к нам:* {}
*Источник трафика:* [чат]({})

Доступно к выводу: *{}💲\(\+{}* за сегодня\)
За вами зафиксировано: *{}* человек \(*\+{}* за сегодня\)

🖤По любому вопросу вы всегда можете обратиться к [совладельцу проекта]({link_admin}), отвветственному за коммуникацию с партнерами или в нашу [техническую поддержку]({link_support})'''
partner_kb_inline = InlineKeyboardMarkup().add(InlineKeyboardButton('👩‍👦Реферальная программа', callback_data='ref_link')).add(InlineKeyboardButton('📤Вывод средств', callback_data='withdraw_money'))


profile_chat_message = '''🎅🏻*Ваш профиль:*

©️*ID*: {}
©️*USERNAME*: @{}
⏰*Вы с нами с*: {}
🍷*Игр сыграно*: {}
🚨*Выигрышей на сумму*: {}💲
🎖️*Был\(а\) в топах*: 0 раз\(а\)


_Напишите_ `/info` _в нашем чате чтобы продемонстрировать участникам свой профиль\.
Чтобы увидеть профиль другого пользователя — напишите_ `/info` _в ответ на его сообщение или_ `/info \[id пользователя\]`'''
error_profile_chat_message = '🔎*Не удалось обнаружить данный профиль\.*'

join_multigame_message = 'Вам предлагает {} сыграть в {} на {} человек со ставкой {}$.\n Согласитесь, либо откажитесь от игры'
join_multigame_inline = InlineKeyboardMarkup().row(InlineKeyboardButton('▪️Согласиться▪️', callback_data=''),InlineKeyboardButton('▪️Отказаться▪️', callback_data='false_leave_21'))



multigame_message_name = {
    'Bowling': '''\n*Пришлите стикер* `🎳` *\(клик чтобы скопировать\) боту*\n''',
    'Penalty': '''\n*Пришлите стикер* `⚽` *\(клик чтобы скопировать\) боту*\n''',
    'Darts': '''\n*Пришлите стикер* `🎯` *\(клик чтобы скопировать\) боту*\n''',
    'Basketball': '''\n*Пришлите стикер* `🏀` *\(клик чтобы скопировать\) боту*\n''',
    'Dice': '''\n*Пришлите стикер* `🎲` *\(клик чтобы скопировать\) боту*\n''',
}

not_enough_balance_message = "❕Сумма средств на вашем балансе меньше чем установленная в этой игре ставка"
keep_tojoin_game_message = "Требуется для начала присоединиться к игре!"

multigame_shapka_message = '''\#ID{}  {}
💸*Ставка:*  {}💲

{}

'''

notready_multigame_message = '''🕑Ожидание игроков…Игра начнется тогда, когда все участники поставят статус «готов»\.
2\-6 игроков'''

leave_without_dep_message = '❗️При выходе из игры ваша ставка останется в банке.\nЕсли вы хотите покинуть игру - еще раз нажмите на кнопку «Выйти».'

victory_multi_message = '''*ИГРА* \#ID{}  {}  *ЗАВЕРШЕНА*
💸*Ставка:  {}*💲

{}

🎇*Поздравляем победителей*🍾'''

draw_multi_message = 'Ничья\. Требуется переиграть игру:\n'


error_deposit = f"⏰*Время заявки на пополнение вышло\!*"


link_multi_message = '*Сообщение с возможностью войти в данную игру уже продублировано для вас в чате, где данная игра была создана\.*\n🔎В случае если игру найти не удается, перейдите к ней через поиск в чате по `\#ID{}`\.\n[видео\-инструкция]({link_video_room})'

help_commands_message = '*КОМАНДЫ В ЧАТЕ*\n\nСОЛО ИГРЫ:\n«`/bask` \[ставка\]» *или *«`/🏀` \[ставка\]»\n«`/bowl` \[ставка\]» *или *«`/🎳` \[ставка\]»\n«`/darts` \[ставка\]» *или* «`/🎯` \[ставка\]»\n«`/slot` \[ставка\]» *или *«`/🎰` \[ставка\]»\n«`/cube` \[число\] \[ставка\]» *или* «`/🎲` \[число\] \[ставка\]»\n_Про коэффициенты выигрышей читайте в [боте]({link_bot})\._\n\nМУЛЬТИИГРЫ:\n_То же самое, только с приставкой mult или m_:\n«`/mult bask` \[ставка\]» *или* «`/m 🏀` \[ставка\]» *Побеждают игрок\(и\), закинувшие мяч в корзину\.*\n«`/mult bowl` \[ставка\]» *или* «`/m 🎳` \[ставка\]» *Побеждают игрок\(и\), сбившие максимальное количество кеглей\.*\n«`/mult darts` \[ставка\]» *или* «`/m 🎯` \[ставка\]» *Побеждают игрок\(и\), попавшие ближе всего к центру\.*\n«`/mult cube` \[ставка\]» *или *«`/m 🎲` \[ставка\]»* Побеждают игрок\(и\), выбросившие наибольшее число\.*\n_Победители делят между собой банк игры с учетом комиссии сервиса 7%\._\n[подробнее]({link_game_chat})\n\nПРИВАТНЫЕ ИГРЫ\(с паролем\)\nСоздаются только в боте и играются только в официальном чате\.\n\n_Все вышеперечисленные команды работают во всех партнерских чатах\._\n*Игровой бот:* {link_bot}'


multi_games_message = 'Выберите тип игры'
multi_games_inline = InlineKeyboardMarkup().row(InlineKeyboardButton('🎲', callback_data='game_multi_private2'),InlineKeyboardButton('🏀', callback_data='game_multi_private3'))
multi_games_inline.row(InlineKeyboardButton('⚽', callback_data='game_multi_private4'),InlineKeyboardButton('🎯', callback_data='game_multi_private5'))
multi_games_inline.row(InlineKeyboardButton('🎳', callback_data='game_multi_private6'))

cancel_multigame_kb_inline = InlineKeyboardMarkup().add(InlineKeyboardButton('Отменить игру', callback_data='cancel_multigame'))


pass_multigame_message = '''*Пароль* от вашей игры: `{}`\n`\#ID{}`\n*Комната создана в чате бота*'''
multigame_kb_inline = InlineKeyboardMarkup().add(InlineKeyboardButton('Чат', url=link_chat))


input_pass_message = '🔐*Введите пароль от комнаты в которую хотите войти:*'
input_pass_kb_inline = InlineKeyboardMarkup().row(InlineKeyboardButton('🔻   Вернуться   🔻', callback_data='0_game_in_chat'))

error_multiprivate_message = '❌*Не найдено комнаты с таким паролем*'
error_multiprivate_kb_inline = InlineKeyboardMarkup().row(InlineKeyboardButton('🔻   Вернуться   🔻', callback_data='join_multi_private'))


shapka_menu_kb_inline = InlineKeyboardMarkup().row(InlineKeyboardButton('🥷🏻СОЗДАТЬ', callback_data=f'create_multi_private'), InlineKeyboardButton('🥷🏻ВОЙТИ', callback_data=f'join_multichat_private'))


end_still_multigame = '🕝*Время игры вышло*\. Ни один участник не принял участия в игре, ставка остается у крупье\.'

notif_startgame_message = 'Игра, в которую вы ранее вошли только что *началась*\.\n🔎 Войдите в чат по кнопке и найдите игру по \#ID{}'

allgames_message = "🧲*Активные игры в этом чате:*\n{}"


dep_ref_message = 'Зафиксирован депозит вашего реферала {} на сумму {}💲\.\n➕*Вам начислено {}*💲'


need_ot_message = 'В соответствии с пунктом 3\.2 [пользовательского соглашения]({link_soglash}) для вывода *вам нужно отыграть еще {}*💲'

withdraw_menu_message = '''🎆 *GAS WITHDRAW* 🎆\n*_Минимальный размер вывода: 5_*💲'''
withdraw_menu_kb_inline = InlineKeyboardMarkup().row(InlineKeyboardButton('🟠QIWI', callback_data=f'qiwi_withdraw_method'), InlineKeyboardButton('🟣ЮMoney', callback_data=f'yoomoney_withdraw_method')).row(InlineKeyboardButton('🏦 Банк.Карта', callback_data=f'bank_withdraw_method')).row(InlineKeyboardButton('💵USDT(TRC-20)', callback_data=f'usdt_withdraw_method'), InlineKeyboardButton('🪙BITCOIN', callback_data=f'bitcoin_withdraw_method'), InlineKeyboardButton('🪙TRX(Tron)', callback_data=f'trx_withdraw_method')).row(InlineKeyboardButton('🤖 BitPapa', callback_data=f'bitpapa_withdraw_method'), InlineKeyboardButton('🤖CryptoBot', callback_data=f'cryptobot_withdraw_method'), InlineKeyboardButton('🤖BTCBanker', callback_data=f'banker_withdraw_method'))
withdraw_return_kb_inline = InlineKeyboardMarkup().add(InlineKeyboardButton('🔙В меню', callback_data='return_wallet'))
withdraw_error_message = 'В соответствии с пунктом 3\.2 [пользовательского соглашения]({link_soglash}) для вывода *вам нужно отыграть еще {}*💲'
withdraw_address_message = '*Введите реквизиты\(адрес/номер кошелька\) куда нам произвести выплату\.*'
withdraw_value_message = '*Введите сумму вывода\.*'
withdraw_end_message = f'✅ *Заявка принята в обработку\.\nОбычно исполнение запроса занимает до 30 минут\.*\n🌒 В ночное время запросы не обрабатываются\. Если возникнет потребность в *отмене* заявки \- вы можете обратиться в [службу поддержки]({link_support})\.'

start_chat_message = '💸Добро пожаловать в GAS\n*Ваш профиль записан в базу бота*\.\nДля доступа к функционалу бота *требуется* [авторизоваться]({link_bot})'

request_withdraw_post = '⭕️Заявка на вывод:\n*Кто:* `{}`   `{}`\n*Сумма:* `{}$`\n*Тип:* `{}`\n*Адрес:* `{}`\n*Последний депозит:* `{}`$\n*Остаток на балансе:* `{}$`\n*Сколько он выиграл у казино, чем число меньше, тем для нас лучше:* `{}$`'
qiwi_notwork_message = '⭕️⭕️⭕️⭕️⭕️⭕️⭕️⭕️\n *Киви не ворк*\n_требуется проверить кошелёк_\n⭕️⭕️⭕️⭕️⭕️⭕️⭕️⭕️\n'


admin_message1 = '''Таблицы:
{}'''
admin_message2 = '''Команды: 
`/add` \[user\_id\] \[сумма\] \- пополнение баланса\(с уведомлением\)
`/sub` \[user\_id\] \[сумма\] \- уборка баланса\(без уведомления\)
`/info` \[название таблицы\] \- вывод списка столбцов таблицы
`/blacklist` \[user\_id\]  \- занесение в ЧС
`/request` \[запрос sql\] \- запрос к БД
`/balanceqiwi` \- баланс киви
`/statistics` \- статистика
`/krik admin` \- чекнуть сообщение для рассылки
`/krik users` \- запустить рассылку
`/partners` \- партнеры
`/partner` \[имя партнера\] \- ЛК партнера
Добавление партнера `/request INSERT INTO partners\(user\_id, name, comment, link, chat\_id\) VALUES\(10000000, 'XBET', 'For admins', 'google\.com', \-18615354\);`
'''

statistics_message = '''Статистика:
Сумма депозитов: \+{}$/{}$
Колво депозитов: \+{}/{}
Игроков: \+{}/{}
Колво 21 игр: \+{}/{}
Сумма ставок 21: \+{}/{}$
Колво соло: \+{}/{}
Сумма ставок соло: \+{}/{}$
Колво мульти: \+{}/{}
Сумма ставок мульти\(сумма банков\): \+{}/{}$
Комисия\(сумма 21 и мульти \* 0\.07\): \+{}/{}$
'''


rb_message = '''♠️*RB*♥️         \#RB{}
💵   *{}*💲

🥃 *Игроки:*
{}

{}'''




reklama_message = '✅*Вам начислен приветственный бонус в размере 20💲🍾*\n🍀 Удачной игры\!'


coming_soon_message = '''⚙️*В Покере ведутся технические работы до 17 января включительно\.*\nВход в игру недоступен\.\n\nВернемся к вам с улучшенной, удобной системой торгов, интуитивно понятным интерфейсом и любовью\.'''
