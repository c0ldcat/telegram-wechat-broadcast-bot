from telegram.ext import Updater
from telegram.ext import (CommandHandler, MessageHandler,
                          ConversationHandler, RegexHandler)
from telegram.ext import Filters

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

import logging
from logging.config import dictConfig
import argparse

from broadcast import ServerChan

# set up logger
logging_config = dict(
    version = 1,
    formatters = {
        'f': {
            'format': '%(asctime)s [%(levelname)s] %(message)s'
        }
    },
    handlers = {
        'h': {
            'class': 'logging.StreamHandler',
            'formatter': 'f',
            'level': logging.INFO
        }
    },
    root = {
        'handlers': ['h'],
        'level': logging.DEBUG
    })
dictConfig(logging_config)

# parse arguments
parser = argparse.ArgumentParser(prog='tele-wxbot',
                                 description='WeChat broadcast bot on Telegram')
parser.add_argument('-t', '--token', help = 'bot token',
                    required = True)

args = parser.parse_args()

token = args.token
broadcast = {}

debug = True

updater = Updater(token=token)
dispatcher = updater.dispatcher

REQUIRE, = range(1)

def start(bot, update):
    update.message.reply_text('Welcome! Please select a boardcast.')
    update.message.reply_text(
        'But you have no choice, we only support Server酱 for now.'
    )

    broadcast[update.message.chat.id] = ServerChan()

    return require(bot, update, True)

def require(bot, update, first = False):
    bc = broadcast[update.message.chat.id]

    # Read reply
    if not first:
        key, setter = bc.need()
        setter(update.message.text)

        update.message.reply_text(
            'OK. ' + key + ' is ' + update.message.text + '.'
        )

    # Try next
    try:
        key, _ = bc.need()
        update.message.reply_text('Please enter your ' + key + '.')

        return REQUIRE
    except ValueError:
        update.message.reply_text('Configuratio completed.')
        return ConversationHandler.END

def sticker(bot, update):
    url = updater.bot.getFile(update.message.sticker.file_id).file_path

    try:
        bc = broadcast[update.message.chat.id]
        bc.send_img(update.message.date, url)
        update.message.reply_text("Got it!")
    except KeyError:
        update.message.reply_text("/start first")

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        REQUIRE: [MessageHandler(Filters.text, require)]
    },
    fallbacks=[]
)

dispatcher.add_handler(conv_handler)
dispatcher.add_handler(MessageHandler(Filters.sticker, sticker))

updater.start_polling()
