import re
import requests
from lxml import html
import time, datetime
from Event import Bookmaker, Event
from tests import *
from splinter import Browser


class BetOnline(Bookmaker):
    def __init__(self, driver=None):
        Bookmaker.__init__(self)
        self.url = 'http://www.betonline.com/sportsbook'
        self.driver = driver
        self.date_format = re.compile('.*(?P<month>\w{3}) (?P<day>\d{2}).*')

    def load(self):
        sport = 'Soccer'
        if self.driver is None:
            self.driver = Browser()
            #self.driver = Browser('phantomjs', load_images=False, wait_time=5)

        visit(self.driver, self.url)
        selector = '.oddsFormatTd > div:nth-child(1) > div:nth-child(4)'
        click(self.driver, selector)
        selector = '.oddsFormatTd > div:nth-child(1) > div:nth-child(5) > ul:nth-child(1) > li:nth-child(2)';
        click(self.driver, selector)
        selector = 'div.topNav>a[cfg*="%s"]' % sport
        click(self.driver, selector)
        selector = 'div.subNav[style*="block"]>div.ckbxWrapper>input'
        check_all(self.driver, selector)
        click(self.driver, '#viewSelectedId')
        wait(self.driver)
        self.html = html.document_fromstring(self.driver.html)
        try:
            self.parse()
        except TypeError:
            print 'retry'; time.sleep(2)
            try:
                self.html = html.document_fromstring(self.driver.html)
            except TypeError:
                pass

    def parse(self):
        root = cssselect(self.html, 'div#contentBody')
        leagues = cssselect(root, 'table.sportsPeriod+table.league')
        for league in leagues:
            events = cssselect(league, 'tbody')
            for event in events:
                if event.get('class') == 'date':
                    date = cssselect(event, 'tr>td.bdt')
                    date = text_content(date)
                    date = self.to_date(date)
                elif event.get('class') == 'event':
                    new_event = Event(date=date)
                    new_event.load(self.event_parser(event))
                    self.store(new_event)

    def event_parser(self, event):
        output = dict()
        output['live at'] = cssselect(event, 'tr:first-child>td:first-child')
        output['team home'] = cssselect(event, 'tr:first-child>td.col_teamname')
        output['bet home'] = cssselect(event, 'tr:first-child>td.moneylineodds')
        output['team away'] = cssselect(event, 'tr:nth-child(2)>td.col_teamname')
        output['bet away'] = cssselect(event, 'tr:nth-child(2)>td.moneylineodds')
        output['bet draw'] = cssselect(event, 'tr:nth-child(3)>td.moneylineodds')
        return text_content(output)
                
        
if __name__ == '__main__':
    ts = time.time()
    b = BetOnline()
    b.load()
    print b;
    b.save()
    print time.time() - ts









