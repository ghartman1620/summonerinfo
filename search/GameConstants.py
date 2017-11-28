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