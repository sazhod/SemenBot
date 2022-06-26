# Created by Sazhod at 23.06.2022
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

import csv

from config import TOKEN, PATH, CATEGORIES, PRODUCTS
from product import getData


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
path = PATH

products = list()
brands = list()
statuses = list()
categories = list()

commandsDiscription = {
    'start': "начать общение с ботом",
    'categories': "вывести список категорий",
    'help': "вывести список команд"
}


@dp.message_handler(commands=['start'])
async def process_start_command(msg: types.Message):
    await msg.reply("Для просмотра списка категорий нажмите кнопку 'Категории' или отправьте /categories\n"
                    "Для просмотра списка команд отправьте /help")


@dp.message_handler(commands=['help'])
async def process_help_command(msg: types.Message):
    helpMessage = str()
    for command, decriptionText in commandsDiscription.items():
        helpMessage += f"/{command} - {decriptionText}\n"
    await msg.reply(helpMessage)


@dp.message_handler(commands=[CATEGORIES])
async def process_categories_command(msg: types.Message):
    message = "Мне удалось найти для Вас следующие категории:"

    categoryButtons = InlineKeyboardMarkup()

    for i, category in enumerate(categories):
        categoryButton = InlineKeyboardButton(category, callback_data=f'{CATEGORIES}_{i}')
        categoryButtons.add(categoryButton)
    await msg.reply(message, reply_markup=categoryButtons)


@dp.callback_query_handler()#func=lambda c: c.data and c.data.startswith(f'{CATEGORIES}_')
async def process_callback_categories_button(callback_query: types.CallbackQuery):

    await bot.answer_callback_query(callback_query.id, text="Загружаем товары...")

    message = "Мне удалось найти для Вас следующие товары:"
    await bot.send_message(callback_query.from_user.id, message)

    categoryIndex = int(callback_query.data.split('_')[1])
    productsPage = 1
    productButtons = InlineKeyboardMarkup()
    for i, product in enumerate(products):
        if product.category.name == categories[categoryIndex]:
            productButton = InlineKeyboardButton(product.name, callback_data=f'{PRODUCTS}_{i}')
            productButtons.add(productButton)
            if i % 10 == 0:
                await bot.send_message(callback_query.from_user.id, f"СТраница товаров №{productsPage}", reply_markup=productButtons)
                productButtons.clean()
                productsPage += 1


@dp.message_handler()
async def echo_message(msg: types.Message):
    message = "Команда не распознана"
    await msg.reply(message)


def parsingData():
    global products, brands, statuses, categories
    data = getData(path)
    products = data['products']
    brands = data['brands']
    statuses = data['statuses']
    categories = data[CATEGORIES]
    print(products, brands, statuses, categories)


def main():
    parsingData()
    # executor.start_polling(dp)


if __name__ == '__main__':
    main()
