import re
import requests
from lxml import html
import time, datetime
from Event import Bookmaker, Event
from tests import *
from splinter import Browser


class BetCity(Bookmaker):
    def __init__(self, driver=None):
        Bookmaker.__init__(self)
        self.url = 'https://www.betcitybk.com/en/'
        self.driver = driver

    def load(self):
        if self.driver is None:
            self.driver = Browser()

        self.visit(self.url); time.sleep(5)
        self.click('#f29'); time.sleep(5)
        self.driver.quit(); time.sleep(5)


if __name__ == '__main__':
    b = BetCity()
    b.load()
