'''
Created on Nov 23, 2017

@author: ghart
'''
from search.GameInfoGetters.GameInfoGetter import GameInfoGetter
from search.MockGenerator import generateMockInfo
from json import loads, dumps


def verifyOpen(filename):
    try: 
        return open(filename, 'r')
    except FileNotFoundError:
        generateMockInfo()
        try:
            return open(filename, 'r')
        except FileNotFoundError:
            raise RuntimeError('no such mock file as ' + str(filename))
    
class MockInfoGetter(GameInfoGetter):
    matches = dict()
    def getSummonerByName(self, name):
        if name != 'l am eternal':
            raise RuntimeError('no mock data for summoner ' + str(name))
        f = verifyOpen('search/mockSummoner')
        return loads(f.read())

    def getMatchlistBySummonerId(self, id, beginIndex, endIndex = None):
        if id != 50164289:
            raise RuntimeError(' no mock matchlist data for account id ' + str(id))
        f = verifyOpen('search/mockMatchlist')
        obj = loads(f.read())
        return obj
        
    def getMatchById(self, id):
        if len(self.matches) == 0:
            for i in range(0, 41):
                f = verifyOpen('search/mockGames/mockGame' + str(i))
                match = loads(f.read())
                self.matches[match['gameId']] = match
        return self.matches[id]
