from datetime import date, timedelta

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

        return closest_subs_list, closest_sub

    def update_events(self, sub):
        """
        adding and deleting tables
        -adding- finding closest subjects and check if "our subject" is in this list
        -deleting-
        """
        closest, closest_sub = Parser.parse(self.schedule_url)

        # today date
        today = date.today()
        day_add = timedelta(days=1)
        d1 = today.today() + day_add

        # adding table
        add_sub = " ".join((sub, str(d1.strftime("%d/%m"))))
        if sub in closest:
            print("Creating table", add_sub)
            self.data_base.add_event(sub, add_sub)

        # deleting table
        queues = list(self.data_base.get_events())
        for queue in queues:
            if queue != add_sub and sub in queue:
                self.data_base.delete_event(sub, queue)