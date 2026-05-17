import logging
import requests
import json
from flask import Flask, request, jsonify, render_template_string

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

GEMINI_API_KEY = "AIzaSyDbFFCziL6pDXkRp9x9A4-u-l0yQJvrqNs"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"

# HTML Form Template
HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>မြန်မာဝတ္ထုစက် - Myanmar Story Generator</title>
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            font-family: 'Pyidaungsu', 'Noto Sans Myanmar', 'Myanmar Text', Arial, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: #2c3e50;
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
        }
        .header p {
            margin: 10px 0 0;
            opacity: 0.9;
        }
        .content {
            padding: 30px;
        }
        .input-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            font-weight: bold;
            margin-bottom: 8px;
            color: #2c3e50;
        }
        input[type="text"] {
            width: 100%;
            padding: 15px;
            font-size: 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-family: inherit;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #2a5298;
        }
        button {
            background: #2a5298;
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 18px;
            border-radius: 10px;
            cursor: pointer;
            width: 100%;
            font-weight: bold;
            transition: background 0.3s;
        }
        button:hover {
            background: #1e3c72;
        }
        button:disabled {
            background: #95a5a6;
            cursor: not-allowed;
        }
        .loading {
            text-align: center;
            padding: 20px;
            display: none;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #2a5298;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .story {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            margin-top: 30px;
            white-space: pre-wrap;
            line-height: 1.8;
            font-size: 16px;
            border-left: 5px solid #2a5298;
            display: none;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            border-left-color: #dc3545;
        }
        .footer {
            background: #f1f1f1;
            padding: 15px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📖 မြန်မာဝတ္ထုစက်</h1>
            <p>ခေါင်းစဉ်တစ်ခုပေးလိုက်ရင် ကျွန်တော် ဝတ္ထုတစ်ပုဒ်ရေးပေးပါမယ်</p>
        </div>
        <div class="content">
            <div class="input-group">
                <label>ဝတ္ထုခေါင်းစဉ် 📝</label>
                <input type="text" id="topic" placeholder="ဥပမာ - ချစ်ခြင်းမေတ္တာ၊ ရွှေမြို့တော်၊ မိတ်ဆွေစစ်..." value="ချစ်ခြင်းမေတ္တာ">
            </div>
            <button id="generateBtn" onclick="generateStory()">✨ ဝတ္ထုရေးမည် ✨</button>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p style="margin-top: 15px;">ဝတ္ထုရေးနေပါပြီ... စက္ကန့် ၂၀-၃၀ ခန့်ကြာပါမည်။ ကျေးဇူးပြု၍ စောင့်ပါ။</p>
            </div>
            
            <div id="storyResult"></div>
        </div>
        <div class="footer">
            Powered by Google Gemini AI | မြန်မာလို ဝတ္ထုများ
        </div>
    </div>

    <script>
        async function generateStory() {
            const topic = document.getElementById('topic').value;
            if (!topic.trim()) {
                alert('ကျေးဇူးပြု၍ ဝတ္ထုခေါင်းစဉ်တစ်ခု ရိုက်ထည့်ပါ။');
                return;
            }
            
            const btn = document.getElementById('generateBtn');
            const loading = document.getElementById('loading');
            const resultDiv = document.getElementById('storyResult');
            
            btn.disabled = true;
            loading.style.display = 'block';
            resultDiv.innerHTML = '';
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic: topic })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    resultDiv.innerHTML = '<div class="story error" style="display:block;">❌ ' + data.error + '</div>';
                } else {
                    const storyHtml = '<div class="story" style="display:block;">' + data.story.replace(/\\n/g, '<br>') + '</div>';
                    resultDiv.innerHTML = storyHtml;
                }
            } catch (error) {
                resultDiv.innerHTML = '<div class="story error" style="display:block;">❌ ဆာဗာအမှားရှိသွားပါပြီ။ နောက်မှထပ်စမ်းပါ။</div>';
            } finally {
                btn.disabled = false;
                loading.style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

def generate_story(topic):
    """Generate story using Gemini API"""
    try:
        headers = {'Content-Type': 'application/json'}
        prompt = f"""Write a beautiful, emotional Burmese story of 2000-2500 words based on this topic: "{topic}"

Important requirements:
1. Write completely in Burmese language (မြန်မာလို ရေးရမည်)
2. Include: Introduction, character development, climax, and conclusion
3. Make it engaging, emotional, and culturally appropriate
4. Use natural, flowing Burmese language

Start writing the story now:"""
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        response = requests.post(GEMINI_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            story = result['candidates'][0]['content']['parts'][0]['text']
            return story, None
        else:
            error_msg = f"API Error {response.status_code}"
            return None, error_msg
            
    except requests.exceptions.Timeout:
        return None, "Request timeout - ကြာလွန်းသွားပါပြီ"
    except Exception as e:
        return None, str(e)

@app.route('/')
def home():
    return render_template_string(HTML_FORM)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        
        if not topic:
            return jsonify({'error': 'ခေါင်းစဉ် လိုအပ်ပါတယ်'}), 400
        
        story, error = generate_story(topic)
        
        if error:
            return jsonify({'error': f'ဝတ္ထုမရေးနိုင်ခဲ့ပါ။ {error}'}), 500
        
        return jsonify({'story': story})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    # Keep for Telegram compatibility
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True)