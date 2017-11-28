from search.WinrateTypes.Winrate import Winrate
class WinrateByOtherSummoner(Winrate):
    thatSummoner = ''
    onThisSummonersTeam = False
    def __init__(self, gamesPlayed, gamesWon, thatSum, team):
        self.thatSummoner = thatSum
        self.onThisSummonersTeam = team        
        super().__init__(gamesPlayed, gamesWon)
    def __str__(self):
        if self.played != 0:
            return '%.2f' % (self.won/self.played*100) + '% winrate ' + ('with ' if self.onThisSummonersTeam else 'against ') + str(self.thatSummoner)\
                + ' over ' + str(self.played) + ' games.'
        else: 
            return 'no games ' + 'with ' if self.onThisSummonersTeam else 'against ' + str(self.thatSummoner)
    __repr__ = __str__