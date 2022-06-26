# Created by Sazhod at 23.06.2022
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from enum import Enum

from config import *
from product import getData, ProductCategorySpecification, BetterFilter


class Page(Enum):
    Categories = 1
    CategoryProducts = 2
    Product = 3


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
path = PATH

products = list()
brands = list()
statuses = list()
categories = list()

categoryButton = KeyboardButton(CATEGORIES_BUTTON)
backButton = KeyboardButton(BACK_BUTTON)
categoryMarkup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(categoryButton).add(backButton)

allMessageIdDict = dict()

currentPage = Page.Categories
currentId = int()


# region Описание команд бота
commandsDescription = {
    START: "начать общение с ботом",
    CATEGORIES: "вывести список категорий",
    BACK: "вернутся назад(доступно при переходе из категорий в товары и тд.",
    HELP: "вывести список команд"
}


# endregion


# region Обработка команды /start
@dp.message_handler(commands=[START])
async def process_start_command(msg: types.Message):
    addChatIdInMessageDict(msg)
    await msg.reply(f"Для просмотра списка категорий нажмите кнопку '{CATEGORIES_BUTTON}' или отправьте /{CATEGORIES}\n"
                    f"Для просмотра списка команд отправьте /{HELP}", reply_markup=categoryMarkup)


# endregion


# region Обработка команды /help
@dp.message_handler(commands=[HELP])
async def process_help_command(msg: types.Message):
    addChatIdInMessageDict(msg)
    helpMessage = str()
    for command, decriptionText in commandsDescription.items():
        helpMessage += f"/{command} - {decriptionText}\n"
    await msg.reply(helpMessage, reply_markup=categoryMarkup)


# endregion


# region Обработка команд /categories и Категории
@dp.message_handler(commands=[CATEGORIES])
async def process_categories_command(msg: types.Message):
    await process_categories(msg)


@dp.message_handler(lambda message: message.text and CATEGORIES_BUTTON == message.text)
async def process_categories_command(msg: types.Message):
    await process_categories(msg)


async def process_categories(msg):
    global currentPage
    addChatIdInMessageDict(msg)
    currentPage = Page.Categories
    message = "Мне удалось найти для Вас следующие категории:"

    categoriesButtons = InlineKeyboardMarkup()

    for i, category in enumerate(categories):
        categoriesButton = InlineKeyboardButton(category.name, callback_data=f'{CATEGORIES}_{i}')
        categoriesButtons.add(categoriesButton)
    t = await msg.reply(message, reply_markup=categoriesButtons)
    allMessageIdDict[t.chat.id].append(t.message_id)


# endregion


# region Вывод списка товаров по выбранной категории
@dp.callback_query_handler(lambda c: c.data and c.data.startswith(f'{CATEGORIES}_'))
async def process_callback_categories_button(callback_query: types.CallbackQuery):
    await loadCategoryProducts(callback_query)


async def loadCategoryProducts(callback_query: types.CallbackQuery = None, msg=None):
    global currentPage, currentId
    currentPage = Page.CategoryProducts
    if callback_query:
        await deleteMessage(callback_query)
        await bot.answer_callback_query(callback_query.id, text="Загружаем товары...")
        chat_id = callback_query.from_user.id
        categoryIndex = int(callback_query.data.split('_')[1])
        currentId = categoryIndex
    else:
        await deleteMessage(msg)
        chat_id = msg.from_user.id
        categoryIndex = currentId

    message = "Мне удалось найти для Вас следующие товары:"
    t = await bot.send_message(chat_id, message)
    allMessageIdDict[t.chat.id].append(t.message_id)

    currentCategorySpec = ProductCategorySpecification(categories[categoryIndex])
    bf = BetterFilter()

    productsPage = 1
    productButtons = InlineKeyboardMarkup()

    for i, product in bf.filter(products, currentCategorySpec):
        productButton = InlineKeyboardButton(product.name, callback_data=f'{PRODUCTS}_{i}')
        productButtons.add(productButton)
        if i % 10 == 0:
            t = await bot.send_message(chat_id, f"Страница товаров №{productsPage}",
                                       reply_markup=productButtons)
            allMessageIdDict[t.chat.id].append(t.message_id)
            productButtons.clean()
            productsPage += 1


# endregion


# region Вывод данных о выбранном товаре
@dp.callback_query_handler(lambda p: p.data and p.data.startswith(f'{PRODUCTS}_'))
async def process_callback_products_button(callback_query: types.CallbackQuery):
    global currentPage
    currentPage = Page.Product
    await deleteMessage(callback_query)

    productIndex = int(callback_query.data.split('_')[1])
    product = products[productIndex]
    t = await bot.send_message(callback_query.from_user.id, product)
    allMessageIdDict[t.chat.id].append(t.message_id)


# endregion


# region Обработка команды /back и Назад
@dp.message_handler(lambda message: message.text and BACK_BUTTON == message.text)
async def echo_message(msg: types.Message):
    global currentPage

    await deleteMessage(msg)
    if currentPage == Page.Product:
        message = "Вы вернулись на страницу товаров"
        t = await msg.reply(message)
        allMessageIdDict[t.chat.id].append(t.message_id)
        await loadCategoryProducts(msg=msg)
    elif currentPage == Page.CategoryProducts:
        message = "Вы вернулись на страницу категорий"
        t = await msg.reply(message)
        allMessageIdDict[t.chat.id].append(t.message_id)
        await process_categories(msg=msg)
    else:
        message = "Вы долши до начала!"
        t = await msg.reply(message)
        allMessageIdDict[t.chat.id].append(t.message_id)


# endregion


# region Обработка нераспознанных команд
@dp.message_handler()
async def echo_message(msg: types.Message):
    message = "Команда не распознана"
    t = await msg.reply(message)
    allMessageIdDict[t.chat.id].append(t.message_id)


# endregion


# region Добавление нового id чата в общий словарь
def addChatIdInMessageDict(data):
    print(type(data))
    if type(data) == types.message.Message:
        if data.chat.id not in allMessageIdDict.keys():
            allMessageIdDict[data.chat.id] = list()


# endregion


# region Удаление всех имеющихся в словаре сообщений по chat_id
async def deleteMessage(data):
    if type(data) == types.message.Message:
        chat_id = data.chat.id
    else:
        chat_id = data.from_user.id
    try:
        messageIdList = allMessageIdDict[chat_id]
    except:
        allMessageIdDict[chat_id] = list()
    else:
        for i in range(messageIdList[0], messageIdList[len(messageIdList) - 1] + 1):
            print(i)
            await bot.delete_message(chat_id=chat_id, message_id=i)
        messageIdList.clear()


# endregion


# region Выгрузка данных
def parsingData():
    global products, brands, statuses, categories
    data = getData(path)
    products = data[PRODUCTS]
    brands = data[BRANDS]
    statuses = data[STATUSES]
    categories = data[CATEGORIES]


# endregion


def main():
    parsingData()
    executor.start_polling(dp)


if __name__ == '__main__':
    main()
