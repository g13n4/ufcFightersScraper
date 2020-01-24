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
        print(f"number of fighters loaded: {self.size_fighters}")

    def dump_archive(self,fname):
        """dumps fname file"""
        json.dump(self.names_ref[fname], open(fname, 'w'))
        print(f"{fname} dump is created")

    def load_archive(self, fname):
        """loads fname file"""
        self.names_ref[fname].extend(json.load(open(fname, 'r')))
        print(f"{fname} dump is loaded")

    def _remove_duplicates(self):
        self.fightsLinks = list(set(self.fightsLinks))

    def _cards_getter(self):
        """downloads sites and extracts links from them"""
        pass

    def dl_cards(self, reload=False, from_archive=False):
        """helper to reduce redundancy in cards dumps/uploads"""
        if self.cardsLinks and not reload and not from_archive:
            print("cards are in memory")
            self.dump_archive(self.fn_cards)
        elif (os.path.isfile(self.fn_cards) and not reload) or from_archive:
            print("archived json of cards is found")
            self.load_archive(self.fn_cards)
            self.size_cards = len(self.cardsLinks)
        else:
            print("downloading cards")
            self._cards_getter()
            self.dump_archive(self.fn_cards)
            self.size_cards = len(self.cardsLinks)

    def _fights_getter(self):
        """downloads cards sites and extracts fighters links from them"""
        pass

    def dl_fights(self, reload=False, from_archive=False):
        """helper to reduce redundancy in fights dumps/loads"""
        if self.fightsLinks and not reload and not from_archive:
            print("bouts are in memory")
            self.dump_archive(self.fn_fights)
        elif (os.path.isfile(self.fn_fights) and not reload) or from_archive:
            print("archived json of bouts is found")
            self.load_archive(self.fn_fighters)
            self.size_fights = len(self.fightsLinks)
        else:
            self.dl_cards()
            print("downloading bouts")
            self._fights_getter()
            self._remove_duplicates()
            self.dump_archive(self.fn_fights)
            self.size_fights = len(self.fightsLinks)

    def _fighters_getter(self, offset=0):
        fighters_len = len(self.fightsLinks)
        print(f"{fighters_len} fighters to download")
        for idx, link in enumerate(self.fightsLinks[offset:], offset):
            self.fightersInfo.append(self._get_one(link))
            if not (idx % 50):
                print(f"{fighters_len - idx} fighters are left to download")
        print(f"All done")

    def _get_one(self,url):
        """get one fighter's info"""
        pass

    def dl_fighters(self, reload=False, from_archive=False):
        """helper that reduces redundancy"""
        if self.fightersInfo and not reload and not from_archive:
            print("fighters are in memory")
            self.dump_archive(self.fn_fighters)
        elif os.path.isfile(self.fn_fighters) and not reload:
            self.load_archive(self.fn_fighters)
        else:
            self.dl_fights()
            self._fighters_getter()
            self.dump_archive(self.fn_fighters)
            self.size_fighters = len(self.fightersInfo)
