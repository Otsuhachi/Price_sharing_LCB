from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import subprocess
import os

app = Flask(__name__)
command = ['heroku', 'config:get', 'YOUR_CHANNEL_ACCESS_TOKEN', '-a', 'pslcb']
shell_options = {
    'args': command,
    'check': True,
    'shell': True,
    'stdout': subprocess.PIPE
}
YOUR_CHANNEL_ACCESS_TOKEN = subprocess.run(**shell_options).stdout.decode()
command[2] = 'YOUR_CHANNEL_SECRET'
YOUR_CHANNEL_SECRET = subprocess.run(**shell_options).stdout.decode()

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(event.reply_token,
                               TextSendMessage(text=event.message.text))


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
