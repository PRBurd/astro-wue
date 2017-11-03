from bs4 import BeautifulSoup as bs
import requests
import re
from datetime import datetime
from datetime import time
import time
import telepot
from telepot.loop import MessageLoop
import sys
import schedule

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

def get_menu_text():
    weekday = datetime.weekday(datetime.now())
    if weekday > 4:
        bot.sendMessage(chat_id, 'Hoch die Hände, Wochenende!')
    else:
        soup = get_site(url)
        meals = get_menu_today(soup, weekday)
        return format_meals(meals)


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type == 'text':
        
        text = msg['text']
        
        if text.startswith('/menu'):
            message = get_menu_text()
            bot.sendMessage(chat_id, message, parse_mode='markdown')

        else:
            return
    else:
        return


TOKEN = sys.argv[1]

bot = telepot.Bot(TOKEN)




MessageLoop(bot, handle).run_as_thread()
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)
