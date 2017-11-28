'''
Created on Nov 23, 2017

@author: ghart
'''

from search.GameInfoGetters.GameInfoGetter import GameInfoGetter
from search.GameInfoGetters.APIInfoGetter import APIInfoGetter
from search.models import Match
from json import dumps, loads

class DBAPIInfoGetter(GameInfoGetter):
    gameinfo = APIInfoGetter()
    def getSummonerByName(self, name):
        return self.gameinfo.getSummonerByName(name)

    def getMatchlistBySummonerId(self, id, beginIndex, endIndex = None):
        return self.gameinfo.getMatchlistBySummonerId(id,beginIndex,endIndex)
    
    def getMatchById(self, id):
        try:
            match = Match.objects.get(gameId=id)
            match = loads(match.jsonString)
            print('GET match ' + str(id) + ' from db successful')
        except Match.DoesNotExist:
            match = self.gameinfo.getMatchById(id)
            matchModel = Match.objects.create(gameId = match['gameId'], jsonString=dumps(match))
            matchModel.save()
            print('Adding match ' + str(id) + 'to DB')
            
        return match