import os
from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from dotenv import load_dotenv
import requests
from gunicorn.app.wsgiapp import run

app = Flask(__name__)
load_dotenv()  # Load environment variables from .env file

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Connector Webhook"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

def verify_basic_auth(request):
    auth = request.authorization
    if not auth or not (auth.username and auth.password):
        return False

    expected_username = os.getenv("WEBHOOK_USERNAME")
    expected_password = os.getenv("WEBHOOK_PASSWORD")

    return auth.username == expected_username and auth.password == expected_password

@app.route('/', methods=['POST'])
def webhook():
    if not verify_basic_auth(request):
        return jsonify({"error": "Unauthorized"}), 401

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
        return jsonify({"error": "Failed to acquire token", "message": str(token_response)}), 500

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
    api_response = requests.post(api_url + message_name, json=data, headers=headers)

    if api_response.status_code == 200:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Failed to forward data", "message": api_response.text}), 500

if __name__ == "__main__":
    run()