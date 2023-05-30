import asyncio
import requests
import re
import time
import threading
import sql
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


from telethon import TelegramClient, events


### CONSTANTS
bots_id = {
    '@CryptoBot':1559501630,
    '@btc_change_bot':159405177,
    '@tether_change_bot':661733274,
    '@doge_change_bot':187146480,
    '@bcc_change_bot':587644817,
    '@dash_change_bot':483240832,
    '@ltc_change_bot':192615197,
    '@eth_change_bot':186937468,
    '@bitpapa_bot':705240261,

}


def activate_gift(bot, user_id, gift):
    asyncio.set_event_loop(asyncio.new_event_loop())

    api_id = "29022839"
    api_hash = "765257eab8073284a8c7d770640d5aba"
    client = TelegramClient(session="TGSession", api_id=api_id, api_hash=api_hash, app_version="version 0.0.1", device_model="Phone", system_version="Android X")
    try:
        bot = '@'+gift[len(gift) - gift[::-1].index('/'):gift.index('?')]
        gift = gift[gift.index('=')+1:]
        with client:
            client.loop.create_task(client.send_message(bot, f"/start {gift}"))
            @client.on(events.NewMessage())
            async def handler(event):
                message_text = event.message.text
                chat_id = event.chat_id
                if chat_id == bots_id[bot]: 
                    if ("Вы получили" in message_text or "Получение" in message_text):
                        print(1)
                        validate_deposit_data(message_text, bot, gift, user_id, 0)
                        await client.disconnect()
                    elif "Упс" in message_text:
                        validate_deposit_data(message_text, bot, gift, user_id, -1)
                        await client.disconnect()  
            client.run_until_disconnected()
        return True
    except:
        print('55 ERROR crypto.py')


def validate_deposit_data(message_text, bot, gift, user_id, status):
    if ((status==-1) or (status==-2)):
       add_active_deposit(bot, gift, user_id, 'None', 0.0, 0.0, status)
    btc_data = re.findall("\d+.\d+ BTC", message_text)
    if not btc_data:
        btc_data = re.findall("\d+ BTC", message_text)
    eth_data = re.findall("\d+.\d+ ETH", message_text)
    if not eth_data:
        eth_data = re.findall("\d+ ETH", message_text)
    trx_data = re.findall("\d+.\d+ TRX", message_text)
    if not trx_data:
        trx_data = re.findall("\d+ TRX", message_text)
    ltc_data = re.findall("\d+.\d+ LTC", message_text)
    if not ltc_data:
        ltc_data = re.findall("\d+ LTC", message_text)
    dash_data = re.findall("\d+.\d+ DASH", message_text)
    if not dash_data:
        dash_data = re.findall("\d+ DASH", message_text)
    bch_data = re.findall("\d+.\d+ BCH", message_text)
    if not bch_data:
        bch_data = re.findall("\d+ BCH", message_text)
    doge_data = re.findall("\d+.\d+ DOGE", message_text)
    if not doge_data:
        doge_data = re.findall("\d+ DOGE", message_text)
    bnb_data = re.findall("\d+.\d+ BNB", message_text)
    if not bnb_data:
        bnb_data = re.findall("\d+ BNB", message_text)
    xmr_data = re.findall("\d+.\d+ XMR", message_text)
    if not xmr_data:
        xmr_data = re.findall("\d+ XMR", message_text)
    ton_data = re.findall("\d+.\d+ TON", message_text)
    if not ton_data:
        ton_data = re.findall("\d+ TON", message_text)
    print(ton_data)
    usd_data = re.findall("\d+.\d+ USD", message_text)
    if not usd_data:
        usd_data = re.findall("\d+ USD", message_text)
    busd_data = re.findall("\d+.\d+ BUSD", message_text)
    if not busd_data:
        busd_data = re.findall("\d+ BUSD", message_text)
    if btc_data:
        btc_amount = float(btc_data[0][:-4])
        usd_amount = float(int(100 * btc_amount * get_curs_BTC_USD()) / 100)
        add_active_deposit(bot, gift, user_id, 'BTC',btc_amount, usd_amount, status)
    elif eth_data:
        eth_amount = float(eth_data[0][:-4])
        usd_amount = float(int(100 * eth_amount * get_curs_ETH_USD()) / 100)
        add_active_deposit(bot, gift, user_id, 'ETH',eth_amount, usd_amount, status)
    elif trx_data:
        trx_amount = float(trx_data[0][:-4])
        usd_amount = float(int(100 * trx_amount * get_curs_TRX_USD()) / 100)
        add_active_deposit(bot, gift, user_id, 'TRX',trx_amount, usd_amount, status)
    elif ltc_data:
        ltc_amount = float(ltc_data[0][:-4])
        usd_amount = float(int(100 * ltc_amount * get_curs_LTC_USD()) / 100)
        add_active_deposit(bot, gift, user_id, 'LTC',ltc_amount, usd_amount, status)
    elif dash_data:
        dash_amount = float(dash_data[0][:-4])
        usd_amount = float(int(100 * dash_amount * get_curs_DASH_USD()) / 100)
        add_active_deposit(bot, gift, user_id, 'DASH',dash_amount, usd_amount, status)
    elif bch_data:
        bch_amount = float(bch_data[0][:-4])
        usd_amount = float(int(100 * bch_amount * get_curs_BCH_USD()) / 100)
        add_active_deposit(bot, gift, user_id, 'BCH',bch_amount, usd_amount, status)
    elif doge_data:
        doge_amount = float(doge_data[0][:-4])
        usd_amount = float(int(100 * doge_amount * get_curs_DOGE_USD()) / 100)
        add_active_deposit(bot, gift, user_id, 'DOGE',doge_amount, usd_amount, status)
    elif bnb_data:
        bnb_amount = float(bnb_data[0][:-4])
        usd_amount = float(int(100 * bnb_amount * get_curs_BNB_USD()) / 100)
        add_active_deposit(bot, gift, user_id, 'BNB',bnb_amount, usd_amount, status)
    elif xmr_data:
        xmr_amount = float(xmr_data[0][:-4])
        usd_amount = float(int(100 * xmr_amount * get_curs_XMR_USD()) / 100)
        add_active_deposit(bot, gift, user_id, 'XMR',xmr_amount, usd_amount, status)
    elif ton_data:
        ton_amount = float(ton_data[0][:-4])
        usd_amount = float(int(100 * ton_amount * get_curs_TON_USD()) / 100)
        print(usd_amount)
        add_active_deposit(bot, gift, user_id, 'TON',ton_amount, usd_amount, status)
    elif busd_data:
        usd_amount = float(busd_data[0][:-4])
        add_active_deposit(bot, gift, user_id, 'BUSD',usd_amount, usd_amount, status)
    elif usd_data:
        usd_amount = float(usd_data[0][:-4])
        add_active_deposit(bot, gift, user_id, 'USD',usd_amount, usd_amount, status)


