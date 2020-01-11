import os
import json

class base():
    def __init__(self,site_name):
        self.cardsLinks = []
        self.fightsLinks = []
        self.fightersInfo = []
        self.fn_cards,self.fn_fights,self.fn_fighters = \
            [site_name + x +".json" for x in ["_cards","_fights","_fighters"]]
        self.names_ref = {self.fn_cards:self.cardsLinks,
                          self.fn_fights:self.fightsLinks,
                          self.fn_fighters:self.fightersInfo}


    def dump_archive(self,fname):
        self.names_ref[fname] = json.load(open(fname, 'r'))

    def load_archieve(self,fname):
        json.dump(self.names_ref[fname],open(fname, 'w'))


    def _cards_getter(self):
        pass

    def dl_cards(self):
        if os.path.isfile(self.fn_cards):
            self.load_archieve(self.fn_cards)
        else:
            self._cards_getter()
            self.dump_archive(self.fn_cards)

    def get_cards(self):
        return self.cardsLinks


    def _fights_getter(self):
        pass

    def dl_fights(self):
        "Extracts all links to the ufc fighters (or ex-fighters) profiles"
        if not self.cardsLinks:
            if os.path.isfile(self.fn_cards):
                self.load_archieve(self.fn_cards)
                self.dl_fights()
            else:
                self._cards_getter()
                self._fights_getter()
        else:
            self._fights_getter()
            self.dump_archive(self.fn_fights)

    def get_fights(self):
        return self.fightsLinks


    def _fighters_getter(self):
        pass

    def dl_fighters(self):
        if not self.fightsLinks:
            if os.path.isfile(self.fn_fights):
                self._update_archive(self.fn_fights, 'load')
                self.dl_fights()
            else:
                self._cards_getter()
                self._fights_getter()
        else:
            self._fights_getter()
            self._update_archive(self.fn_fights, 'dump')

    def get_fighters(self):
        pass
