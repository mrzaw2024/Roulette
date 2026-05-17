import logging
import requests
from flask import Flask, request, jsonify, render_template_string

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = "8790341850:AAEo8qaWU4r9r3W_m-w7sR7-wZTRP0HFl8E"
GEMINI_API_KEY = "AIzaSyDbFFCziL6pDXkRp9x9A4-u-l0yQJvrqNs"

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"

# HTML Template for Web Interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Myanmar Story Generator</title>
    <style>
        body {
            font-family: 'Pyidaungsu', 'Myanmar Text', Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f0f0f0;
        }
        .container {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
        textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            font-family: inherit;
            margin: 10px 0;
        }
        button {
            background: #2c3e50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background: #1a252f;
        }
        .story {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
            white-space: pre-wrap;
            font-family: inherit;
            line-height: 1.6;
        }
        .loading {
            color: #7f8c8d;
            text-align: center;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📖 ဝတ္ထုရေးစက် (Story Generator)</h1>
        <p>ခေါင်းစဉ်တစ်ခု ရိုက်ထည့်ပါ။ ကျွန်တော် ဝတ္ထုတစ်ပုဒ် ရေးပေးပါမယ်။</p>
        
        <textarea id="topic" rows="3" placeholder="ဥပမာ - ချစ်ခြင်းမေတ္တာ၊ စွန့်စားခန်း၊ မိတ်ဆွေစစ်..."></textarea>
        <br>
        <button onclick="generateStory()">ဝတ္ထုရေးမည်</button>
        
        <div class="loading" id="loading">
            <p>⏳ ဝတ္ထုရေးနေပါပြီ... ခဏစောင့်ပါ။</p>
        </div>
        
        <div id="result"></div>
    </div>
    
    <script>
        async function generateStory() {
            const topic = document.getElementById('topic').value;
            if (!topic) {
                alert('ကျေးဇူးပြုပြီး ခေါင်းစဉ်တစ်ခု ရိုက်ထည့်ပါ။');
                return;
            }
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').innerHTML = '';
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({topic: topic})
                });
                const data = await response.json();
                document.getElementById('result').innerHTML = '<div class="story">' + data.story.replace(/\\n/g, '<br>') + '</div>';
            } catch (error) {
                document.getElementById('result').innerHTML = '<div class="story" style="color:red;">အမှားရှိသွားပါပြီ။ နောက်မှထပ်စမ်းပါ။</div>';
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

def generate_story(topic):
    try:
        headers = {'Content-Type': 'application/json'}
        prompt = f"Write a beautiful Burmese story of 1500-2000 words about: {topic}. Write in Burmese language (မြန်မာလို ရေးပါ). Make it emotional and engaging."
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(GEMINI_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"API Error: {response.status_code}. ကျေးဇူးပြုပြီး နောက်မှထပ်စမ်းပါ။"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    topic = data.get('topic', '')
    story = generate_story(topic)
    return jsonify({'story': story})

@app.route('/webhook', methods=['POST'])
def webhook():
    # Keep webhook for Telegram
    data = request.get_json(force=True)
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        if text:
            story = generate_story(text)
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", 
                         json={'chat_id': chat_id, 'text': story})
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True)