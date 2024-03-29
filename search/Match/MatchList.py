from search.Match.Match import Match
from search.WinrateTypes.WinrateByTimeOfDay import WinrateByTimeOfDay
from search.GameConstants import Dragon, RolePlayed, championIds, QueueType
from search.util import ChampionKill

from datetime import datetime, timedelta
import math
    
def getMatchesFromMatchlist(matchlist, gameinfo, season, queue, summonerName, championList, rolePlayed):
    matchDetails = []
    if len(matchlist['matches']) == 0: return []
    else:
        for match in matchlist['matches']:
            #this stuff just checks if a match is in the parameter season and queue.
            #if they're none, then no check is made for season or queue.
            isValid = season == None or season.value == match['season']
            if isValid:
                if queue==None:
                    isValid = match['queue'] == QueueType.NORMAL_BLIND_SR.value or \
                              match['queue'] == QueueType.NORMAL_DRAFT_SR.value or \
                              match['queue'] == QueueType.RANKED_SOLODUO.value or \
                              match['queue'] == QueueType.RANKED_FLEX_SR.value or \
                              match['queue'] == QueueType.RANKED_DYNAMIC.value
                      
                else:
                    isValid = match['queue'] == queue.value
            if isValid:
                isValid = championList == None or match['champion'] in championList
            if isValid:
                isValid = rolePlayed == None or RolePlayed.matchListingIsRole(rolePlayed, match)
                    
            
            if isValid:
                matchDetails.append(Match(gameinfo.getMatchById(match['gameId']), summonerName, match['timestamp'],
                                          gameinfo.getMatchTimelineById(match['gameId'])))
    return matchDetails

#utility functions used in generateTowerKillLossDicts()
def insertTKIntoDict(d, event):
    if (event['towerType'], event['laneType']) in d:
        d[(event['towerType'], event['laneType'])][0]+=1
        d[(event['towerType'], event['laneType'])][1].append(event['timestamp'])
    else:
        d[(event['towerType'], event['laneType'])] = [1, [event['timestamp']]]
