import hmac
import hashlib
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests

app = Flask(__name__)

def verify_signature(request):
    secret = os.getenv("WEBHOOK_SECRET")
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        return False

    sha_name, signature = signature.split('=')
    if sha_name != 'sha256':
        return False

    mac = hmac.new(secret.encode(), msg=request.data, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)

@app.route('/', methods=['POST'])
def webhook():
    if not verify_signature(request):
        return jsonify({"error": "Unauthorized"}), 401

    load_dotenv()  # Load environment variables from .env file
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    token_url = os.getenv("TOKEN_URL")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    token_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "password",
        "username": username,
        "password": password
    }
    token_response = requests.post(token_url, data=token_data)
    
    if token_response.status_code != 200:
        return jsonify({"error": "Failed to acquire token"}), 500

    token_result = token_response.json()
    access_token = token_result.get("access_token")

    # Process the webhook payload
    payload = request.json
    message_name = payload.get("message-name")
    data = payload.get("data")

    if not message_name or not data:
        return jsonify({"error": "Invalid payload"}), 400

    # Forward the data to another API
    api_url = os.getenv("API_URL")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    api_response = requests.post(api_url + message_name, data, headers=headers)

    if api_response.status_code == 200:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Failed to forward data"}), 500