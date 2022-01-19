import datetime

import schedule

from Inheritance import InheritanceClass
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ParseMode, Update, Bot
from telegram.ext import Filters, MessageHandler, Updater, CallbackQueryHandler
import logging
import telegramcalendar
import not_for_git
import time
from threading import Thread

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

btns = {"auth": "зареєструватися", 'one_date': "отримати данні за дату",
        'find_client': "шукати по договору"}

auth_dict = dict()


class Payments(InheritanceClass):
    def __init__(self, token):
        self.bot = Bot(token=token)
        super().__init__()
        self.btn_status = bool()
        self.chat_id_ = bool()

    def callback_send(self, msg, update):
        self.bot.sendMessage(chat_id=update.callback_query.message.chat.id, text=msg if msg else 'нічого не знайдено')
        time.sleep(1)

    def send(self, msg, update):
        self.bot.sendMessage(chat_id=update.message.chat_id, text=msg)
        time.sleep(1)

    def add_keybord(self):
        reply_markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=btns['one_date'])
                ],

                [
                    KeyboardButton(text=btns["find_client"])
                ],
            ],
            resize_keyboard=True, )
        return reply_markup

    def auth_button(self):
        return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=btns['auth'],
                                                             request_contact=True)]], resize_keyboard=True, )

    def callback_func(self, update, context):
        print(auth_dict)
        text = update.message.text
        chat_id = update.message.chat.id
        if chat_id in auth_dict:
            if auth_dict[chat_id]['auth']:
                if text == btns['one_date']:
                    self.calendar_handler(update, context)
                if text == btns['find_client']:
                    self.btn_status = True
                    update.message.reply_text(
                        text=f"напишіть номер договору", reply_markup=ReplyKeyboardRemove(),
                    )

                else:
                    if self.btn_status:
                        res = [i for i in self.cursor.execute(
                            f"""select * from cars_payments
                                where  1=case when '{auth_dict[chat_id]['phone']}'  in (select * from telegram_vip_tels_access) then 1
                                when '{auth_dict[chat_id]['phone']}' not in (select * from telegram_vip_tels_access) and  tel='{auth_dict[chat_id]['phone']}'  then 1 
                               end and dog like '%{text}%'""")]
                        for row in res:
                            string_to_send = """Рахунок №: {}\nДоговір: {}\nДата: {}\nМенеджер: {}\nНадходження: {}\nКлієнт: {}\n""".format(
                                row[2], row[5], row[6], row[4], row[-2], row[3], )
                            self.send(string_to_send, update)
                        self.btn_status = False
                        update.message.reply_text(
                            text="Оберіть кнопку нижче", reply_markup=self.add_keybord(), )
                    else:
                        update.message.reply_text(
                            text="Оберіть кнопку нижче", reply_markup=self.add_keybord(), )
        else:
            update.message.reply_text(text="Нажаль ви не зареєстровані", reply_markup=self.auth_button())

    def calendar_handler(self, update, context):
        update.message.reply_text(text="оберіть дату:", reply_markup=telegramcalendar.create_calendar())

    def check_db(self, income_date, update, context):
        # text = update.message.text
        chat_id_ = update.callback_query.message.chat.id

        res = [i for i in self.cursor.execute(f"""select * from cars_payments
        where  1=case when '{auth_dict[chat_id_]['phone']}'  in (select * from telegram_vip_tels_access) then 1
        when '{auth_dict[chat_id_]['phone']}' not in (select * from telegram_vip_tels_access) and  tel='{auth_dict[chat_id_]['phone']}'  then 1 
       end and paydate='{income_date}'""")]
        for row in res:
            print("{}:\n{}".format(datetime.datetime.now(), row))
            string_to_send = """Рахунок №: {}\nДоговір: {}\nДата: {}\nМенеджер: {}\nНадходження: {}\nКлієнт: {}\n""".format(
                row[2], row[5], row[6], row[4], row[-2], row[3], )
            self.callback_send(string_to_send, update)

    def inline_calendar_handler(self, update, context):
        selected, date = telegramcalendar.process_calendar_selection(update, context)

        if selected:
            self.check_db(date, update, context)
            context.bot.send_message(chat_id=update.callback_query.from_user.id,
                                     text="Ви обрали %s" % (date.strftime("%d/%m/%Y")),
                                     reply_markup=self.add_keybord())

    def contact_callback(self, update, context):
        contact = update.effective_message.contact
        phone = contact.phone_number[-10:]
        res = len(list(self.cursor.execute(f"""select * from telegram_tels_access where phone='{phone}'""")))
        chat_id_ = update.message.chat.id
        if res > 0:
            auth_dict[chat_id_] = {"auth": True, "phone": phone}
            update.message.reply_text(
                text="Оберіть кнопку нижче", reply_markup=self.add_keybord(),
            )
        else:
            auth_dict[chat_id_] = {"auth": False, "phone": phone}
            print(auth_dict)
            update.message.reply_text(
                text="Нажаль ви не зареєстровані",
                reply_markup=self.auth_button())


class Spammer(InheritanceClass):
    def __init__(self, group_chat_id):
        super().__init__()
        self.group_chat_id = group_chat_id
        self.bot = Bot(token=not_for_git.token)

    def set_data(self, val):
        self.cursor.execute(f"insert into telegram_send_bills values('{val}')")
        self.cursor.commit()

    def spammer(self, data):
        self.bot.sendMessage(chat_id=self.group_chat_id, text=data)
        time.sleep(1)

    def get_data(self):
        res = [i for i in
               self.cursor.execute(
                   "select * from cars_payments where id not in (select * from telegram_send_bills)")]
        for row in res:
            print(row)
            self.set_data(row[0])
            self.spammer(
                """Рахунок №: {}\nДоговір: {}\nДата: {}\nМенеджер: {}\nНадходження: {}\nКлієнт: {}\n""".format(
                    row[2], row[5], row[6], row[4], row[-2], row[3], ))


def spammer():
    print(f"i'am check base to sent spam {datetime.datetime.now()}")
    Spammer('-1001680206647').get_data()




def start_spam():
    schedule.every(60).seconds.do(spammer)
    while True:
        schedule.run_pending()


def start_bot():
    updater = Updater(use_context=True,
                      token=not_for_git.token)
    m = Payments(token=not_for_git.token)
    updater.dispatcher.add_handler(MessageHandler(filters=Filters.text, callback=m.callback_func))
    updater.dispatcher.add_handler(CallbackQueryHandler(m.inline_calendar_handler))
    updater.dispatcher.add_handler(MessageHandler(filters=Filters.contact, callback=m.contact_callback))

    updater.start_polling()
    # updater.idle()


thread1 = Thread(target=start_spam)
thread2 = Thread(target=start_bot)

thread1.start()
thread2.start()
thread1.join()
thread2.join()
