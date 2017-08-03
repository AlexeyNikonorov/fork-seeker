import re
import requests
from lxml import html
import time, datetime
import io
from difflib import SequenceMatcher

def parse_match(teams):
    reg = re.compile(r'(?P<home>.+) +[vs:\.\-]+ +(?P<away>.+)')
    try:
        result = reg.match(teams)
        return result.groupdict()
    except AttributeError:
        return False

def parse_bet(bet):
    if type(bet) == float:
        return bet
    dec = re.compile(r'\d+\.\d+')
    try:
        bet = dec.match(bet).group()
        k = float(bet)
        return k
    except (ValueError, AttributeError):
        frac = re.compile(r'(\d+) */ *(\d+)')
        try:
            n, d = frac.match(bet).groups()
            k = round(float(n) / float(d) + 1, 2)
            return k
        except AttributeError:
            return bet

def format_text(text):
    reg = re.compile(r'[^ +\t+\n+\xa0]+')
    try:
        result = reg.findall(text)
        return ' '.join(result)
    except (AttributeError, TypeError,):
        return text
'''
def eq_str(s1, s2):
    if s1 == s2:
        return 1.0
    else:
        l1, l2 = len(s1), len(s2)
        s1, s2 = s1.lower(), s2.lower()
        S1, S2 = set(s1), set(s2)
        drop = set([' ', '\n', '-', ',', '.'])
        S1 -= drop
        S2 -= drop
        dS = S1 & S2
        L = len(dS)
        L1, L2 = len(S1), len(S2)
        v = 2.0*L/(L1+L2)
        return v
'''
def eq_str(s1, s2):
    return SequenceMatcher(lambda x: x in '.,()- ', s1, s2).ratio()

class Event:
    def __init__(self, **kwargs):
        self.bookmaker = None
        self.id = None
        self.dict = dict()
        for key, value in kwargs.items():
            self[key] = value

    def items(self):
        return self.dict.items()

    def keys(self):
        return self.dict.keys()

    def values(self):
        return self.dict.values()

    def load(self, data):
        output = dict()
        for key, value in data.items():
            try:
                if self[key] != value:
                    output[key] = (self[key], value)
                    self[key] = value
            except KeyError:
                self[key] = value
        return output

    def __getitem__(self, key):
        return self.dict[key]

    def __eq__(self, event):
        try:
            date = (self['date'] == event['date'])
        except KeyError:
            date = (self['live'] and event['live'])
        finally:
            if not date:
                return False
        try:
            live_at = (self['live at'][:5] == event['live at'][:5])
        except KeyError:
            pass
        try:
            v1 = eq_str(self['team home'], event['team home'])
            v2 = eq_str(self['team away'], event['team away'])
        except KeyError:
            pass
        return date and (v1>0.95 and v2>0.95)

    def __str__(self):
        indent = ' '*4
        date_format = '%d/%m/%Y'
        event = self.dict
        keys = event.keys()
        s = ''
        if 'date' in keys:
            date = event['date'].strftime(date_format)
            s += '{}Date: {}\n'.format(indent, date)
        if event['live']:
            if 'time' in keys:
                s += '{}Time: {}\n'.format(indent, event['time'])
            if 'score' in keys:
                s += '{}Score: {}\n'.format(indent, event['score'])
        if 'live at' in keys:
            s += '{}Live At: {}\n'.format(indent, event['live at'])
        if ('team home' in keys) and ('team away' in keys):
            s += '{}Teams:\n'.format(indent)
            s += '{}{} v {}\n'.format(indent*2, event['team home'], event['team away'])
        if 'bet home' in keys:
            home = event['bet home']
            draw = event['bet draw']
            away = event['bet away']
            s += '{}Odds:\n'.format(indent)
            s += '{}Home: {}, Draw: {}, Away: {}'.format(indent*2, home, draw, away)
        return s

    def __setitem__(self, key, value):
        value_type = type(value)
        if value_type == dict:
            for key_, value_ in value.items():
                value[key_] = format_text(value_)
            self.dict[key] = value
        else:
            if key == 'date':
                self.dict[key] = value
            else:
                if key == 'live at':
                    value = format_text(value)
                    if not value:
                        self.dict['live at'] = '?'
                    else:
                        self.dict['live at'] = value
                elif key == 'score':
                    value = format_text(value)
                    self.dict[key] = value
                elif key == 'teams':
                    value = format_text(value)
                    value = parse_match(value)
                    self.dict['team home'] = value['home']
                    self.dict['team away'] = value['away']
                elif key in ('bet home', 'bet draw', 'bet away'):
                    value = format_text(value)
                    value = parse_bet(value)
                    self.dict[key] = value
                elif key == 'odds':
                    value = list(map(format_text, value))
                    bet_home, bet_draw, bet_away = list(map(parse_bet, value))
                    self.dict['bet home'] = bet_home
                    self.dict['bet draw'] = bet_draw
                    self.dict['bet away'] = bet_away
                elif value_type == str:
                    value = format_text(value)
                    self.dict[key] = value
                else:
                    self.dict[key] = value

