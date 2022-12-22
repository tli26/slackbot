import json
import slack
from dotenv import dotenv_values
from flask import Flask, Response
from slackeventsapi import SlackEventAdapter

from OpenaiManager import OpenaiManager

generating = False

config = dotenv_values(".env")

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(config["SIGNING_SECRET"], "/slack/events", app)
client = slack.WebClient(token=config["SLACK_TOKEN"])
BOT_ID = client.api_call("auth.test")["user_id"]

OpenaiManager = OpenaiManager()


@app.route("/", methods=["GET"])
def home():
    return Response("Hello world"), 200


@slack_event_adapter.on("message")
def message(payload):
    global generating
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    if user_id == BOT_ID:
        return
    text = event.get("text")
    if text.startswith('!gpt config'):
        if text == '!gpt config':
            client.chat_postMessage(channel=channel_id, text=OpenaiManager.get_config())
        else:
            text = text.split()
            if len(text) != 4:
                client.chat_postMessage(channel=channel_id, text='Invalid config')
            config_res = OpenaiManager.set_config(text[2], text[3])
            if not config_res:
                client.chat_postMessage(channel=channel_id, text='Invalid config')
            else:
                client.chat_postMessage(channel=channel_id, text='Config is updated')
    elif not generating and (text.startswith("!GPT ") or text.startswith("!gpt ")):
        client.chat_postMessage(channel=channel_id, text='Generating...')
        generating = True
        try:
            response, generated_code = OpenaiManager.generate_code(text[5:])
            generating = False
            client.chat_postMessage(channel=channel_id, blocks=[
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': (
                            f'```{text[5:]}'
                            f'{generated_code}'
                            '```'
                        )
                    }
                }
            ])
        except:
            client.chat_postMessage(channel=channel_id, text='Error')


if __name__ == "__main__":
    app.run(debug=True, port=5001)