def add_active_deposit(bot, gift, user_id, moneta, value, usd, status):
    stri = "UPDATE active_deposits_bots SET value = "+str(value)+", moneta = '"+str(moneta)+"', usd = "+str(usd)+", status = "+str(status)+" WHERE user_id = "+str(user_id)+" AND status = 13;"
    sql.request_db_without_async(stri)


# Публичное API от https://coinremitter.com/api/v3/get-coin-rate
def get_curs_BTC_USD():
    return 0.97*float(requests.get("https://coinremitter.com/api/v3/get-coin-rate").json()["data"]["BTC"]["price"])
def get_curs_ETH_USD():
    return 0.97*float(requests.get("https://coinremitter.com/api/v3/get-coin-rate").json()["data"]["ETH"]["price"])
def get_curs_TRX_USD():
    return 0.97*float(requests.get("https://coinremitter.com/api/v3/get-coin-rate").json()["data"]["TRX"]["price"])
def get_curs_LTC_USD():
    return 0.97*float(requests.get("https://coinremitter.com/api/v3/get-coin-rate").json()["data"]["LTC"]["price"])
def get_curs_DASH_USD():
    return 0.97*float(requests.get("https://coinremitter.com/api/v3/get-coin-rate").json()["data"]["DASH"]["price"])
def get_curs_BCH_USD():
    return 0.97*float(requests.get("https://coinremitter.com/api/v3/get-coin-rate").json()["data"]["BCH"]["price"])
def get_curs_DOGE_USD():
    return 0.97*float(requests.get("https://coinremitter.com/api/v3/get-coin-rate").json()["data"]["DOGE"]["price"])
def get_curs_BNB_USD():
    return 0.97*float(requests.get("https://coinremitter.com/api/v3/get-coin-rate").json()["data"]["BNB"]["price"])
def get_curs_XMR_USD():
    return 0.97*float(requests.get("https://coinremitter.com/api/v3/get-coin-rate").json()["data"]["XMR"]["price"])
def get_curs_TON_USD():
    url = 'https://coinchefs.com/ton/usd/1/'
    ua = UserAgent()
    header = {'User-Agent':str(ua.chrome)}
    htmlContent = requests.get(url, headers=header)
    soup = BeautifulSoup(htmlContent.text, "html.parser")
    soup = soup.find('div', class_='col-xs-10 col-sm-10 text-center result-text').text
    return 0.97*float(re.search('\d+.\d+', soup).group(0))

async def get_curs_RUB_USD():
    url = 'https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/usd/rub.json'
    ua = UserAgent()
    header = {'User-Agent':str(ua.chrome)}
    htmlContent = requests.get(url, headers=header)
    htmlContent = htmlContent.json()
    return 1.03*float(htmlContent['rub'])

async def get_curs_EUR_USD():
    url = 'https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/usd/eur.json'
    ua = UserAgent()
    header = {'User-Agent':str(ua.chrome)}
    htmlContent = requests.get(url, headers=header)
    htmlContent = htmlContent.json()
    return 1.03*float(htmlContent['eur'])

async def get_curs_KZT_USD():
    url = 'https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/usd/kzt.json'
    ua = UserAgent()
    header = {'User-Agent':str(ua.chrome)}
    htmlContent = requests.get(url, headers=header)
    htmlContent = htmlContent.json()
    return 1.03*float(htmlContent['kzt'])

async def get_curs_UAH_USD():
    url = 'https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/usd/uah.json'
    ua = UserAgent()
    header = {'User-Agent':str(ua.chrome)}
    htmlContent = requests.get(url, headers=header)
    htmlContent = htmlContent.json()
    return 1.03*float(htmlContent['uah'])
