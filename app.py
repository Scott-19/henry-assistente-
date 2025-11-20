from flask import Flask, jsonify, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Configuração
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')

# Database
negocios = {}

@app.route('/')
def home():
    return jsonify({"message": "🚀 Henry Online!", "status": "✅"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)