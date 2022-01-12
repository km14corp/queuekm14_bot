from bs4 import BeautifulSoup
import requests
from datetime import date, datetime, timedelta
from Data_base.db_help_class import db_help

rozklad_url = "http://rozklad.kpi.ua/Schedules/ViewSchedule.aspx?g=8bb9bcf6-5db2-4124-8c1a-d0debc152bc9"


def parse(url):
    """
    parsing closest subjects
    """
    page = requests.get(url)
    url_items = BeautifulSoup(page.text, "html.parser")

    # finding closest sub num
    closest_subs_list = []
    closest_sub = ''

    for tr in url_items.find_all('tr'):
        if tr.find("td", class_="closest_pair") in tr:
            closest_num = tr.index(tr.find("td", class_="closest_pair"))
            a = tr.find("td", class_="closest_pair")
            for span in a.find_all('span'):
                closest_sub = span.getText()

    # creating a list of closest subjects
        tr = list(tr)
        try:
            tr4 = tr[closest_num]
            for span in tr4.find_all('span'):
                closest_subs_list.append(span.getText())
        except:
            pass

    # creating a list of today subjects
    today_list = []
    for td in url_items.find_all('td', class_="day_backlight"):
        for span in td.find_all('span'):
            today_list.append(span.getText())

    return closest_subs_list, closest_sub, today_list


def main(sub, data_base):
    """
    adding and deleting tables
    -adding- finding closest subjects and check if "our subject" is in this list
    -deleting-
    """
    data_base = data_base
    closest, closest_sub, today = parse(rozklad_url)
    if closest_sub not in today:
        today.append(closest_sub)

    # today or tomorrow closest sub
    compare = all(elem in closest for elem in today)
    if compare:
        day_add = timedelta(days=0)
    else:
        day_add = timedelta(days=1)

    # today date
    today = date.today()
    d1 = today.today() + day_add

    # adding table
    add_sub = " ".join((sub, str(d1.strftime("%d/%m"))))
    if sub in closest:
        print("Создание очереди", add_sub)
        data_base.make_db(add_sub)

    # deleting table
    queues = list(data_base.get_all_tables())
    for queue in queues:
        if queue != add_sub and sub in queue:
            data_base.delete_db(queue)
