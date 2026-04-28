import telebot
import yt_dlp
import os
from keep_alive import keep_alive

# Токен берем из секретов Replit (Environment Variables)
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    print("❌ Ошибка: BOT_TOKEN не найден в секретах Replit!")
    exit(1)

bot = telebot.TeleBot(TOKEN)

# Папка для временных файлов
TEMP_FOLDER = "temp_downloads"

def download_mp3(url, chat_id):
    """Скачивает аудио из YouTube и возвращает путь к файлу и название"""
    os.makedirs(f"{TEMP_FOLDER}/{chat_id}", exist_ok=True)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{TEMP_FOLDER}/{chat_id}/%(title)s.%(ext)s',
        'quiet': False,  # Ставим False, чтобы видеть ошибки в логах Replit
        'noplaylist': True,
        'cookiefile': 'cookies.txt',  # Путь к файлу куков (если есть)
        'remotecomponents': 'ejs:npm',  # Решает проблему с JavaScript
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'audio')
            
            # Ищем скачанный MP3 файл
            for file in os.listdir(f'{TEMP_FOLDER}/{chat_id}'):
                if file.endswith('.mp3'):
                    return os.path.join(f'{TEMP_FOLDER}/{chat_id}', file), title
        
        return None, None
    except Exception as e:
        print(f"Ошибка скачивания: {e}")
        return None, None

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "🎵 Привет! Я скачиваю аудио из YouTube.\n\n"
        "📌 Просто отправь мне ссылку на видео\n"
        "🔄 Бот работает 24/7\n\n"
        "Пример ссылки:\n"
        "https://youtube.com/watch?v=dQw4w9WgXcQ"
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()
    
    # Проверка на ссылку YouTube
    if 'youtube.com' in url or 'youtu.be' in url:
        bot.reply_to(message, "🎵 Скачиваю и конвертирую... Подожди немного (до 1 минуты)")
        
        file_path, title = download_mp3(url, message.chat.id)
        
        if file_path and os.path.exists(file_path):
            try:
                # Отправляем аудио
                with open(file_path, 'rb') as audio:
                    bot.send_audio(
                        message.chat.id, 
                        audio, 
                        title=title,
                        caption="✅ Готово!"
                    )
                
                # Удаляем временные файлы
                os.remove(file_path)
                
                # Удаляем папку, если она пуста
                try:
                    os.rmdir(f"{TEMP_FOLDER}/{message.chat.id}")
                except:
                    pass
                    
                bot.send_message(message.chat.id, "✅ Аудио успешно загружено!")
                
            except Exception as e:
                bot.reply_to(message, f"❌ Ошибка при отправке: {str(e)[:100]}")
        else:
            bot.reply_to(message, 
                "❌ Не удалось скачать аудио.\n\n"
                "Возможные причины:\n"
                "1. YouTube блокирует этот запрос (нужны свежие cookies)\n"
                "2. Ссылка недействительна\n"
                "3. Видео недоступно в вашем регионе"
            )
    else:
        bot.reply_to(message, 
            "❌ Отправь ссылку на YouTube видео\n\n"
            "Пример: https://youtube.com/watch?v=dQw4w9WgXcQ"
        )

# Запуск Flask-сервера для поддержания работы 24/7
keep_alive()

print("🚀 Бот запущен и работает 24/7!")
bot.infinity_polling()