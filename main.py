import telebot
import yt_dlp
import os
import re
from flask import Flask
from threading import Thread

# Токен бота (обязательно добавь в Secrets Replit: BOT_TOKEN)
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    print("❌ Ошибка: добавь BOT_TOKEN в Secrets Replit!")
    exit(1)

bot = telebot.TeleBot(TOKEN)

# Папка для временных файлов
TEMP_FOLDER = "temp"

def download_mp3(url, chat_id):
    """Скачивает аудио из YouTube и возвращает путь к файлу"""
    os.makedirs(f"{TEMP_FOLDER}/{chat_id}", exist_ok=True)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{TEMP_FOLDER}/{chat_id}/%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'audio')
            
            for f in os.listdir(f'{TEMP_FOLDER}/{chat_id}'):
                if f.endswith('.mp3'):
                    return os.path.join(f'{TEMP_FOLDER}/{chat_id}', f), title
        
        return None, None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None, None

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "🎵 Привет! Я бот для скачивания аудио из YouTube.\n\n"
        "📌 Просто отправь мне ссылку на видео\n"
        "🎶 Я пришлю тебе MP3 файл!"
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    
    # Проверяем, что это ссылка YouTube
    if 'youtube.com' in url or 'youtu.be' in url:
        bot.reply_to(message, "🎵 Скачиваю и конвертирую... Подожди немного")
        
        file_path, title = download_mp3(url, message.chat.id)
        
        if file_path:
            with open(file_path, 'rb') as audio:
                bot.send_audio(message.chat.id, audio, title=title)
            
            # Удаляем временный файл
            os.remove(file_path)
            try:
                os.rmdir(f"{TEMP_FOLDER}/{message.chat.id}")
            except:
                pass
                
            bot.send_message(message.chat.id, "✅ Готово!")
        else:
            bot.reply_to(message, "❌ Ошибка при скачивании. Проверь ссылку.")
    else:
        bot.reply_to(message, "❌ Отправь ссылку на YouTube видео")

# Flask-сервер для поддержания работы 24/7
app = Flask('')

@app.route('/')
def home():
    return "🤖 Бот работает 24/7!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("✅ Flask-сервер запущен на порту 8080")

# Запускаем сервер для UptimeRobot
keep_alive()

print("🚀 Бот запущен!")
bot.infinity_polling()