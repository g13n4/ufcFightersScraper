import copy
import json
import re
from urllib.request import urlopen

from bs4 import BeautifulSoup
from unidecode import unidecode

from .base import base

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
        for offset, link in enumerate(self.fightsLinks, 1058):
            self.fightersInfo.append(self._get_one(link))

    def _get_one(self,url):
        """get one fighter's info"""
        site = BeautifulSoup(urlopen(url), 'html.parser')

        fighter = {'Name': '',
                   'Nickname': '',
                   'Weight': '',
                   'Height': '',
                   'Reach': '',
                   'STANCE': '',
                   'DOB': '',
                   'Carrer stats': {"SLpM": '',
                                    'Str. Acc.': '',
                                    'SApM': '',
                                    'Str. Def': '',
                                    'TD Avg.': '',
                                    "TD Acc.": "",
                                    "TD Def.": '',
                                    "Sub. Avg.": ''},
                   'bouts': []}

        fighter['Name'] = site.find('h2', class_='b-content__title').span.text.strip()
        fighter['Nickname'] = site.find('p',
                                        class_='b-content__Nickname').text.strip() if site.find(
            'p', class_='b-content__Nickname') else ''

        for line in site.find('ul', class_='b-list__box-list').find_all('li'):
            fighter[line.contents[1].text.strip()[:-1]] = unidecode(
                line.contents[2]).strip()
        if fighter['Reach'] == '--': fighter['Reach'] = ''

        for line in site.find('div',
                              class_='b-list__info-box-left clearfix').find_all(
            'li'):
            if line.find('i').text == '\n': continue
            fighter['Carrer stats'][
                line.contents[1].text.strip()[:-1]] = unidecode(
                line.contents[2]).strip()

        for bout in site.find('tbody',
                              class_='b-fight-details__table-body').find_all(
            'tr', onclick=True):
            fighter['bouts'].append(self.bout_info_extractor(bout['data-link']))

        return fighter

    def bout_info_extractor(self, url):
        "extracts all information about a bout"
        site = BeautifulSoup(urlopen(url), 'html.parser')

        bout_info = {'Card name': '',
                     'Bout name': '',
                     "fight bonus": '',
                     'perf bonus': '',
                     'sub bonus': '',
                     'ko bonus': '',
                     'Method': '',
                     'Round': '',
                     'title fight': '',
                     'Details': '',
                     'Score 1': '',
                     'Score 2': '',
                     'Score 3': '',
                     'Fighter1 stats': {
                         'Totals': {'Name': '',
                                    'KD': '',
                                    'SIG. STR.': {'attempted': '',
                                                  'landed': ''},
                                    'SIG. STR. %': '',
                                    'TOTAL STR.': {'attempted': '',
                                                   'landed': ''},
                                    'TD': {'attempted': '', 'landed': ''},
                                    'TD %': '',
                                    'SUB. ATT': '',
                                    'PASS': '',
                                    'REV.': ''},

                         'Totals per Round': [],

                         'Significant Strikes': {'Name': '',
                                                 'SIG. STR.': {
                                                     'attempted': '',
                                                     'landed': ''},
                                                 'SIG. STR. %': '',
                                                 'HEAD': {'attempted': '',
                                                          'landed': ''},
                                                 'BODY': {'attempted': '',
                                                          'landed': ''},
                                                 'LEG': {'attempted': '',
                                                         'landed': ''},
                                                 'DISTANCE': {
                                                     'attempted': '',
                                                     'landed': ''},
                                                 'CLINCH': {
                                                     'attempted': '',
                                                     'landed': ''},
                                                 'GROUND': {
                                                     'attempted': '',
                                                     'landed': ''}},

                         'Significant Strikes per Round': [],
                     },

                     'Fighter2 stats': {
                         'Totals': {'Name': '',
                                    'KD': '',
                                    'SIG. STR.': {'attempted': '',
                                                  'landed': ''},
                                    'SIG. STR. %': '',
                                    'TOTAL STR.': {'attempted': '',
                                                   'landed': ''},
                                    'TD': {'attempted': '', 'landed': ''},
                                    'TD %': '',
                                    'SUB. ATT': '',
                                    'PASS': '',
                                    'REV.': ''},

                         'Totals per Round': [],

                         'Significant Strikes': {
                             'Name': '',
                             'SIG. STR.': {'attempted': '', 'landed': ''},
                             'SIG. STR. %': '',
                             'HEAD': {'attempted': '', 'landed': ''},
                             'BODY': {'attempted': '', 'landed': ''},
                             'LEG': {'attempted': '', 'landed': ''},
                             'DISTANCE': {'attempted': '', 'landed': ''},
                             'CLINCH': {'attempted': '', 'landed': ''},
                             'GROUND': {'attempted': '', 'landed': ''}},

                         'Significant Strikes per Round': [],
                     },

                     'Fighter1': {'Result': '', 'Name': '', },
                     'Fighter2': {'Result': '', 'Name': '', }}

        totals_round = {'Round': '',
                        'Name': '',
                        'KD': '',
                        'SIG. STR.': {'attempted': '', 'landed': ''},
                        'SIG. STR. %': '',
                        'TOTAL STR.': {'attempted': '', 'landed': ''},
                        'TD': {'attempted': '', 'landed': ''},
                        'TD %': '',
                        'SUB. ATT': '',
                        'PASS': '',
                        'REV.': ''}

        sigstrikes_round = {'Name': '', 'Round': '',
                            'SIG. STR.': {'attempted': '', 'landed': ''},
                            'SIG. STR. %': '',
                            'HEAD': {'attempted': '', 'landed': ''},
                            'BODY': {'attempted': '', 'landed': ''},
                            'LEG': {'attempted': '', 'landed': ''},
                            'DISTANCE': {'attempted': '', 'landed': ''},
                            'CLINCH': {'attempted': '', 'landed': ''},
                            'GROUND': {'attempted': '', 'landed': ''}}

        # Card name
        bout_info['Card name'] = site.find('a',
                                           class_='b-link').text.strip()
        bout_info['Bout name'] = site.find('i',
                                           class_='b-fight-details__fight-title').text.strip()
        bout_info['Fighter1']['Result'], bout_info['Fighter2'][
            'Result'] = [x.text.strip() for x in site.find('div',
                                                           class_='b-fight-details__persons clearfix').find_all(
            'i')]
        bout_info['Fighter1']['Name'], bout_info['Fighter2']['Name'] = [
            x.text.strip() for x in site.find('div',
                                              class_='b-fight-details__persons clearfix').find_all(
                'h3')]
        bout_info['Fighter1']['Nickname'], bout_info['Fighter2'][
            'Nickname'] = [x.text.strip()[1:-1] for x in site.find('div',
                                                                   class_='b-fight-details__persons clearfix').find_all(
            'p')]
        for bonus in site.find('i',
                               class_='b-fight-details__fight-title').find_all(
            'img'):
            if re.search('/(\w+).png', bonus['src'])[1] == 'belt':
                bout_info['title fight'] = True
            else:
                bout_info[re.search('/(\w+).png', bonus['src'])[
                              1] + ' bonus'] = True
        # Methods
        method = site.find('p', class_="b-fight-details__text").find('i',
                                                                     'b-fight-details__text-item_first').contents
        bout_info[method[1].text.strip()[:-1]] = method[3].text.strip()
        descs = site.find('p', class_="b-fight-details__text").find_all(
            'i', class_="b-fight-details__text-item")
        bout_info[descs[0].contents[1].text.strip()[:-1]] = \
            descs[0].contents[2].strip()
        bout_info[descs[1].contents[1].text.strip()[:-1]] = \
            descs[1].contents[2].strip()
        bout_info[descs[2].contents[1].text.strip()[:-1]] = \
            descs[2].contents[2].strip()
        bout_info[descs[3].contents[1].text.strip()[:-1]] = \
            descs[3].contents[3].text.strip()

        # Refs or details
        if len(site.find_all('p', class_='b-fight-details__text')[
                   1].find_all('i', 'b-fight-details__text-item')) == 3:
            cards = site.find_all('p', class_='b-fight-details__text')[
                1].find_all('i', 'b-fight-details__text-item')

            bout_info['Score 1'] = {'Name': cards[0].contents[1].text}
            bout_info['Score 1']['Fighter1'], bout_info['Score 1'][
                'Fighter2'] = cards[0].contents[2].strip()[:-1].split('-')

            bout_info['Score 2'] = {'Name': cards[0].contents[1].text}
            bout_info['Score 2']['Fighter1'], bout_info['Score 2'][
                'Fighter2'] = cards[1].contents[2].strip()[:-1].split('-')

            bout_info['Score 3'] = {'Name': cards[0].contents[1].text}
            bout_info['Score 3']['Fighter1'], bout_info['Score 3'][
                'Fighter2'] = cards[2].contents[2].strip()[:-1].split('-')
        else:
            bout_info['Details'] = \
                site.find_all('p', class_='b-fight-details__text')[1].contents[
                    2].strip()

        if not site.find('section',
                         class_='b-fight-details__section js-fight-section').find(
            'p'):
            return bout_info

        stats = site.find_all('tbody',
                              class_='b-fight-details__table-body')

        # Totals
        f1, f2 = bout_info['Fighter1 stats']['Totals'], \
                 bout_info['Fighter2 stats']['Totals']
        totals_head = stats[0].find_all('td')
        f1['Name'], f2['Name'] = [x.text.strip() for x in
                                  totals_head[0].find_all('p')]
        f1['KD'], f2['KD'] = [x.text.strip() for x in
                              totals_head[1].find_all('p')]
        f1['SIG. STR.']['landed'], f1['SIG. STR.']['attempted'], \
        f2['SIG. STR.']['landed'], f2['SIG. STR.']['attempted'] = [
            a.strip() for x in totals_head[2].find_all('p') for a in
            x.text.split('of')]
        f1['SIG. STR. %'], f2['SIG. STR. %'] = [x.text.strip() for x in
                                                totals_head[3].find_all(
                                                    'p')]
        f1['TOTAL STR.']['landed'], f1['TOTAL STR.']['attempted'], \
        f2['TOTAL STR.']['landed'], f2['TOTAL STR.']['attempted'] = [
            a.strip() for x in totals_head[4].find_all('p') for a in
            x.text.split('of')]
        f1['TD']['landed'], f1['TD']['attempted'], f2['TD']['landed'], \
        f2['TD']['attempted'] = [a.strip() for x in
                                 totals_head[5].find_all('p') for a in
                                 x.text.split('of')]
        f1['TD %'], f2['TD %'] = [x.text.strip() for x in
                                  totals_head[6].find_all('p')]
        f1['SUB. ATT'], f2['SUB. ATT'] = [x.text.strip() for x in
                                          totals_head[7].find_all('p')]
        f1['PASS'], f2['PASS'] = [x.text.strip() for x in
                                  totals_head[8].find_all('p')]
        f1['REV.'], f2['REV.'] = [x.text.strip() for x in
                                  totals_head[9].find_all('p')]

        # TotalsPR
        totals_per_round = stats[1].find_all('td')

        for col_index in range(0, len(totals_per_round), 10):
            fighter1round = copy.deepcopy(totals_round)
            fighter2round = copy.deepcopy(totals_round)

            fighter1round['Round'], fighter2round['Round'] = \
                [f'{(col_index // 10) + 1}'] * 2
            fighter1round['Name'], fighter2round['Name'] = [x.text.strip()
                                                            for x in
                                                            totals_per_round[
                                                                0 + col_index].find_all(
                                                                'p')]
            fighter1round['KD'], fighter2round['KD'] = [x.text.strip() for
                                                        x in
                                                        totals_per_round[
                                                            1 + col_index].find_all(
                                                            'p')]
            fighter1round['SIG. STR.']['landed'], \
            fighter1round['SIG. STR.']['attempted'], \
            fighter2round['SIG. STR.']['landed'], \
            fighter2round['SIG. STR.']['attempted'] = [a.strip() for x in
                                                       totals_per_round[
                                                           2 + col_index].find_all(
                                                           'p') for a in
                                                       x.text.split('of')]
            fighter1round['SIG. STR. %'], fighter2round['SIG. STR. %'] = [
                x.text.strip() for x in
                totals_per_round[3 + col_index].find_all('p')]
            fighter1round['TOTAL STR.']['landed'], \
            fighter1round['TOTAL STR.']['attempted'], \
            fighter2round['TOTAL STR.']['landed'], \
            fighter2round['TOTAL STR.']['attempted'] = [a.strip() for x in
                                                        totals_per_round[
                                                            4 + col_index].find_all(
                                                            'p') for a in
                                                        x.text.split('of')]
            fighter1round['TD']['landed'], fighter1round['TD'][
                'attempted'], fighter2round['TD']['landed'], \
            fighter2round['TD']['attempted'] = [a.strip() for x in
                                                totals_per_round[
                                                    5 + col_index].find_all(
                                                    'p') for a in
                                                x.text.split('of')]
            fighter1round['TD %'], fighter2round['TD %'] = [x.text.strip()
                                                            for x in
                                                            totals_per_round[
                                                                6 + col_index].find_all(
                                                                'p')]
            fighter1round['SUB. ATT'], fighter2round['SUB. ATT'] = [
                x.text.strip() for x in
                totals_per_round[7 + col_index].find_all('p')]
            fighter1round['PASS'], fighter2round['PASS'] = [x.text.strip()
                                                            for x in
                                                            totals_per_round[
                                                                8 + col_index].find_all(
                                                                'p')]
            fighter1round['REV.'], fighter2round['REV.'] = [x.text.strip()
                                                            for x in
                                                            totals_per_round[
                                                                9 + col_index].find_all(
                                                                'p')]

            bout_info['Fighter1 stats']['Totals per Round'].append(
                dict(fighter1round))
            bout_info['Fighter2 stats']['Totals per Round'].append(
                dict(fighter2round))

        # Sigs
        sig_strikes = stats[2].find_all('td')
        f1, f2 = bout_info['Fighter1 stats']['Significant Strikes'], \
                 bout_info['Fighter2 stats']['Significant Strikes']

        f1['Name'], f2['Name'] = [x.text.strip() for x in
                                  totals_head[0].find_all('p')]
        f1['SIG. STR.']['landed'], f1['SIG. STR.']['attempted'], \
        f2['SIG. STR.']['landed'], f2['SIG. STR.']['attempted'] = [
            a.strip() for x in sig_strikes[1].find_all('p') for a in
            x.text.split('of')]
        f1['SIG. STR. %'], f2['SIG. STR. %'] = [x.text.strip() for x in
                                                sig_strikes[2].find_all(
                                                    'p')]
        f1['HEAD']['landed'], f1['HEAD']['attempted'], f2['HEAD'][
            'landed'], f2['HEAD']['attempted'] = [a.strip() for x in
                                                  sig_strikes[3].find_all(
                                                      'p') for a in
                                                  x.text.split('of')]
        f1['BODY']['landed'], f1['BODY']['attempted'], f2['BODY'][
            'landed'], f2['BODY']['attempted'] = [a.strip() for x in
                                                  sig_strikes[4].find_all(
                                                      'p') for a in
                                                  x.text.split('of')]
        f1['LEG']['landed'], f1['LEG']['attempted'], f2['LEG']['landed'], \
        f2['LEG']['attempted'] = [a.strip() for x in
                                  sig_strikes[5].find_all('p') for a in
                                  x.text.split('of')]
        f1['DISTANCE']['landed'], f1['DISTANCE']['attempted'], \
        f2['DISTANCE']['landed'], f2['DISTANCE']['attempted'] = [a.strip()
                                                                 for x in
                                                                 sig_strikes[
                                                                     6].find_all(
                                                                     'p')
                                                                 for a in
                                                                 x.text.split(
                                                                     'of')]
        f1['CLINCH']['landed'], f1['CLINCH']['attempted'], f2['CLINCH'][
            'landed'], f2['CLINCH']['attempted'] = [a.strip() for x in
                                                    sig_strikes[
                                                        7].find_all('p')
                                                    for a in
                                                    x.text.split('of')]
        f1['GROUND']['landed'], f1['GROUND']['attempted'], f2['GROUND'][
            'landed'], f2['GROUND']['attempted'] = [a.strip() for x in
                                                    sig_strikes[
                                                        8].find_all('p')
                                                    for a in
                                                    x.text.split('of')]

        # SigsPR

        sig_strikes_per_round = stats[3].find_all('td')

        for col_index in range(0, len(sig_strikes_per_round), 9):
            fighter1round = copy.deepcopy(sigstrikes_round)
            fighter2round = copy.deepcopy(sigstrikes_round)

            fighter1round['Round'], fighter2round['Round'] = \
                [f'{((col_index + 3) // 10) + 1}'] * 2
            fighter1round['Name'], fighter2round['Name'] = [x.text.strip()
                                                            for x in
                                                            sig_strikes_per_round[
                                                                0 + col_index].find_all(
                                                                'p')]
            fighter1round['SIG. STR.']['landed'], \
            fighter1round['SIG. STR.']['attempted'], \
            fighter2round['SIG. STR.']['landed'], \
            fighter2round['SIG. STR.']['attempted'] = [a.strip() for x in
                                                       sig_strikes_per_round[
                                                           1 + col_index].find_all(
                                                           'p') for a in
                                                       x.text.split('of')]
            fighter1round['SIG. STR. %'], fighter2round['SIG. STR. %'] = [
                x.text.strip() for x in
                sig_strikes_per_round[2 + col_index].find_all('p')]
            fighter1round['HEAD']['landed'], fighter1round['HEAD'][
                'attempted'], fighter2round['HEAD']['landed'], \
            fighter2round['HEAD']['attempted'] = [a.strip() for x in
                                                  sig_strikes_per_round[
                                                      3 + col_index].find_all(
                                                      'p') for a in
                                                  x.text.split('of')]
            fighter1round['BODY']['landed'], fighter1round['BODY'][
                'attempted'], fighter2round['BODY']['landed'], \
            fighter2round['BODY']['attempted'] = [a.strip() for x in
                                                  sig_strikes_per_round[
                                                      4 + col_index].find_all(
                                                      'p') for a in
                                                  x.text.split('of')]
            fighter1round['LEG']['landed'], fighter1round['LEG'][
                'attempted'], fighter2round['LEG']['landed'], \
            fighter2round['LEG']['attempted'] = [a.strip() for x in
                                                 sig_strikes_per_round[
                                                     5 + col_index].find_all(
                                                     'p') for a in
                                                 x.text.split('of')]
            fighter1round['DISTANCE']['landed'], fighter1round['DISTANCE'][
                'attempted'], fighter2round['DISTANCE']['landed'], \
            fighter2round['DISTANCE']['attempted'] = [a.strip() for x in
                                                      sig_strikes_per_round[
                                                          6 + col_index].find_all(
                                                          'p') for a in
                                                      x.text.split('of')]
            fighter1round['CLINCH']['landed'], fighter1round['CLINCH'][
                'attempted'], fighter2round['CLINCH']['landed'], \
            fighter2round['CLINCH']['attempted'] = \
                [a.strip() for x in sig_strikes_per_round[7 + col_index].find_all('p') for a in x.text.split('of')]
            fighter1round['GROUND']['landed'], fighter1round['GROUND'][
                'attempted'], fighter2round['GROUND']['landed'], \
            fighter2round['GROUND']['attempted'] = [a.strip() for x in
                                                    sig_strikes_per_round[
                                                        8 + col_index].find_all(
                                                        'p') for a in
                                                    x.text.split('of')]

            bout_info['Fighter1 stats'][
                'Significant Strikes per Round'].append(dict(fighter1round))
            bout_info['Fighter2 stats']['Significant Strikes per Round'].append(dict(fighter2round))

        return bout_info
