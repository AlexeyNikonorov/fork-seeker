import re
import requests
from lxml import html
import time, datetime
from Event import Bookmaker, Event
from tests import *
from splinter import Browser


class Leon(Bookmaker):
    def __init__(self, driver=None):
        Bookmaker.__init__(self)
        self.url = 'https://www.leonbets.net/'
        self.driver = driver
        self.date_format = re.compile('(?P<day>\d{2})/(?P<month>\d{2})')

    def load(self):
        sport = 'soccer'
        if self.driver is None:
            self.driver = Browser('phantomjs', load_images=False, wait_time=5)
        visit(self.driver, self.url)

        selector = '.live24>a:nth-child(1)'
        click(self.driver, selector)

        selector = '#sortedSportFutureMapAbove > tbody:nth-child(1) > tr:nth-child(1) > th:nth-child(2) > label:nth-child(2)'
        click(self.driver, selector)

        selector = '#sortedSportFutureMapAbove > tbody:nth-child(1) > tr:nth-child(1) > th:nth-child(3) > label:nth-child(2)'
        click(self.driver, selector)
        wait(self.driver)
        self.html = html.document_fromstring(self.driver.html)
        try:
            self.parse()
        except TypeError:
            print 'retry'; time.sleep(2)
            try:
                self.html = html.document_fromstring(self.driver.html)
                self.parse()
            except TypeError:
                pass
            
    def parse(self):
        events = self.html.cssselect('table#sportsTable24 tr.sportsRow')
        for event in events:
            new_event = Event()
            new_event.load(self.event_parser(event))
            self.store(new_event)

    def event_parser(self, event):
        output = dict()
        date = cssselect(event, 'td[class="tm"]')
        date = text_content(date)
        output['date'] = self.to_date(date)
        output['live at'] = cssselect(event, 'td.tm span')
        output['teams'] = cssselect(event, 'td.event strong')
        output['bet home'] = cssselect(event, 'td[title~="home"] strong')
        output['bet draw'] = cssselect(event, 'td[title~="draw"] strong')
        output['bet away'] = cssselect(event, 'td[title~="away"] strong')
        return text_content(output)


if __name__ == '__main__':
    ts = time.time()
    b = Leon()
    b.load()
    b.driver.quit(); print b
    b.save()
    print time.time() - ts




