from .base import base

from bs4 import BeautifulSoup
from unidecode import unidecode
from urllib.request import urlopen

import re
import json
import os.path

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ufcstats(base):
    def __init__(self):
        super(ufcstats, self).__init__("ufcstats")
        self.dates = {}

    def _cards_getter(self):
        """downloads sites and extracts links from them"""
        for page in range(20, 0, -1):
            link = urlopen(
                f'http://ufcstats.com/statistics/events/completed?page={page}')
            site = BeautifulSoup(link, 'html.parser')
            for link in site.find('tbody').find_all('a', class_='b-link')[
                        ::-1]:
                self.cardsLinks.append(link['href'])


    def _fights_getter(self):
        fighters_wclasses = dict()
        for link in self.cardsLinks:
            site = BeautifulSoup(urlopen(link), 'html.parser')
            #weight class part
            for fight in site.find('tbody',
                                   class_='b-fight-details__table-body').find_all(
                    'tr', class_='b-fight-details__table-row'):
                info = fight.find_all('p', 'b-fight-details__table-text')
                wclass = info[11].text.strip()
                f1 = info[1].text.strip()
                f2 = info[2].text.strip()
                fighters_wclasses[f1] = wclass
                fighters_wclasses[f2] = wclass

            #actual scraping
                for fighter in fight.find_all('a',class_='b-link_style_black'):
                    if fighter.text.strip() not in self.fightsLinks:
                        self.fightsLinks.append(fighter['href'])

        #helps recognizing women weightclasses
        def is_woman(string):
            if re.search('women', string, re.IGNORECASE):
                return 1
            else:
                return 0

        women = {k: is_woman(v) for k, v in fighters_wclasses.items()}
        json.dump(women, open("womens_dict_ufcstats.json", 'w'))


    def _fighters_getter(self):
        """uses links to get the information about the fighters. One at a time"""
        pass

    def _get_one(self,url):
        """get one fighter's info"""
        pass
