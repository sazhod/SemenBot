# Created by Sazhod at 23.06.2022
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

import csv

from config import *
from product import getData, ProductCategorySpecification, BetterFilter


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
path = PATH

products = list()
brands = list()
statuses = list()
categories = list()


# region Описание команд бота
commandsDescription = {
    START: "начать общение с ботом",
    CATEGORIES: "вывести список категорий",
    'help': "вывести список команд"
}
# endregion


# region Обработка команды /start
@dp.message_handler(commands=[START])
async def process_start_command(msg: types.Message):

    categoryButton = KeyboardButton(CATEGORIES_BUTTON)
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(categoryButton)

    await msg.reply("Для просмотра списка категорий нажмите кнопку 'Категории' или отправьте /categories\n"
                    "Для просмотра списка команд отправьте /help", reply_markup=markup)
# endregion


# region Обработка команды /help
@dp.message_handler(commands=['help'])
async def process_help_command(msg: types.Message):
    helpMessage = str()
    for command, decriptionText in commandsDescription.items():
        helpMessage += f"/{command} - {decriptionText}\n"
    await msg.reply(helpMessage)
# endregion


# region Обработка команд /categories и Категории
@dp.message_handler(commands=[CATEGORIES])
async def process_categories_command(msg: types.Message):
    await process_categories(msg)


@dp.message_handler(lambda message: message.text and CATEGORIES_BUTTON == message.text)
async def process_categories_command(msg: types.Message):
    await process_categories(msg)


async def process_categories(msg):
    message = "Мне удалось найти для Вас следующие категории:"

    categoryButtons = InlineKeyboardMarkup()

    for i, category in enumerate(categories):
        categoryButton = InlineKeyboardButton(category.name, callback_data=f'{CATEGORIES}_{i}')
        categoryButtons.add(categoryButton)
    await msg.reply(message, reply_markup=categoryButtons)
# endregion


# region Вывод списка товаров по выбранной категории
@dp.callback_query_handler(lambda c: c.data and c.data.startswith(f'{CATEGORIES}_'))
async def process_callback_categories_button(callback_query: types.CallbackQuery):
    """
    Отправка кнопок с товарами по выбранной категории
    :param callback_query:
    :return:
    """
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id, text="Загружаем товары...")

    message = "Мне удалось найти для Вас следующие товары:"
    await bot.send_message(callback_query.from_user.id, message)

    categoryIndex = int(callback_query.data.split('_')[1])

    currentCategorySpec = ProductCategorySpecification(categories[categoryIndex])
    bf = BetterFilter()

    productsPage = 1
    productButtons = InlineKeyboardMarkup()

    for i, product in bf.filter(products, currentCategorySpec):
        productButton = InlineKeyboardButton(product.name, callback_data=f'{PRODUCTS}_{i}')
        productButtons.add(productButton)
        if i % 10 == 0:
            await bot.send_message(callback_query.from_user.id, f"Страница товаров №{productsPage}",
                                   reply_markup=productButtons)
            productButtons.clean()
            productsPage += 1
# endregion


# region Вывод данных о выбранном товаре
@dp.callback_query_handler(lambda c: c.data and c.data.startswith(f'{PRODUCTS}_'))
async def process_callback_products_button(callback_query: types.CallbackQuery):

    productIndex = int(callback_query.data.split('_')[1])
    product = products[productIndex]
    await bot.send_message(callback_query.from_user.id, product)
# endregion


# region Обработка нераспознанных команд
@dp.message_handler()
async def echo_message(msg: types.Message):
    message = "Команда не распознана"
    await msg.reply(message)
# endregion


# region Выгрузка данных
def parsingData():
    global products, brands, statuses, categories
    data = getData(path)
    products = data[PRODUCTS]
    brands = data['brands']
    statuses = data['statuses']
    categories = data[CATEGORIES]
# endregion


def main():
    parsingData()
    executor.start_polling(dp)


if __name__ == '__main__':
    main()
