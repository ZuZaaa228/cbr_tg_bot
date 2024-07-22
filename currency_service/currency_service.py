import asyncio
import xml.etree.ElementTree as ET
import os
import aiohttp
import redis

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))

CBR_URL = 'https://www.cbr.ru/scripts/XML_daily.asp'


def parse_currency_rates(xml_content):
    tree = ET.ElementTree(ET.fromstring(xml_content))
    root = tree.getroot()
    rates = {}
    for currency in root.findall('Valute'):
        char_code = currency.find('CharCode').text
        value = float(currency.find('Value').text.replace(',', '.'))
        nominal = int(currency.find('Nominal').text)
        rates[char_code] = value / nominal
    return rates


async def fetch_currency_rates():
    async with aiohttp.ClientSession() as session:
        async with session.get(CBR_URL) as response:
            if response.status == 200:
                return await response.text()


async def update_currency_rates():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.set("RUB", 1)
    while True:
        xml_content = await fetch_currency_rates()
        if xml_content:
            rates = parse_currency_rates(xml_content)
            for char_code, rate in rates.items():
                r.set(char_code, rate)
        await asyncio.sleep(86400)


if __name__ == '__main__':
    asyncio.run(update_currency_rates())
