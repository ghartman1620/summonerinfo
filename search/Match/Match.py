'''
Created on Nov 25, 2017

@author: ghart
'''

from search.WinrateTypes.WinrateByOtherSummoner import WinrateByOtherSummoner
from search.GameConstants import Team, Dragon

BLUE_TEAM = 100
RED_TEAM = 200
class Match():
    matchDto = dict()
    timestamp = 0
    timeline = dict()
    summoner = ''
    
    def __init__(self, matchInfo, summonerName, time, tl):
        self.matchDto = matchInfo
        assert 'queueId' in self.matchDto.keys(), 'Match created with a dict passed thats not a MatchDto'
        assert 'seasonId' in self.matchDto.keys(), 'Match created with a dict passed thats not a MatchDto'
        assert 'participants' in self.matchDto.keys(), 'Match created with a dict passed thats not a MatchDto'
        assert 'teams' in self.matchDto.keys(), 'Match created with a dict passed thats not a MatchDto'
        self.summoner = summonerName.lower()
        self.timestamp = time
        self.timeline = tl
        
    def thisSummonersTeamId(self):
        for i in range(0,5):
            if self.matchDto['participantIdentities'][i]['player']['summonerName'].lower() == self.summoner:
                return BLUE_TEAM
            
        return RED_TEAM
    
    '''
    Returns an array of tuples reprenting the dragon kills in this game in chronological order.
    (TEAM, DRAGON) where TEAM is a value of GameConstants.Team and DRAGON is
    a value of GameConstants.Dragon
    
    interesting dragons information
    how much you kill each dragon
    how much time you leave each dragon up for when you take the next
    how much time the enemy leaves each dragon up for when they take next
    % you get each dragon
    % you get the first dragon
    % you get the first elder dragon
    what time you get the first dragon on average
    what time the enemy gets the first dragon from you on average
    
    is using this tuple here good? or is it better to have some DragonKill type
    that has the three fields team dragontype and timestamp
    pro: eaiser to read
    con: harder to write, need import everywhere its used (views,matchlist)
    '''
    def dragons(self):
        dragons = []
        team = self.thisSummonersTeamId()
        for frame in self.timeline['frames']:
            for event in frame['events']:
                if event['type'] == 'ELITE_MONSTER_KILL':
                    if event['monsterType'] == 'DRAGON':
                        #print(str(event))
                        dragons.append( (True if team == BLUE_TEAM and event['killerId'] <= 5
                                              or team == RED_TEAM  and event['killerId'] > 5 else False    
                            ,Dragon.fromStr(event['monsterSubType'])
                            ,event['timestamp']))
        return dragons
    
    def isWin(self):
        
        winningTeam = 0 if self.matchDto['teams'][0]['win'] == 'Win' else 1
        for i in range(0,5):
            if self.matchDto['participantIdentities'][i]['player']['summonerName'].lower() == self.summoner: #name is on 1st team
                if winningTeam == 0: #and 1st team won
                    return True
                else:
                    return False
        #if we get here name is on second team
        if winningTeam == 1: #and second team won
            return True
        return False #else player is on second team and first team won

    def extendWrBySummonerDicts(self, allyWrDict, enemyWrDict):
        team = self.thisSummonersTeamId()
        win = self.isWin()

        for participant in self.matchDto['participantIdentities']:
            if (participant['participantId'] in range(1,6) and team == BLUE_TEAM)\
               or (participant['participantId'] in range(6, 11) and team == RED_TEAM):
                    
                if participant['player']['summonerName'].lower() in allyWrDict.keys():
                    allyWrDict[participant['player']['summonerName'].lower()].played+=1
                    allyWrDict[participant['player']['summonerName'].lower()].won+=int(win)
                else:
                    allyWrDict[participant['player']['summonerName'].lower()] = WinrateByOtherSummoner(1, int(win), participant['player']['summonerName'].lower(), True)
            else:
                if participant['player']['summonerName'].lower() in enemyWrDict.keys():
                    enemyWrDict[participant['player']['summonerName'].lower()].played+=1
                    enemyWrDict[participant['player']['summonerName'].lower()].won+= int(not win)
                else:
                    enemyWrDict[participant['player']['summonerName'].lower()] = WinrateByOtherSummoner(1, int(not win), participant['player']['summonerName'].lower(), False)
            
        