import time
import not_for_git
import telegram
import asyncio
bot = telegram.Bot(token=not_for_git.token)


def spammer():
    print("iam called")
    while True:
        bot.sendMessage(chat_id='-613028414', text='msg2')


try:
    spammer()
except Exception as err:
    print(err)
