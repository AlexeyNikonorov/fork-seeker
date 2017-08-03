import re
import requests
from lxml import html


def parse_match(teams):
    reg = re.compile(r'(?P<home>.+) +[vs:\.\-]+ +(?P<away>.+)')
    try:
        result = reg.match(teams)
        return result.groups()
    except AttributeError:
        return False

def parse_bet(bet):
    try:
        k = float(bet)
        return k
    except ValueError:
        reg = re.compile(r'(\d+) */ *(\d+)')
        try:
            n, d = reg.match(bet).groups()
            k = round(float(n) / float(d) + 1, 2)
            return k
        except AttributeError:
            raise ValueError

def format_text(text):
    reg = re.compile(r'[^ +\t+\n+\xa0]+')
    try:
        result = reg.findall(text)
        return ' '.join(result)
    except (AttributeError, TypeError,):
        return False

class Game:
    def __init__(self):
        self.bookmaker = None
        self.id = None
        self.dict = dict()
        self.valid_keys1 = (
            'live at',
            'teams',
            'bet home',
            'bet draw',
            'bet away',
        )
        self.valid_keys2 = (
            'live at',
            'team home',
            'team away',
            'bet home',
            'bet draw',
            'bet away',
        )

    def __eq__(self, game):
        date = (self['live at'] == game['live at'])
        home = (self['team home'] == game['team home'])
        away = (self['team away'] == game['team away'])
        return (home + away) == 2

    def show(self):
        game = self.dict
        try:
            print '   live at: %s' % game['live at']
            print '   team home: %s' % game['team home']
            print '   team away: %s' % game['team away']
            print '   odds:'
            print '      home: %.2f, draw: %.2f, away: %.2f' % (game['bet home'], game['bet draw'], game['bet away'])
        except KeyError:
            return False

    def __setitem__(self, key, value):
        len_value = len(value)
        if len_value == 0:
            raise ValueError
        if (value.__class__ == list) and (len_value >= 1):
            value = value[0]
        value = value.text_content()
        data = format_text(value)
        if data:
            if 'bet' in key:
                bet = parse_bet(data)
                self.dict[key] = bet
            elif 'teams' in key:
                home, away = parse_match(data)
                self.dict['team home'] = home
                self.dict['team away'] = away
            else:
                self.dict[key] = data
        else:
            raise ValueError

    def __getitem__(self, key):
        return self.dict[key]


class Bookmaker:
    def __init__(self):
        self.name = str(self.__class__).split('.')[-1]
        self.html = None
        self.games_total = 0
        self.games = []
        self.months = {
            'Jan': 1, 'Feb': 2, 'Mar': 3,
        }

    def show_data(self):
        for game in self.games:
            print '\n Event #%d:' % game.id
            game.show()

    def get_data_online(self, url):
        r = requests.get(url)
        s = r.text
        self.html = html.document_fromstring(s)

    def get_data_offline(self, html_name):
        with open(html_name, 'r') as f:
            s = f.read()
        self.html = html.document_fromstring(s)

    def extract_data(self):
        pass

    def store_data(self, data):
        data_class = data.__class__
        if data_class == Game:
            self.games_total += 1
            data.id = self.games_total
            data.bookmaker = self.name
            self.games.append(data)
            return True

        elif data_class == dict:
            game = Game()
            for key, value in data.items():
                try:
                    game[key] = value
                except ValueError:
                    return False
            self.games_total += 1
            game.id = self.games_total
            game.bookmaker = self.name
            self.games.append(game)
            return True

        elif (data_class == list) or (data_class == tuple):
            game = Game()
            n = len(data)
            if n == 5:
                keys = game.valid_keys1
            elif n == 6:
                keys = game.valid_keys2
            for key, item in zip(keys, data):
                try:
                    game[key] = item
                except ValueError:
                    return False
            self.games_total += 1
            game.id = self.games_total
            game.bookmaker = self.name
            self.games.append(game)
            return True

        else:
            return False         


if __name__ == '__main__':
    b = Bookmaker()
    print id(b)





