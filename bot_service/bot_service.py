import os

import redis
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@dp.message(Command(commands=['exchange']))
async def exchange(message: Message):
    try:
        _, from_currency, to_currency, amount = message.text.split()
        amount = float(amount)
        from_rate = r.get(from_currency)
        to_rate = r.get(to_currency)

        if from_rate is None:
            await message.answer(f"Валюта {from_currency} не найдена.")
            return
        if to_rate is None:
            await message.answer(f"Валюта {to_currency} не найдена.")
            return

        from_rate = float(from_rate)
        to_rate = float(to_rate)
        converted_amount = (amount * from_rate) / to_rate
        await message.answer(f"{amount} {from_currency} = {converted_amount:.2f} {to_currency}")
    except Exception as e:
        await message.answer(f"Неверная команда. Пожалуйста, используйте формат: /exchange USD RUB 10")


@dp.message(Command(commands=['rates']))
async def rates(message: Message):
    keys = r.keys()
    rates = [f"{key}: {r.get(key)}" for key in keys]
    await message.answer("\n".join(rates))


if __name__ == '__main__':
    dp.run_polling(bot)
