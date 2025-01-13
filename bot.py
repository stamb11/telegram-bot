from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import hashlib

API_TOKEN = "7649330488:AAG1O2nA-U2W897oWpSs0b3hTDqlrK5h7OI"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Словарь для хранения состояния пользователей и хэшей фотографий
user_states = {}
photo_hashes = set()

# Клавиатура с кнопкой "Готов работать"
ready_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Готов работать")]
    ],
    resize_keyboard=True
)

# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_states:
        user_states[user_id] = {"ready_to_work": False, "screenshot_count": 0}
    await message.answer("🔵 Нажмите 'Готов работать', чтобы начать отправлять скриншоты.", reply_markup=ready_keyboard)

# Обработчик кнопки "Готов работать"
@dp.message(lambda message: message.text and message.text.strip() == "✅ Готов работать")
async def ready_to_work(message: types.Message):
    user_id = message.from_user.id
    user_states[user_id]["ready_to_work"] = True
    user_states[user_id]["screenshot_count"] = 0  # Сбрасываем счетчик скриншотов при новом начале
    await message.answer("✅ Можете отправлять скриншоты. После каждого скриншота я проверю его уникальность и посчитаю!")

# Обработчик скриншотов
@dp.message(lambda message: message.photo)
async def handle_screenshots(message: types.Message):
    user_id = message.from_user.id
    if not user_states.get(user_id, {}).get("ready_to_work", False):
        await message.answer("🔴 Вы ещё не готовы работать. Пожалуйста, нажмите 'Готов работать'.")
        return

    # Получаем файл
    photo = message.photo[-1]  # Берём фото с максимальным размером
    file = await bot.get_file(photo.file_id)
    file_path = file.file_path

    # Скачиваем файл
    file_data = await bot.download_file(file_path)

    # Вычисляем хэш файла
    photo_hash = hashlib.md5(file_data.read()).hexdigest()

    # Проверяем на уникальность
    if photo_hash in photo_hashes:
        await message.answer("❌ Этот скриншот уже был отправлен. Отправьте другой.")
    else:
        # Добавляем хэш в общий набор
        photo_hashes.add(photo_hash)

        # Увеличиваем счетчик уникальных скриншотов для пользователя
        user_states[user_id]["screenshot_count"] += 1
        count = user_states[user_id]["screenshot_count"]

        await message.answer(f"📸 Скриншот засчитан! Вы отправили уже {count} скриншет(ов). Продолжайте!")

# Обработчик других сообщений
@dp.message(lambda message: not message.photo)
async def handle_other_messages(message: types.Message):
    user_id = message.from_user.id
    if user_states.get(user_id, {}).get("ready_to_work", False):
        await message.answer("❌ Вы можете отправлять только скриншоты!")
    else:
        await message.answer("🔴 Вы ещё не готовы работать. Пожалуйста, нажмите 'Готов работать'.")

if __name__ == "__main__":
    dp.run_polling(bot)
