
from search.GameInfoGetters.APIInfoGetter import APIInfoGetter
from json import dumps, loads

def generateMockInfo(prepend = 'search/'):

    gameinfo = APIInfoGetter()
    
    

    matchlist = dict()
    with open(prepend+'mockMatchlist', 'r') as f:
        matchlist = loads(f.read())
    index = 0
    for match in matchlist['matches']:
        matchinfo = gameinfo.getMatchById(match['gameId'])
        matchtl = gameinfo.getMatchTimelineById(match['gameId'])
        with open(prepend+'mockGames/mockGame' + str(index), 'w') as f:
            f.write(dumps(matchinfo))   
        with open(prepend+'mockGames/mockTimeline' + str(index), 'w') as f:
            f.write(dumps(matchtl))
        index+=1
if __name__ == '__main__':
    print('generating mock info from API')
    generateMockInfo(prepend = '')