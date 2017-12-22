'''
Created on Nov 27, 2017

@author: ghart
'''
from search.GameInfoGetters.GameInfoFactory import getInfoGetter
from search.GameConstants import Team,Dragon
from search.Match.Match import Match
from search.util import DragonKill
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
        
    
    def testIsWin(self):
        self.assertFalse(self.match.isWin(), 'incorrect match win results produced for mockGame0')
        self.assertTrue(self.match1.isWin(), 'incorrect match win results produced for mockGame2')
    def testExtendWrList(self):
        allyWrDict = dict()
        enemyWrDict = dict()
        print(self.match2.matchDto['gameId'])
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
        
        
        
        