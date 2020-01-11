from .sherdog import sherdog
from bs4 import BeautifulSoup
import bs4
from urllib.request import Request, urlopen
from unidecode import unidecode

import os
import re
import pickle
import json
import copy

# downloadAllCardsInfo
# downloadAllFightersProfiles
# get_fighters_info

class ufctats(sherdog):
    def __init__(self):
        self.doc_name = 'ufcstats'
        self.cardsLinks = []
        self.fightersLinks = []
        self.fightersInfo = []


    def downloadAllCardsInfo(self):
        for page in range(1, 100):
            link = urlopen(
                f'http://ufcstats.com/statistics/events/completed?page={page}')
            site = BeautifulSoup(link, 'html.parser')
            if site.find('tbody'):
                for link in site.find('tbody').find_all('a', class_='b-link')[
                        ::-1]:
                    self.cardsLinks.append(link['href'])
            else:
                json.dump(self.cardsLinks, open(f'{self.doc_name}_cards.json', 'w'))
                break

    def get_cards_links(self):
        return self.cardsLinks if self.cardsLinks else self.downloadAllCardsInfo()


