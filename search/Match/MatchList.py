from search.Match.Match import Match
from search.WinrateTypes.WinrateByTimeOfDay import WinrateByTimeOfDay
from search.WinrateTypes.WinrateByOtherSummoner import WinrateByOtherSummoner
from search.GameConstants import Dragon

from datetime import datetime, timedelta
import math
    
def getMatchesFromMatchlist(matchlist, gameinfo, season, queue, summonerName):
    matchDetails = []
    if len(matchlist['matches']) == 0: return []
    else:
        for match in matchlist['matches']:
            #this stuff just checks if a match is in the parameter season and queue.
            #if they're none, then no check is made for season or queue.
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
    
    #This instance variable holds a list of lists 
    #holding the results of calls to dragons() on every match
    #in this matchlist.
    dragonKillList = []
    #These instance variables hold the result of generateDragonTimeInfo().
    #They are saved this way instead of computed individually on the appropriate
    #function call because they can be computed all at once easily rather than 
    #requiring extra iterations over the dragon kill list by computing them individually.
    backToBackDragons =None # number of dragons you get that were preceded by a team dragon kill
    backToBackDragonTime =None# average time it takes your team to get dragons that are preceded by a team dragon kill
    contestedDragons =None# number of dragons you get that were preceded by an enemy dragon kill
    contestedDragonTime =None# average time it takes your team to get dragons that are preceded by an enemy dragon kill
    enemyBackToBackDragons =None# number of dragons you lose that were preceded by an enemy dragon kill
    enemyBackToBackDragonTime =None# average time it takes the enemy to get dragons that are preceded by an enemy dragon kill
    enemyContestedDragons =None# number of dragons you lose that were preceded by a team dragon kill
    enemyContestedDragonTime =None# average time it takes the enemy to get dragons that are preceded by a team dragon kill
    
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
        self.dragonKillList = []
        for match in self.matches:
            self.dragonKillList.append(match.dragons())
        
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
   
    #pctAllElemental
    
    def pctAllElemental(self):
        ''''      
        @rtype: number
        @return: the percentage of all elemental dragons this summoner kills in the listed matches. 
        '''
        totalTeamElementalKills = 0
        totalEnemyElementalKills = 0
        for dkL in self.dragonKillList:
            for dk in dkL:
                if dk.type != Dragon.ELDER:
                    if dk.thisSummonerKilled: #if this summoner killed this dragon
                            totalTeamElementalKills+=1
                    else:
                        totalEnemyElementalKills+=1
        
        
        if totalTeamElementalKills + totalEnemyElementalKills== 0:
            return float('NaN')
        else:
            return 100*totalTeamElementalKills/(totalTeamElementalKills+totalEnemyElementalKills)
    #pctAllElders
    def pctAllElders(self):
        '''    
        @rtype: number
        @return: the percentage of all elemental dragons this summoner kills in the listed matches. 
        '''
        totalTeamElderKills = 0
        totalEnemyElderKills = 0
        for dkL in self.dragonKillList:
            for dk in dkL:
                if dk.thisSummonerKilled: #if this summoner killed this dragon
                    if dk.type == Dragon.ELDER:
                        totalTeamElderKills+=1
                else:
                    if dk.type == Dragon.ELDER:
                        totalEnemyElderKills+=1

        if totalTeamElderKills + totalEnemyElderKills== 0:
            return float('NaN')
        else:
            return 100*totalTeamElderKills/(totalTeamElderKills+totalEnemyElderKills)
        
    #Returns the percentage of all elemental dragons this summoner kills in the listed matches.
    #pctDragonsKilledByType
    def pctDragonsKilledByType(self):
        '''
        Returns a dictionary that maps up to the five types of dragons to the number of times
        that each was killed as a fraction of the total number of dragon kills by this summoner
        in the listed games.
        
        If no dragons were killed in the listed games, each value in the dictionary will be nan.
        
        @rtype: a dictionary {Dragon : number}
        @return: a mapping of dragon types to their percentage of deaths to this summoner
        '''
        teamDragonKillsByType = dict()
        totalKills = 0
        for dkL in self.dragonKillList:
            for dk in dkL:
                if dk.thisSummonerKilled: #if this summoner killed this dragon
                    if not dk.type in teamDragonKillsByType.keys():
                        teamDragonKillsByType[dk.type] = 0
                    teamDragonKillsByType[dk.type]+=1
                    totalKills+=1
        dragons = dict()
        if totalKills == 0:
            for d in Dragon.types():
                dragons[d] = float('nan')
        for d in Dragon.types():
            if not d in teamDragonKillsByType.keys():
                dragons[d] = 0
            else:
                dragons[d] = 100*teamDragonKillsByType[d]/(totalKills)
        return dragons
    #pctEachDragonType
    def pctEachDragonType(self):
        '''
        Returns a dictionary mapping each dragon type to the percentage of the
        total times that dragon has died to the total times this summoner has killed
        that dragon in the listed games.
        
        If no dragons of a particular type have been killed in the listed games,
        that dragon's key in the dictionary will map to the value nan.
        
        @rtype: a dictionary {Dragon : number}
        @return: mapping of each dragon type to the percentage of the time that summoner kills it
        '''
        teamDragonKillsByType = dict()
        enemyDragonKillsByType = dict()
        for dkL in self.dragonKillList:
            for dk in dkL:
                if dk.thisSummonerKilled: #if this summoner killed this dragon
                    if not dk.type in teamDragonKillsByType.keys():
                        teamDragonKillsByType[dk.type] = 0
                    teamDragonKillsByType[dk.type]+=1
                else:
                    if not dk.type in enemyDragonKillsByType.keys():
                        enemyDragonKillsByType[dk.type] = 0
                    enemyDragonKillsByType[dk.type]+=1
        dragons = dict()
        for d in Dragon.types():
            if d in enemyDragonKillsByType.keys() and d in teamDragonKillsByType.keys():
                dragons[d] = 100*(teamDragonKillsByType[d]/ (teamDragonKillsByType[d] + enemyDragonKillsByType[d]))
            elif d in enemyDragonKillsByType.keys():
                dragons[d] = 0
            elif d in teamDragonKillsByType.keys():
                dragons[d] = 100
            else:
                dragons[d] = float('NaN')
        return dragons
    #pctElementalKilledByOrder
    def pctElementalKilledByOrder(self):
        '''
        Returns a list of the percentage of the nth dragons in the listed games
        that this summoner kills.
        
        @rtype: list of numbers
        @return: list of the percent of the time that this summoner kills the nth elemental drake
        '''
        
        killsOfDragonsByOrder = []
        lostDragonsByOrder = []
        for dkL in self.dragonKillList:
            i = 0
            for dk in dkL:
                if dk.type != Dragon.ELDER:
                    if dk.thisSummonerKilled:
                        while len(killsOfDragonsByOrder) < i+1:
                            killsOfDragonsByOrder.append(0)
                        killsOfDragonsByOrder[i]+=1
                    else:
                        while len(lostDragonsByOrder) < i+1:
                            lostDragonsByOrder.append(0)
                        lostDragonsByOrder[i]+=1

                i +=1
        i = 0
        dragons = []

        #set ds.percentOfDragonsByOrder
        for k,l in zip(killsOfDragonsByOrder, lostDragonsByOrder):
            if k!=0 or l != 0:
                dragons.append(100*k/(k+l))
            i+=1
        #if killsOfDragonsByOrder or lostDragonsByOrder do not ahve the same length
        #those kills should still count (for example if the summoner has never killed the 5th elemental drake in a game,
        #they should know they kill 0% of 5th drakes
        if len(killsOfDragonsByOrder) > len(lostDragonsByOrder):
            while len(dragons) < len(killsOfDragonsByOrder):
                dragons.append(100.00)
        elif len(killsOfDragonsByOrder) < len(lostDragonsByOrder):
            while len(dragons) < len(lostDragonsByOrder):
                dragons.append(0)
        return dragons
    #pctElderKilledByOrder
    def pctElderKilledByOrder(self):
        '''
        Returns a list of the percentage of the nth elder dragons in the listed games
        that this summoner kills.
        
        @rtype: list of numbers
        @return: list of the percent of the time that this summoner kills the nth elder drake
        '''
        killsOfDragonsByOrder = []
        lostDragonsByOrder = []
        for dkL in self.dragonKillList:
            i = 0
            for dk in dkL:
                if dk.type == Dragon.ELDER:
                    if dk.thisSummonerKilled:
                        while len(killsOfDragonsByOrder) < i+1:
                            killsOfDragonsByOrder.append(0)
                        killsOfDragonsByOrder[i]+=1
                    else:
                        while len(lostDragonsByOrder) < i+1:
                            lostDragonsByOrder.append(0)
                        lostDragonsByOrder[i]+=1

                    i +=1
        i = 0
        dragons = []

        #set ds.percentOfDragonsByOrder
        for k,l in zip(killsOfDragonsByOrder, lostDragonsByOrder):
            if k!=0 or l != 0:
                dragons.append(100*k/(k+l))
            i+=1
        #if killsOfDragonsByOrder or lostDragonsByOrder do not ahve the same length
        #those kills should still count (for example if the summoner has never killed the 5th elemental drake in a game,
        #they should know they kill 0% of 5th drakes
        if len(killsOfDragonsByOrder) > len(lostDragonsByOrder):
            while len(dragons) < len(killsOfDragonsByOrder):
                dragons.append(100.00)
        elif len(killsOfDragonsByOrder) < len(lostDragonsByOrder):
            while len(dragons) < len(lostDragonsByOrder):
                dragons.append(0)
        return dragons
    
    
    def firstElementalDragonTime(self):
        '''
        Returns a timedelta object with the average time at which this summoner
        kills the first dragon when they kill it.
        
        @rtype timedelta
        @return average time of first dragon
        '''
        
        firstDragonTimes = []
        for dkL in self.dragonKillList:
            if dkL != [] and dkL[0].thisSummonerKilled:
                firstDragonTimes.append(dkL[0].timestamp)
        
        return timedelta(milliseconds=sum(firstDragonTimes)/len(firstDragonTimes))

    def timePercentEnemyContestedElementalDragons(self):
        '''
        Returns the percent of enemy dragon kills that are preceded by one of your dragon kills 
        and the average time it takes the enemy to secure such dragons.
        
        @rtype (timedelta,num)
        @return a pair - first of the average time for the enemy to kill dragons after you kill them
                the second the percentage of your dragon kills that are followed by enemy dragon kills
        '''
        if self.enemyContestedDragonTime == None:
            self.generateDragonTimeInfo()
        return (self.enemyContestedDragonTime, 100*self.enemyContestedDragons/(self.enemyContestedDragons+self.backToBackDragons))
    def timePercentEnemyBackToBackElementalDragons(self):
        '''
        Returns the percent of enemy dragon kills that are preceded by one of their dragon kills
        and the average time it takes the enemy to secure such dragons.
        
        @rtype (timedelta,num)
        @return a pair - first of the average time for the enemy to kill dragons after they kill them
                the second the percentage of enemy dragon kills that are followed by enemy dragon kills.
        '''
        if self.enemyBackToBackDragonTime == None:
            self.generateDragonTimeInfo()
        return (self.enemyBackToBackDragonTime, 100*self.enemyBackToBackDragons/(self.enemyBackToBackDragons+self.contestedDragons))

    def timePercentContestedElementalDragons(self):
        '''
        Returns the percent of your dragon kills that are preceded by an enemy dragon kill
        and the average time it takes you to secure such dragons.
        
        @rtype (timedelta,num)
        @return a pair - first of the average time for you to kill dragons after the enemy kills them
                the second the percentage of enemy dragon kills that are followed by your dragon kills.
        '''
        if self.contestedDragonTime == None:
            self.generateDragonTimeInfo()
        return (self.contestedDragonTime, 100*self.contestedDragons/(self.contestedDragons+self.enemyBackToBackDragons))
    def timePercentBackToBackElementalDragons(self):
        '''
        Returns the percent of your dragon kills that are followed by another of your dragon kills
        and the average time it takes you to secure such dragons.
        
        @rtype (timedelta,num)
        @return a pair - first of the average time for you to kill dragons after you kill them
                the second the percentage of your dragon kills that are followed by another of your dragon kills.
        '''
        if self.backToBackDragonTime == None:
            self.generateDragonTimeInfo()
        return (self.backToBackDragonTime, 100*self.backToBackDragons/(self.enemyContestedDragons+self.backToBackDragons))
                
    
    def generateDragonTimeInfo(self):
        '''
        This helper function is called by the four above functions that return
        information about dragon kill times. It generates that info.
        
        This function exists because the four above computations are all interdependent
        and by computing one it is trivally easy to compute the others- so we'll do them all at once,
        here.
        Assigns:
        backToBackDragons - number of dragons you get that were preceded by a team dragon kill
        backToBackDragonTime - average time it takes your team to get dragons that are preceded by a team dragon kill
        contestedDragons - number of dragons you get that were preceded by an enemy dragon kill
        contestedDragonTime - average time it takes your team to get dragons that are preceded by an enemy dragon kill
        enemyBackToBackDragons - number of dragons you lose that were preceded by an enemy dragon kill
        enemyBackToBackDragonTime - average time it takes the enemy to get dragons that are preceded by an enemy dragon kill
        enemyContestedDragons - number of dragons you lose that were preceded by a team dragon kill
        enemyContestedDragonTime - average time it takes the enemy to get dragons that are preceded by a team dragon kill
        '''
        backToBackDragonTimes = []
        contestedDragonTimes = []
        enemyBackToBackDragonTimes = []
        enemyContestedDragonTimes = []
        self.backToBackDragons = 0
        self.contestedDragons = 0
        self.enemyBackToBackDragons = 0
        self.enemyContestedDragons = 0
        for dkL in self.dragonKillList:
            i = 0
            while i < len(dkL):
                if dkL[i].type == Dragon.ELDER:
                    break
                if dkL[i].thisSummonerKilled:
                    if i!=0:
                        if dkL[i-1].thisSummonerKilled:
                            self.backToBackDragons +=1
                            backToBackDragonTimes.append(dkL[i].timestamp-dkL[i-1].timestamp)
                        else:
                            self.contestedDragons+=1
                            contestedDragonTimes.append(dkL[i].timestamp-dkL[i-1].timestamp)
                else:
                    if i!=0:
                        if dkL[i-1].thisSummonerKilled:
                            self.enemyContestedDragons+=1
                            enemyContestedDragonTimes.append(dkL[i].timestamp-dkL[i-1].timestamp)
                        else:
                            self.enemyBackToBackDragons+=1
                            enemyBackToBackDragonTimes.append(dkL[i].timestamp-dkL[i-1].timestamp)
                i+=1
        self.contestedDragonTime = timedelta(milliseconds=sum(contestedDragonTimes)/len(contestedDragonTimes))
        self.backToBackDragonTime = timedelta(milliseconds=sum(backToBackDragonTimes)/len(backToBackDragonTimes))
        self.enemyContestedDragonTime = timedelta(milliseconds=sum(enemyContestedDragonTimes)/len(enemyContestedDragonTimes))
        self.enemyBackToBackDragonTime = timedelta(milliseconds=sum(enemyBackToBackDragonTimes)/len(enemyBackToBackDragonTimes))
        
    '''
    THIS code is bad. it is here as a reminder of how not to write code.
    The functionality of this function is implemented by the several functions above that deal with 
    dragon stats. They do this in multiple, single-responsibility functions like they're supposed to.
    This function is just nonsense.
    Don't use it.
    Tyler told me to leave it here.
    def dragonStats(self):
        
        #Initialize the dragon stats object and the dragon kill list 
        #dragonKillList is a list of the dragon kill lists of each game.
        ds = DragonStats()
        dragonKillList = []
        for match in self.matches:
            dragonKillList.append(match.dragons())

        #% of total dragons pie chart is ds.percentTotals
        teamDragonKillsByType = dict()
        enemyDragonKillsByType = dict()
        totalEnemyElementalKills = 0
        totalEnemyElderKills = 0
        totalTeamElementalKills = 0
        totalTeamElderKills = 0
        for dkL in dragonKillList:
            for dk in dkL:
                if dk.thisSummonerKilled: #if this summoner killed this dragon
                    if dk.type != Dragon.ELDER:
                        totalTeamElementalKills+=1
                    else:
                        totalTeamElderKills+=1
                    if not dk.type in teamDragonKillsByType.keys():
                        teamDragonKillsByType[dk.type] = 0
                    teamDragonKillsByType[dk.type]+=1
                else:
                    if dk.type != Dragon.ELDER:
                        totalEnemyElementalKills+=1
                    else:
                        totalEnemyElderKills+=1
                    if not dk.type in enemyDragonKillsByType.keys():
                        enemyDragonKillsByType[dk.type] = 0
                    enemyDragonKillsByType[dk.type]+=1
        
        #Getting the total percent of all drakes that die in this summoners' games that this summoner kills.
        #Elemental and elder.
        if totalTeamElementalKills + totalEnemyElementalKills== 0:
            ds.percentOfAllElementalDragonsKilledByThisSummoner = float('NaN')
        else:
            ds.percentOfAllElementalDragonsKilledByThisSummoner = 100*totalTeamElementalKills/(totalTeamElementalKills+totalEnemyElementalKills)
        if totalTeamElderKills + totalEnemyElderKills == 0:
            ds.percentOfAllElderDragonsKilledByThisSummoner = float('NaN')
        else:
            ds.percentOfAllElderDragonsKilledByThisSummoner = 100*totalTeamElderKills/(totalEnemyElderKills+totalTeamElderKills)
        #Getting the percent of total dragons killed by this summoner by type
        ds.percentOfTotalDragonsKilledByThisSummonerOfEachType = dict()
        for d in Dragon.types():
            if not d in teamDragonKillsByType.keys():
                ds.percentOfTotalDragonsKilledByThisSummonerOfEachType[d] = 0
            else:
                ds.percentOfTotalDragonsKilledByThisSummonerOfEachType[d] = 100*teamDragonKillsByType[d]/(totalTeamElementalKills+totalTeamElderKills)
            
        #Getting the percent of dragons of each type killed by this summoner
        ds.percentOfDragonsOfEachTypeKilledByThisSummoner = dict()
        for d in Dragon.types():
            if d in enemyDragonKillsByType.keys() and d in teamDragonKillsByType.keys():
                ds.percentOfDragonsOfEachTypeKilledByThisSummoner[d] = 100*(teamDragonKillsByType[d]/ (teamDragonKillsByType[d] + enemyDragonKillsByType[d]))
            elif d in enemyDragonKillsByType.keys():
                ds.percentOfDragonsOfEachTypeKilledByThisSummoner[d] = 0
            elif d in teamDragonKillsByType.keys():
                ds.percentOfDragonsOfEachTypeKilledByThisSummoner[d] = 100
            else:
                ds.percentOfDragonsOfEachTypeKilledByThisSummoner[d] = float('NaN')
        #Getting how much of each dragon by order (first dragon, second dragon, etc) this summoner kills
        killsOfDragonsByOrder = []
        lostDragonsByOrder = []
        killsOfElderDragonsByOrder = []
        lostElderDragonsByOrder = []
        for dkL in dragonKillList:
            i = 0
            elemental = True
            for dk in dkL:
                if dk.type == Dragon.ELDER: 
                    i=0
                    elemental = False
                if elemental:
                    if dk.thisSummonerKilled:
                        while len(killsOfDragonsByOrder) < i+1:
                            killsOfDragonsByOrder.append(0)
                        killsOfDragonsByOrder[i]+=1
                    else:
                        while len(lostDragonsByOrder) < i+1:
                            lostDragonsByOrder.append(0)
                        lostDragonsByOrder[i]+=1
                else:
                    if dk.thisSummonerKilled:
                        while len(killsOfElderDragonsByOrder) < i+1:
                            killsOfElderDragonsByOrder.append(0)
                        killsOfElderDragonsByOrder[i]+=1
                    else:
                        while len(lostElderDragonsByOrder) < i+1:
                            lostElderDragonsByOrder.append(0)
                        lostElderDragonsByOrder[i] +=1
                    
                i +=1
        i = 0
        ds.percentOfDragonsKilledByThisSummonerByOrder = []
        ds.percentOfElderDragonsKilledByThisSummonerByOrderByOrder = []

        #set ds.percentOfDragonsByOrder
        for k,l in zip(killsOfDragonsByOrder, lostDragonsByOrder):
            if k!=0 or l != 0:
                ds.percentOfDragonsKilledByThisSummonerByOrder.append(100*k/(k+l))
            i+=1
        #if killsOfDragonsByOrder or lostDragonsByOrder do not ahve the same length
        #those kills should still count (for example if the summoner has never killed the 5th elemental drake in a game,
        #they should know they kill 0% of 5th drakes
        if len(killsOfDragonsByOrder) > len(lostDragonsByOrder):
            while len(ds.percentOfDragonsKilledByThisSummonerByOrder) < len(killsOfDragonsByOrder):
                ds.percentOfDragonsKilledByThisSummonerByOrder.append(100.00)
        elif len(killsOfDragonsByOrder) < len(lostDragonsByOrder):
            while len(ds.percentOfDragonsKilledByThisSummonerByOrder) < len(lostDragonsByOrder):
                ds.percentOfDragonsKilledByThisSummonerByOrder.append(0)
    
        #set ds.percentOfElderDragonsByOrder
        #set it for dragon order for which there's both a kill and a loss
        for k,l in zip(killsOfElderDragonsByOrder, lostElderDragonsByOrder):
            if k!= 0 or l != 0:
                ds.percentOfElderDragonsByOrder.append(100*k/(k+l))
            i+=1
        #if killsOfDragonsByOrder or lostDragonsByOrder do not ahve the same length
        #those kills should still count (for example if the summoner has never killed the 5th elder drake in a game,
        #they should know they kill 0% of 5th drakes
        if len(killsOfElderDragonsByOrder) > len(lostElderDragonsByOrder):
            while len(ds.percentOfElderDragonsKilledByThisSummonerByOrder) < len(killsOfElderDragonsByOrder):
                ds.percentOfElderDragonsKilledByThisSummonerByOrder.append(100.00)
        elif len(killsOfElderDragonsByOrder) < len(lostElderDragonsByOrder):
            while len(ds.percentOfElderDragonsKilledByThisSummonerByOrder) < len(lostElderDragonsByOrder):
                ds.percentOfElderDragonsKilledByThisSummonerByOrder.append(0)

        return ds
        '''
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
    
    def avgBarons(self):
        '''
        Returns the average number of barons this summoner's team kills in their games.

        @rtype: a number
        @return: average baron kills per game
        '''
        if self.size() == 0:
            return 0
        numBarons = 0
        for match in self.matches:
            numBarons+= match.barons()
        return numBarons  /  self.size()
    