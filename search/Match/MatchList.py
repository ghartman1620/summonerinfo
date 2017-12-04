from datetime import datetime
from search.Match.Match import Match
from search.WinrateTypes.WinrateByTimeOfDay import WinrateByTimeOfDay
from search.WinrateTypes.WinrateByOtherSummoner import WinrateByOtherSummoner
from datetime import datetime
import math
    
def getMatchesFromMatchlist(matchlist, gameinfo, season, queue, summonerName):
    matchDetails = []
    if len(matchlist['matches']) == 0: return []
    else:
        for match in matchlist['matches']:
            isValid = True if season == None else season.value == match['season']
            if isValid:
                isValid = True if queue == None else queue.value == match['queue']
            
            if isValid:
                matchDetails.append(Match(gameinfo.getMatchById(match['gameId']), summonerName, match['timestamp']))
    return matchDetails
'''
Matchlist contains a list of MatchDtos, the value returned by a call to get match by match Id.
The constructor enables callers to filter MatchLists to certain sorts of matches
Other methods perform diagnostics on those matches.
'''
class MatchList():
    matches = []
    summoner = ''
    season = 0
    queue = 0
    def __str__(self):
        return str(len(self.matches)) + ' matches analyzed. ' +(('queue: ' + str(self.queue)) if self.queue != None else '') + \
            (('season: ' + str(self.season)) if self.season != None else '')
    '''
    Create a new MatchList querying the given gameinfo for games that match the parameter criteria.
    @param gameinfo The GameInfoGetter object to be queried.
    @param summonerName the summoner whose matches are searched for
    @param maxMatches the maximum number of matches that will be queried. NOT the number of matches to be in the matchlist.
    @param season the season to include games from. Note that if a low number of maxMatches is specified and an old season then there will probably be no games in this MatchList.
    @param queues queue type to query for. 
    Values for season and queues can be found in search.GameConstants.QueueType and search.GameConstants.SeasonId
    '''
    def __init__(self,gameinfo, summonerName, maxMatches = 100, season = None, queue = None):
        self.matches = []
        summoner = gameinfo.getSummonerByName(summonerName)
        self.summoner = summonerName
        id = summoner['accountId']
        
        for i in range(0, math.floor(maxMatches/100)):
            matchExt = getMatchesFromMatchlist(gameinfo.getMatchlistBySummonerId(id, i*100), gameinfo, season, queue, summonerName)
            self.matches.extend(matchExt)
        if maxMatches%100 != 0:
            self.matches.extend(getMatchesFromMatchlist(gameinfo.getMatchlistBySummonerId(id, (math.floor(maxMatches/100))*100, maxMatches), gameinfo, season, queue, summonerName))
        self.season = season
        self.queue = queue
        
    def filter(self, predicate):
        newMatches = []
        for match in self.matches:
            if predicate(match):
                newMatches.append(match)
        return MatchList(newMatches)
    def size(self):
        return len(self.matches)
    
    '''
    Returns a list of 4 WinrateByTimeofDay objects describing the winrates of this summoner within the matches of this MatchList:
    0-6
    6-12
    12-18
    18-24
    '''
    def winrateByTime(self):
        winrates = [WinrateByTimeOfDay(0,0,0,6), WinrateByTimeOfDay(0,0,6,12), WinrateByTimeOfDay(0,0,12,18), WinrateByTimeOfDay(0,0,18,24)]
        for match in self.matches:
            
            time = datetime.fromtimestamp(match.timestamp/1000)
            #print(str(time)+ ' ' + str(match.matchDto['gameId']) + ' '+ str(match.isWin()) )
            ind = math.floor(time.hour/6)
            if match.isWin():
                winrates[ind].won+=1
                winrates[ind].played+=1
            else:
                winrates[ind].played+=1
        return winrates
    '''
    returns a pair of lists, the first describing the winrates of this summoner
    that appear on this summoner's team more than once and the second describing
    the winrates of this summoner against any summoner that appears on the enemy team more than once.
    '''
    def winrateByOtherSummoners(self):
        allyTeamWrDict = dict()
        enemyTeamWrDict = dict()
        for match in self.matches:
            match.extendWrBySummonerDicts(allyTeamWrDict, enemyTeamWrDict)

        winrates = []
        for v in allyTeamWrDict.values():
            if v.played > 1:
                winrates.append(v)
        for v in enemyTeamWrDict.values():
            if v.played > 1:
                winrates.append(v)
            
        return winrates
    