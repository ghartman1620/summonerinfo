'''
Created on Nov 24, 2017

@author: ghart
'''

#12/5 TODO: get the mock matches back from the most recent commit
#and use their match ids to get timelines, not the match ids from matchlist
#cause otherwise it'll fuck up all the other tests

from search.GameInfoGetters.GameInfoFactory import getInfoGetter
from search.GameConstants import QueueType, SeasonId
from search.Match.MatchList import MatchList
from search.Match.Match import Match
from search.WinrateTypes.WinrateByTimeOfDay import WinrateByTimeOfDay
from search.GameConstants import Dragon
from django.test import TestCase
import math

class MatchListCtorTest (TestCase):
    gameinfo = None
    matchlist = None
    def setUp(self):
        self.gameinfo = getInfoGetter(True)
    def tearDown(self):
        self.matchlist = None
        self.gameinfo = None

        
    def testCtorReturnsListOfMatchObjects(self):
        self.matchlist = MatchList(self.gameinfo, 'l am eternal')
        msg = 'matches in MatchList object not MatchDtos as described by RGAPI'
        #this isn't an exhuastive list of the things that make something a MatchDto
        
        for match in self.matchlist.matches:
            self.assertTrue(isinstance (match, Match), 'match not a Matchobj')
            self.assertIn('seasonId', match.matchDto.keys(), msg)
            self.assertIn('gameId', match.matchDto.keys(), msg)
            self.assertIn('teams', match.matchDto.keys(), msg)
            self.assertIn('participants', match.matchDto.keys(), msg)
            self.assertIn('frames', match.timeline.keys(), msg)
            self.assertIn('frameInterval', match.timeline.keys(), msg)
        self.assertTrue(len(self.matchlist.matches) > 0, 'no matches in this matchlist')
        
    
    def testCtorFiltersBySeason(self):
        self.matchlist = MatchList(self.gameinfo, 'l am eternal', 100, SeasonId.SEASON_2016)
        for match in self.matchlist.matches:
            self.assertEquals(SeasonId.SEASON_2016.value, match.matchDto['seasonId'])
        self.assertTrue(len(self.matchlist.matches) > 0, 'bad test; got no games. Try increasing maxMatches to search for,'
                            + ' probable cause season comes earlier in time than the latest match searched for by this number of maxMatches')    
        
    def testCtorFiltersByQueue(self):
        self.matchlist = MatchList(self.gameinfo, 'l am eternal', queue=QueueType.RANKED_SOLODUO)
        for match in self.matchlist.matches:
            self.assertEquals(QueueType.RANKED_SOLODUO.value, match.matchDto['queueId'])
        
    def testCtorFiltersByQueueAndSeason(self):
        self.matchlist = MatchList(self.gameinfo, 'l am eternal', 100, SeasonId.SEASON_2016, QueueType.RANKED_DYNAMIC)
        self.assertTrue(len(self.matchlist.matches) > 0, 'bad test; got no games. Try increasing maxMatches to search for,'
                            + ' probable cause season comes earlier in time than the latest match searched for by this number of maxMatches')    
        for match in self.matchlist.matches:  
            self.assertEquals(QueueType.RANKED_DYNAMIC.value, match.matchDto['queueId'])  
            self.assertEquals(SeasonId.SEASON_2016.value, match.matchDto['seasonId'])
