import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine
from utils import send_text_message

load_dotenv()


machine = TocMachine(
    states=["start", "menu", "illustrated_book", "section", "attribute", "ID", "introduction", "generation1", "generation2", "generation3", "generation4", "generation5", "generation6", "generation7", "generation8"],
    transitions=[
        {
            "trigger": "advance",
            "source": "start",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "illustrated_book",
            "conditions": "is_going_to_illustrated_book",
        },
        {
            "trigger": "advance",
            "source": "illustrated_book",
            "dest": "section",
            "conditions": "is_going_to_section",
        },
        {
            "trigger": "advance",
            "source": "section",
            "dest": "attribute",
            "conditions": "is_going_to_attribute",
        },
        {
            "trigger": "advance",
            "source": "attribute",
            "dest": "ID",
            "conditions": "is_going_to_ID",
        },
        {
            "trigger": "advance", 
            "source": "ID", 
            "dest": "illustrated_book",
            "conditions": "go_back_to_illustrated_book",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "introduction",
            "conditions": "is_going_to_introduction",
        },
        {
            "trigger": "advance",
            "source": "introduction",
            "dest": "generation1",
            "conditions": "is_going_to_generation1",
        },
        {
            "trigger": "advance",
            "source": "introduction",
            "dest": "generation2",
            "conditions": "is_going_to_generation2",
        },
        {
            "trigger": "advance",
            "source": "introduction",
            "dest": "generation3",
            "conditions": "is_going_to_generation3",
        },
        {
            "trigger": "advance",
            "source": "introduction",
            "dest": "generation4",
            "conditions": "is_going_to_generation4",
        },
        {
            "trigger": "advance",
            "source": "introduction",
            "dest": "generation5",
            "conditions": "is_going_to_generation5",
        },
        {
            "trigger": "advance",
            "source": "introduction",
            "dest": "generation6",
            "conditions": "is_going_to_generation6",
        },
        {
            "trigger": "advance",
            "source": "introduction",
            "dest": "generation7",
            "conditions": "is_going_to_generation7",
        },
        {
            "trigger": "advance",
            "source": "introduction",
            "dest": "generation8",
            "conditions": "is_going_to_generation8",
        },
        {
            "trigger": "advance", 
            "source": ["generation1", "generation2", "generation3", "generation4", "generation5", "generation6", "generation7", "generation8"], 
            "dest": "introduction",
            "conditions": "go_back_to_introduction",
        },
        {
            "trigger": "advance", 
            "source": ["illustrated_book", "section", "attribute", "ID", "introduction", "generation1", "generation2", "generation3", "generation4", "generation5", "generation6", "generation7", "generation8"], 
            "dest": "menu",
            "conditions": "go_back_to_menu",
        },
    ],
    initial="start",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            send_text_message(event.reply_token, "輸入錯誤!請重新輸入")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
