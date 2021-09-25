from flask import Blueprint, request, abort, render_template, redirect, url_for, flash
from flask_login import login_user
from . import db
from .models import User
import requests
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import os
import json
import jwt

# import testget.moduletestget as md

line = Blueprint('line', __name__)

YOUR_CHANNEL_ACCESS_TOKEN = os.getenv("YOUR_CHANNEL_ACCESS_TOKEN", 'none')
YOUR_CHANNEL_SECRET = os.getenv("YOUR_CHANNEL_SECRET", 'none')
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# @line.before_request
# def before_request():
#     if not request.is_secure:
#         url = request.url.replace('http://', 'https://', 1)
#         code = 301
#         return redirect(url, code=code)


@line.route("/callback/line_bot_res", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    # line.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == '課題一覧':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='【課題一覧】\n9/25 プレゼン\n10/9 結果発表'))


LINE_CHANNEL_ID = os.getenv("LINE_CHANNEL_ID", 'none')
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", 'none')
REDIRECT_URL = "https://miteh.jp.ngrok.io/line/login"


@line.route("/", methods=["GET"])
def index():
    return render_template("index.html",
                           random_state="line1216",
                           channel_id=LINE_CHANNEL_ID,
                           redirect_url=REDIRECT_URL)


@line.route("/line/login", methods=["GET"])
def line_login():

    # 認可コードを取得する
    request_code = request.args["code"]
    uri_access_token = "https://api.line.me/oauth2/v2.1/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data_params = {
        "grant_type": "authorization_code",
        "code": request_code,
        "redirect_uri": REDIRECT_URL,
        "client_id": LINE_CHANNEL_ID,
        "client_secret": LINE_CHANNEL_SECRET
    }

    # トークンを取得するためにリクエストを送る
    response_post = requests.post(
        uri_access_token, headers=headers, data=data_params)

    line_id_token = json.loads(response_post.text)["id_token"]

    access_token = json.loads(response_post.text)["access_token"]

    decoded_id_token = jwt.decode(line_id_token,
                                  LINE_CHANNEL_SECRET,
                                  audience=LINE_CHANNEL_ID,
                                  issuer='https://access.line.me',
                                  algorithms=['HS256'])

    user = User.query.filter_by(line_id=decoded_id_token['sub']).first()
    if not user:
        new_user = User(line_id=decoded_id_token['sub'])
        db.session.add(new_user)
        db.session.commit()
        user = new_user

    login_user(user)
    flash('')

    return redirect(url_for('main.option_name', name=user.manaba_id))