class MatchListTest (TestCase):
    def setUp(self):
        gameinfo = getInfoGetter(True)
        self.matchlist = MatchList(gameinfo, 'l am eternal', queue=QueueType.RANKED_SOLODUO)
    def tearDown(self):
        self.matchlist = None
    
    def testMatchListWinrateByTime(self):
        winrates = self.matchlist.winrateByTime()
        self.assertEqual(winrates[0].beginTime, 0, 'incorrect range of times in the WinrateByTimeOfDays returned by MatchList.winrateByTime()')
        self.assertEqual(winrates[0].endTime, 6, 'incorrect range of times in the WinrateByTimeOfDays returned by MatchList.winrateByTime()')
        self.assertEqual(winrates[1].beginTime, 6, 'incorrect range of times in the WinrateByTimeOfDays returned by MatchList.winrateByTime()')
        self.assertEqual(winrates[1].endTime, 12, 'incorrect range of times in the WinrateByTimeOfDays returned by MatchList.winrateByTime()')
        self.assertEqual(winrates[2].beginTime, 12, 'incorrect range of times in the WinrateByTimeOfDays returned by MatchList.winrateByTime()')
        self.assertEqual(winrates[2].endTime, 18, 'incorrect range of times in the WinrateByTimeOfDays returned by MatchList.winrateByTime()')
        self.assertEqual(winrates[3].beginTime, 18, 'incorrect range of times in the WinrateByTimeOfDays returned by MatchList.winrateByTime()')
        self.assertEqual(winrates[3].endTime, 24, 'incorrect range of times in the WinrateByTimeOfDays returned by MatchList.winrateByTime()')
        self.assertEqual(winrates[0].played, 0)
        self.assertEqual(winrates[0].won, 0)
        self.assertEqual(winrates[1].played, 1)
        self.assertEqual(winrates[1].won, 1)
        self.assertEqual(winrates[2].played, 5)
        self.assertEqual(winrates[2].won, 1)
        self.assertEqual(winrates[3].played, 7)
        self.assertEqual(winrates[3].won, 3)
        
        
        
        
    
    def testMatchListWinrateByOtherSummoners(self):
        winrates = self.matchlist.winrateByOtherSummoners()
        eternalIn = False
        makotoIn = False
        montaroIn= False
        
        for wr in winrates:
            if wr.thatSummoner == 'l am eternal':
                eternalIn = True
                self.assertTrue(wr.onThisSummonersTeam, 'bad l am eternal winrate values')
                self.assertEqual(wr.thatSummoner, 'l am eternal', 'bad l am eternal winrate values')
                self.assertEqual(wr.played, 13, 'bad l am eternal winrate values')
                self.assertEqual(wr.won, 5, 'bad l am eternal winrate values')
            if wr.thatSummoner == 'lilmontaro':
                montaroIn = True
                self.assertTrue(wr.onThisSummonersTeam, 'bad lilmontaro winrate values')
                self.assertEqual(wr.thatSummoner, 'lilmontaro', 'bad lilmontaro winrate values')
                self.assertEqual(wr.played, 5, 'bad lilmontaro winrate values')
                self.assertEqual(wr.won, 1, 'bad lilmontaro winrate values')
            if wr.thatSummoner == 'itou makoto':
                makotoIn= True
                self.assertFalse(wr.onThisSummonersTeam, 'bad itou makoto winrate values')
                self.assertEqual(wr.thatSummoner, 'itou makoto', 'bad itou makoto winrate values')
                self.assertEqual(wr.played, 2, 'bad itou makoto winrate values')
                self.assertEqual(wr.won, 1, 'bad itou makoto winrate values')
        self.assertTrue(eternalIn, 'l am eternal not in winrates')
        self.assertTrue(makotoIn, 'itou makoto not in winrates')
        self.assertTrue(montaroIn, 'lilmontaro not in winrates')
        self.assertEqual(len(winrates), 3)
       
    #TODO: write this test. use python shell in root of project directory to generate these stats.
    '''
    def testDragonInfo(self):
        dragonStats = self.matchlist.dragonStats()
        self.assertEqual(dragonStats.percentOfTotalDragonKillsByDragon, {
                (Dragon.FIRE : 27.52),
                (Dragon.EARTH: 29.36),
                (Dragon.AIR  : 20.18),
                (Dragon.WATER: 20.18),
                (Dragon.ELDER:  2.75)})'''