class Bookmaker:
    def __init__(self):
        self.name = str(self.__class__).split('.')[-1]
        self.html = None
        self.events = dict()
        self.total = 0
        self.months = {
            'Jan': 1, 'Feb': 2, 'Mar': 3,
        }
        self.date_formats = [
            re.compile(r'\w+ (?P<day>\d+)\w{2} of (?P<month>\w{3})'),
            re.compile('.+ (?P<day>\d{1,2}).(?P<month>\w{3}) .+'),
        ]

    def __str__(self):
        indent = '_'*10
        s = ''
        keys = list(self.events.keys())
        keys.sort()
        for key in keys:
            events = self.events[key]
            for event in events:
                s += '\n{0}Event #{1}/{2}{0}\n'.format(indent, event.id, self.total)
                s += '{}'.format(event)            
        return s

    def load_offline(self, path):
        with open(path, 'r') as f:
            s = f.read()
            self.html = html.document_fromstring(s)

    def screenshot(self, i=[0]):
        i[0] += 1
        self.driver.driver.save_screenshot('%d.png' % i[0])

    def wait(self):
        ts = time.time()
        while True:
            js_ready = self.driver.evaluate_script("document.readyState") == 'complete'
            try:
                jquery_ready = self.driver.evaluate_script("jQuery.active") == 0
            except:
                jquery_ready = True
            finally:
                if js_ready and jquery_ready:
                    break
                time.sleep(0.05)
        print time.time() - ts

    def visit(self, url):
        self.driver.visit(url)

    def click(self, selector):
        btn = self.driver.find_by_css(selector)
        try:
            btn.mouse_over(); time.sleep(0.05)
            btn.click(); time.sleep(0.05)
            btn.mouse_out()
        except AttributeError:
            btn[0].mouse_over(); time.sleep(0.05)
            btn[0].click()        

    def check_all(self, selector):
        btns = self.driver.find_by_css(selector)
        for btn in btns:
            time.sleep(0.1)
            btn.click()

    def save(self):
        keys = list(self.events.keys())
        keys.sort()
        html = '''
<head>
<script src="src-css/jquery-1.12.0.min.js"></script>
<script src="src-css/1.js"></script>
<link href="src-css/a.css" type="text/css" rel="stylesheet"></link>
<link href="src-css/bootstrap.min.css" type="text/css" rel="stylesheet"></link>
</head>
<body>
<table class="table-condensed table-striped">
    <thead>
        <tr class="row">
            <td class="#">#</td>
            <td align="center">Date</td>
            <td align="center">Live At</td>
            <td>Team Home</td>
            <td>Team Away</td>
            <td align="center">Home</td>
            <td align="center">Draw</td>
            <td align="center">Away</td>
        </tr>
    </thead>
    <tbody>'''
        n = 0
        for key in keys:
            events = self.events[key]
            for event in events:
                n += 1
                html += '''
        <tr class="row">
            <td class="#">{0}.</td>
            <td class="date" align="center">{1}</td>
            <td class="live_at" align="center">{live at}</td>
            <td class="team_home">{team home}</td>
            <td class="team_away">{team away}</td>
            <td class="bet_home" align="center">{bet home}</td>
            <td class="bet_draw" align="center">{bet draw}</td>
            <td class="bet_away" align="center">{bet away}</td>
        </tr>'''.format(n, key.strftime('%d/%m'), **event.dict)
        html += '''
    </tbody>
</table>
</body>'''
        with open('data/%s.html' % self.name, 'w') as f:
            f.write(html)

    def to_date(self, date):
        date = format_text(date)
        try:
            date = self.date_format.match(date).groupdict()
        except AttributeError:
            return None
        else:
            day = int(date['day'])
            month = date['month']
            try:
                month = self.months[month]
            except KeyError:
                month = int(month)
            finally:
                year = 2016
                date = datetime.date(year, month, day)
                return date

    def store(self, data):
        if type(data) == dict:
            data = Event(**data)
        try:
            date = data['date']
            try:
                event_list = self.events[date]
                data.id = len(event_list) + 1
                data.bookmaker = self.name
                event_list.append(data)
                self.total += 1
            except KeyError:
                data.id = 1
                data.bookmaker = self.name
                self.events[date] = [data]
                self.total += 1
        except KeyError:
            try:
                event_list = self.events['live']
                try:
                    i = event_list.index(data)
                    prev = event_list[i]
                    d = prev.load(data)
                    if len(d) != 0:
                        try:
                            s1 = '{} -> {}'.format(*d['bet home'])
                        except KeyError:
                            s1 = ' _____ '
                        try:
                            s2 = '{} -> {}'.format(*d['bet draw'])
                        except KeyError:
                            s2 = ' _____ '
                        try:
                            s3 = '{} -> {}'.format(*d['bet away'])
                        except KeyError:
                            s3 = ' _____ '
                        print '{} v {}'.format(prev['team home'], prev['team away'])
                        print '   {} | {} | {}'.format(s1, s2, s3)
                except ValueError:
                    data.id = len(event_list) + 1
                    data.bookmaker = self.name
                    event_list.append(data)
                    self.total += 1
            except KeyError:
                data.id = 1
                data.bookmaker = self.name
                self.events['live'] = [data]
                self.total += 1


if __name__ == '__main__':
    pass





