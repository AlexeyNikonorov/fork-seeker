import re
import requests
from lxml import html
import time, datetime
from Event import Bookmaker, Event
from tests import *
from splinter import Browser


class BoyleSports(Bookmaker):
    def __init__(self):
        Bookmaker.__init__(self)
        self.dir = 'html/BoyleSports'
        self.url = 'http://www.boylesports.com'
        self.date_format = re.compile('(?P<day>\d{1,2})\w{2} (?P<month>\w{3})')

    def load_data(self, online=False):
        sport = 'Football'
        if online:
            b = Browser()
            b.visit(self.url+'/betting')

            sport = b.find_by_css('#boNav24_1>ul>li>a[id="%s2"]' % sport)
            sport[0].click()

            upcoming = b.find_by_css('#tabUpcoming')
            upcoming[0].click()
            time.sleep(5)
            self.html = html.document_fromstring(b.html)
            b.quit()
        else:
            path = 'html/{0}/{0}_football_31_01.html'.format(self.name)
            with open(path, 'r') as f:
                s = f.read()
            self.html = html.document_fromstring(s)

    def load_live(self):
        sport = 'Football'
        b = Browser()
        url = '%s/inplay/?first=%s' % (self.url, sprot.lower())
        b.visit(url)
        show_all = b.find_by_css('#plusfootball')
        show_all[0].click()
        self.html = html.document_fromstring(b.html)
        b.quit()

    def live_parser(self):
        sport = 'FOOTBALL'
        root = cssselect(self.html, 'section#%s' % sport)
        leagues = cssselect(self.html, 'section#%s>ul' % sport)
        for league in leagues:
            events = league.cssselect('ul>li.clearfix')
            for event in events:
                self.live_event_parser(event)
                
    def parser(self):
        coupon_headers = cssselect(self.html, 'div[id*="CouponsHeader"]')
        root = coupon_headers[0]
        view_date = datetime.date(2016, 1, 31)
        events = cssselect(root, 'table tr')
        for event in events:
            if get(event, 'class') is None:
                date = cssselect(event, 'td:first-child>span')
                date = text_content(date)
                date = self.to_date(date)
            else:
                new_event = Event(date=date)
                new_event.load(self.event_parser(event))
                self.store(new_event)

    def live_event_parser(self, event):
        teams = cssselect(event, 'div:nth-child(2)>span:first-child>h4>div')
        odds = cssselect(event, 'div:nth-child(2) table tr td>div>span[price]')

    def event_parser(self, event):
        output = dict()
        event_time = cssselect(event, 'td:first-child>span')
        teams = cssselect(event, 'td:nth-child(2)>span>a')
        bet_home = cssselect(event, 'td:nth-child(3)>span')
        bet_draw = cssselect(event, 'td:nth-child(4)>span')
        bet_away = cssselect(event, 'td:nth-child(5)>span')

        output['live at'] = event_time
        output['teams'] = teams.get('title')
        output['odds'] = [bet_home, bet_draw, bet_away]
        return text_content(output)

if __name__ == '__main__':
    b = BoyleSports()
    b.load_data(online=True)
    b.parser()
    print b
    


    
