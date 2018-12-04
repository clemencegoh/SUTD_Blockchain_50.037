import json

from flask import Flask, render_template, request, redirect


app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
@app.route('/login', methods=['POST', 'GET'])
def HelloPage():
    return "Hello world"


if __name__ == '__main__':
    # Actual address: http://<Wireless LAN adaptor Wi-Fi IP>:5000
    app.run(host='0.0.0.0', port=5000)
