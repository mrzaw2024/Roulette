import os
import logging
import asyncio
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.constants import ParseMode
import google.generativeai as genai
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# API Keys
TELEGRAM_BOT_TOKEN = "8790341850:AAEo8qaWU4r9r3W_m-w7sR7-wZTRP0HFl8E"
GEMINI_API_KEY = "AIzaSyDbFFCziL6pDXkRp9x9A4-u-l0yQJvrqNs"

bot = Bot(TELEGRAM_BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def async_route(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(f(*args, **kwargs))
        loop.close()
        return result
    return wrapped

def generate_story(topic):
    try:
        prompt = f"""Write a beautiful Burmese story of 3000-3500 words about: {topic}
The story must have introduction, development, climax and conclusion."""
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

@app.route('/')
def home():
    return 'Bot is running!'

@app.route('/webhook', methods=['POST'])
@async_route
async def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), bot)
        
        if update.message and update.message.text:
            chat_id = update.message.chat_id
            text = update.message.text
            
            if text == '/start':
                await bot.send_message(chat_id=chat_id, text="ဂျပုလား။ ဝတ္ထုခေါင်းစဉ်ပေးပါ။")
            else:
                await bot.send_message(chat_id=chat_id, text="ဝတ္ထုရေးနေပါပြီ...")
                story = generate_story(text)
                
                if len(story) > 4096:
                    for i in range(0, len(story), 4000):
                        await bot.send_message(chat_id=chat_id, text=story[i:i+4000])
                else:
                    await bot.send_message(chat_id=chat_id, text=story)
        
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'status': 'error'}), 500

if __name__ == '__main__':
    app.run(debug=True)