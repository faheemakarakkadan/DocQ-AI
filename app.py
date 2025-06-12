import os
from flask import Flask, render_template, request, jsonify
from groq import Groq
from PyPDF2 import PdfReader
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load PDF content once
pdf_path="doc/cloud_security_policy.pdf"
def extract_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

pdf_path = "doc/cloud_security_policy.pdf"
pdf_content = extract_pdf_text(pdf_path)

# Initialize Groq client
client = Groq(api_key=os.getenv("API_KEY"))  

# Keep chat history (reset on server restart)
chat_history = []

# Serve the main page
@app.route('/')
def index():
    return render_template('index.html')

    
# Handle user message
@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json.get('message')

    if not chat_history:
        chat_history.append({
            "role": "system",
            "content": f"You are an AI assistant. Use this PDF content to help answer questions:\n{pdf_content}"
        })

    chat_history.append({"role": "user", "content": user_input})

    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=chat_history,
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
    )

    reply = completion.choices[0].message.content
    chat_history.append({"role": "assistant", "content": reply})

    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(debug=True)































