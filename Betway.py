import re
import requests
from lxml import html
import time, datetime
from Event import Bookmaker, Event
from tests import *
from splinter import Browser


class Betway(Bookmaker):
    def __init__(self, driver=None):
        Bookmaker.__init__(self)
        self.url = 'https://sports.betway.com'
        self.driver = driver
        self.date_format = re.compile('(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)')

    def load_offline(self):
        path = 'Betway_football_04_02.html'
        with open(path, 'r') as f:
            s = f.read()
            self.html = html.document_fromstring(s)

    def load(self):
        SPORTS = ['Football']
        COUNTRIES = ['England', 'Italy', 'Spain', 'Brasil', 'Germany']
        if self.driver is None:
            self.driver = Browser()

        self.visit(self.url); time.sleep(2)
        self.click('#odds-qf-live'); time.sleep(2)
        sports = self.driver.find_by_css('#oddsmenu-inner>ul.parent>li')
        for sport in sports:
            name = sport.find_by_css('li>div>a').value
            if name in SPORTS:
                sport.click(); time.sleep(2)
                countries = sport.find_by_css('ul.child>li')
                for country in countries:
                    name = country.find_by_css('li>div>a').value
                    if (name in COUNTRIES) or ('Any' in COUNTRIES):
                        btn = country.find_by_css('li>div>span:nth-child(2)')
                        btn.click(); time.sleep(5)
                        self.html = html.document_fromstring(self.driver.html)
                        self.parse()
                        btn.click(); time.sleep(2)

    def parse(self):
        leagues = cssselect(self.html, '#multibettypetable>table')
        for league in leagues:
            name = cssselect(league, 'table>thead')
            events = cssselect(league, 'table>tbody>tr:not(.header)')
            for event in events:
                if get(event, 'class') == 'date':
                    date = cssselect(event, 'tr>td')
                    date = text_content(date)
                    date = self.to_date(date)
                elif get(event, 'class') == '':
                    data = {'date': date}
                    data.update(self.event_parser(event))
                    self.store(data)
                    
    def event_parser(self, event):
        output = dict()
        output['live at'] = cssselect(event, 'tr>td.market_title>div:first-child')
        output['teams'] = cssselect(event, 'tr>td.market_title>a')
        output['odds'] = cssselect(event, 'div.outcome_button')
        return text_content(output)

    def load_live(self):
        if self.driver is None:
            self.driver = Browser()

        self.driver.visit('https://inplay.betway.com/#live-betting/all-live')
        
    def parse_live(self):
        self.html = html.document_fromstring(self.driver.html)
        sports = self.html.cssselect('div.all_events_menu>div.all_events_sportContainer')
        for sport in sports:
            name = cssselect(sport, 'div.all_events_sportContainer span.alleventspage_sportTitle')
            name = text_content(name)
            if name != 'Football':
                continue
            events = cssselect(sport, 'div.all_events_sportContainer div.all_events_sportChildren>div')
            for event in events:
                data = {'live': True}
                data.update(self.live_event_parser(event))
                self.store(data)

    def live_event_parser(self, event):
        output = dict()
        output['time'] = cssselect(event, 'div.all_events_time_text')
        output['teams'] = cssselect(event, 'div.all_events_eventTitle')
        output['score'] = cssselect(event, 'div.all_events_scoreboardData_score')
        odds = cssselect(event, 'div.all_events_outcome_container')
        home, draw, away = cssselect(odds, 'span.odds')
        if home != []:
            output['bet home'] = home
        else:
            output['bet home'] = 'EVS'
        if draw != []:
            output['bet draw'] = draw
        else:
            output['bet draw'] = 'EVS'
        if away != []:
            output['bet away'] = away
        else:
            output['bet away'] = 'EVS'
        return text_content(output)

    def update(self):
        self.html = html.document_fromstring(self.driver.html)
        sports = self.html.cssselect('div.all_events_menu>div.all_events_sportContainer')
        for sport in sports:
            name = cssselect(sport, 'div.all_events_sportContainer span.alleventspage_sportTitle')
            name = text_content(name)
            if name != 'Football':
                continue
            events = cssselect(sport, 'div.all_events_sportContainer div.all_events_sportChildren>div')
            for event in events:
                data = {'live': True}
                updated, updates = self.check_updates(event)
                if updated:
                    data.update(updates)
                    self.store(data)

    def check_updates(self, event):
        output = dict()
        updated = False
        output['time'] = cssselect(event, 'div.all_events_time_text')
        output['teams'] = cssselect(event, 'div.all_events_eventTitle')
        output['score'] = cssselect(event, 'div.all_events_scoreboardData_score')
        home = cssselect(event, 'div.all_events_outcome_container:first-child>div')
        draw = cssselect(event, 'div.all_events_outcome_container:nth-child(2)>div')
        away = cssselect(event, 'div.all_events_outcome_container:nth-child(3)>div')
        if ('odds_up' in home.get('class')) or ('odds_down' in home.get('class')):
            updated = True
            output['bet home'] = home
        if ('odds_up' in draw.get('class')) or ('odds_down' in draw.get('class')):
            updated = True
            output['bet draw'] = draw
        if ('odds_up' in away.get('class')) or ('odds_down' in away.get('class')):
            updated = True
            output['bet away'] = away
        return updated, text_content(output)

if __name__ == '__main__':
    b = Betway()
    b.load_live(); time.sleep(2)
    b.parse_live()
    while True:
        b.update(); time.sleep(1)



