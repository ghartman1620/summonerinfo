from datetime import timedelta
from builtins import str
class DragonKill():
    thisSummonerKilled = False
    type = None
    timestamp = 0
    def __init__(self, thisSumm, t, ts):
        self.thisSummonerKilled = thisSumm
        self.type= t
        self.timestamp = ts
    def __str__(self):
        return ('This summoner killed ' if self.thisSummonerKilled else \
                 'The enemy team killed ') + str(self.type)\
                 + ' at ' + str(timedelta(milliseconds=self.timestamp))
    def __eq__(self, other):
        return self.thisSummonerKilled == other.thisSummonerKilled and \
               self.type == other.type and \
               self.timestamp == other.timestamp
    def __repr__(self):
        return self.__str__()
'''
TowerKill has:
tier is 'OUTER_TURRET', 'INNER_TURRET', 'BASE_TURRET' or 'NEXUS_TURRET'
lane is 'MID_LANE', 'BOT_LANE', 'TOP_LANE'p
timestamp is a number
teamid is 100 or 200
'''
class TowerKill():

    def __init__(self, tier, lane, timestamp, teamid):
        self.tier = tier
        self.lane = lane
        self.timestamp = timestamp
        if not (teamid == 100 or teamid == 200):
            raise RuntimeError('TowerKill constructed with a teamid not 100 or 200')
        
        self.teamid = teamid
    def __eq__(self, other):
        return self.tier == other.tier and self.lane == other.lane and self.timestamp == other.timestamp \
            and self.teamid == other.teamid
    def __str__(self):
        return ('blue team' if self.teamid == 100 else 'red team') +' lost ' + self.lane + ' ' + self.tier + ' at ' + str(timedelta(milliseconds=self.timestamp))
    def __repr__(self):
        return self.__str__()
    
'''
ChampionKill has:
isKill - if true, the searching summoner got this kill, if false, they assisted it
x - a coordinate x [-120, 14870]
y - a coordinate y  [-120, 14980]
timestamp - a number
'''
class ChampionKill():
    def __init__(self, isKill, x, y, timestamp):
        self.isKill = isKill
        self.x = x
        self.y= y
        self.timestamp = timestamp
    def __eq__(self, other):
        return self.isKill == other.isKill and self.x == other.x and self.y == other.y and self.timestamp == other.timestamp
    def __str__(self):
        return ('kill' if self.isKill else 'assist') + ' at (' + str(self.x) + ',' + str(self.y) + ')' + ' at ' + str(self.timestamp)
    def __repr__(self):
        return self.__str__()
    
    
    
    