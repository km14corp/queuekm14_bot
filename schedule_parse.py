from datetime import date, timedelta, datetime

import requests
from bs4 import BeautifulSoup


class Parser:
    def __init__(self, url, data):
        self.schedule_url = url
        self.data_base = data

    @staticmethod
    def parse(url):
        """
        parsing closest subjects
        """
        page = requests.get(url)
        url_items = BeautifulSoup(page.text, "html.parser")

        # finding closest sub num

        for tr in url_items.find_all('tr'):
            if tr.find("td", class_="closest_pair") in tr:
                closest_num = tr.index(tr.find("td", class_="closest_pair"))
                # creating a list of closest subjects
                tr4 = list(tr)[closest_num]
                closest_subs_list = [span.getText() for span in tr4.find_all('span')]

        return closest_subs_list

    def update_events(self, sub):
        """
        adding and deleting tables
        -adding- finding closest subjects and check if "our subject" is in this list
        -deleting-
        """
        closest = Parser.parse(self.schedule_url)

        # today date
        today = date.today()
        today_day = datetime.today().weekday()
        interesting_days = [4, 5]
        day_add = timedelta(days=today_day - 1 if today_day in interesting_days else 1)
        d1 = today.today() + day_add

        # adding table

        if sub in closest:
            add_sub = " ".join((sub, str(d1.strftime("%d/%m"))))
            self.data_base.add_event(sub, add_sub)
            queues = list(self.data_base.get_events())

            # deleting table
            for queue in queues:
                if queue != add_sub and sub in queue:
                    self.data_base.delete_event(queue)
                    print("DELETING EVENT", queue)
