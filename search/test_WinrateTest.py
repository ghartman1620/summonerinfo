'''
Created on Nov 25, 2017

@author: ghart
'''
from search.WinrateTypes.WinrateByTimeOfDay import WinrateByTimeOfDay
from django.test import TestCase
class TestWinrateByTimeOfDay(TestCase):
    def testWinrateByTimeOfDayCtorReturnsObjectWithFourFields(self):
        wr = WinrateByTimeOfDay(10, 5, 0, 6)
        self.assertEqual(wr.beginTime, 0, 'beginTime field of wr incorrect')
        self.assertEqual(wr.endTime, 6, 'endTime field of wr incorrect')
        self.assertEqual(wr.won, 5, 'gamesWon field of wr incorrect')
        self.assertEqual(wr.played, 10, 'gamesPlayed field of wr incorrect')
        self.assertEqual(wr.__str__(), '50.00% winrate from 0:00 to 6:00 over 10 games.')
