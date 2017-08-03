import re
import requests
from lxml import html
import time, datetime
from Event import Event, Bookmaker


class PaddyPower(Bookmaker):
    def __init__(self):
        Bookmaker.__init__(self)
        self.date_format = re.compile(r'- (?P<day>\d+)\w{2} of (?P<month>\w{3})')

    def extract_data_offline(self, date=datetime.date.today()):
        self.events[date] = []
        self.get_data_offline('html/PaddyPower_football_28_01.html')
        schedule = self.html.cssselect('div.fb_day_type_wrapper')
        for day in schedule:
            try:
                date_ = day.cssselect('div.fb_hdr h2 span.normal')[0].text_content()
            except IndexError:
                break
            date_ = self.to_date(date_)
            if date_ == date:
                events = day.cssselect('div[class="pp_fb_event "]')    
                for event in events:
                    data = Event()
                    data['date'] = date_
                    data['live at'] = event.cssselect('div.fb_event_time p')[0].text_content()
                    data['teams'] = event.cssselect('div.fb_event_name p a')[0].text_content()
                    bets = event.cssselect('div[class="fb_odds item"]')[0]
                    data['bet home'] = bets.cssselect('div[id*="H"] span a')[0].text_content()
                    data['bet draw'] = bets.cssselect('div[id*="D"] span a')[0].text_content()
                    data['bet away'] = bets.cssselect('div[id*="A"] span a')[0].text_content()
                    self.store_data(date_, data)


if __name__ == '__main__':
    bm = PaddyPower()
    bm.extract_data_offline(date=datetime.date(2016, 1, 30))
    print bm

