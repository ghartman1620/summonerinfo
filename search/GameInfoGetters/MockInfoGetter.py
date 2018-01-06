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

    def getMatchlistBySummonerId(self, sId, beginIndex, endIndex = None):
        if sId != 50164289:
            raise RuntimeError(' no mock matchlist data for account id ' + str(sId))
        f = verifyOpen('search/mockMatchlist')
        obj = loads(f.read())
        
        if endIndex != None:
            if endIndex > 41:
                raise RuntimeError('bad endIndex for MockInfoGetter.getMatchlistBySummonerId')
            obj['matches'] = obj['matches'][0:endIndex]
        return obj
    def checkMatchInfo(self):
        if len(self.matches) == 0:
            for i in range(0, 41):
                f = verifyOpen('search/mockGames/mockGame' + str(i))
                match = loads(f.read())
                f2 = verifyOpen('search/mockGames/mockTimeline' + str(i))
                matchtl = loads(f2.read())
                self.matches[match['gameId']] = (match, matchtl)
    def getMatchById(self, id):
        self.checkMatchInfo()
        return self.matches[id][0]

    def getMatchTimelineById(self, id):
        self.checkMatchInfo()
        return self.matches[id][1]