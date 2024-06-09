from flask import Flask, request
import threading
import pendulum
import argparse
import telebot
import time
import json
import os

from bot import createBot
from utils import customLogger, getMe

logger = customLogger(__file__)

parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()

DEBUG_MODE = args.debug

if __name__ == '__main__':
    app = Flask(__name__)
    bot = createBot(logger=logger)

    @app.route("/stop", methods=["GET", "POST"])
    def stop():
        if request.method == 'POST':
            password = os.getenv('PASSWORD', '1234')
            if 'password' in request.json and str(request.json['password']) == password:
                shutdown_hook = request.environ.get("werkzeug.server.shutdown")
                try:
                    shutdown_hook()
                    print("--End--")
                except:
                    pass
                return {'status': 'OK'}, 200
            else:
                return {'ERROR': 'Wrong password!'}, 400
        else:
            return {'ERROR': 'Nothing here!'}, 404

    @app.route("/" + bot.token, methods=["POST"])
    def getMessage():
        try:
            updates = request.stream.read().decode("utf-8")
            bot.process_new_updates(
                [telebot.types.Update.de_json(updates)]
            )
            message = json.loads(updates)
            logger.info(f'[{pendulum.now().to_datetime_string()}] received message: {message}')
            return {'status': 'OK'}, 200
        except Exception as e:
            print(f'Unable to process new message: {e}')
            return {'status': 'NOT_OK'}, 400

    @app.route("/", methods=["GET", "POST"])
    def webhook():
        if request.method != 'GET':
            bot.remove_webhook()
            try:
                bot.set_webhook(url=os.getenv("PUBLIC_URL") + bot.token)
                return {'status': 'Webhook set!'}, 200
            except:
                return {'status': 'Webhook not set...Try again...'}, 400
        else:
            return {'ERROR': 'Nothing here!'}, 404

    def start():
        bot.remove_webhook()
        time.sleep(4)
        logger.info(f'[{pendulum.now().to_datetime_string()}] Setting webhook...')
        try:
            bot.set_webhook(url=os.getenv("PUBLIC_URL").rstrip('/') + f'/{bot.token}')
            logger.info(f'[{pendulum.now().to_datetime_string()}] Webhook set!')
            return "Webhook set!"
        except Exception as e:
            msg = f"[{pendulum.now().to_datetime_string()}] Webhook not set...Try again...\n{e}"
            logger.info(msg)
            return

    startThread = threading.Thread(target=start, daemon=True)
    startThread.start() # .join()
    logger.info(f'\n[{pendulum.now().to_datetime_string()}] Starting telebot ({getMe()}) on PORT-{int(os.environ.get("PORT", 5005))}..')
    app.run(debug=DEBUG_MODE, host="0.0.0.0", port=int(os.environ.get("PORT", 5005)))
