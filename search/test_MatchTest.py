'''
Created on Nov 27, 2017

@author: ghart
'''
from search.GameInfoGetters.GameInfoFactory import getInfoGetter
from search.GameConstants import Team,Dragon
from search.Match.Match import Match
from search.util import DragonKill, TowerKill, ChampionKill
from django.test import TestCase

class MatchTest(TestCase):
    def setUp(self):
        gameinfo = getInfoGetter(True)
        ml = gameinfo.getMatchlistBySummonerId(50164289, 0)
        
        self.match = Match(gameinfo.getMatchById(ml['matches'][0]['gameId']), 'l am eternal', 
                            ml['matches'][0]['timestamp'],
                            gameinfo.getMatchTimelineById(ml['matches'][0]['gameId'])) #loss, mockGame0
        self.match1 = Match(gameinfo.getMatchById(ml['matches'][2]['gameId']), 'l am eternal', 
                            ml['matches'][2]['timestamp'],
                            gameinfo.getMatchTimelineById(ml['matches'][2]['gameId'])) #win, mockGame 2
        self.match2 = Match(gameinfo.getMatchById(ml['matches'][6]['gameId']), 'l am eternal',
                            ml['matches'][6]['timestamp'],
                            gameinfo.getMatchTimelineById(ml['matches'][6]['gameId'])) #win, mockGame6
        self.match3 = Match(gameinfo.getMatchById(ml['matches'][7]['gameId']), 'l am eternal', 
                            ml['matches'][7]['timestamp'],
                            gameinfo.getMatchTimelineById(ml['matches'][7]['gameId'])) #loss, mockGame7
        
    def testBarons(self):
        self.assertEqual(0, self.match.barons(), 'wrong number of barons for mock game 0')
    def testIsWin(self):
        self.assertFalse(self.match.isWin(), 'incorrect match win results produced for mockGame0')
        self.assertTrue(self.match1.isWin(), 'incorrect match win results produced for mockGame2')
    def testExtendWrList(self):
        allyWrDict = dict()
        enemyWrDict = dict()
        self.match2.extendWrBySummonerDicts(allyWrDict, enemyWrDict)
        self.assertEqual(allyWrDict['psrn'].played, 1)
        self.assertEqual(allyWrDict['psrn'].won, 0)
        self.assertEqual(allyWrDict['lilmontaro'].played, 1)
        self.assertEqual(allyWrDict['lilmontaro'].won, 0)
        self.assertEqual(enemyWrDict['itou makoto'].played, 1)
        self.assertEqual(enemyWrDict['itou makoto'].won, 1)
        self.assertEqual(enemyWrDict['muterevised'].played, 1)
        self.assertEqual(enemyWrDict['muterevised'].won, 1)
        
        self.match3.extendWrBySummonerDicts(allyWrDict, enemyWrDict)
        self.assertEqual(allyWrDict['lilmontaro'].played, 2)
        self.assertEqual(allyWrDict['lilmontaro'].won, 1)
        self.assertEqual(enemyWrDict['itou makoto'].played, 2)
        self.assertEqual(enemyWrDict['itou makoto'].won, 1)
        self.assertEqual(enemyWrDict['woahhesgood'].played, 1)
        self.assertEqual(enemyWrDict['itou makoto'].onThisSummonersTeam, False)
        for wr in allyWrDict.values():
            self.assertTrue(wr.onThisSummonersTeam)
        for wr in enemyWrDict.values():
            self.assertFalse(wr.onThisSummonersTeam)    
        for k,v in allyWrDict.items():
            self.assertEqual(k, v.thatSummoner)
        for k,v in enemyWrDict.items():
            self.assertEqual(k, v.thatSummoner)
    def testNumDragons(self):
        self.maxDiff = None
        dragons = self.match.dragons()
        #print(str(dragons))

        self.assertEqual(dragons, \
                         [DragonKill(False, Dragon.AIR, 580304), 
                          DragonKill(True, Dragon.AIR, 1039151), 
                          DragonKill(False, Dragon.EARTH, 1439257)])
        dragons1 = self.match1.dragons()
        #print(str(dragons1))
        self.assertEqual(dragons1, \
                         [DragonKill(True, Dragon.EARTH, 482252), 
                          DragonKill(True, Dragon.AIR, 1011005), 
                          DragonKill(True, Dragon.WATER, 1409648)])
        
    def testTowerList(self):
        towers = self.match.towers()
        self.assertEqual(towers, [
            TowerKill('OUTER_TURRET', 'BOT_LANE', 337714, 200),
            TowerKill('OUTER_TURRET', 'TOP_LANE', 493231, 200),
            TowerKill('OUTER_TURRET', 'MID_LANE', 666492, 200),
            TowerKill('INNER_TURRET', 'BOT_LANE', 820533, 200),
            TowerKill('INNER_TURRET', 'MID_LANE', 982155, 200),
            TowerKill('BASE_TURRET', 'MID_LANE', 995295, 200),
            TowerKill('INNER_TURRET', 'TOP_LANE', 1388517, 200),
            TowerKill('BASE_TURRET', 'TOP_LANE', 1405610, 200),
            TowerKill('NEXUS_TURRET', 'MID_LANE', 1420952, 200),
            TowerKill('NEXUS_TURRET', 'MID_LANE', 1428430, 200),
            TowerKill('BASE_TURRET', 'BOT_LANE', 1471984, 200),
            
        ])
        towers = self.match3.towers()
        self.assertEqual(towers, [
            TowerKill('OUTER_TURRET', 'BOT_LANE', 475913, 100),
            TowerKill('OUTER_TURRET', 'TOP_LANE', 651552, 200),
            TowerKill('OUTER_TURRET', 'MID_LANE', 724186, 100),
            TowerKill('INNER_TURRET', 'BOT_LANE', 803298, 100),
            TowerKill('OUTER_TURRET', 'TOP_LANE', 913147, 100),
            TowerKill('INNER_TURRET', 'TOP_LANE', 939263, 100),
            TowerKill('OUTER_TURRET', 'BOT_LANE', 960806, 200),
            TowerKill('OUTER_TURRET', 'MID_LANE', 1061422, 200),
            TowerKill('INNER_TURRET', 'MID_LANE', 1338571, 100),
            TowerKill('BASE_TURRET', 'BOT_LANE', 1536714, 100),
            TowerKill('INNER_TURRET', 'MID_LANE', 1566798, 200),
            TowerKill('BASE_TURRET', 'MID_LANE', 1759042, 100),
            TowerKill('NEXUS_TURRET', 'MID_LANE', 1789997, 100),
            TowerKill('NEXUS_TURRET', 'MID_LANE', 1803638, 100),
            
        ])
        
    #This test was written based on a faulty dependency. Needs rewriting.
    #for now itll be commented out.
    '''
    def testchampionKillList(self):
        kills = self.match.kills()

        self.assertEqual(kills, [
            ChampionKill(True, 13069, 3302, 776631),
            ChampionKill(False, 8972, 8206, 927917),
            ChampionKill(False, 7964, 7922, 931382),
            ChampionKill(True, 10658, 11152, 1003367),
            ChampionKill(False, 10741, 11145, 1003937),
            ChampionKill(True, 10130, 8170, 1108685),
            ChampionKill(False, 10769, 8726, 1111309),
            ChampionKill(True, 8515, 8927, 1170333),
            ChampionKill(False, 4953, 10426, 1271767),
            ChampionKill(False, 4636, 9069, 1277833),
            ChampionKill(True, 4829, 13382, 1345721),
            ChampionKill(False, 12624, 12608, 1432802),
            ChampionKill(False, 12874, 12856, 1435695)
        ])
    '''
    
        