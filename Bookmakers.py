import re
import requests
from lxml import html
from Abstract import Bookmaker, Game
import time, datetime


class WilliamHill(Bookmaker):
    def __init__(self):
        Bookmaker.__init__(self)
        self.get_data_offline('html/WilliamHill/WilliamHill_football_27_01.html')
        self.extract_data()

    def to_date(self, date):
        try:
            reg = re.compile('\w+ (?P<day>\d+) (?P<month>\w{3}) \d+')
            date = reg.match(date).groupdict()
        except AttributeError:
            return None
        day = int(date['day'])
        month = date['month']
        month = self.months[month]
        year = 2016
        date = datetime.date(year, month, day)
        return date

    def extract_data(self):
        date = datetime.date(2016, 1, 29)
        schedule = self.html.cssselect('div.paginationDailyMatches li')
        for day in schedule:
            current = bool(day.get('id'))
            date_ = day.text_content()
            date_ = self.to_date(date_)
            link = day.cssselect('a')[0].get('href')

        all_matches = self.html.get_element_by_id('ip_sport_0_types')
        groups = all_matches.cssselect('table.tableData')
        for group in groups:
            matches = group.cssselect('tr')
            for match in matches:
                info = match.cssselect('td')
                if len(info) > 6:
                    data = []
                    data.append(info[1]) # match time
                    data.append(info[2]) # teams
                    data.append(info[4]) # bet home
                    data.append(info[5]) # bet draw
                    data.append(info[6]) # bet away
                    self.store_data(data)


class Betfair(Bookmaker):
    def __init__(self):
        Bookmaker.__init__(self)
        self.get_data_offline('html/Betfair/Betfair_football_27_01.html')
        self.extract_data()

    def extract_data(self):
        all_matches = self.html.cssselect('ul.section-list')[0]
        live, comming_up = all_matches.cssselect('li.section')
        comming_up_matches = comming_up.cssselect('li.com-coupon-line')
        for match in comming_up_matches:
            bets = match.cssselect('li.selection')
            data = []
            data.append(match.cssselect('span.date')) # match time
            data.append(match.cssselect('span.home-team-name')) # team home
            data.append(match.cssselect('span.away-team-name')) # team away
            data.append(bets[0]) # bet home
            data.append(bets[1]) # bet draw
            data.append(bets[2]) # bet away
            self.store_data(data)


class Leon(Bookmaker):
    def __init__(self):
        Bookmaker.__init__(self)
        self.get_data_offline('html/Leon/Leon_football_27_01.html')
        self.extract_data()

    def extract_data(self):
        matches = self.html.cssselect('table#sportsTable24 tr.sportsRow')
        for match in matches:
            data = []
            data.append(match.cssselect('td.tm span')) # match time
            data.append(match.cssselect('td.event strong')) # teams
            data.append(match.cssselect('td[title~="home"] strong')) # bet home
            data.append(match.cssselect('td[title~="draw"] strong')) # bet draw
            data.append(match.cssselect('td[title~="away"] strong')) # bet away
            self.store_data(data)


class Betway(Bookmaker):
    def __init__(self):
        Bookmaker.__init__(self)
        self.get_data_offline('html/Betway/Betway_football_28_01.html')
        self.extract_data()

    def extract_data(self):
        matches = self.html.cssselect('tbody.oddsbody tr[class=""]')
        for match in matches:
            data = []
            data.append(match.cssselect('td.market_title div:first-child')) # match time
            data.append(match.cssselect('td.market_title a.event_name')) # teams
            data.append(match.cssselect('td[class*="outcome-td 1"]')) # bet home
            data.append(match.cssselect('td[class*="outcome-td x"]')) # bet draw
            data.append(match.cssselect('td[class*="outcome-td 2"]')) # bet away
            self.store_data(data)


class PaddyPower(Bookmaker):
    def __init__(self):
        Bookmaker.__init__(self)
        self.get_data_offline('html/PaddyPower/PaddyPower_football_28_01.html')
        self.extract_data()

    def to_date(self, date):
        try:
            reg = re.compile(r'(?P<day>\d+)\w{2} of (?P<month>\w{3})')
            date = reg.match(date).groupdict()
        except AttributeError:
            return None
        day = int(date['day'])
        month = self.months[date['month']]
        year = 2016
        date = datetime.date(year, month, day)
        return date

    def extract_data(self):
        schedule = self.html.cssselect('div.fb_day_type_wrapper')
        for day in schedule:
            try:
                date = day.cssselect('div.fb_hdr h2 span.normal')[0].text_content()
            except IndexError:
                break
            self.to_date(date)
            matches = day.cssselect('div[class="pp_fb_event "]')
            for match in matches:
                data = []
                data.append(match.cssselect('div.fb_event_time p')) # match time
                data.append(match.cssselect('div.fb_event_name p a')) # teams
                bets = match.cssselect('div[class="fb_odds item"]')[0]
                data.append(bets.cssselect('div[id*="H"] span a')) # bet home
                data.append(bets.cssselect('div[id*="D"] span a')) # bet draw
                data.append(bets.cssselect('div[id*="A"] span a')) # bet away
                self.store_data(data)
   

class Matchbook(Bookmaker):
    def __init__(self):
        Bookmaker.__init__(self)
        self.get_data_offline('html/Matchbook_football_28_01.html')
        self.extract_data()

    def extract_data(self):
        pass


class BetOnline(Bookmaker):
    def __init__(self):
        Bookmaker.__init__(self)
        self.get_data_offline('html/BetOnline_football_28_01.html')
        self.extract_data()
    
    def extract_data(self):
        pass


if __name__ == '__main__':
 
    bm = WilliamHill()
    bm.show_data()





