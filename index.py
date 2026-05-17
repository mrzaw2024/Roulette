import logging
import requests
from flask import Flask, request, jsonify, render_template_string

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

GEMINI_API_KEY = "AIzaSyAjbBvQrqLopYZoxz_FAdTDs8dafT_AHzI"

# HTML Form
HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>မြန်မာဝတ္ထုစက်</title>
    <style>
        body {
            font-family: 'Pyidaungsu', 'Myanmar Text', Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
        input {
            width: 100%;
            padding: 15px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 10px;
            margin: 15px 0;
        }
        button {
            width: 100%;
            padding: 15px;
            background: #27ae60;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            cursor: pointer;
        }
        button:hover {
            background: #219a52;
        }
        .loading {
            text-align: center;
            padding: 20px;
            display: none;
        }
        .story {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            white-space: pre-wrap;
            line-height: 1.6;
            display: none;
            max-height: 500px;
            overflow-y: auto;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>📖 မြန်မာဝတ္ထုစက်</h1>
        <p style="text-align:center">ခေါင်းစဉ်တစ်ခုပေးလိုက်ရင် ဝတ္ထုတစ်ပုဒ်ရေးပေးမယ်</p>
        
        <input type="text" id="topic" placeholder="ဥပမာ - ချစ်ခြင်းမေတ္တာ" value="ချစ်ခြင်းမေတ္တာ">
        <button onclick="generate()">✨ ဝတ္ထုရေးမည် ✨</button>
        
        <div class="loading" id="loading">
            <div>⏳ ဝတ္ထုရေးနေပါပြီ... စက္ကန့် ၂၀-၃၀ ကြာမည်။ စောင့်ပါ။</div>
        </div>
        <div id="result"></div>
        <div class="footer">Powered by Google Gemini AI</div>
    </div>
    
    <script>
        async function generate() {
            const topic = document.getElementById('topic').value;
            if(!topic) {
                alert('ခေါင်းစဉ်ထည့်ပါ');
                return;
            }
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').innerHTML = '';
            
            try {
                const res = await fetch('/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({topic: topic})
                });
                const data = await res.json();
                
                if(data.error) {
                    document.getElementById('result').innerHTML = '<div class="story error" style="display:block;">❌ ' + data.error + '</div>';
                } else {
                    document.getElementById('result').innerHTML = '<div class="story" style="display:block;">' + data.story.replace(/\\n/g, '<br>') + '</div>';
                }
            } catch(e) {
                document.getElementById('result').innerHTML = '<div class="story error" style="display:block;">❌ အမှားရှိသွားပါပြီ</div>';
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

def generate_story(topic):
    """Generate story using Gemini API with v1beta"""
    try:
        # Use v1beta API with correct model
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"
        
        prompt = f"""Write a beautiful Burmese story of 2000-2500 words about: {topic}
        
Write completely in Burmese language (မြန်မာလို ရေးပါ).
Make it emotional and engaging with clear beginning, middle, and end."""
        
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
        return jsonify({'error': str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True)