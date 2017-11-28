
from search.GameInfoGetters.APIInfoGetter import APIInfoGetter
from json import dumps, loads

def generateMockInfo(prepend = 'search/'):

    gameinfo = APIInfoGetter()
    
    
    summ = gameinfo.getSummonerByName('l am eternal')
    with open(prepend+'mockSummoner', 'w') as f:
        f.write(dumps(summ))
    matchlist = dict()
    with open(prepend+'mockMatchlist', 'r') as f:
        matchlist = loads(f.read())
    index = 0
    for match in matchlist['matches']:
        matchinfo = gameinfo.getMatchById(match['gameId'])
        with open(prepend+'mockGames/mockGame' + str(index), 'w') as f:
            f.write(dumps(matchinfo))
        index+=1
if __name__ == '__main__':
    print('generating mock info from API')
    generateMockInfo(prepend = '')