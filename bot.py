import asyncio
import logging
import time
import ipaddress

from config_reader import config
from aiogram import Bot, Dispatcher, types, html, F
from aiogram.filters.command import Command, CommandObject
from aiogram.types import Message

from yeelight import Bulb

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value())

dp = Dispatcher()

# ip
strIP = ""

# yeelight
YeelightConnect = None


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if not check_ip(''):
        help_command = html.underline(f"/ip 127.0.0.1")
        await message.answer(f"Укажите ip\n\n{help_command}", parse_mode="HTML")

        return

    await render_button(message)


@dp.message(F.text.lower() == "включить")
@dp.message(F.text.lower() == "выключить")
async def bulb_turn(message: types.Message):
    global YeelightConnect
    try:
        if YeelightConnect is None:
            raise Exception("сначала укажите ip")

        if message.text.lower() == "включить":
            YeelightConnect.turn_on()
        else:
            YeelightConnect.turn_off()

    except Exception as err:
        await message.answer(
            "❌ Ошибка: " + str(err)
        )


@dp.message(Command("ip"))
async def input_ip(
        message: Message,
        command: CommandObject
):
    global strIP, YeelightConnect

    if not check_ip(command.args):
        await message.answer(
            "Ошибка: ip некорректный"
        )
        return

    await message.answer(
        "✅ IP сохранен"
    )

    try:
        YeelightConnect = Bulb(strIP)

        YeelightConnect.toggle()

        time.sleep(1)

        YeelightConnect.toggle()

        await message.answer(
            "✅ Подключение выполнено"
        )

        await render_button(message)

    except Exception as err:
        await message.answer(
            "❌ Ошибка: " + str(err)
        )


async def render_button(message):
    kb = [
        [
            types.KeyboardButton(text="Включить"),
            types.KeyboardButton(text="Выключить")
        ],
    ]

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Лампочка.."
    )

    await message.answer("Действие:", reply_markup=keyboard)


def check_ip(ip):
    global strIP
    try:
        if ip:
            strIP = ip

        ipaddress.ip_address(strIP)
        return True
    except ValueError:
        return False


# start
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
