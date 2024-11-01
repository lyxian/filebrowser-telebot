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

saveDir = ''

def createBot(logger=None):
    TOKEN = getToken()
    bot = telebot.TeleBot(token=TOKEN)
    basePath = os.getenv('APP_SAVE', '').rstrip('/')

    validCallbacks = ['date', 'category', 'comment', 'payor', 'ratio', 'confirm']

    def botLogger(logger, message):
        if logger:
            logger.info(message)
        return

    @bot.message_handler(commands=['start', 'help'])
    def start(message):
        global saveDir
        text = [
            'Hello',
            f'/path - set save directory, dir = "{saveDir}")'
        ]
        bot.send_message(message.chat.id, '\n'.join(text))
        return

    @bot.message_handler(commands=['path'])
    def setPath(message):
        global saveDir
        command = message.text.split()
        if len(command) == 1:
            saveDir = ''
        else:
            saveDir = command[1]
        botLogger(logger, f'saveDir = {saveDir}')
        bot.send_message(message.chat.id, f'saveDir = {saveDir}')
        return
    
    @bot.message_handler(content_types=['photo'])
    def downloadPhoto(message):
        bot.delete_message(message.chat.id, message.id)
        try:
            photos = sorted(message.photo, key=lambda x: x.file_size, reverse=True)
            try:
                if 'forward_origin' in message.json:
                    botLogger(logger, 'using forward_origin date')
                    saveTime = str(pendulum.from_timestamp(message.json['forward_origin']['date'], tz='Asia/Singapore')).split('+')[0]
                else:
                    saveTime = str(pendulum.from_timestamp(message.date, tz='Asia/Singapore')).split('+')[0]
            except Exception as e:
                botLogger(logger, str(e))
                saveTime = str(pendulum.now()).split('+')[0][:-3]
            dateDir = saveTime.split('T')[0]
            # remove all ":" "T" "-"
            saveTime = re.sub(r':|T|-', '', saveTime)
            if saveDir:
                if not os.path.exists(f'{basePath}/{saveDir}'):
                    os.makedirs(f'{basePath}/{saveDir}')
                savePath = os.path.join(f'{basePath}/{saveDir}/{saveTime}.jpg')
            else:
                if not os.path.exists(f'{basePath}/{saveDir}/{message.chat.id}/{dateDir}'):
                    os.makedirs(f'{basePath}/{saveDir}/{message.chat.id}/{dateDir}')
                savePath = os.path.join(f'{basePath}/{saveDir}/{message.chat.id}/{dateDir}/{saveTime}.jpg')
            getTelegramFilePath(photos[0].file_id, path=savePath, logger=logger)
            bot.send_message(message.chat.id, f'{saveTime}: downloaded photo')
        except Exception as e:
            botLogger(logger, str(e))
            bot.send_message(message.chat.id, f'{saveTime}: unable to download photo')
        return
    
    return bot
          