class SmallMatchListTest(TestCase):
    def setUp(self):
        self.matchlist = MatchList(getInfoGetter(True), 'l am eternal', 5)
    def testAvgBarons(self):
        self.assertEqual(.4, self.matchlist.avgBarons())
    def testMatchlistOnlyHas5Matches(self):
        self.assertEqual(5, len(self.matchlist.matches))

    def testPctAllElemental(self):
        self.assertEqual(self.matchlist.pctAllElemental(), 7/(8+7)*100)
    def testPctAllElder(self):
        self.assertTrue(math.isnan(self.matchlist.pctAllElders()))
    def testPctDragonsKilledByType(self):
        self.assertEqual(self.matchlist.pctDragonsKilledByType(), { 
            Dragon.AIR  : 200/7,
            Dragon.FIRE : 100/7,
            Dragon.EARTH: 300/7,
            Dragon.WATER: 100/7,
            Dragon.ELDER: 0     
            })
    def testPctEachDragonType(self):
        pctDragonsOfEachTypeKIlled = self.matchlist.pctEachDragonType()
        dTypes = {
            Dragon.AIR  : 200/5        ,
            Dragon.FIRE : 100/4        ,
            Dragon.EARTH: 300/5        ,
            Dragon.WATER: 100          ,
            Dragon.ELDER: float('NaN') ,
        }
        for k,v in pctDragonsOfEachTypeKIlled.items():
            if k == Dragon.ELDER:
                self.assertTrue(math.isnan(v))
            else:
                self.assertEqual(dTypes[k], v)
    def testPctElementatKilledByOrder(self):
        self.assertEqual(self.matchlist.pctElementalKilledByOrder(), [40.0, 75.0, 25.0, 0.0, 100.0])
    def testPctElderKilledByOrderIsEmpty(self):
        self.assertEqual(self.matchlist.pctElderKilledByOrder(), [])
    
    def testAvgFirstDragonTime(self):
        firstDragon = self.matchlist.firstElementalDragonTime()
        self.assertEqual(firstDragon.seconds, 493)
    def testTimePercentEnemyContDragons(self):
        result = self.matchlist.timePercentEnemyContestedElementalDragons()
        self.assertEqual(result[0].seconds, 384)
        self.assertEqual(result[1], 40)
    def testTimePercentEnemyB2BDragons(self):
        result = self.matchlist.timePercentEnemyBackToBackElementalDragons()
        self.assertEqual(result[0].seconds, 426)
        self.assertEqual(result[1], 60)
    def testTimePercentContDragons(self):
        result = self.matchlist.timePercentContestedElementalDragons()
        self.assertEqual(result[0].seconds, 416)
        self.assertEqual(result[1], 40)
    def testTimePercentB2BDragons(self):
        result = self.matchlist.timePercentBackToBackElementalDragons()
        self.assertEqual(result[0].seconds, 437)
        self.assertEqual(result[1], 60)
         
    #def testTimeFirstDragon(self):
        #self.assertEqual(493, self.matchlist.avgFirstDragonTime())
    '''
    this is a test of a bad function in matchlist - dragonStats()
    see the comments of that function to know why this is commented out.
    def testDragonStatsOnListWithNoElders(self):
        ds = self.matchlist.dragonStats()
        self.maxDiff = None
        self.assertEqual(ds.percentOfAllElementalDragonsKilledByThisSummoner, 7/(8+7)*100)
        self.assertTrue(math.isnan(ds.percentOfAllElderDragonsKilledByThisSummoner))

        
        self.assertDictEqual(ds.percentOfTotalDragonsKilledByThisSummonerOfEachType, { 
            Dragon.AIR  : 200/7,
            Dragon.FIRE : 100/7,
            Dragon.EARTH: 300/7,
            Dragon.WATER: 100/7,
            Dragon.ELDER: 0     
            })
        dTypes = {
            Dragon.AIR  : 200/5        ,
            Dragon.FIRE : 100/4        ,
            Dragon.EARTH: 300/5        ,
            Dragon.WATER: 100          ,
            Dragon.ELDER: float('NaN') ,
        }
        for k,v in ds.percentOfDragonsOfEachTypeKilledByThisSummoner.items():
            if k == Dragon.ELDER:
                self.assertTrue(math.isnan(v))
            else:
                self.assertEqual(dTypes[k], v)
        

        self.assertEqual(ds.percentOfDragonsKilledByThisSummonerByOrder, [40.0, 75.0, 25.0, 0.0, 100.0])
    '''
    