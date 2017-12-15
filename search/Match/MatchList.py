from search.Match.Match import Match
from search.WinrateTypes.WinrateByTimeOfDay import WinrateByTimeOfDay
from search.WinrateTypes.WinrateByOtherSummoner import WinrateByOtherSummoner
from search.util import DragonStats
from search.GameConstants import Dragon

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
                matchDetails.append(Match(gameinfo.getMatchById(match['gameId']), summonerName, match['timestamp'],
                                          gameinfo.getMatchTimelineById(match['gameId'])))
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
    Returns a DragonStats obj. DragonStats has:
    how much you kill each dragon
    how much time you leave each dragon up for when you take the next
    how much time the enemy leaves each dragon up for when they take next
    % you get each dragon
    % you get the first dragon
    % you get the first elder dragon
    what time you get the first dragon on average
    what time the enemy gets the first dragon from you on average
    '''
    def dragonStats(self):
        ds = DragonStats()
        dragonKillList = []
        for match in self.matches:
            dragonKillList.append(match.dragons())
        
        #% of total dragons pie chart is ds.percentTotals
        teamDragonKillsByType = dict()
        enemyDragonKillsByType = dict()
        totalEnemyKills = 0
        totalTeamKills = 0
        for dkL in dragonKillList:
            for dk in dkL:
                if dk[0]: #if this summoner killed this dragon
                    totalTeamKills+=1
                    if not dk[1] in teamDragonKillsByType.keys():
                        teamDragonKillsByType[dk[1]] = 0
                    teamDragonKillsByType[dk[1]]+=1
                else:
                    totalEnemyKills+=1
                    if not dk[1] in enemyDragonKillsByType.keys():
                        enemyDragonKillsByType[dk[1]] = 0
                    enemyDragonKillsByType[dk[1]]+=1
        print(str(dragonKillList)) 
        ds.percentTotals = dict()
        for d in teamDragonKillsByType.keys():
            ds.percentTotals[d] = teamDragonKillsByType[d]/totalTeamKills
            
        #% of each type of dragon your team kills is ds.percentOfEachDragon
        #chart
        ds.percentOfEachDragon = dict()
        #print(str(teamDragonKillsByType))
        #print(str(enemyDragonKillsByType))
        for d in teamDragonKillsByType.keys():
            if d in enemyDragonKillsByType.keys():
                ds.percentOfEachDragonSecured[d] = (teamDragonKillsByType[d]/ (teamDragonKillsByType[d] + enemyDragonKillsByType[d]))
            
        #% of elemental dragons by chronological order is ds.percentOfDragonsByOrder
        killsOfDragonsByOrder = [0 for x in range(10)]
        lostDragonsByOrder = [0 for x in range(10)]
        ds.percentOfDragonsByOrder = [0 for x in range(10)]
        ds.percentOfElderDragonsByOrder = [0 for x in range(10)]
        killsOfElderDragonsByOrder = [0 for x in range(10)]
        lostElderDragonsByOrder = [0 for x in range(10)]
        for dkL in dragonKillList:
            i = 0
            elemental = True
            for dk in dkL:
                if dk[1] == Dragon.ELDER: 
                    i=0
                    elemental = False
                if elemental:
                    if dk[0]:
                        killsOfDragonsByOrder[i]+=1
                    else:
                        lostDragonsByOrder[i]+=1
                else:
                    if dk[0]:
                        killsOfElderDragonsByOrder[i]+=1
                    else:
                        lostElderDragonsByOrder[i] +=1
                    
                i +=1
        i = 0
        #print(str(killsOfDragonsByOrder))
        #print(str(lostDragonsByOrder))
        for k,l in zip(killsOfDragonsByOrder, lostDragonsByOrder):
            if k!=0 or l != 0:
                ds.percentOfDragonsByOrder[i] = 100*k/(k+l)
            i+=1
        if len(killsOfDragonsByOrder) > len(lostDragonsByOrder):
            ds.percentOfDragonsByOrder[len(killsOfDragonsByOrder)] = 100.00
        elif len(killsOfDragonsByOrder) < len(lostDragonsByOrder):
            ds.percentOfDragonsByOrder[len(killsOfDragonsByOrder)] = 0.00
        for k,l in zip(killsOfElderDragonsByOrder, lostElderDragonsByOrder):
            if k!= 0 or l != 0:
                ds.percentOfElderDragonsByOrder[i] = 100*k/(k+l)
            i+=1
        if len(killsOfElderDragonsByOrder) > len(lostElderDragonsByOrder):
            ds.percentOfElderDragonsByOrder[len(killsOfElderDragonsByOrder)] = 100.00
        elif len(killsOfElderDragonsByOrder) < len(lostElderDragonsByOrder):
            ds.percentOfElderDragonsByOrder[len(killsOfElderDragonsByOrder)] = 0.00   
        ds.totalPercent = 100*totalTeamKills/totalEnemyKills
        #print(str(ds.totalPercent))
        #print(str(ds.percentTotals))
        #print(str(ds.percentOfEachDragonSecured))
        #print(str(ds.percentOfDragonsByOrder))
        #print(str(ds.percentOfElderDragonsByOrder))
        return ds
        
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
    