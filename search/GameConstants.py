'''
Created on Nov 24, 2017

@author: ghart
'''
from enum import Enum
class QueueType(Enum):
    RANKED_SOLODUO = 420
    RANKED_FLEX_SR = 440
    RANKED_FLEX_TT = 470
    NORMAL_DRAFT_SR = 400
    NORMAL_BLIND_SR = 430
    NORMAL_BLIND_TT = 460
    RANKED_DYNAMIC = 410

class SeasonId(Enum):
    PRESEASON_3 = 0
    SEASON_3 = 1
    PRESEASON_2014 = 2
    SEASON_2014 = 3
    PRESEASON_2015 = 4
    SEASON_2015 = 5
    PRESEASON_2016 = 6
    SEASON_2016 = 7
    PRESEASON_2017 = 8
    SEASON_2017 = 9
    
class Team(Enum):
    BLUE = 100
    RED = 200
class Dragon(Enum):
    FIRE = 1
    WATER = 2
    EARTH = 3
    AIR = 4
    ELDER = 5
    @staticmethod
    def fromStr(dragon):
        if dragon == "AIR_DRAGON":
            return Dragon.AIR
        if dragon == "WATER_DRAGON":
            return Dragon.WATER
        if dragon == "FIRE_DRAGON":
            return Dragon.FIRE
        if dragon == "EARTH_DRAGON":
            return Dragon.EARTH
        if dragon == "ELDER_DRAGON":
            return Dragon.ELDER
    @staticmethod
    def types():
        return [Dragon.FIRE, Dragon.WATER, Dragon.EARTH, Dragon.AIR, Dragon.ELDER]
    def __lt__(self, other):
        return self.value < other.value