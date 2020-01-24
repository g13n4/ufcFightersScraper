import re

from bs4 import BeautifulSoup
from selenium import webdriver
from unidecode import unidecode

from .base import base

class scraper(base):
    def __init__(self,wd: webdriver, path_to_umatrix: str):
        super(scraper, self).__init__("sherdog")
        self.wd = wd
        self.wd.install_addon(path_to_umatrix)

    def _cards_getter(self):
        for x in range(0, 100):
            self.wd.get(
                f"https://www.sherdog.com/organizations/Ultimate-Fighting-Championship-UFC-2/recent-events/{x}")
            site = BeautifulSoup(self.wd.page_source, 'html.parser')
            if site.find('span',class_="no_events"): break
            for line in (site.find('div', {'id': 'recent_tab'})
                                 .find('tbody').find_all('tr')[::-1]):
                if line.find('a'):
                    self.cardsLinks.append(
                        "https://www.sherdog.com" + line.a['href'])

    def _fights_getter(self):
        for cnumber, card in enumerate(self.cardsLinks):
            if not ((len(self.cardsLinks) - cnumber) % 100):
                print("{len(self.fightersLinks) - cnumber} cards are left")

            self.wd.implicitly_wait(1)
            self.wd.get(card)
            site = BeautifulSoup(self.wd.page_source, 'html.parser')
            if not site.find('div', class_='module fight_card'): continue
            for main_card in (site.find('div', class_='module fight_card')
                    .find_all('a')):

                if main_card.find('span') and main_card.find(
                        'span').text not in self.fightsLinks:
                    self.fightsLinks.append("https://www.sherdog.com" + main_card['href'])

            for fight in (site.find('div', class_='content table')
                    .find_all('tr', {'itemprop': 'subEvent'})):
                for fighter in (fight
                        .find_all('td', {'itemprop': 'performer'})):
                    if fighter.a.text not in self.fightsLinks:
                        self.fightsLinks.append("https://www.sherdog.com" + fighter.a['href'])


    def _get_one(self,url):
        def dateDecoder(string):
            months = {'Jan': '01', 'Feb': '02', 'Mar': '03',
                      'Apr': '04', 'May': '05', 'Jun': '06',
                      'Jul': '07', 'Aug': '08', 'Sep': '09',
                      'Oct': '10', 'Nov': '11', 'Dec': '12'}
            new_date = string.split('/')
            return '-'.join([new_date[2].strip(), months[new_date[0].strip()],new_date[1].strip()])

        def tostr(elem):
            if type(elem) == list:
                return list(map(str, elem))
            else:
                return str(elem)

        fighter = {'Name': '',
                   'Nickname': '',
                   'Birth date': '',
                   'Height': '',
                   'Record': {'wins': '', 'loses': '', 'draws': '',
                              'nc': ''},
                   'Affiliation': '',
                   'Nationality': '',
                   'Location region': '',
                   'Location city': '',
                   'Weight': '',
                   'wins summary': {'KO/TKO': '', 'SUBMISSIONS': '',
                                    'DECISIONS': '', 'OTHERS': ''},
                   'loses summary': {'KO/TKO': '', 'SUBMISSIONS': '',
                                     'DECISIONS': '', 'OTHERS': ''},
                   'bouts': []}

        self.wd.get(url)
        site = BeautifulSoup(self.wd.page_source, 'html.parser')

        # fighters summary
        bio = site.find('div', class_='module bio_fighter vcard')

        if not site.find('div', class_='module bio_fighter tagged'):
            if len(bio.find('h1').find_all('span')) > 1:
                fighter['Name'], fighter['Nickname'] = \
                    [str(x.text) for x in bio.find('h1').find_all('span')]
            else:
                fighter['Name'] = str(bio.find('h1').find('span').text)
        else:
            fighter['Name'] = str(site.find('span', class_='fn').text)
            fighter['Nickname'] = \
                str(site.find('span', class_='nickname').text if
                site.find('span', class_='nickname') else '')

        fighter['Birth date'] = \
            str(bio.find('span', {'itemprop': 'birthDate'}).text if
                bio.find('span', {'itemprop': 'birthDate'}) else '')

        if re.search('(\d+\.\d+) cm',
                     bio.find('div', class_='size_info').find('span', class_='item height').text):

            fighter['Height'] = \
                (str(re.search('(\d+\.\d+) cm', bio.find('div', class_='size_info')
                              .find('span', class_='item height').text)[1]))

        if re.search('(\d+\.\d+) kg',
                     bio.find('div', class_='size_info').find('span',
                                                              class_='item weight').text):
            fighter['Weight'] = str(re.search('(\d+\.\d+) kg',
                                              bio.find('div',
                                                       class_='size_info').find(
                                                  'span',
                                                  class_='item weight').text)[1])
        fighter['Record']['wins'] = str(
            bio.find('span', class_='counter').text)
        fighter['Record']['loses'] = str(
            bio.find('div', class_='bio_graph loser').find('span',
                                                           class_='counter').text)

        if bio.find('div', class_='right_side'):
            for outs in bio.find('div', class_='right_side').find_all('div', class_='bio_graph'):
                if outs.find('span', 'result').text == 'Draws':
                    fighter['Record']['draws'] = str(outs.find('span', 'counter').text)
                if outs.find('span', 'result').text == 'N/C':
                    fighter['Record']['nc'] = str(outs.find('span', 'counter').text)

        bouts_summary = [re.match('\d+', x.text)[0] for x in bio.find_all('span', class_='graph_tag')]
        if len(bouts_summary) == 8:
            fighter['wins summary']['KO/TKO'], fighter['wins summary']['SUBMISSIONS'], fighter['wins summary'][
                'DECISIONS'], \
            fighter['wins summary']['OTHERS'] = tostr(bouts_summary[0:4])
            fighter['loses summary']['KO/TKO'], fighter['loses summary'][
                'SUBMISSIONS'], fighter['loses summary']['DECISIONS'], \
            fighter['loses summary']['OTHERS'] = tostr(bouts_summary[4:])
        else:
            fighter['wins summary']['KO/TKO'], fighter['wins summary'][
                'SUBMISSIONS'], fighter['wins summary'][
                'DECISIONS'] = tostr(bouts_summary[0:3])
            fighter['loses summary']['KO/TKO'], fighter['loses summary'][
                'SUBMISSIONS'], fighter['loses summary'][
                'DECISIONS'] = tostr(bouts_summary[3:])

        fighter['Nationality'] = str(bio.find('strong', {
            'itemprop': 'nationality'}).text if bio.find('strong', {
            'itemprop': 'nationality'}) else '')
        fighter['Affiliation'] = str(
            bio.find('a', class_='association').text if bio.find('a',
                                                                 class_='association') else '')

        if bio.find('span', class_='locality'):
            if ',' in bio.find('span', class_='locality').text:
                fighter['Location city'], fighter['Location region'] = tostr(
                    bio.find('span', class_='locality').text.split(','))
            else:
                fighter['Location city'] = str(bio.find('span', class_='locality').text)

        # fights description
        for history in site.find_all('div', class_='module fight_history'):
            if (re.search('Pro Exhibition', history.find('h2').text,
                          re.IGNORECASE) or
                    re.search('Amateur', history.find('h2').text,
                              re.IGNORECASE) or
                    re.search('Upcoming', history.find('h2').text,
                              re.IGNORECASE)): continue

            for bout in history.find_all('tr')[1:][::-1]:
                bout_info = {'result': '', 'opponent': '', 'event': '',
                             'date': '', 'method': '', 'referee': '',
                             'round': '', 'time': '', 'dc reason': ""}
                fight_info = bout.find_all('td')
                bout_info['result'] = str(fight_info[0].text)
                bout_info['opponent'] = str(fight_info[1].text)
                bout_info['event'] = str(fight_info[2].a.text)
                bout_info['date'] = str(dateDecoder(
                    fight_info[2].find('span', 'sub_line').text) if
                                        fight_info[2].find('span',
                                                           'sub_line') else '')
                bout_info['method'] = str(fight_info[3].contents[0])
                if len(fight_info[3].contents) == 2:
                    pass
                elif len(fight_info[3].contents[2]) == 1:
                    bout_info['referee'] = str(
                        fight_info[3].contents[2].text if
                        fight_info[3].contents[2] else '')
                else:
                    bout_info['referee'] = str(
                        fight_info[3].contents[4].text if str(
                            fight_info[3].contents[4]) != 'N/A' else '')
                    bout_info['dc reason'] = str(
                        unidecode(fight_info[3].contents[2]))

                bout_info['round'] = str(fight_info[4].text)
                bout_info['time'] = str(fight_info[5].text)
                fighter['bouts'].append(bout_info)

            return fighter
