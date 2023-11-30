import asyncio
import logging

from aiogram import Bot, Dispatcher, types

TOKEN = "YOUR_BOT_TOKEN"


async def on_startup(dp):
    logging.warning(
        'Bot has been started'
    )


async def on_shutdown(dp):
    logging.warning(
        'Bot has been stopped'
    )


async def on_message(msg: types.Message):
    await msg.answer("Привет! Я готов отвечать на любые сообщения.")


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher(bot)

    dp.register_message_handler(on_message, content_types=types.ContentType.ANY)

    try:
        logging.info("Start polling")
        await dp.start_polling()
    finally:
        logging.info("Stop polling")
        await dp.storage.close()
        await dp.storage.wait_closed()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
