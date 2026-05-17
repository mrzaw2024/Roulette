import logging
import requests
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = "8790341850:AAEo8qaWU4r9r3W_m-w7sR7-wZTRP0HFl8E"
GEMINI_API_KEY = "AIzaSyDbFFCziL6pDXkRp9x9A4-u-l0yQJvrqNs"

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
# မှန်ကန်တဲ့ Gemini API endpoint (version v1)
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"

def send_message(chat_id, text):
    try:
        if len(text) > 4096:
            for i in range(0, len(text), 4000):
                payload = {'chat_id': chat_id, 'text': text[i:i+4000]}
                requests.post(f"{TELEGRAM_URL}/sendMessage", json=payload)
        else:
            payload = {'chat_id': chat_id, 'text': text}
            requests.post(f"{TELEGRAM_URL}/sendMessage", json=payload)
        return True
    except Exception as e:
        logger.error(f"Send message error: {e}")
        return False

def generate_story(topic):
    try:
        headers = {'Content-Type': 'application/json'}
        
        prompt = f"""Write a beautiful Burmese story of 1500-2000 words about: {topic}
        
Write in Burmese language (မြန်မာလို ရေးပါ).
Make it emotional and engaging."""
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        response = requests.post(GEMINI_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            story = result['candidates'][0]['content']['parts'][0]['text']
            return story
        else:
            error_msg = f"API Error {response.status_code}: {response.text}"
            logger.error(error_msg)
            return f"API အမှား: {response.status_code} - ကျေးဇူးပြုပြီး နောက်မှထပ်စမ်းပါ။"
            
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return f"ဝတ္ထုမရေးနိုင်ခဲ့ပါ။ အမှား: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def home():
    return 'Bot is running!'

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        logger.info(f"Received: {data}")
        
        if 'message' in data:
            chat_id = data['message']['chat']['id']
            text = data['message'].get('text', '')
            
            if text == '/start':
                send_message(chat_id, "မင်္ဂလာပါ။ ဝတ္ထုခေါင်းစဉ်တစ်ခုပေးပါ။")
            elif text == '/help':
                send_message(chat_id, "ဝတ္ထုခေါင်းစဉ်တစ်ခုပေးလိုက်ရင် ကျွန်တော် ဝတ္ထုရေးပေးမယ်။")
            elif text:
                send_message(chat_id, "ဝတ္ထုရေးနေပါပြီ... ခဏစောင့်ပါ။")
                story = generate_story(text)
                send_message(chat_id, story)
        
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)