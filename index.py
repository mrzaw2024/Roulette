
import os
import logging
import json
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.constants import ParseMode
import google.generativeai as genai

# Configure logging
logging.basicConfig(
    format=\'%(asctime)s - %(name)s - %(levelname)s - %(message)s\',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Hardcoded API Keys and Tokens (for easier deployment as requested by user)
# IMPORTANT: For production environments, it's generally safer to use environment variables.
TELEGRAM_BOT_TOKEN = "8790341850:AAEo8qaWU4r9r3W_m-w7sR7-wZTRP0HFl8E"
GEMINI_API_KEY = "AIzaSyDbFFCziL6pDXkRp9x9A4-u-l0yQJvrqNs"

if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN is missing. Please provide it.")
    # In a real deployment, you might want to raise an exception or handle this more gracefully
    # For Vercel, it\'s crucial these are set in the project settings.
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY is missing. Please provide it.")

# Initialize Telegram Bot and Gemini API
bot = Bot(TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(\'gemini-pro\')

async def generate_story_async(topic: str) -> str:
    """Asynchronously generate a story using Gemini API."""
    try:
        prompt = f"""You are a creative story writer. Write a beautiful, emotionally resonant Burmese story of 3000-3500 words based on the following topic. The story should have a clear introduction, development, climax, and conclusion. Ensure the language is natural and engaging. \n\nTopic: {topic}"""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error generating story with Gemini: {e}")
        return f"An error occurred while generating the story: {e}"

@app.route(\'/\')
def home():
    return \'Myanmar Story Generator Bot is running!\'

@app.route(\'/webhook\', methods=[\'POST\'])
async def webhook():
    if request.method == "POST":
        update_json = request.get_json(force=True)
        update = Update.de_json(update_json, bot)

        if update.message and update.message.text:
            chat_id = update.message.chat_id
            user_message = update.message.text

            if user_message == \'/start\':
                await bot.send_message(chat_id=chat_id, text="Hi! I\'m a story generator bot. Send me a topic and I\'ll craft a story for you.")
            elif user_message == \'/help\':
                await bot.send_message(chat_id=chat_id, text="Just send me a topic and I will generate a story for you!")
            else:
                await bot.send_message(chat_id=chat_id, text="Generating your story... This might take a moment.")
                story = await generate_story_async(user_message)
                
                if story:
                    # Telegram message limit is 4096 characters. Split if necessary.
                    if len(story) > 4096:
                        chunks = [story[i:i+4000] for i in range(0, len(story), 4000)] # Leave some buffer
                        for i, chunk in enumerate(chunks):
                            await bot.send_message(chat_id=chat_id, text=f"Part {i+1}/{len(chunks)}:\n{chunk}", parse_mode=ParseMode.MARKDOWN)
                    else:
                        await bot.send_message(chat_id=chat_id, text=story, parse_mode=ParseMode.MARKDOWN)
                else:
                    await bot.send_message(chat_id=chat_id, text="Sorry, I couldn\'t generate a story for that topic. Please try another one.")
        return jsonify({\'status\': \'ok\'}) 
    return jsonify({\'status\': \'error\', \'message\': \'Method not allowed\'}), 405

if __name__ == \'__main__\':
    app.run(debug=True)
