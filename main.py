import os
import requests
from dotenv import load_dotenv

def main():
    load_dotenv()  # Load environment variables from .env file

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    token_url = os.getenv("TOKEN_URL")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    # Acquire a token using Keycloak resource owner password credentials flow
    token_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "password",
        "username": username,
        "password": password
    }
    token_response = requests.post(token_url, data=token_data)
    
    if token_response.status_code == 200:
        token_result = token_response.json()
        print("Access token acquired")
        print(token_result["access_token"])
        
        # Send authenticated POST request
        headers = {
            "Authorization": f"Bearer {token_result['access_token']}",
            "Content-Type": "application/json"
        }
        data = {
            "message": "test-event"
        }
        response = requests.post("https://api.bueckendorf.org/v1.0/messages/test-event", headers=headers, json=data)
        
        if response.status_code == 200:
            print("POST request successful")
            print(response.json())
        else:
            print("POST request failed")
            print(response.status_code)
            print(response.text)
    else:
        print("Failed to acquire token")
        print(token_response.status_code)
        print(token_response.text)
        print(token_response.json())  # Print detailed error message

if __name__ == "__main__":
    main()
