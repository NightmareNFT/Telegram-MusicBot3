import telebot
import yt_dlp
import os
import uuid
import requests

# Токен от Telegram / BOT TOKEN TELEGRAM
TOKEN = "YOUR BOT TOKEN"
bot = telebot.TeleBot(TOKEN)

# Ключ YouTube API / YOUTUBE API KEY
API_KEY = "YOUR API KEY"


def youtube_search(query, max_results=1):
    """Поиск коротких видео на YouTube"""
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "videoDuration": "short",  # ✅ только до 4 минут
        "maxResults": max_results,
        "key": API_KEY
    }
    r = requests.get(url, params=params, timeout=15)  # ✅ 15 секунд на запрос
    r.raise_for_status()
    return r.json()


def download_audio(url, title="track"):
    """Скачать аудио напрямую (без ffmpeg)"""
    unique_id = str(uuid.uuid4())[:8]
    base_filename = f"{title}_{unique_id}"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': base_filename + ".%(ext)s",
        'quiet': True,
        'noplaylist': True,
        'socket_timeout': 30,  # ✅ ждём до 30 секунд
        'postprocessors': []   # ❌ без ffmpeg
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        downloaded_file = ydl.prepare_filename(info)

    return downloaded_file


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет, я помогу найти музыку на YouTube. Введи название!")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    try:
        response = youtube_search(message.text, max_results=1)

        if not response["items"]:
            bot.send_message(message.chat.id, "Ничего не нашёл 😔")
            return

        item = response["items"][0]
        video_id = item["id"]["videoId"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        title = item["snippet"]["title"]

        file = download_audio(video_url, "track")

        with open(file, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, title=title)

        os.remove(file)  # удаляем файл после отправки

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


if __name__ == "__main__":
    print("Готов искать музыку 🎵")
    bot.polling(none_stop=True)
