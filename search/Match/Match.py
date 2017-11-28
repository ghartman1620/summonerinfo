'''
Created on Nov 25, 2017

@author: ghart
'''

from search.WinrateTypes.WinrateByOtherSummoner import WinrateByOtherSummoner

BLUE_TEAM = 100
RED_TEAM = 200
class Match():
    matchDto = dict()
    timestamp = 0
    summoner = ''
    def __init__(self, matchInfo, summonerName, time):
        self.matchDto = matchInfo
        assert 'queueId' in self.matchDto.keys(), 'Match created with a dict passed thats not a MatchDto'
        assert 'seasonId' in self.matchDto.keys(), 'Match created with a dict passed thats not a MatchDto'
        assert 'participants' in self.matchDto.keys(), 'Match created with a dict passed thats not a MatchDto'
        assert 'teams' in self.matchDto.keys(), 'Match created with a dict passed thats not a MatchDto'
        self.summoner = summonerName.lower()
        self.timestamp = time
        
    def thisSummonersTeamId(self):
        for i in range(0,5):
            if self.matchDto['participantIdentities'][i]['player']['summonerName'].lower() == self.summoner:
                return BLUE_TEAM
            
        return RED_TEAM
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
            
        