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
        "dumps fname file"
        self.names_ref[fname] = json.load(open(fname, 'r'))

    def load_archieve(self,fname):
        "loads fname file "
        json.dump(self.names_ref[fname],open(fname, 'w'))


    def _cards_getter(self):
        "downloads sites and extracts links from them"
        pass

    def dl_cards(self):
        "helper to reduce redundancy in cards dumps/uploads"
        if os.path.isfile(self.fn_cards):
            self.load_archieve(self.fn_cards)
        else:
            self._cards_getter()
            self.dump_archive(self.fn_cards)

    def get_cards(self):
        "returns cards"
        return self.cardsLinks


    def _fights_getter(self):
        "downloads cards sites and extracts fighters links from them"
        pass

    def dl_fights(self):
        "helper to reduce redundancy in fights dumps/loads"
        if not self.cardsLinks:
            if os.path.isfile(self.fn_cards):
                self.load_archieve(self.fn_cards)
                self.dl_fights()
            else:
                self._cards_getter()
                self.dl_fights()
        else:
            self._fights_getter()
            self.dump_archive(self.fn_fights)

    def get_fights(self):
        "return links to fighters profiles"
        return self.fightsLinks


    def _fighters_getter(self):
        "uses links to get the information about the fighters. One at a time"
        pass

    def dl_fighters(self):
        "helper that reduces redundancy"
        if not self.fightsLinks:
            if os.path.isfile(self.fn_fights):
                self.load_archieve(self.fn_fights)
                self.dl_fighters()
            else:
                self._fights_getter()
                self.dl_fighters()
        else:
            self._fights_getter()
            self.dump_archive(self.fn_fights)

    def get_fighters(self):
        "return information about the fighters"
        pass
