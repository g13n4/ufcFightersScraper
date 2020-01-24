import re
from urllib.request import urlopen

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from unidecode import unidecode

from .base import base

class scraper(base):
    def __init__(self,wd: webdriver):
        super(scraper, self).__init__("tapology")
        self.wd = wd

    def _cards_getter(self):
        """Get all the UFC cards from tapology's site"""
        for page in range(20, 0, -1):
            link = urlopen(
                f'https://www.tapology.com/fightcenter?group=ufc&page={page}&region=&schedule=results')
            site = BeautifulSoup(link, 'html.parser')
            links_on_page = []
            for result in site.find_all('section', class_="fcListing"):
                elem = result.find('span', 'name').a
                links_on_page.append(
                    ("https://www.tapology.com" + elem.get('href'), elem.text))
                self.cardsLinks.extend(links_on_page[::-1])

    def _fights_getter(self):
        list_of_fighters = []
        checked_fighters = []
        for card_link, card_name in self.cardsLinks:
            link = urlopen(card_link)
            site = BeautifulSoup(link, 'html.parser')
            for bout in site.find_all('li', 'fightCard'):
                for name in bout.find_all('a'):
                    if re.match('/fightcenter/bouts/', name.get(
                            'href')) or name.text in checked_fighters: continue
                    list_of_fighters.append(
                        "https://www.tapology.com" + name.get('href'))
                    checked_fighters.append(name.text)
        self.fightsLinks += list(set(list_of_fighters))

    def _get_one(self,url):
        def get_score(string):
            if not string: return {'nc': '0', 'wins': '0', 'loses': '0',
                                   'draws': '0'}
            score = {'nc': '0'}
            score['wins'], score['loses'], score['draws'] = \
                re.search('\d+-\d+-\d+', string)[0].split('-')
            if re.search('NC', string):
                score['nc'] = \
                    re.search('(\d+) NC', "16-4-0, 1 NC (Win-Loss-Draw)")[1]
            return score

        def get_last_fight_date(string):
            months = {'January': '01', 'February': '02', 'March': '03',
                      'April': '04', 'May': '05', 'June': '06',
                      'July': '07', 'August': '08', 'September': '09',
                      'October': '10', 'November': '11', 'December': '12'}
            month = months[re.search('\w+', string)[0]]
            day, year = list(re.findall('\d+', string))
            return f'{year}-{month}-{day}'

        self.wd.implicitly_wait(2)
        self.wd.get(url)

        element = WebDriverWait(self.wd, 3).until(
            EC.presence_of_element_located((By.ID, "fighterRecordControls")))
        element.find_element_by_class_name('right').click()
        #   driver.find_element_by_id('fighterRecordControls').find_element_by_class_name('right').click()
        site = BeautifulSoup(self.wd.page_source, 'html.parser')

        fighter = {'Name': '',
                   'Nickame': '',
                   'Birth date': '',
                   'Given name': '',
                   'Height': '',
                   'Reach': '',
                   'Record': {'wins': '', 'loses': '', 'draws': '', 'nc': ''},
                   'Last fight': '',
                   'Affiliation': '',
                   'Born': '',
                   'Fighting out of': '',
                   'bouts': []}

        fighter['Name'] = unidecode(
            site.find('div', 'fighterUpcomingHeader').find_all('h1')[1].string)
        fighter['Nickame'] = '' if not site.find('div',
                                                 'fighterUpcomingHeader').find(
            'h4', 'nickname').string else site.find('div',
                                                    'fighterUpcomingHeader').find(
            'h4', 'nickname').string.strip()[1:-1]

        for row in site.find('div', 'details details_two_columns').find_all(
                'li'):
            for strong_text, plain_text in zip(row.find_all('strong'),
                                               row.find_all('span')):
                strong_text, plain_text = strong_text.string, plain_text.string
                if re.search('Given Name:', strong_text): fighter[
                    'Given name'] = plain_text
                if re.search('Pro MMA Record:', strong_text): fighter[
                    'Record'] = get_score(plain_text)
                if re.search('Date of Birth', strong_text): fighter[
                    'Birth date'] = plain_text.replace('.', '-')
                if re.search('Last Fight:', strong_text): fighter[
                    'Last fight'] = get_last_fight_date(plain_text)
                if re.search('Affiliation:', strong_text): fighter[
                    'Affiliation'] = plain_text
                if re.search('Height:', strong_text) and re.search(
                    '\((.*)cm\)', plain_text): fighter['Height'] = \
                re.search('\((.*)cm\)', plain_text)[1]
                if re.search('Reach:', strong_text) and re.search('\((.*)cm\)',
                                                                  plain_text):
                    fighter['Reach'] = re.search('\((.*)cm\)', plain_text)[1]
                if re.search('Born:', strong_text): fighter[
                    'Born'] = plain_text
                if re.search('Fighting out of:', strong_text): fighter[
                    'Fighting out of'] = plain_text

        for fight in site.find('section',
                               class_='fighterFightResults').find_all('li')[::-1]:

            bout_info = {
                'Billing': '',
                'Class weight': '',
                'Decision': '',
                'Duration': '',
                'Fight under': '',
                "Fighter's record": '',
                'Injuries': '',
                'Odds': '',
                "Opponent's name": '',
                "Opponent's record": '',
                'Pay': '',
                'Referee': '',
                'Round': '',
                'Time': '',
                'Title in a fight': '',
                'Way': '',
                'Weigh-In': '',
                'Weightclass': '',
                'Weightclass title name': '',
                'Win or Lose': '',
                'fight date': ''}

            if (fight.find('div', 'record nonMma') or
                    re.search('Cancelled Bout',
                              fight.find('div', 'lead').text) or
                    re.search('Confirmed Upcoming Bout',
                              fight.find('div', 'lead').text) or
                    fight.find('div', {'data-result': 'cancelled'})): continue

            bout_info["Opponent's name"] = unidecode(
                fight.find('div', 'name').text)

            if fight.find('span', {"title": 'Fighter Record Before Fight'}):
                bout_info["Fighter's record"] = get_score(fight.find('span', {
                    "title": 'Fighter Record Before Fight'}).text)
                del bout_info["Fighter's record"]['nc']
            else:
                bout_info["Fighter's record"] = {'wins': '0', 'loses': '0',
                                                 'draws': '0'}

            if fight.find('span', {"title": 'Opponent Record Before Fight'}):
                bout_info["Opponent's record"] = get_score(fight.find('span', {
                    "title": 'Opponent Record Before Fight'}).text)
                del bout_info["Opponent's record"]['nc']

            if '·' in fight.find('div', 'lead').text:
                win_info = fight.find('div', 'lead').text.split('·')
                if len(win_info) == 2:
                    bout_info["Win or Lose"] = win_info[0]
                    bout_info["Way"] = win_info[1]
                elif len(win_info) == 3:
                    bout_info["Win or Lose"] = win_info[0]
                    bout_info["Way"] = win_info[1]
                    bout_info["Decision"] = win_info[2]
                else:
                    bout_info["Win or Lose"] = win_info[0]
                    bout_info["Way"] = win_info[1]
                    bout_info["Time"] = win_info[2]
                    bout_info['Round'] = win_info[3]
            else:
                bout_info["Win or Lose"] = fight.find('div', 'lead').text

            bout_info["Fight under"] = fight.find('div', 'notes').text
            bout_info["fight date"] = fight.find('div', 'date').text.replace(
                '.', '-')

            if fight.find('div', class_='detail tall'):
                for additional_info in fight.find('div',
                                                  class_='detail tall').find_all(
                        'div'):
                    if additional_info.find_all('span'):
                        first, second = list(additional_info.find_all('span'))

                        if first.text == 'Title Bout:':
                            if '·' in second.text:
                                bout_info['Title in a fight'], bout_info[
                                    'Weightclass title name'] = second.text.split(
                                    '·')
                            else:
                                bout_info[
                                    'Weightclass title name'] = second.text

                        if first.text == 'Billing:': bout_info[
                            'Billing'] = second.text
                        if first.text == 'Duration:':
                            if re.search("(.*\d)", second.text)[0]:
                                bout_info['Duration'] = \
                                re.search("(.*\d)", second.text)[0]
                            else:
                                bout_info['Duration'] = second.text

                        if first.text == 'Weight:':
                            for weightclass_info in second.text.split('·'):
                                if not re.search("\d", weightclass_info):
                                    bout_info['Weightclass'] = weightclass_info

                                elif re.search("Weigh-In", weightclass_info,
                                               re.IGNORECASE):
                                    bout_info['Weigh-In'] = \
                                    re.search('(\d+\.?\d? lbs)',
                                              weightclass_info)[0]

                                else:
                                    bout_info['Class weight'] = \
                                    re.search('(\d+\.?\d? lbs)',
                                              weightclass_info)[
                                        0] if re.search('(\d+\.?\d? lbs)',
                                                        weightclass_info) else ''


                        if first.text == 'Odds:': bout_info['Odds'] = \
                        second.text.split('·')[0]
                        if first.text == 'Referee:': bout_info[
                            'Referee'] = second.text
                        if first.text == 'Disclosed Pay:': bout_info['Pay'] = \
                        re.search('\$(\d+) ', second.text.replace(',', ''))[1]
                        if first.text == 'Injuries:': bout_info[
                            'Injuries'] = second.text

            fighter['bouts'].append(bout_info)

        return fighter


