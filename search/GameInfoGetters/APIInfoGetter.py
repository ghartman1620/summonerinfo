#This class gets info about actual League games from the
#riot games API.

from urllib.request import urlopen
from urllib.error import HTTPError
from json import loads
from search.GameInfoGetters.GameInfoGetter import GameInfoGetter
from time import sleep
from summonerinfo.settings import DEBUG

API_KEY = ''
with open('api-key', 'r') as f:
    API_KEY = f.read()

def jsonFromUrl(url):
    
    callSuccess = False
    while not callSuccess:
        try:
            print('GET from ' + url)
            txt = urlopen(url).read().decode('utf-8')
            callSuccess = True
        except HTTPError as e:
            if e.code == 429:
                print("429: too many api calls. Trying again in 10 seconds.")
                sleep(10)
            else:
                if DEBUG:
                    raise(e)
                else:
                    raise RuntimeError('Looks like there\'s a problem with the riot games API or you put in an invalid summoner name. Try again in a minute.')
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
        
    def getMatchTimelineById(self, id):
        return jsonFromUrl('https://na1.api.riotgames.com/lol/match/v3/timelines/by-match/'+ str(id) + '?api_key='+str(API_KEY))
    
