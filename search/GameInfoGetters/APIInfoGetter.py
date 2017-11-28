#This class gets info about actual League games from the
#riot games API.

from urllib.request import urlopen
from urllib.error import HTTPError
from json import loads
from search.GameInfoGetters.GameInfoGetter import GameInfoGetter
from time import sleep


API_KEY = 'RGAPI-1c447349-877a-449e-bff4-6d4bd5d71d5d'
def jsonFromUrl(url):
    
    callSuccess = False
    while not callSuccess:
        try:
            print('GET from ' + url)
            txt = urlopen(url).read().decode('utf-8')
            callSuccess = True
        except HTTPError as e:
            if( e.code == 429):
                print("too many api calls. Trying again in 10 seconds.")
                sleep(10)
            else:
                raise(e)
    return loads(txt)
    
class APIInfoGetter(GameInfoGetter):


        
    def getSummonerByName(self, name):
        nameSpaces = name.replace(' ', '%20')
        jsonObj = jsonFromUrl('https://na1.api.riotgames.com/lol/summoner/v3/summoners/by-name/'
                + nameSpaces + '?api_key=' + API_KEY)
        return jsonObj
        

    def getMatchlistBySummonerId(self, id, beginIndex, endIndex = None):
        matches = None
        if endIndex == None:
            matches = jsonFromUrl('https://na1.api.riotgames.com/lol/match/v3/matchlists/by-account/'
                    + str(id) + '?beginIndex='+ str(beginIndex) + '&api_key='+ API_KEY)
        else:
            matches = jsonFromUrl('https://na1.api.riotgames.com/lol/match/v3/matchlists/by-account/'
                    + str(id) + '?beginIndex='+ str(beginIndex) + '&api_key='+ API_KEY + '&endIndex=' + str(endIndex))
        return matches
        

    def getMatchById(self, id):
        jsonObj = jsonFromUrl('https://na1.api.riotgames.com/lol/match/v3/matches/' + str(id) + '?api_key=' + API_KEY)
        return jsonObj
        
        