import mysql.connector
from mysql.connector import Error


async def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        #print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def create_connection_without_async(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        #print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def request_db_without_async(query):
    connection = create_connection_without_async("address", "login", "password","NAME DB")
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        #print(f"{query} - SUCCESS")
        a = cursor.fetchall()
        cursor.close()
        connection.commit()
        return a
    except Error as e:
        print(f"The error '{e}' occurred in {query}")


async def request_db(query, key = 0):
    connection = await create_connection("address", "login", "password","NAME DB")
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        if(key == 1):
            print(f"{query} - SUCCESS")
        a = cursor.fetchall()
        cursor.close()
        connection.commit()
        return a
    except Error as e:
        print(f"The error '{e}' occurred in {query}")


def init_db():
    request_db_without_async('''CREATE TABLE IF NOT EXISTS users (user_id BIGINT UNSIGNED NOT NULL, username TEXT NOT NULL,firstname TEXT NOT NULL, balance DECIMAL(16, 8) NOT NULL DEFAULT 0.0, balance_ref DECIMAL(16, 8) NOT NULL DEFAULT 0.0, balance_solo DECIMAL(16, 8) NOT NULL DEFAULT 0.0, need_play_for_withdraw DECIMAL(16, 8) NOT NULL DEFAULT 0.0, address VARCHAR(100), status INT NOT NULL DEFAULT 0, count_games INT NOT NULL DEFAULT 0, count_prizes FLOAT NOT NULL DEFAULT 0.0, subscribe BOOLEAN NOT NULL DEFAULT 0, last_message_bot INT NOT NULL, playing_game_id_mini INT NOT NULL DEFAULT 0,playing_multigame_id INT NOT NULL DEFAULT 0, playing_game_id_21 INT NOT NULL DEFAULT 0, playing_rb_id INT NOT NULL DEFAULT 0, from_ref_id BIGINT UNSIGNED NOT NULL, dat DATE, UNIQUE (user_id)); ''')
    request_db_without_async('''CREATE TABLE  IF NOT EXISTS addresses (address VARCHAR(100) NOT NULL, type VARCHAR(5) NOT NULL, status BOOLEAN NOT NULL DEFAULT 0, value DECIMAL(16, 8) NOT NULL DEFAULT 0, date DATETIME NOT NULL DEFAULT NOW());''')
    request_db_without_async('''CREATE TABLE IF NOT EXISTS active_deposits_bots (bot TEXT NOT NULL, gift TEXT NOT NULL, user_id BIGINT UNSIGNED NOT NULL, moneta TEXT NOT NULL, value DECIMAL(16, 8) NOT NULL, usd FLOAT NOT NULL, date DATETIME NOT NULL, status SMALLINT NOT NULL DEFAULT 0);''')
    request_db_without_async('''CREATE TABLE IF NOT EXISTS games (id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, user_id BIGINT UNSIGNED NOT NULL, type TEXT NOT NULL, target_number INT NOT NULL DEFAULT 1, stavka FLOAT NOT NULL, date DATETIME NOT NULL, status INT NOT NULL DEFAULT 0, result FLOAT, result_point TINYINT DEFAULT 0);''')
    request_db_without_async('''CREATE TABLE IF NOT EXISTS multigames (id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, type TEXT NOT NULL, stavka FLOAT NOT NULL,players VARCHAR(100), list_id_game VARCHAR(100), date DATETIME NOT NULL, status INT NOT NULL DEFAULT 0, winners VARCHAR(100), message_id BIGINT NOT NULL, chat_id TEXT, password VARCHAR(20) DEFAULT '0');''')
    request_db_without_async('''CREATE TABLE IF NOT EXISTS blacklist (user_id BIGINT UNSIGNED NOT NULL, UNIQUE (user_id));''')
    request_db_without_async('''CREATE TABLE IF NOT EXISTS game_21 (id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, max_players TINYINT UNSIGNED, is_closed BOOLEAN NOT NULL DEFAULT 0, stavka FLOAT, cards_1 VARCHAR(60) NOT NULL DEFAULT '', cards_2 VARCHAR(60) NOT NULL DEFAULT '', cards_3 VARCHAR(60) NOT NULL DEFAULT '', cards_4 VARCHAR(60) NOT NULL DEFAULT '', cards_5 VARCHAR(60) NOT NULL DEFAULT '', cards_6 VARCHAR(60) NOT NULL DEFAULT '', password VARCHAR(20) DEFAULT '0',player_1 BIGINT UNSIGNED DEFAULT 0,player_2 BIGINT UNSIGNED DEFAULT 0,player_3 BIGINT UNSIGNED DEFAULT 0,player_4 BIGINT UNSIGNED DEFAULT 0,player_5 BIGINT UNSIGNED DEFAULT 0,player_6 BIGINT UNSIGNED DEFAULT 0, winner_1 BIGINT UNSIGNED, winner_2 BIGINT UNSIGNED, winner_3 BIGINT UNSIGNED, winner_4 BIGINT UNSIGNED, winner_5 BIGINT UNSIGNED, date DATETIME NOT NULL DEFAULT NOW());''')
    request_db_without_async('''CREATE TABLE IF NOT EXISTS rb_game (id INT AUTO_INCREMENT PRIMARY KEY, players TEXT, zagad TINYINT UNSIGNED, stavka FLOAT, message_id BIGINT NOT NULL, chat_id TEXT, date DATETIME NOT NULL DEFAULT NOW());''')
    request_db_without_async('''CREATE TABLE IF NOT EXISTS gifts (from_user_id BIGINT UNSIGNED NOT NULL, text VARCHAR(15) NOT NULL, value FLOAT NOT NULL, to_user_id BIGINT UNSIGNED NOT NULL, is_activated BOOLEAN NOT NULL DEFAULT 0);''')
    request_db_without_async('''CREATE TABLE IF NOT EXISTS mess_21_list (id_game INT UNSIGNED NOT NULL, from_user VARCHAR(50) NOT NULL, message VARCHAR(200) NOT NULL);''')
    request_db_without_async('''CREATE TABLE IF NOT EXISTS qiwi (number TEXT, token TEXT);''')
    request_db_without_async('''CREATE TABLE IF NOT EXISTS request_qiwi(user_id BIGINT UNSIGNED NOT NULL, comment TEXT, valuta VARCHAR(3) DEFAULT 'USD', amount FLOAT, amount_dollar FLOAT, data DATETIME NOT NULL DEFAULT NOW());''')
    request_db_without_async('''CREATE TABLE IF NOT EXISTS chats(chat_id TEXT, link TEXT, comment TEXT, last_allgames_message BIGINT NOT NULL DEFAULT 0);''')
    request_db_without_async('''CREATE TABLE IF NOT EXISTS partners(user_id BIGINT UNSIGNED NOT NULL, name TEXT, comment TEXT, link TEXT, chat_id TEXT);''')
    request_db_without_async('''CREATE TABLE IF NOT EXISTS withdraws(user_id BIGINT UNSIGNED NOT NULL, type TEXT, address TEXT, count FLOAT NOT NULL DEFAULT 0, status INT NOT NULL DEFAULT 0);''')
    request_db_without_async('''CREATE TABLE IF NOT EXISTS boards_poker_draw(id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, name TEXT, players TEXT, ante FLOAT, small_blind FLOAT, date DATETIME, status TINYINT, st_p TINYINT UNSIGNED, position TINYINT UNSIGNED, last_message TEXT, cards TEXT, koloda TEXT);''')
