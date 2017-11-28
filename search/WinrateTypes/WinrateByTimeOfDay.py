'''
Created on Nov 25, 2017

@author: ghart
'''
from search.WinrateTypes.Winrate import Winrate
class WinrateByTimeOfDay(Winrate):
    beginTime = 0
    endTime = 0
    def __init__(self, gamesPlayed, gamesWon, begin, end, ):
        self.beginTime= begin
        self.endTime = end
        super().__init__(gamesPlayed, gamesWon)
    def __str__(self):
        if self.played != 0:
            return '%.2f' % (self.won/self.played*100) + '% winrate from ' + str(self.beginTime) + ':00 to ' + str(self.endTime) +  ':00 over ' + str(self.played) +  ' games.'
        else: 
            return 'no games from ' + str(self.beginTime) + ':00 to ' + str(self.endTime) +  ':00'
    __repr__ = __str__