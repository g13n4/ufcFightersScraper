import json
import os

class base():
    def __init__(self,site_name):
        self.cardsLinks, self.fightsLinks, self.fightersInfo = [], [], []
        self.fn_cards,self.fn_fights,self.fn_fighters = \
            [site_name + x +".json" for x in ["_cards","_fights","_fighters"]]
        self.names_ref = {self.fn_cards:self.cardsLinks,
                          self.fn_fights:self.fightsLinks,
                          self.fn_fighters:self.fightersInfo}
        self.size_cards, self.size_fights, self.size_fighters = 0, 0, 0

    def __call__(self):
        print(f"number of cards loaded: {self.size_cards}")
        print(f"number of cards' bouts loaded: {self.size_fights}")
        print(f"number of fighters loaded {self.size_fighters}")

    def dump_archive(self,fname):
        """dumps fname file"""
        json.dump(self.names_ref[fname], open(fname, 'w'))

    def load_archieve(self,fname):
        """loads fname file"""
        self.names_ref[fname].extend(json.load(open(fname, 'r')))

    def _cards_getter(self):
        """downloads sites and extracts links from them"""
        pass

    def dl_cards(self):
        """helper to reduce redundancy in cards dumps/uploads"""
        if os.path.isfile(self.fn_cards):
            self.load_archieve(self.fn_cards)
            self.size_cards = len(self.cardsLinks)
        else:
            self._cards_getter()
            self.dump_archive(self.fn_cards)
            self.size_cards = len(self.cardsLinks)

    def get_cards(self):
        """returns cards"""
        return self.cardsLinks

    def _fights_getter(self):
        """downloads cards sites and extracts fighters links from them"""
        pass

    def dl_fights(self):
        """helper to reduce redundancy in fights dumps/loads"""
        if os.path.isfile(self.fn_fights):
            self.load_archieve(self.fn_fighters)
            self.size_fights = len(self.fightsLinks)
        else:
            self.dl_cards()
            self._fights_getter()
            self.dump_archive(self.fn_fights)
            self.size_fights = len(self.fightsLinks)

    def get_fights(self):
        """return links to fighters profiles"""
        return self.fightsLinks

    def _fighters_getter(self):
        """uses links to get the information about the fighters. One at a time"""
        pass

    def _get_one(self,url):
        """get one fighter's info"""
        pass

    def dl_fighters(self):
        """helper that reduces redundancy"""
        if os.path.isfile(self.fn_fighters):
            self.load_archieve(self.fn_fighters)
        else:
            self.dl_fights()
            self._fighters_getter()
            self.dump_archive(self.fn_fighters)

    def get_fighters(self):
        """return information about the fighters"""
        return self.fightersInfo
