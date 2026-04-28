from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "🤖 Бот работает 24/7! Статус: активен"

@app.route('/health')
def health():
    return "OK", 200

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Запускает Flask-сервер в отдельном потоке"""
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("✅ Flask-сервер для UptimeRobot запущен на порту 8080")