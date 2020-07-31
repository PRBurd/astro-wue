from bs4 import BeautifulSoup as bs
import requests
from datetime import datetime
import time
import telepot
from telepot.loop import MessageLoop
import sys
import schedule
from peewee import SqliteDatabase, IntegerField, Model
from telepot.exception import BotWasBlockedError, BotWasKickedError


database_file = 'recipients.db'

db = SqliteDatabase(None)


class Recipient(Model):
    chat_id = IntegerField(unique=True)

    class Meta:
        database = db


url = "https://www.studentenwerk-wuerzburg.de/essen-trinken/speiseplaene/plan/show/mensateria-campus-nord.html"


def get_site(url):
    site = requests.get(url)
    return bs(site.text, "lxml")


def get_menu_today(soup, weekday):
        currentweek = soup.find('div', {'class': 'week currentweek'})
        menu = currentweek.find_all('div', {'class': 'day'})
        if menu[weekday].find('div', {'class': 'holiday'}) is not None:
            print("Die Mensa hat heute zu.")
            return [['Holiday', 'Die Mensa hat heute zu.']]
        else:
            meals = menu[weekday].find_all('article', {'class': 'menu'})
            return list(map(get_meal, meals))


def get_meal(day):
    station = day.find('div', {'class': 'icon'})["title"]
    meal = day.find('div', {'class': 'title'}).text
    price = day.find('div', {'class': 'price'}).text
    return [station, meal, price]


def format_meals(meals):
    text = 'Menü von heute: \n'
    if meals[0] == 'Holiday':
        return meals[1]
    else:
        for meal in meals:
            text = text + "- ***" + meal[0] + "***:\n    - " + meal[1] + "\n    - " + meal[2] + "\n \n"
        return text


def get_menu_text(weekday):
        soup = get_site(url)
        meals = get_menu_today(soup, weekday)
        return format_meals(meals)


def send_menu_to_all():
    weekday = datetime.weekday(datetime.now())
    print("##########################")
    print("Sending menus:")
    if weekday > 4:
        return
    else:
        message = get_menu_text(weekday)
        for recipient in Recipient.select():
            print("   Sending menu to",recipient.chat_id)
            sendMessage(recipient.chat_id, message, parse_mode='markdown')
    print("##########################")

def sendMessage(chat_id, message, **kwargs):
    print("    Trying to send message")
    try:
        bot.sendMessage(chat_id, message, **kwargs)
        print("        succeed")
    except (BotWasBlockedError, BotWasKickedError):
        try:
            recipient = Recipient.get(chat_id=chat_id)
            recipient.delete_instance()
            print("    Bot was kicked or blocked, removed entry from DB,",chat_id)
        except Recipient.DoesNotExist:
            print("    Bot was kicked or blocked, but no entry in DB")
    except:
        print("    Got connection reset error, wait 1 Sec and try again.")
        time.sleep(1)
        bot.sendMessage(chat_id, message, **kwargs)
        print("        succeed")


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type == 'text':
        
        text = msg['text']
        print('Message from',msg['chat']['first_name'])
        if text.startswith('/menu'):
            weekday = datetime.weekday(datetime.now())
            print("Trying to send menu")
            if weekday > 4:
                sendMessage(chat_id, 'Hoch die Hände, Wochenende!')
            else:
                message = get_menu_text(weekday)
                sendMessage(chat_id, message, parse_mode='markdown')

        elif text.startswith('/start'):
            recipient, new = Recipient.get_or_create(chat_id=chat_id)
            print("received /start")
            if new:
                print("Add Client to DB")
                message = 'Hier gibts ab jetzt jeden Tag um 10:50 das Menü'
            else:
                message = 'Das Abo ist schon abgeschlossen!'
            sendMessage(chat_id, message)

        elif text.startswith('/stop'):
            print("received /stop")
            try:
                recipient = Recipient.get(chat_id=chat_id)
                recipient.delete_instance()
                message = 'Das Menü gibts ab jetzt nicht mehr'
                print("Remove Client from DB")

            except Recipient.DoesNotExist:
                message = 'Es gab noch gar kein Abo.'
            sendMessage(chat_id, message)

        else:
            return
    else:
        return


TOKEN = sys.argv[1]

if __name__ == '__main__':
    
    db.init(database_file)
    db.create_tables([Recipient], safe=True)
    bot = telepot.Bot(TOKEN)
    MessageLoop(bot, handle).run_as_thread()
    print('Listening ...')
    schedule.every().day.at("10:50").do(send_menu_to_all)
    # Keep the program running.
    while 1:
        schedule.run_pending()
        time.sleep(5)