def changeTimeListsToAverageTimes(d, numGames):
    for k in d.keys():
        #d[k][1] = timedelta(milliseconds=sum(d[k][1])/len(d[k][1]))
        if numGames == 0:
            d[k] = (0, timedelta(seconds=0))
        else:
            if k[0] == 'NEXUS_TURRET':
                d[k] = (100*d[k][0]/numGames/2, timedelta(milliseconds=sum(d[k][1])/len(d[k][1])))
            else:
                d[k] = (100*d[k][0]/numGames,  timedelta(milliseconds=sum(d[k][1])/len(d[k][1])))
    
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
        return str(len(self.matches)) + ' matches analyzed of ' +(('queue: ' + str(self.queue)) if self.queue != None else 'all standard SR modes') + \
            (('season: ' + str(self.season)) if self.season != None else '')
    '''
    Create a new MatchList querying the given gameinfo for games that match the parameter criteria.
    @param gameinfo The GameInfoGetter object to be queried.
    @param summonerName the summoner whose matches are searched for
    @param maxMatches the maximum number of matches that will be queried. NOT the number of matches to be in the matchlist.
    @param season the season to include games from. Note that if a low number of maxMatches is specified and an old season then there will probably be no games in this MatchList.
    @param queue a string valid as passed to QueueType.fromStr()
    @param championList a list of champions as written by the user in the format ChampionName, ChampionName, ChampionName, etc.
    @param rolePlayed a string valid as passed to RolePlayed.fromStr()
    Values for season and queues can be found in search.GameConstants.QueueType and search.GameConstants.SeasonId
    '''
    def __init__(self,gameinfo, summonerName, maxMatches = 100, season = None, queue = None, championList = None, rolePlayed = None):
        self.matches = []
        summoner = gameinfo.getSummonerByName(summonerName)
        self.summoner = summonerName
        self.id = summoner['accountId']
        if rolePlayed != None and rolePlayed != "":
            rolePlayed = RolePlayed.fromStr(rolePlayed)
        if championList != None:
            championList = championList.split(',')
            i=0
            while i < len(championList):
                championList[i] = championList[i].strip()
                try:
                    championList[i] = championIds[championList[i].lower()]
                except KeyError:
                    raise RuntimeError('invalid champion list')
                i+=1
        if queue != None:
            queue = QueueType.fromStr(queue)
        for i in range(0, math.floor(maxMatches/100)):
            matchExt = getMatchesFromMatchlist(gameinfo.getMatchlistBySummonerId(self.id, i*100), gameinfo, season, queue, summonerName,championList, rolePlayed)
            self.matches.extend(matchExt)
        if maxMatches%100 != 0:
            self.matches.extend(getMatchesFromMatchlist(gameinfo.getMatchlistBySummonerId(self.id, 
                                                        (math.floor(maxMatches/100))*100, maxMatches), gameinfo, season, queue, summonerName, championList, rolePlayed))
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
    
    def matchIdList(self):
        '''
        Returns a list of the match ids in the listed matches.
        
        @rtype list of numbers
        @return list of match ids
        '''
        matchids = []
        for match in self.matches:
            matchids.append(match.matchDto['gameId'])
        return matchids
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
    
    def compileKillLists(self):
        '''
        Returns a list that is all of the champion kill lists of the listed
        matches concatenated.
        
        Also changes the coordinates generated by kills() into coordinates from 0 to 510.
        @rtype a list of ChampionKills
        @return the champion kills in all the listed games.
        '''
        kills = []
        for match in self.matches:
            killList = match.kills()
            i= 0
            while i < len(killList):
                #returned by Match x and y are:
                #x - a coordinate x [-120, 14870]
                #y - a coordinate y  [-120, 14980]
                #map x and y to integers in 0 to 510
                #also y needs to get flipped because html coords
                #and ingame coords are different
                killList[i] = ChampionKill(killList[i].isKill,
                                           int(510*(120+killList[i].x)/14990),
                                           510-int(510*(120+killList[i].y)/15100),
                                           killList[i].timestamp)

                i+=1
            kills.extend(killList)
            
        return kills
    
    
    
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
        if len(firstDragonTimes) == 0:
            return timedelta(0)
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
        
        self.contestedDragonTime = timedelta(0) if len(contestedDragonTimes)==0 else timedelta(milliseconds=sum(contestedDragonTimes)/len(contestedDragonTimes))
        self.backToBackDragonTime = timedelta(0) if len(backToBackDragonTimes)==0 else timedelta(milliseconds=sum(backToBackDragonTimes)/len(backToBackDragonTimes))
        self.enemyContestedDragonTime = timedelta(0) if len(enemyContestedDragonTimes)==0 else timedelta(milliseconds=sum(enemyContestedDragonTimes)/len(enemyContestedDragonTimes))
        self.enemyBackToBackDragonTime = timedelta(0) if len(enemyBackToBackDragonTimes)==0 else timedelta(milliseconds=sum(enemyBackToBackDragonTimes)/len(enemyBackToBackDragonTimes))
    
    def generateTowerKillLossDicts(self):
        '''
        Helper function that sets the following attributes:
        self.towerKillWinDict
        self.towerKillLossDict
        self.towerDestroyedWinDict
        self.towerDestroyedlossDict
        '''
        wins = 0
        losses = 0
        towers = [
            ('OUTER_TURRET', 'MID_LANE'),
            ('OUTER_TURRET', 'BOT_LANE'),
            ('OUTER_TURRET', 'TOP_LANE'),
            ('INNER_TURRET', 'MID_LANE'),
            ('INNER_TURRET', 'BOT_LANE'),
            ('INNER_TURRET', 'TOP_LANE'),
            ('BASE_TURRET', 'MID_LANE'),
            ('BASE_TURRET', 'BOT_LANE'),
            ('BASE_TURRET', 'TOP_LANE'),
            ('NEXUS_TURRET', 'MID_LANE')
        ]
        
        self.towerKillWinDict = dict()
        self.towerDestroyedWinDict = dict()
        self.towerKillLossDict = dict()
        self.towerDestroyedLossDict = dict()
        for match in self.matches:
            if match.isWin():
                wins+=1
            else:
                losses+=1
            for frame in match.timeline['frames']:
                if match.isWin():
                    for event in frame['events']:
                        if event['type'] == 'BUILDING_KILL' and event['buildingType'] == 'TOWER_BUILDING':
                            if event['teamId'] == match.teamid:
                                insertTKIntoDict(self.towerDestroyedWinDict, event)
                            else:
                                insertTKIntoDict(self.towerKillWinDict, event)
                else:
                    for event in frame['events']:
                        if event['type'] == 'BUILDING_KILL' and event['buildingType'] == 'TOWER_BUILDING':
                            if event['teamId'] == match.teamid:
                                insertTKIntoDict(self.towerDestroyedLossDict, event)
                            else:
                                insertTKIntoDict(self.towerKillLossDict, event)
        for k in towers:
            if not k in self.towerKillWinDict:
                self.towerKillWinDict[k] = [0, [0]]
            if not k in self.towerKillLossDict:
                self.towerKillLossDict[k] = [0, [0]]
            if not k in self.towerDestroyedWinDict:
                self.towerDestroyedWinDict[k] = [0, [0]]
            if not k in self.towerDestroyedLossDict:
                self.towerDestroyedLossDict[k] = [0, [0]]
                    
        changeTimeListsToAverageTimes(self.towerKillLossDict, losses)
        changeTimeListsToAverageTimes(self.towerKillWinDict, wins)
        changeTimeListsToAverageTimes(self.towerDestroyedLossDict, losses)
        changeTimeListsToAverageTimes(self.towerDestroyedWinDict, wins)

    
    def towersKilledInWins(self):
        '''
        Returns a dictionary mapping pairs of strings (Tower type, lane type)
        to pairs of the % of the time that that tower is killed in this summoner's wins and
        the average time in which this summoner kills those towers in this summoner's wins.

        @rtype dict: {pair(string, string): pair(num, timedelta)}
        @return the % and time in which this summoner kills each tower type in their wins
        '''
        
        try:
            return self.towerKillWinDict
        except AttributeError:
            self.generateTowerKillLossDicts()
            return self.towerKillWinDict
    def towersKilledInLosses(self):
        '''
        Returns a dictionary mapping pairs of strings (Tower type, lane type)
        to pairs of the % of the time that that tower is killed in this summoner's wins and
        the average time in which this summoner kills those towers in this summoner's wins.

        @rtype dict: {pair(string, string): pair(num, timedelta)}
        @return the % and time in which this summoner kills each tower type in their wins
        '''
        
        try:
            return self.towerKillLossDict
        except AttributeError:
            self.generateTowerKillLossDicts()
            return self.towerKillLossDict
    def towersLostInWins(self):
        '''
        Returns a dictionary mapping pairs of strings (Tower type, lane type)
        to pairs of the % of the time that that tower is killed in this summoner's wins and
        the average time in which this summoner kills those towers in this summoner's wins.

        @rtype dict: {pair(string, string): pair(num, timedelta)}
        @return the % and time in which this summoner kills each tower type in their wins
        '''
        
        try:
            return self.towerDestroyedWinDict
        except AttributeError:
            self.generateTowerKillLossDicts()
            return self.towerDestroyedWinDict
    def towersLostInLosses(self):
        '''
        Returns a dictionary mapping pairs of strings (Tower type, lane type)
        to pairs of the % of the time that that tower is killed in this summoner's wins and
        the average time in which this summoner kills those towers in this summoner's wins.

        @rtype dict: {pair(string, string): pair(num, timedelta)}
        @return the % and time in which this summoner kills each tower type in their wins
        '''
        
        try:
            return self.towerDestroyedLossDict
        except AttributeError:
            self.generateTowerKillLossDicts()
            return self.towerDestroyedLossDict
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
    #refactor me!
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
        for wr in winrates:
            wr.pct = float('nan') if wr.played == 0 else int(wr.won/wr.played *10000 )/100
        return winrates
    '''
    returns a pair of lists, the first describing the winrates of this summoner
    that appear on this summoner's team more than once and the second describing
    the winrates of this summoner against any summoner that appears on the enemy team more than once.
    '''
    #refactor me!
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
        for wr in winrates:
            wr.pct = float('nan') if wr.played == 0 else int(wr.won/wr.played *10000 )/100
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

