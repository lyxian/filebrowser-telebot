from cryptography.fernet import Fernet
import traceback
import requests
import logging
import telebot
import time
import re
import os

from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
import subprocess
import pendulum

from utils import getToken, getTelegramFilePath


def callTelegramAPI(method, params):
    url = 'https://api.telegram.org/bot{}/{}'.format(getToken(), method)
    response = requests.post(url=url, params=params)
    print(response.json())
    return response

def createBot(logger=None):
    TOKEN = getToken()
    bot = telebot.TeleBot(token=TOKEN)
    saveDir = os.getenv('APP_SAVE', 'files')

    validCallbacks = ['date', 'category', 'comment', 'payor', 'ratio', 'confirm']

    def botLogger(logger, message):
        if logger:
            logger.info(message)
        return

    @bot.message_handler(commands=['start', 'help'])
    def start(message):
        text = [
            'Hello'
        ]
        bot.send_message(message.chat.id, '\n'.join(text))
        return


    @bot.message_handler(content_types=['photo'])
    def downloadPhoto(message):
        try:
            photos = sorted(message.photo, key=lambda x: x.file_size, reverse=True)
            if not os.path.exists(f'{saveDir}/{message.chat.id}'):
                os.mkdir(f'{saveDir}/{message.chat.id}')
            savePath = os.path.join(f'{saveDir}/{message.chat.id}', str(pendulum.now()).split('+')[0][:-3] + '.jpg')
            getTelegramFilePath(photos[0].file_id, path=savePath, logger=logger)
            bot.send_message(message.chat.id, 'downloaded photo')
        except Exception as e:
            botLogger(logger, str(e))
            bot.send_message(message.chat.id, 'unable to download photo')
        return
    
    return bot
          