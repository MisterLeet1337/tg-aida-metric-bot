import apscheduler
import telebot
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from telebot import types

header_pos = 6
aida_log_path = 'D:/aida_log_log.csv'
BOT_TOKEN = ''
CPU_TEMP = 70
CPU_LOAD = 90
RAM_HIGH = 20000

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['get'])
def start(message: types.Message):
    msg = bot.send_message(chat_id=message.chat.id, text='Начинаю парсинг логов CSV...')
    scheduler.add_job(func=update_metrics, args=[msg], id='main', trigger='interval', seconds=10, next_run_time=datetime.now())

@bot.message_handler(commands=['stop'])
def stop(message: types.Message):
    msg = bot.send_message(chat_id=message.chat.id, text='Заканчиваю парсинг логов CSV...')
    scheduler.remove_job('main')

def update_metrics(message):
    try:
        with open(aida_log_path, 'r') as f:
            logs = f.readlines()
            header_line = logs[header_pos].split(';')
            last_line = logs[-1].split(';')

            cpu_temps = last_line[18:26]
            for value in cpu_temps:
                if int(value) > CPU_TEMP:
                    bot.send_message(chat_id=message.chat.id,
                                     text=f'WARNING! Температура CPU достигла {CPU_TEMP} градусов!', parse_mode='HTML')
                    break

            cpu_loads = last_line[7:15]
            for value in cpu_loads:
                if int(value) > CPU_LOAD:
                    bot.send_message(chat_id=message.chat.id, text=f'WARNING! Загрузка CPU достигла {CPU_LOAD} градусов!',
                                     parse_mode='HTML')
                    break

            if int(last_line[16]) > RAM_HIGH:
                bot.send_message(chat_id=message.chat.id, text=f'WARNING! Загрузка ОЗУ достигла {RAM_HIGH} GB!',
                                 parse_mode='HTML')
            values = ''
            for id, val in enumerate(header_line):
                values += header_line[id] + ': ' + f'<b>{last_line[id]}</b>\n'
            bot.edit_message_text(text=values, chat_id=message.chat.id, message_id=message.id, parse_mode='HTML')
    except:
        bot.send_message(chat_id=message.chat.id, text='Ошибка открытия файла логов AIDA', parse_mode='HTML')

scheduler = BackgroundScheduler()
scheduler.start()
bot.infinity_polling()
