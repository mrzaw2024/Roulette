import logging
import requests
from flask import Flask, request, jsonify, render_template_string

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

GEMINI_API_KEY = "AIzaSyAjbBvQrqLopYZoxz_FAdTDs8dafT_AHzI"

# HTML Form (အရောင်လှလှလေးနဲ့)
HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>မြန်မာဝတ္ထုစက်</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Pyidaungsu', 'Myanmar Text', 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        .card {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        .content {
            padding: 30px;
        }
        input {
            width: 100%;
            padding: 15px;
            font-size: 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            margin: 15px 0;
            font-family: inherit;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 15px;
            font-size: 18px;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: scale(1.02);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .loading {
            text-align: center;
            padding: 20px;
            display: none;
        }
        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .story {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            white-space: pre-wrap;
            line-height: 1.8;
            max-height: 500px;
            overflow-y: auto;
            display: none;
        }
        .error {
            background: #ffebee;
            color: #c62828;
            border-left: 4px solid #c62828;
        }
        .footer {
            background: #f5f5f5;
            padding: 15px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="header">
                <h1>📖 မြန်မာဝတ္ထုစက်</h1>
                <p>ခေါင်းစဉ်တစ်ခုပေးလိုက်ရင် ဝတ္ထုတစ်ပုဒ်ရေးပေးမယ်</p>
            </div>
            <div class="content">
                <input type="text" id="topic" placeholder="ဥပမာ - ချစ်ခြင်းမေတ္တာ" value="ချစ်ခြင်းမေတ္တာ">
                <button id="btn" onclick="generateStory()">✨ ဝတ္ထုရေးမည် ✨</button>
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p style="margin-top:15px">ဝတ္ထုရေးနေပါပြီ... ခဏစောင့်ပါ။</p>
                </div>
                <div id="result"></div>
            </div>
            <div class="footer">
                Powered by Google Gemini AI
            </div>
        </div>
    </div>
    <script>
        async function generateStory() {
            const topic = document.getElementById('topic').value;
            if (!topic) {
                alert('ကျေးဇူးပြုပြီး ခေါင်းစဉ်တစ်ခု ရိုက်ထည့်ပါ။');
                return;
            }
            
            const btn = document.getElementById('btn');
            const loading = document.getElementById('loading');
            const resultDiv = document.getElementById('result');
            
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
                    resultDiv.innerHTML = '<div class="story" style="display:block;">' + data.story.replace(/\\n/g, '<br>') + '</div>';
                }
            } catch (error) {
                resultDiv.innerHTML = '<div class="story error" style="display:block;">❌ အမှားရှိသွားပါပြီ။ နောက်မှထပ်စမ်းပါ။</div>';
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
    """Try multiple Gemini models"""
    
    # Model တွေ အစဉ်လိုက်စမ်းမယ်
    models_to_try = [
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-pro',
        'gemini-1.0-pro',
        'gemini-2.0-flash-exp'
    ]
    
    for model_name in models_to_try:
        try:
            url = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
            
            prompt = f"""Write a beautiful Burmese story of 1500-2000 words about: {topic}
            
Write completely in Burmese language (မြန်မာလို ရေးပါ).
Make it emotional and interesting with clear beginning, middle, and end."""
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                story = result['candidates'][0]['content']['parts'][0]['text']
                logger.info(f"Success with model: {model_name}")
                return story, None
            elif response.status_code == 404:
                logger.warning(f"Model {model_name} not found, trying next...")
                continue
            else:
                logger.error(f"Model {model_name} error: {response.status_code}")
                continue
                
        except Exception as e:
            logger.error(f"Error with {model_name}: {e}")
            continue
    
    return None, "No working model found. Please check your API key or try again later."

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
            return jsonify({'error': error}), 500
            
        return jsonify({'story': story})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True)