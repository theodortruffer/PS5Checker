import requests
import random
import configparser
import telegram_send
import sys
import os
import logging

dirname = os.path.dirname(__file__)
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

# ================= #
# PARSE CONFIG FILE #
# ================= #
parser = configparser.ConfigParser()
parser.read(os.path.join(dirname, 'config.ini'))
in_production = parser.getboolean("developer", "production")
force_notification = len(sys.argv) > 1 and sys.argv[1] == "--force-notification"

referers = [
    'http://www.bing.com/',
    'http://www.google.com/',
    'https://search.yahoo.com/',
    'http://www.baidu.com/',
    'https://duckduckgo.com/'
]

with open(os.path.join(dirname, 'user-agents.txt')) as f:
    user_agents = f.read().splitlines()
    f.close()

locations = {
    'Mediamarkt': {
        'url': 'https://www.mediamarkt.ch/de/product/_sony-ps-playstation-5-digital-edition-2018097.html',
        'inStockLabel': "In den Warenkorb",
        'detectedAsBotLabel': "Das ging uns leider zu schnell"
    },
    'Fust': {
        'url': 'https://www.fust.ch/de/playstation-5-_content---1--1266--8055329.html',
        'outOfStockLabel': "Leider k&ouml;nnen wir aufgrund der sehr hohen Nachfrage nicht alle Bestellungen ber&uuml;cksichtigen.",
    },
    'Gamestop': {
        'url': 'https://www.gamestop.ch/PS5/Games/73794',
        'outOfStockLabel': '/Content/Images/deliveryUnavailable.png',
    },
    'World of Games': {
        'url': 'https://www.wog.ch/index.cfm/details/product/107285-PlayStation-5-Digital-Edition',
        'outOfStockLabel': 'derzeit nicht bestellbar'
    },
    'melectronics': {
        'url': 'https://www.melectronics.ch/de/p/785445800000/sony-playstation-5-digital-edition',
        'outOfStockLabel': 'Nicht lieferbar'
    },
    'Microspot': {
        'url': 'https://www.microspot.ch/de/cms/sony-playstation-5',
        'outOfStockLabel': 'PlayStation 5 ausverkauft'
    },
    'Interdiscount': {
        'url': 'https://www.interdiscount.ch/de/computer-gaming/gaming/spielkonsolen--c211000/sony-digital-edition-825-gb--p0002509351',
        'outOfStockLabel': 'Zur Zeit nicht lieferbar'
    }
}


def main():
    user_agent = random.choice(user_agents)
    referer = random.choice(referers)
    available = []
    not_available = []
    for place, info in locations.items():
        logging.info('checking ' + place)
        headers = {
            "User-Agent": user_agent,
            "Accept-Encoding": "gzip, deflate",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'en-US,en;q=0.9,de;q=0.88',
            'cache-control': 'no-cache',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': referer,
            "Connection": "close", "Upgrade-Insecure-Requests": "1"
        }
        try:
            content = requests.get(info.get('url'), timeout=10, headers=headers).content.decode('utf-8')
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout,
                requests.exceptions.ChunkedEncodingError) as e:
            logging.error("REQUEST ERROR: " + place)
            continue
        if 'detectedAsBotLabel' in info and info.get('detectedAsBotLabel') in content:
            logging.warning('detected as bot')
        elif ('outOfStockLabel' not in info or info.get('outOfStockLabel') not in content) \
                and ('inStockLabel' not in info or info.get('inStockLabel') in content):
            logging.info('AVAILABLE!')
            available.append(place + ": " + info.get('url'))
        else:
            logging.info('not available')
            not_available.append(place + ": " + info.get('url'))

    body = "Available at:\n" + "\n".join(available) + "\n\nNot Available:\n" + "\n".join(not_available)
    if len(available) > 0:
        body = "!!!PS5 AVAILABLE!!!\n\n" + body
        telegram_send.send(messages=[body], conf=os.path.join(dirname, 'telegram.conf'))
    elif not in_production or force_notification:
        body = "daily notification test\n\n" + body
        telegram_send.send(messages=[body], conf=os.path.join(dirname, 'telegram.conf'))


main()
