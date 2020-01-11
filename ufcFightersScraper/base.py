import os
import json

class base():
    def __init__(self,site_name):
        self.cardsLinks = []
        self.fightersLinks = []
        self.fightersInfo = []
        self.fn_cards,self.fn_fights,self.fn_fighters = \
            [site_name + x +".json" for x in ["_cards","_fights","_fighters"]]
        self.names_ref = {self.fn_cards:self.cardsLinks,
                          self.fn_fights:self.fightersLinks,
                          self.fn_fighters:self.fightersInfo}

    def _update_archive(self,fname,dir):
        if dir == 'dump':
            json.dump(self.names_ref[fname],
                      open(fname, 'w'))
        elif dir == 'load':
            self.names_ref[fname] = \
                json.load(open(fname, 'r'))
        else:
            raise NameError

    def _cards_getter(self):
        pass

    def dl_cards(self):
        if os.path.isfile(self.fn_cards):
            self._update_archive(self.fn_cards,'load')
        else:
            self._cards_getter()
            self._update_archive(self.fn_cards, 'dump')

    def get_cards(self):
        return self.cardsLinks

    def _fights_getter(self):
        pass

    def dl_fights(self):
        "Extracts all links to the ufc fighters (or ex-fighters) profiles"
        if not self.cardsLinks:
            if os.path.isfile(self.fn_cards):
                self._update_archive(self.fn_fights,'load')
                self.dl_fights()
            else:
                self._cards_getter()
                self._fights_getter()
        else:
            self._fights_getter()
            self._update_archive(self.fn_fights,'dump')
