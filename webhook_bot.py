from flask import Flask, jsonify, request
import datetime
import json
import requests

app = Flask(__name__)

with open('token_api.txt', 'r') as f:
	token = f.read()

def welcom_message(item):
    if item['text'] == "hi":
        msg = "Hi, I'm a bot"
        chat_id = item['chat']['id']
        user_id = item['from']['id']
        user_name = item['from'].get('username', user_id)
        welcome_msg = f"Hi {user_name}, I'm a bot"
        to_url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={welcome_msg}&parse_mode=HTML"
        resp = requests.get(to_url)
        
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        data = request.json
        print(data)
        if 'message' in data:
            welcom_message(data['message'])
        return jsonify(data)
    else:
        return 'Hello World!'
        
if __name__ == '__main__':
    app.run(debug=True)