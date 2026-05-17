import logging
import requests
from flask import Flask, request, jsonify, render_template_string

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# သင့် API Key အသစ် (သေချာထည့်ထားပါ)
GEMINI_API_KEY = "AIzaSyAjbBvQrqLopYZoxz_FAdTDs8dafT_AHzI"

# လှပသော Web Interface
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
            font-family: 'Pyidaungsu', 'Noto Sans Myanmar', 'Myanmar Text', system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        .card {
            background: white;
            border-radius: 24px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
            animation: fadeIn 0.5s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #1a252f 100%);
            color: white;
            padding: 35px 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 32px;
            letter-spacing: 2px;
        }
        .header p {
            margin: 12px 0 0;
            opacity: 0.9;
            font-size: 16px;
        }
        .content {
            padding: 35px;
        }
        .input-group {
            margin-bottom: 25px;
        }
        label {
            display: block;
            font-weight: 600;
            margin-bottom: 10px;
            color: #2c3e50;
            font-size: 16px;
        }
        input[type="text"] {
            width: 100%;
            padding: 14px 18px;
            font-size: 16px;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            font-family: inherit;
            transition: all 0.3s;
            background: #f8fafc;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
            background: white;
            box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px 30px;
            font-size: 18px;
            border-radius: 12px;
            cursor: pointer;
            width: 100%;
            font-weight: 600;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102,126,234,0.3);
        }
        button:active {
            transform: translateY(0);
        }
        button:disabled {
            background: #94a3b8;
            cursor: not-allowed;
            transform: none;
        }
        .loading {
            text-align: center;
            padding: 30px;
            display: none;
        }
        .spinner {
            border: 4px solid #e2e8f0;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .story {
            background: #f8fafc;
            border-radius: 16px;
            padding: 25px;
            margin-top: 30px;
            white-space: pre-wrap;
            line-height: 1.8;
            font-size: 16px;
            border-left: 5px solid #667eea;
            display: none;
            max-height: 600px;
            overflow-y: auto;
        }
        .error {
            background: #fee2e2;
            color: #dc2626;
            border-left-color: #dc2626;
        }
        .footer {
            background: #f1f5f9;
            padding: 15px;
            text-align: center;
            font-size: 13px;
            color: #64748b;
        }
        @media (max-width: 640px) {
            .content { padding: 25px; }
            .header h1 { font-size: 24px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="header">
                <h1>📖 မြန်မာဝတ္ထုစက်</h1>
                <p>ခေါင်းစဉ်တစ်ခုပေးလိုက်ရင် ကျွန်တော် ဝတ္ထုတစ်ပုဒ်ရေးပေးပါမယ်</p>
            </div>
            <div class="content">
                <div class="input-group">
                    <label>📝 ဝတ္ထုခေါင်းစဉ်</label>
                    <input type="text" id="topic" placeholder="ဥပမာ - ချစ်ခြင်းမေတ္တာ၊ ရွှေမြို့တော်၊ မိတ်ဆွေစစ်..." value="ချစ်ခြင်းမေတ္တာ">
                </div>
                <button id="generateBtn" onclick="generateStory()">✨ ဝတ္ထုရေးမည် ✨</button>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>ဝတ္ထုရေးနေပါပြီ... စက္ကန့် ၂၀-၃၀ ခန့်ကြာပါမည်။<br>ကျေးဇူးပြု၍ စောင့်ပါ။</p>
                </div>
                
                <div id="storyResult"></div>
            </div>
            <div class="footer">
                Powered by Google Gemini AI | မြန်မာလို ဝတ္ထုများ
            </div>
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
                    const formattedStory = data.story.replace(/\\n/g, '<br>').replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
                    resultDiv.innerHTML = '<div class="story" style="display:block;">' + formattedStory + '</div>';
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
        # Use stable model
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
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
        
        response = requests.post(url, json=payload, timeout=90)
        
        if response.status_code == 200:
            result = response.json()
            story = result['candidates'][0]['content']['parts'][0]['text']
            return story, None
        else:
            error_text = response.text
            logger.error(f"API Error: {response.status_code} - {error_text}")
            return None, f"API Error {response.status_code}"
            
    except requests.exceptions.Timeout:
        return None, "Request timeout - ကြာလွန်းသွားပါပြီ"
    except Exception as e:
        logger.error(f"Error: {e}")
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
            return jsonify({'error': error}), 500
            
        return jsonify({'story': story})
        
    except Exception as e:
        logger.error(f"Generate endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    # Keep for Telegram compatibility
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True)