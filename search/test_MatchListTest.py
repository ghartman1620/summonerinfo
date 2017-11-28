'''
Created on Nov 24, 2017

@author: ghart
'''

from search.GameInfoGetters.GameInfoFactory import getInfoGetter
from search.GameConstants import QueueType, SeasonId
from search.Match.MatchList import MatchList
from search.Match.Match import Match
from search.WinrateTypes.WinrateByTimeOfDay import WinrateByTimeOfDay
from django.test import TestCase

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
        self.assertTrue(makotoIn, 'ito makoto not in winrates')
        self.assertTrue(montaroIn, 'lilmontaro not in winrates')
        self.assertEqual(len(winrates), 3)
        