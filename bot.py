import os
import telebot
import threading
from flask import Flask
from dotenv import load_dotenv
from telebot import types

# Загружаем токен из .env (при локальном запуске)
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))

# Если ты запускаешь на Render, токен будет браться из переменных окружения Render
# (то есть из панели управления Render, а не из файла .env)
BOT_TOKEN = os.environ.get('BOT_TOKEN', BOT_TOKEN)
ADMIN_ID = int(os.environ.get('ADMIN_ID', ADMIN_ID))

bot = telebot.TeleBot(BOT_TOKEN)


# =====================================================================
# 1. Команда /start
# =====================================================================
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Услуги')
    btn2 = types.KeyboardButton('Цены')
    btn3 = types.KeyboardButton('Оставить заявку')
    markup.add(btn1, btn2, btn3)

    text = f'Здравствуйте, {message.from_user.first_name}!\nЯ бот-помощник. Выберите, что вас интересует:'
    bot.send_message(message.chat.id, text, reply_markup=markup)


# =====================================================================
# 2. Обработка кнопки "Услуги"
# =====================================================================
@bot.message_handler(func=lambda message: message.text == 'Услуги')
def show_services(message):
    bot.send_message(message.chat.id, '🛠 Мы делаем парсинг сайтов и пишем Telegram-ботов под заказ.')


# =====================================================================
# 3. Обработка кнопки "Цены"
# =====================================================================
@bot.message_handler(func=lambda message: message.text == 'Цены')
def show_prices(message):
    bot.send_message(message.chat.id, '💰 Парсинг: от 1000 руб.\n🤖 Бот: от 1500 руб.')


# =====================================================================
# 4. Обработка кнопки "Оставить заявку"
# =====================================================================
@bot.message_handler(func=lambda message: message.text == 'Оставить заявку')
def ask_for_request(message):
    msg = bot.send_message(message.chat.id, 'Напишите вашу задачу или телефон, и я передам это администратору.')
    bot.register_next_step_handler(msg, process_request)


# =====================================================================
# 5. Функция, которая принимает заявку и пересылает админу
# =====================================================================
def process_request(message):
    user_name = message.from_user.username
    text = message.text

    admin_text = f'🔥 НОВАЯ ЗАЯВКА!\nОт: @{user_name}\nТекст: {text}'

    bot.send_message(ADMIN_ID, admin_text)
    bot.send_message(message.chat.id, '✅ Спасибо! Ваша заявка отправлена. Мы скоро свяжемся.')


# =====================================================================
# ЗАГЛУШКА ДЛЯ RENDER (Чтобы сервер не засыпал)
# =====================================================================
app = Flask(__name__)


@app.route('/')
def index():
    return "Bot is running!"


def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)


# =====================================================================
# ЗАПУСК
# =====================================================================
if __name__ == '__main__':
    print('Бот запущен...')
    # Запускаем Flask в фоновом режиме
    threading.Thread(target=run_flask).start()

    # Запускаем бота
    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
        # Если бот упал, перезапускаем его через 5 секунд (полезно для Render)
        import time

        time.sleep(5)