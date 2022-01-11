from bs4 import BeautifulSoup
import requests
from datetime import date, datetime, timedelta
from Data_base.db_help_class import db_help

import sqlite3


url = "http://rozklad.kpi.ua/Schedules/ViewSchedule.aspx?g=8bb9bcf6-5db2-4124-8c1a-d0debc152bc9"
#data_base = db_help('test.db')
a = "МА-1"


def queue_manager(sub, sub_url):
    # time settings
    conn = sqlite3.connect('Data_base/queue.db')

    today = date.today()
    d1 = today.today()
    now = datetime.now()
    today7pm = now.replace(hour=19, minute=0, second=0, microsecond=0)

    closest_sub = ''
    today_subs = []

    # bs4 settings
    page = requests.get(sub_url)
    url_items = BeautifulSoup(page.text, "html.parser")

    # data collecting
    for td in url_items.find_all("td", class_="closest_pair"):
        for span in td.find_all('span'):
            closest_sub = span.getText()

    for td in url_items.find_all("td", class_="day_backlight"):
        for span in td.find_all('span'):
            today_subs.append(span.getText())

    # creating/deleting queues
    conn.cursor().execute("SELECT name FROM sqlite_master WHERE type='table';")
    for i in today_subs:
        check_sub = " ".join((i, str(d1 - timedelta(days=7))))
        if sub.lower() == i.lower() and now > today7pm and check_sub not in conn.cursor().fetchall():
            print("Удаление очереди", check_sub)
            conn.execute("DROP TABLE '{}'".format(check_sub))

    if sub.lower() == closest_sub.lower():
        add_sub = " ".join((closest_sub, str(d1 + timedelta(days=1))))
        print("Создание очереди", add_sub)
        conn.execute("CREATE TABLE IF NOT EXISTS '{}' (number INTEGER PRIMARY KEY AUTOINCREMENT, id   STRING  UNIQUE)".format(add_sub))
    conn.commit()
    conn.close()
