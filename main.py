import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = ''

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Определение состояний
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


# Создание клавиатуры
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button_calculate = KeyboardButton("Рассчитать")
button_info = KeyboardButton("Информация")
keyboard.add(button_calculate, button_info)


# Функция для начала работы с ботом
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("Выберите опцию:", reply_markup=keyboard)


# Измененный обработчик для нажатия кнопки "Рассчитать"
@dp.message_handler(lambda message: message.text == 'Рассчитать')
async def set_age(message: types.Message):
    await UserState.age.set()  # Устанавливаем состояние age
    await message.answer("Введите свой возраст:")


# Функция для установки роста
@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)  # Сохраняем возраст
    await UserState.growth.set()  # Устанавливаем состояние growth
    await message.answer("Введите свой рост:")


# Функция для установки веса
@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)  # Сохраняем рост
    await UserState.weight.set()  # Устанавливаем состояние weight
    await message.answer("Введите свой вес:")


# Обработчик всех текстовых сообщений
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def all_messages(message: types.Message):
    await message.reply("Вы написали: " + message.text)


# Функция для расчета нормы калорий
@dp.message_handler(state=UserState.weight)

async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)  # Сохраняем вес
    data = await state.get_data()  # Получаем все данные

    # Формула для расчета калорий (пример для мужчин)
    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])

    calories = 10 * weight + 6.25 * growth - 5 * age + 5  # Формула для мужчин

    await message.answer(f"Ваша норма калорий: {calories} ккал.")
    await state.finish()  # Завершаем состояние


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
