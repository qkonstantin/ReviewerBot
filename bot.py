import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gpt import GPT
from parser_ozon import FeedbackParserOZN
from parser_wb import FeedbackParserWB

TOKEN = "6266404942:AAFKyd6fYXjmbiwrBLLN3sYBN6-B9NpiBUI"

form_router = Router()


class States(StatesGroup):
    ask_link = State()
    process_link = State()
    ask_for_another_link = State()
    ask_link_again = State()
    answer = State()


@form_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(States.ask_link)
    builder = InlineKeyboardBuilder()
    builder.button(text=f'Отлично, давай!', callback_data='yes')
    builder.button(text=f'Нет, спасибо', callback_data='no')
    await message.answer("Привет, я помогу тебе в анализе отзывов на любой товар с Wildberries или Озон!",
                         reply_markup=builder.as_markup())


@form_router.callback_query(States.ask_link, F.data == "yes")
async def ask_link(callback: CallbackQuery, state: FSMContext):
    await state.set_state(States.process_link)
    await callback.message.answer(
        "Отлично, тогда пришли мне ссылку на товар и я проанализирую все отзывы, которые оставили пользователи! ",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.callback_query(States.ask_link, F.data == "no")
async def ask_link(callback: CallbackQuery, state: FSMContext):
    await state.set_state(States.process_link)
    await callback.message.answer(
        "Извини, но пока я не обладаю большим функционалом, поэтому не могу тебе помочь с чем-нибудь ещё. Если понадоблюсь понадобится анализ отзывов - дай знать, я рядом!",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(States.process_link)
async def process_link(message: Message, state: FSMContext):
    await state.set_state(States.ask_for_another_link)
    text = ''
    url = message.text

    progress_message = await message.answer("Анализирую отзывы: 0% [          ]")

    # Отображаем 50% перед обработкой данных
    for i in range(1, 3):
        await asyncio.sleep(1)
        percentage = i * 10
        progress = "[" + "█" * i + " " * (5 - i) + "]"
        await progress_message.edit_text(f"Анализирую отзывы: {percentage}% {progress}")

    if url.split('/')[2] == 'www.ozon.ru' or url.split('/')[2] == 'ozon.ru':
        extractor = FeedbackParserOZN(url)
        item_name = extractor.get_item_name()
        text = extractor.get_formatted_reviews()
        if not item_name or not text:
            await progress_message.edit_text("Не удалось получить все необходимые данные. Попробуйте еще раз.")
            return
    elif url.split('/')[2] == 'www.wildberries.ru':
        extractor = FeedbackParserWB(url)
        text = extractor.get_formatted_feedbacks()

    question_str = text
    logging.info(question_str)
    gpt_instance = GPT(question_str)

    # Отображаем ещё 50% после обработки данных
    for i in range(4, 11):
        await asyncio.sleep(4)
        percentage = i * 10
        progress = "[" + "█" * (i - 5) + " " * (5 - (i - 5)) + "]"
        await progress_message.edit_text(f"Анализирую отзывы: {percentage}% {progress}")

    result = await gpt_instance.ask_gpt_async()
    await progress_message.edit_text(str(result))  # Преобразуем результат в строку

    builder = InlineKeyboardBuilder()
    builder.button(text=f'Да, пожалуй', callback_data='да')
    builder.button(text=f'Нет, спасибо!', callback_data='нет')
    await message.answer("Я могу провести анализ ещё одного товара, если хочешь?", reply_markup=builder.as_markup())


@form_router.callback_query(States.ask_for_another_link, F.data == "да")
async def process_another_link(callback: CallbackQuery, state: FSMContext):
    await state.set_state(States.process_link)
    await callback.message.answer(
        "Отлично. Тогда я жду ссылку! ",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(States.process_link)


@form_router.callback_query(States.ask_for_another_link, F.data == "нет")
async def process_another_link(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await callback.message.answer(
        "До новых встреч!",
        reply_markup=ReplyKeyboardRemove(),
    )


async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(form_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
