'''
Created on Nov 23, 2017

@author: ghart
'''

from search.GameInfoGetters.GameInfoGetter import GameInfoGetter
from search.GameInfoGetters.APIInfoGetter import APIInfoGetter
from search.models import Match, MatchTimeline
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
            print('GET match ' + str(id) + ' from db')
        except Match.DoesNotExist:
            match = self.gameinfo.getMatchById(id)
            matchModel = Match.objects.create(gameId = match['gameId'], jsonString=dumps(match))
            matchModel.save()
            print('Adding match ' + str(id) + 'to DB')
            
        return match
    #TODO: make timelines saved in database.
    def getMatchTimelineById(self,id):
        try:
            timeline = MatchTimeline.objects.get(gameId=id)
            timeline = loads(timeline.jsonString)
            print('GET match timeline ' + str(id) + 'from db')
        except MatchTimeline.DoesNotExist:
            timeline = self.gameinfo.getMatchTimelineById(id)
            matchTimeline = MatchTimeline.objects.create(gameId= id, jsonString = dumps(timeline))
            matchTimeline.save()
            print('adding match timeline ' + str(id) + 'to db')
        return timeline