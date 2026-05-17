from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

GEMINI_API_KEY = "AIzaSyAjbBvQrqLopYZoxz_FAdTDs8dafT_AHzI"

HTML_CODE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>မြန်မာဝတ္ထုစက်</title>
    <style>
        body {
            font-family: 'Pyidaungsu', Arial, sans-serif;
            max-width: 700px;
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
            text-align: center;
            color: #333;
        }
        input {
            width: 100%;
            padding: 15px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 10px;
            margin: 15px 0;
            box-sizing: border-box;
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
            font-weight: bold;
        }
        button:hover {
            background: #219a52;
        }
        .loading {
            text-align: center;
            padding: 20px;
            display: none;
            color: #666;
        }
        .story {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            white-space: pre-wrap;
            line-height: 1.6;
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
            font-size: 12px;
            color: #999;
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
            ⏳ ဝတ္ထုရေးနေပါပြီ... စက္ကန့် ၂၀-၃၀ ကြာပါမယ်။ စောင့်ပါ...
        </div>
        <div id="result"></div>
        <div class="footer">Powered by Google Gemini AI</div>
    </div>

    <script>
        async function generate() {
            const topic = document.getElementById('topic').value;
            if (!topic) {
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
                
                document.getElementById('loading').style.display = 'none';
                
                if (data.error) {
                    document.getElementById('result').innerHTML = '<div class="story error">❌ ' + data.error + '</div>';
                } else {
                    document.getElementById('result').innerHTML = '<div class="story">' + data.story.replace(/\\n/g, '<br>') + '</div>';
                }
            } catch(e) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('result').innerHTML = '<div class="story error">❌ အမှားရှိသွားပါပြီ</div>';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [{"text": f"Write a 1500 word Burmese story about: {topic}. Write completely in Burmese language."}]
            }]
        }
        
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            story = response.json()['candidates'][0]['content']['parts'][0]['text']
            return jsonify({'story': story})
        else:
            return jsonify({'error': f'API Error {response.status_code}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True)