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
    @staticmethod
    def fromStr(q):
        if q=="BLIND":
            return QueueType.NORMAL_BLIND_SR
        elif q=="DRAFT":
            return QueueType.NORMAL_DRAFT_SR
        elif q=="SOLODUO":
            return QueueType.RANKED_SOLODUO
        elif q=="FLEX":
            return QueueType.RANKED_FLEX_SR

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
class RolePlayed(Enum):
    TOP=1
    JUNGLE=2
    MID=3
    BOT=4
    SUPPORT=5
    @staticmethod
    def matchListingIsRole(role, match):
        if(match['lane']=='MID' and role==RolePlayed.MID) or (match['lane']=='TOP' and role==RolePlayed.TOP) or \
           (match['lane']=='JUNGLE' and role==RolePlayed.JUNGLE) or (match['lane']=='BOTTOM' and match['role']== 'DUO_CARRY' and role==RolePlayed.BOT) or\
           (match['lane']=='BOTTOM' and match['role']== 'DUO_SUPPORT' and role==RolePlayed.SUPPORT):
            return True
        else:
            return False
    @staticmethod
    def fromStr(role):
        if role=='TOP':
            return RolePlayed.TOP
        elif role=='JUNGLE':
            return RolePlayed.JUNGLE
        elif role=='MID':
            return RolePlayed.MID
        elif role=='BOT':
            return RolePlayed.BOT
        else:
            return RolePlayed.SUPPORT
        
championIds = {
'jax':24,
'sona':37,
'tristana':18,
'varus':110,
'fiora':114,
'singed':27,
'tahmkench':223,
'leblanc':7,
'thresh':412,
'karma':43,
'jhin':202,
'rumble':68,
'udyr':77,
'leesin':64,
'yorick':83,
'ornn':516,
'kayn':141,
'kassadin':38,
'sivir':15,
'missfortune':21,
'draven':119,
'yasuo':157,
'kayle':10,
'shaco':35,
'renekton':58,
'hecarim':120,
'fizz':105,
'kogmaw':96,
'maokai':57,
'lissandra':127,
'jinx':222,
'urgot':6,
'fiddlesticks':9,
'galio':3,
'pantheon':80,
'talon':91,
'gangplank':41,
'ezreal':81,
'gnar':150,
'teemo':17,
'annie':1,
'mordekaiser':82,
'azir':268,
'kennen':85,
'riven':92,
'chogath':31,
'aatrox':266,
'poppy':78,
'taliyah':163,
'illaoi':420,
'heimerdinger':74,
'alistar':12,
'xinzhao':5,
'lucian':236,
'volibear':106,
'sejuani':113,
'nidalee':76,
'garen':86,
'leona':89,
'zed':238,
'blitzcrank':53,
'rammus':33,
'velkoz':161,
'caitlyn':51,
'trundle':48,
'kindred':203,
'quinn':133,
'ekko':245,
'nami':267,
'swain':50,
'taric':44,
'syndra':134,
'rakan':497,
'skarner':72,
'braum':201,
'veigar':45,
'xerath':101,
'corki':42,
'nautilus':111,
'ahri':103,
'jayce':126,
'darius':122,
'tryndamere':23,
'janna':40,
'elise':60,
'vayne':67,
'brand':63,
'zoe':142,
'graves':104,
'soraka':16,
'xayah':498,
'karthus':30,
'vladimir':8,
'zilean':26,
'katarina':55,
'shyvana':102,
'warwick':19,
'ziggs':115,
'kled':240,
'khazix':121,
'olaf':2,
'twistedfate':4,
'nunu':20,
'rengar':107,
'bard':432,
'irelia':39,
'ivern':427,
'monkeyking':62,
'ashe':22,
'kalista':429,
'akali':84,
'vi':254,
'amumu':32,
'lulu':117,
'morgana':25,
'nocturne':56,
'diana':131,
'aurelionsol':136,
'zyra':143,
'viktor':112,
'cassiopeia':69,
'nasus':75,
'twitch':29,
'drmundo':36,
'orianna':61,
'evelynn':28,
'reksai':421,
'lux':99,
'sion':14,
'camille':164,
'masteryi':11,
'ryze':13,
'malphite':54,
'anivia':34,
'shen':98,
'jarvaniv':59,
'malzahar':90,
'zac':154,
'gragas':79,
}